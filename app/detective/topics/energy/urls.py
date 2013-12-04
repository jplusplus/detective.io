from .resources       import *
from django.conf.urls import patterns, include, url
from tastypie.api     import Api

api = Api(api_name='v1')
api.register(AmountResource())
api.register(CommentaryResource())
api.register(DistributionResource())
api.register(FundraisingRoundResource())
api.register(OrganizationResource())
api.register(PersonResource())
api.register(PriceResource())
api.register(RevenueResource())
api.register(EnergyProductResource())
api.register(EnergyProjectResource())

urlpatterns = patterns('app.detective.topics.energy',
    url(r'', include(api.urls)),
)