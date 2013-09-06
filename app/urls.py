from app.detective.api.resources import *
from app.detective.api.user      import UserResource
from app.detective.api.summary   import SummaryResource
from app.detective.api.utils     import DetailedApi
from django.conf.urls            import patterns, include, url
from neo4django                  import admin


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
v1_api.register(PersonResource())
v1_api.register(RevenueResource())
v1_api.register(ProductResource())
v1_api.register(EnergyProductResource())
v1_api.register(SummaryResource())

admin.autodiscover()

urlpatterns = patterns('',	
    url(r'^$', 'app.detective.views.home', name='home'),
    url(r'^\w+/contribute$', 'app.detective.views.home', name='contribute'),
    url(r'^\w+/explore$', 'app.detective.views.home', name='explore'),
    url(r'^admin/', include(admin.site.urls)),    
    url(r'^api/', include(v1_api.urls)),    
    url(r'^partial/(?P<partial_name>([a-zA-Z0-9_\-/]+))\.html$', 'app.detective.views.partial', name='partial'),
)

