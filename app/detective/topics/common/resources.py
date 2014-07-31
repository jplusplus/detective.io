# -*- coding: utf-8 -*-
from .models                          import *
from app.detective.models             import QuoteRequest, Topic, TopicToken, Article, User
from app.detective.utils              import get_registered_models, is_valid_email
from app.detective.topics.common.user import UserResource, AuthorResource
from django.conf.urls                 import url
from tastypie                         import fields, http
from tastypie.authorization           import ReadOnlyAuthorization
from tastypie.constants               import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions              import Unauthorized
from tastypie.resources               import ModelResource
from tastypie.utils                   import trailing_slash
from easy_thumbnails.files            import get_thumbnailer
from easy_thumbnails.exceptions       import InvalidImageFormatError
from django.core.mail                 import EmailMultiAlternatives
from django.core.urlresolvers         import reverse
from django.db                        import IntegrityError
from django.db.models                 import Q
from django.http                      import Http404, HttpResponse
from django.template                  import Context
from django.template.loader           import get_template

import json
import re

# Only staff can consult QuoteRequests
class QuoteRequestAuthorization(ReadOnlyAuthorization):
    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user and user.is_staff:
            return object_list
        else:
            raise Unauthorized("Only staff user can access to the quote requests.")
    def read_detail(self, object_list, bundle):
        user = bundle.request.user
        return user and user.is_staff
    # But anyone can create a QuoteRequest
    def create_detail(self, object_list, bundle):
        return True

class QuoteRequestResource(ModelResource):
    class Meta:
        authorization = QuoteRequestAuthorization()
        queryset      = QuoteRequest.objects.all()


class TopicAuthorization(ReadOnlyAuthorization):
    def update_detail(self, object_list, bundle):
        contributor_group = bundle.obj.get_contributor_group().name
        isAuthor = bundle.obj.author == bundle.request.user
        # Only authenticated user can update there own topic or people from the contributor group
        return isAuthor or not not bundle.request.user.groups.filter(name=contributor_group)
    # Only authenticated user can create topics
    def create_detail(self, object_list, bundle):
        return bundle.request.user.is_authenticated()

class TopicResource(ModelResource):

    author             = fields.ToOneField(AuthorResource, 'author', full=True, null=True)
    link               = fields.CharField(attribute='get_absolute_path', readonly=True)
    search_placeholder = fields.CharField(attribute='search_placeholder', readonly=True)

    class Meta:
        authorization = TopicAuthorization()
        queryset  = Topic.objects.all().prefetch_related('author')
        filtering = {'id': ALL, 'slug': ALL, 'author': ALL_WITH_RELATIONS, 'featured': ALL_WITH_RELATIONS, 'ontology_as_mod': ALL, 'public': ALL, 'title': ALL}

    def prepend_urls(self):
        params = (self._meta.resource_name, trailing_slash())
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/invite%s$" % params, self.wrap_view('invite'), name="api_invite"),
        ]

    def invite(self, request, **kwargs):
        # only allow POST requests
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        # Get current topic
        topic = Topic.objects.get(id=kwargs["pk"])
        # Check authorization
        bundle = self.build_bundle(obj=topic, request=request)
        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)

        body = json.loads(request.body)
        collaborator = body.get("collaborator", None)
        if collaborator is None:
            return http.HttpBadRequest("Missing 'collaborator' parameter")

        try:
            # Try to get the user by its email
            if is_valid_email(collaborator):
                user = User.objects.get(email=collaborator)
            # Try to get the user by its username
            else:
                # Add existing user
                user = User.objects.get(username=collaborator)
            # You can't invite the author of the topic
            if user == topic.author:
                return http.HttpBadRequest("You can't invite the author of the topic.")
            # Email options for kown user
            template = get_template("email.topic-invitation.existing-user.txt")
            from_email, to_email = 'contact@detective.io', user.email
            subject = '[Detective.io] You’ve just been added to an investigation'
            signup = request.build_absolute_uri( reverse("signup") )
            # Add user to the collaborator group
            topic.get_contributor_group().user_set.add(user)
        # Unkown username
        except User.DoesNotExist:
            # User doesn't exist and we don't have any email address
            if not is_valid_email(collaborator): return http.HttpNotFound("User unkown.")
            # Send an invitation to create an account
            template = get_template("email.topic-invitation.new-user.txt")
            from_email, to_email = 'contact@detective.io', collaborator
            subject = '[Detective.io] Someone needs your help on an investigation'
            try:
                # Creates a topictoken
                topicToken = TopicToken(topic=topic, email=collaborator)
                topicToken.save()
            except IntegrityError:
                # Can't invite the same user once!
                return http.HttpBadRequest("You can't invite someone twice to the same topic.")
            signup = request.build_absolute_uri( reverse("signup", args=[topicToken.token]) )

        # Creates link to the topic
        link = request.build_absolute_uri(topic.get_absolute_path())
        context = Context({
            'topic' : topic,
            'user'  : request.user,
            'link'  : link,
            'signup': signup
        })
        # Render template
        text_content = template.render(context)
        # Prepare and send email
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.send()

        return HttpResponse("Invitation send!")

    def dehydrate(self, bundle):
        from app.detective import register
        # Get the model's rules manager
        rulesManager = register.topics_rules()
        # Get all registered models
        models = get_registered_models()
        # Filter model to the one under app.detective.topics
        bundle.data["models"] = []
        # Create a thumbnail for this topic
        try:
            thumbnailer = get_thumbnailer(bundle.obj.background)
            thumbnailSmall = thumbnailer.get_thumbnail({'size': (60, 60), 'crop': True})
            thumbnailMedium = thumbnailer.get_thumbnail({'size': (300, 200), 'crop': True})
            bundle.data['thumbnail'] = {
                'small' : thumbnailSmall.url,
                'medium': thumbnailMedium.url
            }
        # No image available
        except InvalidImageFormatError:
            bundle.data['thumbnail'] = None

        for m in bundle.obj.get_models():
            model = {
                'name': m.__name__,
                'verbose_name': m._meta.verbose_name,
                'verbose_name_plural': m._meta.verbose_name_plural,
                'is_searchable': rulesManager.model(m).all().get("is_searchable", False)
            }
            bundle.data["models"].append(model)
        return bundle

    def get_object_list(self, request):
        # Check if the user is staff
        is_staff    = request.user and request.user.is_staff

        # Retrieve all groups in which the user is in
        can_read    = []
        if request.user:
            for permission in request.user.get_all_permissions():
                matches = re.match('^(\w+)\.contribute_read$', permission)
                if matches:
                    can_read.append(matches.group(1))

        object_list = super(TopicResource, self).get_object_list(request)
        # Return only topics the user can see
        object_list = object_list if is_staff else object_list.filter(Q(ontology_as_mod__in=can_read)|Q(public=True))

        return object_list


class ArticleResource(ModelResource):
    topic = fields.ToOneField(TopicResource, 'topic', full=True)
    class Meta:
        authorization = ReadOnlyAuthorization()
        queryset      = Article.objects.filter(public=True)
        filtering     = {'slug': ALL, 'topic': ALL_WITH_RELATIONS, 'public': ALL, 'title': ALL}
