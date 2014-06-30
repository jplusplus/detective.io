# -*- coding: utf-8 -*-
from .models                          import *
from app.detective.models             import QuoteRequest, Topic, Article
from app.detective.utils              import get_registered_models
from app.detective.topics.common.user import UserResource
from tastypie                         import fields
from tastypie.authorization           import ReadOnlyAuthorization
from tastypie.constants               import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions              import Unauthorized
from tastypie.resources               import ModelResource
from easy_thumbnails.files            import get_thumbnailer
from easy_thumbnails.exceptions       import InvalidImageFormatError
from django.db.models                 import Q
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

    author             = fields.ToOneField(UserResource, 'author', full=True, null=True)
    link               = fields.CharField(attribute='get_absolute_path', readonly=True)
    search_placeholder = fields.CharField(attribute='search_placeholder', readonly=True)

    class Meta:
        queryset  = Topic.objects.all().prefetch_related('author')
        filtering = {'id': ALL, 'slug': ALL, 'author': ALL_WITH_RELATIONS, 'featured': ALL_WITH_RELATIONS, 'module': ALL, 'public': ALL, 'title': ALL}

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
            thumbnailMedium = thumbnailer.get_thumbnail({'size': (300, 200), 'crop': True})
            bundle.data['thumbnail_medium'] = thumbnailMedium.url
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
        object_list = object_list if is_staff else object_list.filter(Q(module__in=can_read)|Q(public=True))

        return object_list


class ArticleResource(ModelResource):
    topic = fields.ToOneField(TopicResource, 'topic', full=True)
    class Meta:
        authorization = ReadOnlyAuthorization()
        queryset      = Article.objects.filter(public=True)
        filtering     = {'slug': ALL, 'topic': ALL_WITH_RELATIONS, 'public': ALL, 'title': ALL}
