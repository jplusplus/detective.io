#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core                  import signing
from django.core.urlresolvers     import reverse
from django.conf.urls             import url
from django.contrib.auth          import authenticate, login, logout
from django.contrib.auth.models   import User
from django.middleware.csrf       import _get_new_csrf_key as get_new_csrf_key
from tastypie.authorization       import Authorization
from tastypie.authentication      import SessionAuthentication, BasicAuthentication, MultiAuthentication
from tastypie.constants           import ALL
from tastypie.resources           import ModelResource
from tastypie.utils               import trailing_slash
from django.contrib.auth.hashers  import make_password

from password_reset.views import Reset
from .message import Recover 

class UserAuthorization(Authorization):
    def read_detail(self, object_list, bundle):
        return True

    def create_detail(self, object_list, bundle):
        return True

    def update_detail(self, object_list, bundle):
        return bundle.request.user.is_staff

    def delete_detail(self, object_list, bundle):
        return bundle.request.user.is_staff


class UserResource(ModelResource):
    class Meta:
        allowed_methods    = ['get', 'post']
        always_return_data = True
        authentication     = MultiAuthentication(BasicAuthentication(), SessionAuthentication())
        authorization      = UserAuthorization()
        fields             = ['first_name', 'last_name', 'username', 'email', 'is_staff', 'password']
        filtering          = {'username': ALL, 'email': ALL}
        queryset           = User.objects.all()
        resource_name      = 'user'

    def prepend_urls(self):
        params = (self._meta.resource_name, trailing_slash())
        return [
            url(r"^(?P<resource_name>%s)/login%s$"                  % params, self.wrap_view('login'),                  name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$'                 % params, self.wrap_view('logout'),                 name='api_logout'),
            url(r'^(?P<resource_name>%s)/status%s$'                 % params, self.wrap_view('status'),                 name='api_status'),
            url(r'^(?P<resource_name>%s)/reset_password%s$'         % params, self.wrap_view('reset_password'),         name='api_reset_password'),
            url(r'^(?P<resource_name>%s)/reset_password_confirm%s$' % params, self.wrap_view('reset_password_confirm'), name='api_reset_password_confirm'),
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
            if user.is_active:
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
            else:
                return self.create_response(request, {
                    'success': False,
                    'error_message': 'Account not activated yet.',
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

    def hydrate(self, bundle):
        bundle.data["is_staff"]     = False
        bundle.data["is_active"]    = False
        bundle.data["is_superuser"] = False
        bundle.data["password"]     = make_password(bundle.data["password"])
        return bundle


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

    def reset_password(self, request, **kwargs):
        """
        Send the reset password email to user with the proper URL.
        """ 
        self.method_check(request, allowed=['post'])
        data    = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        user    = User.objects.get(email=data['email'])
        recover = Recover()
        recover.user = user
        recover.request = request
        recover.email_template_name = 'reset-password.html'
        recover.send_notification()

        return self.create_response(request, { 'success': True })

    def reset_password_confirm(self, request, **kwargs):
        """
        Reset the password if the POST's token parameter is a valid token
        """
        self.method_check(request, allowed=['post'])
        reset        = Reset()
        data         = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        tok          = data['token']
        raw_password = data['password']
        try:
            pk = signing.loads(tok, max_age=reset.token_expires,salt=reset.salt)
        except signing.BadSignature:
            return self.create_response(request, { 'success': False, 'error_message': 'Wrong signature, your token may had expired (valid for 48 hours)' })
        
        user = User.objects.get(pk=pk)
        user.set_password(raw_password)
        user.save()
        return self.create_response(request, { 'success': True })



