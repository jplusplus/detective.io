from .resources       import QuoteRequestResource, TopicResource, ArticleResource
from .summary         import SummaryResource
from .user            import UserResource, ProfileResource
from .cypher          import CypherResource
from django.conf.urls import patterns, include, url
from tastypie.api     import NamespacedApi
from .jobs            import JobResource

api = NamespacedApi(api_name='v1', urlconf_namespace='common')
api.register(QuoteRequestResource())
api.register(TopicResource())
api.register(SummaryResource())
api.register(CypherResource())
api.register(ProfileResource())
api.register(UserResource())
api.register(ArticleResource())
api.register(JobResource())

urlpatterns = patterns('common',
    url(r'', include(api.urls)),
)

