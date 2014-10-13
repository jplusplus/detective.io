# -*- coding: utf-8 -*-
from .models                          import *
from app.detective.exceptions         import UnavailableImage, NotAnImage, OversizedFile
from app.detective.models             import QuoteRequest, Topic, TopicToken, \
                                             TopicSkeleton, Article, User, \
                                             Subscription, TopicDataSet
from app.detective.utils              import get_registered_models, get_topics_from_request, is_valid_email
from app.detective.topics.common.user import UserResource, UserNestedResource
from django.conf                      import settings
from django.conf.urls                 import url
from django.core.exceptions           import SuspiciousOperation
from django.core.mail                 import EmailMultiAlternatives
from django.core.urlresolvers         import reverse
from django.core.files                import File
from django.core.files.temp           import NamedTemporaryFile
from django.db                        import IntegrityError
from django.db.models                 import Q
from django.http                      import Http404, HttpResponse, HttpResponseForbidden
from django.template                  import Context
from django.template.loader           import get_template
from easy_thumbnails.exceptions       import InvalidImageFormatError
from easy_thumbnails.files            import get_thumbnailer
from tastypie                         import fields, http
from tastypie.authentication          import SessionAuthentication, BasicAuthentication, MultiAuthentication, Authentication
from tastypie.authorization           import ReadOnlyAuthorization, Authorization
from tastypie.constants               import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions              import Unauthorized
from tastypie.resources               import ModelResource
from tastypie.utils                   import trailing_slash
from tastypie.validation              import Validation
from easy_thumbnails.files            import get_thumbnailer
from easy_thumbnails.exceptions       import InvalidImageFormatError
from django.db.models                 import Q
from django.contrib.auth.models       import Group

import copy
import json
import magic
import re
import urllib2
import os
from urlparse import urlparse

TopicValidationErrors = {
    'background': {
        'unavailable': {
            'code': 0,
            'message': "Passed url is unreachable or cause HTTP errors."
        },
        'oversized_file': {
            'code': 1,
            'message': "Retrieved file is oversized, please enter a new URL."
        },
        'not_an_image': {
            'code': 2,
            'message': "Retrieved file is not an image, please check your URL."
        }
    }
}

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


class TopicSkeletonAuthorization(ReadOnlyAuthorization):
    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated():
            plan = user.detectiveprofileuser.plan
            # no filter for superuser
            if not user.is_superuser:
                q_filter = Q(target_plans__contains=plan)
                if plan == 'free':
                    q_filter = q_filter | Q(enable_teasing=True)
                object_list = object_list.filter(q_filter)
            return object_list
        else:
            raise Unauthorized("Only logged user can retrieve skeletons")

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

class TopicSkeletonNestedResource(ModelResource):
    class Meta:
        authorization = TopicSkeletonAuthorization()
        queryset = TopicSkeleton.objects.all()
        filtering = { 'id' : ALL }
        fields = ("id",)


class TopicDataSetAuthorization(TopicSkeletonAuthorization):
    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated():
            plan = user.detectiveprofileuser.plan
            # no filter for superuser
            if not user.is_superuser:
                q_filter = Q(target_plans__contains=plan)
                object_list = object_list.filter(q_filter)
            return object_list
        else:
            raise Unauthorized("Only logged user can retrieve skeletons")


class TopicDataSetResource(ModelResource):
    skeletons = fields.ToManyField(TopicSkeletonNestedResource, 'target_skeletons', full=True)
    plans = fields.ListField(attribute='selected_plans')

    class Meta:
        authorization = TopicDataSetAuthorization()
        queryset = TopicDataSet.objects.all()
        excludes = ["zip_file", "target_skeletons", "target_plans"]
        filtering = {
            'skeletons' : ALL_WITH_RELATIONS
        }

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

