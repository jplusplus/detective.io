# -*- coding: utf-8 -*-
from .models                          import *
from app.detective.models             import QuoteRequest, Topic, TopicToken, \
                                             TopicSkeleton, Article, User, \
                                             TopicFactory
from app.detective.utils              import get_registered_models, get_topics_from_request, is_valid_email
from app.detective.topics.common.user import UserResource
from django.conf                      import settings
from django.conf.urls                 import url
from django.core.mail                 import EmailMultiAlternatives
from django.core.urlresolvers         import reverse
from django.db                        import IntegrityError
from django.db.models                 import Q
from django.http                      import Http404, HttpResponse
from django.template                  import Context
from django.template.loader           import get_template
from easy_thumbnails.exceptions       import InvalidImageFormatError
from easy_thumbnails.files            import get_thumbnailer
from tastypie                         import fields, http
from tastypie.authorization           import ReadOnlyAuthorization
from tastypie.constants               import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions              import Unauthorized
from tastypie.resources               import ModelResource
from tastypie.utils                   import trailing_slash
from tastypie.validation              import Validation
from easy_thumbnails.files            import get_thumbnailer
from easy_thumbnails.exceptions       import InvalidImageFormatError
from django.db.models                 import Q

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
        user         = bundle.request.user
        contributors = bundle.obj.get_contributor_group().name
        is_author    = user.is_authenticated() and bundle.obj.author == user
        # Only authenticated user can update there own topic or people from the
        # contributor group
        return is_author or user.groups.filter(name=contributors).exists()

    # Only authenticated user can create topics
    def create_detail(self, object_list, bundle):
        return bundle.request.user.is_authenticated()

    def read_list(self, object_list, bundle):
        if bundle.request.user and bundle.request.user.is_staff:
            return object_list
        else:
            if bundle.request.user:
                read_perms = [perm.split('.')[0] for perm in bundle.request.user.get_all_permissions() if perm.endswith(".contribute_read")]
                q_filter = Q(public=True) | Q(author__id=bundle.request.user.id) | Q(ontology_as_mod__in=read_perms)
            else:
                q_filter = Q(public=True)
            return object_list.filter(q_filter)

    def delete_detail(self, obj_list, bundle):
        return bundle.request.user == bundle.obj.author

class TopicSkeletonAuthorization(ReadOnlyAuthorization):
    def read_list(self, object_list, bundle):
        if bundle.request.user.is_authenticated():
            return object_list
        else:
            raise Unauthorized("Only logged user can retrieve skeletons")

class TopicValidation(Validation):
    # Ways of improvements: use FormValidation instead of Validation and
    # relies on model validation instead of this API validation.
    def is_valid(self, bundle, request=None):
        errors = super(TopicValidation, self).is_valid(bundle, request)
        title = bundle.data['title']
        results = Topic.objects.filter(author=request.user, title__iexact=title)
        if results.exists():
            title = results[0].title
            errors['title'] = (
                u"You already have a topic called {title}, "
                u"please chose another title").format(title=title)
        return errors

class TopicResource(ModelResource):
    author             = fields.ToOneField(UserResource, 'author', full=True, null=True)
    link               = fields.CharField(attribute='get_absolute_path', readonly=True)
    search_placeholder = fields.CharField(attribute='search_placeholder', readonly=True)
    class Meta:
        always_return_data = True
        authorization      = TopicAuthorization()
        validation         = TopicValidation()
        queryset           = Topic.objects.all().prefetch_related('author')
        filtering          = {'id': ALL, 'slug': ALL, 'author': ALL_WITH_RELATIONS, 'featured': ALL_WITH_RELATIONS, 'ontology_as_mod': ALL, 'public': ALL, 'title': ALL}

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
        from_email = settings.DEFAULT_FROM_EMAIL
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
            to_email = user.email
            subject = '[Detective.io] You’ve just been added to an investigation'
            signup = request.build_absolute_uri( reverse("signup") )
            # Get the contributor group for this topic
            contributor_group = topic.get_contributor_group()
            # Check that the user isn't already in this group
            if user.groups.filter(name=contributor_group.name):
                return http.HttpBadRequest("You can't invite someone twice to the same topic.")
            else:
                # Add user to the collaborator group
                contributor_group.user_set.add(user)
        # Unkown username
        except User.DoesNotExist:
            # User doesn't exist and we don't have any email address
            if not is_valid_email(collaborator): return http.HttpNotFound("User unkown.")
            # Send an invitation to create an account
            template = get_template("email.topic-invitation.new-user.txt")
            to_email = collaborator
            subject = '[Detective.io] Someone needs your help on an investigation'
            try:
                # Creates a topictoken
                topicToken = TopicToken(topic=topic, email=collaborator)
                topicToken.save()
            except IntegrityError:
                # Can't invite the same user once!
                return http.HttpBadRequest("You can't invite someone twice to the same topic.")
            signup = request.build_absolute_uri( reverse("signup-invitation", args=[topicToken.token]) )

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

        return HttpResponse("Invitation sent!")

    def dehydrate(self, bundle):
        # Get the model's rules manager
        rulesManager = bundle.request.current_topic.get_rules()
        # Get all registered models
        models = get_registered_models()
        # Filter model to the one under app.detective.topics
        bundle.data["models"] = []
        if bundle.obj.background:
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
            try:
                idx = m.__idx__
            except AttributeError:
                idx = 0
            model = {
                'name': m.__name__,
                'verbose_name': m._meta.verbose_name,
                'verbose_name_plural': m._meta.verbose_name_plural,
                'is_searchable': rulesManager.model(m).all().get("is_searchable", False),
                'index': idx
            }
            bundle.data["models"].append(model)
        return bundle

    def hydrate(self, bundle):
        bundle.data['author'] = bundle.request.user
        bundle.data = TopicFactory.get_topic_bundle(**bundle.data)
        return bundle


class TopicSkeletonResource(ModelResource):
    class Meta:
        authorization = TopicSkeletonAuthorization()
        queryset = TopicSkeleton.objects.all()

    def dehydrate(self, bundle):
        try:
            thumbnailer     = get_thumbnailer(bundle.obj.picture)
            thumbnailSmall  = thumbnailer.get_thumbnail({'size': (60, 60), 'crop': True})
            thumbnailMedium = thumbnailer.get_thumbnail({'size': (350, 240), 'crop': True})
            bundle.data['thumbnail'] = {
                'small' : thumbnailSmall.url,
                'medium': thumbnailMedium.url
            }
        # No image available
        except InvalidImageFormatError:
            bundle.data['thumbnail'] = None

        return bundle

class ArticleResource(ModelResource):
    topic = fields.ToOneField(TopicResource, 'topic', full=True)
    class Meta:
        authorization = ReadOnlyAuthorization()
        queryset      = Article.objects.filter(public=True)
        filtering     = {'slug': ALL, 'topic': ALL_WITH_RELATIONS, 'public': ALL, 'title': ALL}
