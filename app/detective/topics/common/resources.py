# -*- coding: utf-8 -*-
from .models                          import *
from app.detective.models             import QuoteRequest, Topic, Article, User
from app.detective.utils              import get_registered_models, is_valid_email
from app.detective.topics.common.user import UserResource, AuthorResource
from django.conf.urls                 import url
from tastypie                         import fields
from tastypie.authorization           import ReadOnlyAuthorization
from tastypie.constants               import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions              import Unauthorized
from tastypie.resources               import ModelResource
from tastypie.utils                   import trailing_slash
from easy_thumbnails.files            import get_thumbnailer
from easy_thumbnails.exceptions       import InvalidImageFormatError
from django.core.mail                 import EmailMultiAlternatives
from django.db.models                 import Q
from django.http                      import Http404, HttpResponse
from django.template.loader           import get_template
from django.template                  import Context

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

class TopicResource(ModelResource):

    author             = fields.ToOneField(AuthorResource, 'author', full=True, null=True)
    link               = fields.CharField(attribute='get_absolute_path', readonly=True)
    search_placeholder = fields.CharField(attribute='search_placeholder', readonly=True)

    class Meta:
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

        topic = Topic.objects.get(id=kwargs["pk"])

        body = json.loads(request.body)
        collaborator = body.get("collaborator", None)
        if collaborator is None:
            raise Exception("Missing 'collaborator' parameter")

        if is_valid_email(collaborator):
            try:
                user = User.objects.get(email=collaborator)
            # Send an invitation to register
            except User.DoesNotExist:
                pass
        else:
            try:
                # Add existing user
                user = User.objects.get(username=collaborator)
            # Unkown username
            except User.DoesNotExist:
                # Nothing yet here!
                raise Http404("Sorry, unkown user.")

        # Creates link to the topic
        link = request.build_absolute_uri(topic.get_absolute_url())
        # Load email template
        template = get_template("email.topic-invitation.existing-user.txt")
        context = Context({ 'topic': topic, 'user': request.user, 'link': link })
        # Render template
        text_content = template.render(context)
        # Prepare and send email
        subject = '[Detective.io] You’ve just been added to an investigation'
        from_email, to_email = 'contact@detective.io', user.email
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.send()
        # Add user to the collaborator group
        topic.get_contributor_group().user_set.add(user)

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
