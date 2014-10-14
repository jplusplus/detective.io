from .resources       import QuoteRequestResource, TopicNestedResource, \
                             TopicSkeletonResource, ArticleResource, \
                             SubscriptionResource, TopicDataSetResource
from .summary         import SummaryResource
from .user            import UserNestedResource, ProfileResource
from .cypher          import CypherResource
from django.conf.urls import patterns, include, url
from tastypie.api     import NamespacedApi
from .jobs            import JobResource

api = NamespacedApi(api_name='v1', urlconf_namespace='common')
api.register(QuoteRequestResource())
api.register(TopicNestedResource())
api.register(TopicSkeletonResource())
api.register(TopicDataSetResource())
api.register(SummaryResource())
api.register(CypherResource())
api.register(ProfileResource())
api.register(UserNestedResource())
api.register(ArticleResource())
api.register(JobResource())
api.register(SubscriptionResource())

urlpatterns = patterns('common',
    url(r'', include(api.urls)),
)

