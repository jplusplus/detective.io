from .resources       import *
from .summary         import SummaryResource
from .user            import UserResource
from .cypher          import CypherResource
from django.conf.urls import patterns, include, url
from tastypie.api     import Api

api = Api(api_name='v1')
api.register(CountryResource())
api.register(QuoteRequestResource())
api.register(SummaryResource())
api.register(CypherResource())
api.register(UserResource())

urlpatterns = patterns('app.detective.apps.common',
    url(r'', include(api.urls)),
)

