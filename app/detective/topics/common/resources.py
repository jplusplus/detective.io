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

    author = fields.ToOneField(UserResource, 'author', full=False)

    class Meta:
        queryset = Topic.objects.all()
        filtering = {'slug': ALL, 'author': ALL_WITH_RELATIONS, 'module': ALL, 'public': ALL, 'title': ALL}

    def dehydrate(self, bundle):
        # Get all registered models
        models = get_registered_models()
        in_topic = lambda m: m.__module__.startswith("app.detective.topics.%s." % bundle.obj.module)
        # Filter model to the one under app.detective.topics
        bundle.data["models"] = [ m.__name__ for m in models if in_topic(m) ]
        # Every topic has a single permalink
        bundle.data['link']   = bundle.obj.get_absolute_path()
        return bundle

    def get_object_list(self, request):
        is_staff    = request.user and request.user.is_staff
        object_list = super(TopicResource, self).get_object_list(request)
        # Return only public topics for non-staff user
        return object_list if is_staff else object_list.filter(public=True)


class ArticleResource(ModelResource):
    topic = fields.ToOneField(TopicResource, 'topic', full=True)
    class Meta:
        authorization = ReadOnlyAuthorization()
        queryset      = Article.objects.filter(public=True)
        filtering     = {'slug': ALL, 'topic': ALL_WITH_RELATIONS, 'public': ALL, 'title': ALL}
