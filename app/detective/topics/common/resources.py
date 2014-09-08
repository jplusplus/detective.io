# -*- coding: utf-8 -*-
from .models                          import *
from app.detective.exceptions         import UnavailableImage, NotAnImage
from app.detective.models             import QuoteRequest, Topic, TopicToken, \
                                             TopicSkeleton, Article, User
from app.detective.utils              import get_registered_models, get_topics_from_request, is_valid_email
from app.detective.topics.common.user import UserResource
from django.conf                      import settings
from django.conf.urls                 import url
from django.core.exceptions           import SuspiciousOperation
from django.core.mail                 import EmailMultiAlternatives
from django.core.urlresolvers         import reverse
from django.core.files                import File
from django.core.files.temp           import NamedTemporaryFile
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

import copy
import json
import magic
import re
import urllib2, os
from urlparse import urlparse

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
        authorize = False
        user = bundle.request.user
        if user.is_authenticated():
            profile     = user.detectiveprofileuser
            unlimited   = profile.topics_max() < 0
            under_limit = profile.topics_count() < profile.topics_max()
            authorize   = unlimited or under_limit
        return authorize

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
        user = bundle.request.user
        if user.is_authenticated():
            plan = user.detectiveprofileuser.plan
            return object_list.filter(target_plans__contains=plan)
        else:
            raise Unauthorized("Only logged user can retrieve skeletons")



TopicValidationErrors = {
    'background': {
        'image_unavailable': {
            'code': 0,
            'message': "Passed url is unreachable or cause HTTP errors."
        },
        'oversized_file': {
            'code': 1,
            'message': "Passed url is unreachable or cause HTTP errors."
        },
        'not_an_image': {
            'code': 2,
            'message': "Retrieved file is not an image, please check your URL"
        }
    }
}

class TopicValidation(Validation):

    def is_valid_background_image(self, bundle, request, errors={}):
        def get_error_message(code):
            errors =  TopicValidationErrors['background']
            for error_key in errors.keys():
                error = errors[error_key]
                if error['code'] == code:
                    return error['message']
            return None

        background = bundle.data.get('background', None)
        if type(background) == type(0):
            errors['background_url'] = get_error_message(background)


    def is_valid_topic_title(self, bundle, request, errors={}):
        if request and request.method == 'POST':
            title = bundle.data['title']
            results = Topic.objects.filter(author=request.user, title__iexact=title)
            if results.exists():
                title = results[0].title
                errors['title'] = (
                    u"You already have a topic called {title}, "
                    u"please chose another title"
                ).format(title=title)


    # Ways of improvements: use FormValidation instead of Validation and
    # relies on model validation instead of this API validation.
    def is_valid(self, bundle, request=None):
        errors = super(TopicValidation, self).is_valid(bundle, request)
        self.is_valid_background_image(bundle, request, errors)
        self.is_valid_topic_title(bundle, request, errors)
        return errors

class TopicResource(ModelResource):
    author             = fields.ToOneField(UserResource, 'author', full=True, null=True)
    link               = fields.CharField(attribute='get_absolute_path',  readonly=True)
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
        else:
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

    def download_url(self, url):
        def is_image(tmp):
            mimetype = magic.from_file(tmp.name, True)
            return mimetype.startswith('image')

        if url == None:
            return None
        try:
            name = urlparse(url).path.split('/')[-1]
            tmp_file = NamedTemporaryFile(delete=True)
            tmp_file.write(urllib2.urlopen(url).read())
            tmp_file.flush()
            if not is_image(tmp_file):
                raise NotAnImage()
            return File(tmp_file, name)
        except urllib2.HTTPError:
            raise UnavailableImage()
        except urllib2.URLError:
            raise UnavailableImage()

    def get_skeleton(self, bundle):
        # workaround to avoid SQL lazyness, store topic skeleton in bundle obj.
        topic_skeleton = getattr(bundle, 'skeleton', None)
        if not topic_skeleton:
            topic_skeleton_pk = bundle.data.get('topic_skeleton', None)
            if topic_skeleton_pk:
                topic_skeleton = TopicSkeleton.objects.get(pk=topic_skeleton_pk)
                setattr(bundle, 'skeleton', topic_skeleton)
        return topic_skeleton

    def hydrate_skeleton_title(self, bundle):
        topic_skeleton = self.get_skeleton(bundle)
        if topic_skeleton:
            bundle.data['skeleton_title'] = topic_skeleton.title
        return bundle

    def hydrate_author(self, bundle):
        bundle.data['author'] = bundle.request.user
        return bundle

    def hydrate_background(self, bundle):
        # handle background setting from topic skeleton and from background_url
        # if provided
        topic_skeleton = self.get_skeleton(bundle)
        background_url = bundle.data.get('background_url', None)
        if topic_skeleton and not background_url:
            bundle.data['background'] = topic_skeleton.picture
        else:
            if background_url:
                try:
                    bundle.data['background'] = self.download_url(background_url)
                except UnavailableImage:
                    bundle.data['background'] = TopicValidationErrors['background']['image_unavailable']['code']
                except NotAnImage:
                    bundle.data['background'] = TopicValidationErrors['background']['not_an_image']['code']
            elif bundle.data.get('background', None):
                # we remove from data the previously setted background to avoid
                # further supsicious operation errors
                self.clean_bundle_key('background', bundle)
        return bundle

    def hydrate_about(self, bundle):
        def should_have_credits(about, skeleton):
            if not skeleton:
                return False
            credits = ( skeleton.picture_credits or '')
            return (skeleton and not (credits.lower() in about.lower()))

        topic_skeleton = self.get_skeleton(bundle)
        topic_about = bundle.data.get('about', '')
        if should_have_credits(topic_about, topic_skeleton):
            if topic_about != '':
                topic_about = "%s<br/><br/>" % topic_about

            topic_about = "%s%s" % (topic_about, topic_skeleton.picture_credits)
        bundle.data['about'] = topic_about
        return bundle

    def hydrate_ontology_as_json(self, bundle):
        # feed ontology_as_json attribute when needed
        topic_skeleton = self.get_skeleton(bundle)
        if topic_skeleton:
            bundle.data['ontology_as_json'] = topic_skeleton.ontology
        else:
            self.clean_bundle_key('ontology_as_json', bundle)
        return bundle

    def full_hydrate(self, bundle):
        bundle = super(TopicResource, self).full_hydrate(bundle)
        bundle = self.clean_bundle(bundle)
        return bundle

    def clean_bundle_key(self, key, bundle):
        # safely remove a key from bundle.data dict
        if bundle.data.has_key(key):
            del bundle.data[key]
        return bundle

    def clean_bundle(self, bundle):
        # we remove useless (for topic's model class) keys from bundle
        self.clean_bundle_key('background_url', bundle)
        self.clean_bundle_key('topic_skeleton', bundle)
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
