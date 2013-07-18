from django.conf.urls import patterns, include, url
from neo4django import admin
from tastypie.api import Api
from app.detective.api import AmountResource, CountryResource, FundraisingRoundResource, OrganizationResource, PriceResource, ProjectResource, CommentaryResource, DistributionResource, EnergyProjectResource, InternationalOrganizationResource, PersonResource, RevenueResource, CompanyResource, FundResource, ProductResource, EnergyProductResource, NgoResource

v1_api = Api(api_name='v1')
v1_api.register(AmountResource())
v1_api.register(CommentaryResource())
v1_api.register(CompanyResource())
v1_api.register(CountryResource())
v1_api.register(DistributionResource())
v1_api.register(EnergyProductResource())
v1_api.register(EnergyProjectResource())
v1_api.register(FundraisingRoundResource())
v1_api.register(FundResource())
v1_api.register(InternationalOrganizationResource())
v1_api.register(NgoResource())
v1_api.register(OrganizationResource())
v1_api.register(PersonResource())
v1_api.register(PriceResource())
v1_api.register(ProductResource())
v1_api.register(ProjectResource())
v1_api.register(RevenueResource())

admin.autodiscover()

urlpatterns = patterns('',	
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
)

