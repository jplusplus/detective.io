# -*- coding: utf-8 -*-
from .models                  import *
from app.detective.models     import QuoteRequest
from app.detective.individual import IndividualResource, IndividualMeta
from tastypie.authorization   import ReadOnlyAuthorization
from tastypie.resources       import ModelResource
from tastypie.exceptions      import Unauthorized

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

class CountryResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Country.objects.all().select_related(depth=1)
