from .resources       import *
from .summary         import SummaryResource
from .user            import UserResource
from .cypher          import CypherResource
from django.conf.urls import patterns, include, url
from tastypie.api     import NamespacedApi

api = NamespacedApi(api_name='v1', urlconf_namespace='common')
api.register(QuoteRequestResource())
api.register(TopicResource())
api.register(SummaryResource())
api.register(CypherResource())
api.register(UserResource())

urlpatterns = patterns('common',
    url(r'', include(api.urls)),
)

