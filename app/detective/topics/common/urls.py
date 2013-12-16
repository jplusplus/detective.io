from .resources       import *
from .summary         import SummaryResource
from .user            import UserResource
from .cypher          import CypherResource
from django.conf.urls import patterns, include, url
from tastypie.api     import NamespacedApi

api = NamespacedApi(api_name='v1')
api.register(CountryResource())
api.register(QuoteRequestResource())
api.register(TopicResource())
api.register(SummaryResource())
api.register(CypherResource())
api.register(UserResource())

urlpatterns = patterns('app.detective.topics.common',
    url(r'', include(api.urls, namespace='common')),
)

