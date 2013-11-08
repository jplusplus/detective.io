#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls             import url
from django.contrib.auth          import authenticate, login, logout
from django.contrib.auth.models   import User
from django.contrib.sites.models  import RequestSite
from django.db                    import IntegrityError
from django.middleware.csrf       import _get_new_csrf_key as get_new_csrf_key
from registration.models          import RegistrationProfile
from tastypie.authentication      import Authentication, SessionAuthentication, BasicAuthentication, MultiAuthentication
from tastypie.authorization       import ReadOnlyAuthorization
from tastypie.constants           import ALL
from tastypie.resources           import ModelResource
from tastypie.utils               import trailing_slash
import hashlib
import random


class UserAuthorization(ReadOnlyAuthorization):
    def update_detail(self, object_list, bundle):
        return bundle.request.user and bundle.request.user.is_staff

    def delete_detail(self, object_list, bundle):
        return bundle.request.user and bundle.request.user.is_staff


class UserResource(ModelResource):
    class Meta:
        authentication     = MultiAuthentication(Authentication(), SessionAuthentication(), BasicAuthentication())
        authorization      = UserAuthorization()
        allowed_methods    = ['get', 'post']
        always_return_data = True
        fields             = ['first_name', 'last_name', 'username', 'email', 'is_staff', 'password']
        filtering          = {'username': ALL, 'email': ALL}
        queryset           = User.objects.all()
        resource_name      = 'user'

    def prepend_urls(self):
        params = (self._meta.resource_name, trailing_slash())
        return [
            url(r"^(?P<resource_name>%s)/login%s$"  % params, self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' % params, self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/status%s$' % params, self.wrap_view('status'), name='api_status'),
            url(r'^(?P<resource_name>%s)/signup%s$' % params, self.wrap_view('signup'), name='api_signup'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

        username    = data.get('username', '')
        password    = data.get('password', '')
        remember_me = data.get('remember_me', False)

        if username == '' or password == '':
            return self.create_response(request, {
                'success': False,
                'error_message': 'Missing username or password',
            })

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active and user.is_staff:
                login(request, user)

                # Remember me opt-in
                if not remember_me: request.session.set_expiry(0)

                response = self.create_response(request, {
                    'success' : True,
                    'is_staff': user.is_staff,
                    'username': user.username
                })
                # Create CSRF token
                response.set_cookie("csrftoken", get_new_csrf_key())

                return response
            elif not user.is_active:
                return self.create_response(request, {
                    'success': False,
                    'error_message': 'Account not activated yet.',
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'error_message': 'Account not authorized yet.',
                })
        else:
            return self.create_response(request, {
                'success': False,
                'error_message': 'Incorrect password or username.',
            })

    def dehydrate(self, bundle):
        bundle.data["email"]    = u"☘"
        bundle.data["password"] = u"☘"
        return bundle

    def signup(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

        try:
            user = User.objects.create_user(
                data.get("username"),
                data.get("email"),
                data.get("password")
            )
            # Create an inactive user
            setattr(user, "is_active", False)
            user.save()
        except IntegrityError as e:
            return self.create_response(request, {
                'success': False,
                'error': e
            })
        # Send activation key by email
        activation_key = self.get_activation_key(user.username)
        rp = RegistrationProfile.objects.create(user=user, activation_key=activation_key)
        rp.send_activation_email( RequestSite(request) )
        # Output the answer
        return self.create_response(request, {
            'success': True
        })

    def get_activation_key(self, username=""):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        return hashlib.sha1(salt+username).hexdigest()


    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False })

    def status(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            return self.create_response(request, { 'is_logged': True,  'username': request.user.username })
        else:
            return self.create_response(request, { 'is_logged': False, 'username': '' })