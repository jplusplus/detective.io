from .resources       import *
from .summary         import SummaryResource
from .user            import UserResource
from .cypher          import CypherResource
from django.conf.urls import patterns, include, url
from tastypie.api     import Api

api = Api(api_name='v1')
api.register(AmountResource())
api.register(CommentaryResource())
api.register(CountryResource())
api.register(DistributionResource())
api.register(FundraisingRoundResource())
api.register(OrganizationResource())
api.register(PersonResource())
api.register(PriceResource())
api.register(ProductResource())
api.register(ProjectResource())
api.register(RevenueResource())

api.register(SummaryResource())
api.register(CypherResource())
api.register(UserResource())

urlpatterns = patterns('app.detective.apps.base',
    url(r'', include(api.urls)),    
)