class TopicValidation(Validation):

    def is_valid_background_image(self, bundle, request, errors={}):
        def get_error(code):
            topic_errors =  TopicValidationErrors['background']
            for error_key in topic_errors.keys():
                error = topic_errors[error_key]
                if error['code'] == code:
                    return error_key, error
            return None, None

        background = bundle.data.get('background', None)
        if type(background) == type(0):
            key, error = get_error(background)
            errors['background_url'] = {}
            errors['background_url'][key] = error


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
        user      = bundle.request.user
        skeleton  = TopicSkeleton.objects.get(title=bundle.data['skeleton_title'])
        if user.is_authenticated():
            profile     = user.detectiveprofileuser
            unlimited   = profile.topics_max()   < 0
            under_limit = profile.topics_count() < profile.topics_max()
            authorize   = unlimited or under_limit
            authorize   = authorize and (profile.plan in skeleton.target_plans)
        return authorize

    def get_read_permissions(self, user):
        return [perm.split('.')[0] for perm in user.get_all_permissions() if perm.endswith(".contribute_read")]

    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated() and user.is_staff:
            result_list =  object_list
        else:
            if user.is_authenticated():
                read_perms = self.get_read_permissions(user)
                q_filter = Q(public=True) | Q(author__id=user.id) | Q(ontology_as_mod__in=read_perms)
            else:
                q_filter = Q(public=True)
            result_list =  object_list.filter(q_filter)
        return result_list

    def read_detail(self, object_list, bundle):
        authorized = False
        user = bundle.request.user
        obj  = bundle.obj
        if user.is_authenticated() and user.is_staff:
            authorized = True
        else:
            if user.is_authenticated():
                read_perms = self.get_read_permissions(user)
                has_read_perms = obj.ontology_as_mod in read_perms
                is_author  = obj.author == user
                authorized = obj.public or has_read_perms or is_author
            else:
                authorized = obj.public

        return authorized

    def delete_detail(self, obj_list, bundle):
        return bundle.request.user == bundle.obj.author


