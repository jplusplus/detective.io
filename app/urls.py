from django.conf.urls  import patterns, include, url
from neo4django        import admin
from app.detective.api import *


v1_api = DetailedApi(api_name='v1')
v1_api.register(UserResource())
v1_api.register(AmountResource())
v1_api.register(CountryResource())
v1_api.register(FundraisingRoundResource())
v1_api.register(OrganizationResource())
v1_api.register(PriceResource())
v1_api.register(ProjectResource())
v1_api.register(CommentaryResource())
v1_api.register(DistributionResource())
v1_api.register(EnergyProjectResource())
v1_api.register(InternationalOrganizationResource())
v1_api.register(PersonResource())
v1_api.register(RevenueResource())
v1_api.register(CompanyResource())
v1_api.register(GovernmentOrganizationResource())
v1_api.register(ProductResource())
v1_api.register(EnergyProductResource())
v1_api.register(NgoResource())

admin.autodiscover()

urlpatterns = patterns('',	
    url(r'^$', 'app.detective.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),    
    url(r'^api/', include(v1_api.urls)),    
    url(r'^partial/(?P<partial_name>([a-zA-Z0-9_\-/]+))\.html$', 'app.detective.views.partial', name='partial'),
)

