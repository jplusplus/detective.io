from .resources       import *
from django.conf.urls import patterns, include, url
from tastypie.api     import NamespacedApi

api = NamespacedApi(api_name='v1', urlconf_namespace='energy')
api.register(SummaryResource())
api.register(AmountResource())
api.register(CommentaryResource())
api.register(CountryResource())
api.register(DistributionResource())
api.register(FundraisingRoundResource())
api.register(OrganizationResource())
api.register(PersonResource())
api.register(PriceResource())
api.register(RevenueResource())
api.register(EnergyProductResource())
api.register(EnergyProjectResource())

urlpatterns = patterns('energy',
    url(r'', include(api.urls)),
)