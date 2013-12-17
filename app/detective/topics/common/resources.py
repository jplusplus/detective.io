# -*- coding: utf-8 -*-
from .models                  import *
from app.detective.models     import QuoteRequest, Topic
from app.detective.individual import IndividualResource, IndividualMeta
from app.detective.utils      import get_registered_models
from django.conf              import settings
from tastypie.authorization   import ReadOnlyAuthorization
from tastypie.constants       import ALL
from tastypie.exceptions      import Unauthorized
from tastypie.resources       import ModelResource

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
    class Meta:
        queryset = Topic.objects.all()
        filtering = {'slug': ALL, 'module': ALL, 'public': ALL, 'title': ALL}

    def dehydrate(self, bundle):
        # Get all registered models
        models = get_registered_models()
        in_topic = lambda m: m.__module__.startswith("app.detective.topics.%s." % bundle.obj.module)
        # Filter model to the one under app.detective.topics
        bundle.data["models"] = [ m.__name__ for m in models if in_topic(m) ]
        return bundle

    def get_object_list(self, request):
        is_staff    = request.user and request.user.is_staff
        object_list = super(TopicResource, self).get_object_list(request)
        # Return only public topics for non-staff user
        return object_list if is_staff else object_list.filter(public=True)

class CountryResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Country.objects.all().select_related(depth=1)