class TopicNestedResource(ModelResource):
    author             = fields.ToOneField(UserNestedResource, 'author', full=True, null=True)
    link               = fields.CharField(attribute='get_absolute_path',  readonly=True)
    search_placeholder = fields.CharField(attribute='search_placeholder', readonly=True)
    dataset = fields.ToOneField(TopicDataSetResource, 'dataset', full=False, null=True)

    class Meta:
        resource_name      = 'topic'
        always_return_data = True
        authorization      = TopicAuthorization()
        authentication     = MultiAuthentication(Authentication(), BasicAuthentication(), SessionAuthentication())

        validation         = TopicValidation()
        queryset           = Topic.objects.all().prefetch_related('author')
        filtering          = {'id': ALL, 'slug': ALL, 'author': ALL_WITH_RELATIONS, 'featured': ALL_WITH_RELATIONS, 'ontology_as_mod': ALL, 'public': ALL, 'title': ALL}

    def prepend_urls(self):
        params = (self._meta.resource_name, trailing_slash())
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/invite%s$" % params, self.wrap_view('invite'), name="api_invite"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/leave%s$"  % params, self.wrap_view('leave'),  name="api_leave"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/collaborators%s$"  % params, self.wrap_view('list_collaborators'),  name="api_list_collaborators"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/administrators%s$"  % params, self.wrap_view('list_administrators'),  name="api_list_administrators"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/grant-admin%s$" % params, self.wrap_view('grant_admin'), name="api_grant_admin")
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

    # opposite of invite: a user want to leave a topic
    def leave(self,  request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        topic = Topic.objects.get(id=kwargs["pk"])

        body = json.loads(request.body)
        collaborator = body.get("collaborator", None)
        if collaborator != None:
            # Check authorization
            bundle = self.build_bundle(obj=topic, request=request)
            self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
            collaborator = User.objects.get(pk=collaborator)

        user  = collaborator or request.user
        contributors = topic.get_contributor_group()
        potential_user = contributors.user_set.filter(pk=user.pk)
        if potential_user.exists():
            # remove user from contributor group
            contributors.user_set.remove(user)
            return HttpResponse(u"{username} successfuly left {topic} contributors.".format(
                username=user.username, topic=topic.title))
        else:
            return HttpResponseForbidden("You are not a contributor of this topic.")

    def list_collaborators(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        bundles = self.get_collaborators(request, kwargs['pk'])

        return self.create_response(request, bundles)

    def list_administrators(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        bundles = self.get_collaborators(request, kwargs['pk'], True)

        return self.create_response(request, bundles)

    def get_collaborators(self, request, topic_id, admin=False):
        ur = UserResource()

        topic = Topic.objects.get(id=topic_id)
        if admin:
            users = Group.objects.get(name="{topic_id}_administrator".format(topic_id=topic.ontology_as_mod)).user_set.all()
        else:
            users = topic.get_contributor_group().user_set.all()

        bundles = []
        for user in users:
            bundle = ur.build_bundle(obj=user, request=request)
            bundles.append(ur.full_dehydrate(bundle, for_list=True))

        return bundles

    def grant_admin(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        topic = Topic.objects.get(id=kwargs["pk"])
        body = json.loads(request.body)
        grant = body['grant']
        collaborator = body['collaborator']

        try:
            collaborator = topic.get_contributor_group().user_set.get(pk=collaborator['id'])
            admin_group = Group.objects.get(name="{topic_id}_administrator".format(topic_id=topic.ontology_as_mod))
            if grant:
                collaborator.groups.add(admin_group)
                collaborator.save()
            else:
                admin_group.user_set.remove(collaborator)
                admin_group.save()
            return HttpResponse()
        except User.DoesNotExist:
            return Http404()

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
        tmp_file = None
        def is_image(tmp):
            mimetype = magic.from_file(tmp.name, True)
            return mimetype.startswith('image')

        def is_oversized(tmp, url):
            max_size_in_bytes = 1 * 1024 ** 2 # 1MB
            file_size = os.stat(tmp.name).st_size
            oversized = file_size > max_size_in_bytes
            return oversized

        if url == None:
            return None
        try:
            name = urlparse(url).path.split('/')[-1]
            tmp_file = NamedTemporaryFile(delete=True)
            tmp_file.write(urllib2.urlopen(url).read())
            tmp_file.flush()
            if not is_image(tmp_file):
                raise NotAnImage()
            if is_oversized(tmp_file, url):
                raise OversizedFile()
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
                    bundle.data['background'] = TopicValidationErrors['background']['unavailable']['code']
                except NotAnImage:
                    bundle.data['background'] = TopicValidationErrors['background']['not_an_image']['code']
                except OversizedFile:
                    bundle.data['background'] = TopicValidationErrors['background']['oversized_file']['code']

            elif bundle.data.get('background', None):
                # we remove from data the previously setted background to avoid
                # further supsicious operation errors
                self.clean_bundle_key('background', bundle)
        return bundle

    def hydrate_about(self, bundle):
        def should_have_credits(bundle, skeleton):
            topic_about    = bundle.data.get('about', '')
            background_url = bundle.data.get('background_url', None)
            if not skeleton:
                return False
            credits = ( skeleton.picture_credits or '')
            return (not background_url) and skeleton and \
                   (not (credits.lower() in topic_about.lower()))

        topic_skeleton = self.get_skeleton(bundle)
        if should_have_credits(bundle, topic_skeleton):
            topic_about = bundle.data.get('about', '')
            if topic_about != '':
                topic_about = "%s<br/><br/>" % topic_about
            bundle.data['about'] = "%s%s" % (topic_about, topic_skeleton.picture_credits)
        return bundle

    def hydrate_ontology_as_json(self, bundle):
        # feed ontology_as_json attribute when needed
        topic_skeleton = self.get_skeleton(bundle)
        if topic_skeleton:
            bundle.data['ontology_as_json'] = topic_skeleton.ontology
        else:
            self.clean_bundle_key('ontology_as_json', bundle)
        return bundle

    def hydrate_dataset(self, bundle):
        if 'dataset' in bundle.data:
            try:
                bundle.data['dataset'] = TopicDataSet.objects.get(pk=bundle.data['dataset'])
            except TopicDataSet.DoesNotExist:
                bundle.data['dataset'] = None
        return bundle

    def full_hydrate(self, bundle):
        bundle = super(TopicNestedResource, self).full_hydrate(bundle)
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

# simpler version of TopicResource, this resource doesn't use the full
# version of User resource (UserNestedResource), this allows us to avoid
# retrieving user profile everywhere (which can slows down a lot of request,
# like UserNestedResource.get_groups for instance)
class TopicResource(TopicNestedResource):
    author = fields.ToOneField(UserResource, 'author', full=True, null=True)
    # make this resource's meta inherit from its parent Meta (to allow filter,
    # authorization, authentication etc.)
    class Meta(TopicNestedResource):
        resource_name = 'topic-simpler'

class ArticleResource(ModelResource):
    topic = fields.ToOneField(TopicResource, 'topic', full=True)
    class Meta:
        authorization = ReadOnlyAuthorization()
        queryset      = Article.objects.filter(public=True)
        filtering     = {'slug': ALL, 'topic': ALL_WITH_RELATIONS, 'public': ALL, 'title': ALL}

class SubscriptionAuthorization(Authorization):
    def read_list(self, object_list, bundle): raise Unauthorized()
    def read_detail(self, object_list, bundle): raise Unauthorized()
    def create_list(self, object_list, bundle): raise Unauthorized()
    def update_list(self, object_list, bundle): raise Unauthorized()
    def update_detail(self, object_list, bundle): raise Unauthorized()
    def delete_list(self, object_list, bundle): raise Unauthorized()
    def delete_detail(self, object_list, bundle): raise Unauthorized()

class SubscriptionResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=False)
    class Meta:
        authorization = SubscriptionAuthorization()
        queryset = Subscription.objects.all()

    def hydrate(self, bundle):
        if bundle.data.has_key('user'):
            if hasattr(bundle.request, 'user') and bundle.data['user'] == bundle.request.user.id:
                bundle.data['user'] = bundle.request.user
            else:
                raise Unauthorized()
        return bundle