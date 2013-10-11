from app.detective.api.resources   import *
from app.detective.apps.energy.api import *
from app.detective.api.user        import UserResource
from app.detective.api.summary     import SummaryResource
from app.detective.api.cypher      import CypherResource
from tastypie.api                  import Api
from django.conf.urls              import patterns, include, url
from neo4django                    import admin


v1_api = Api(api_name='v1')
v1_api.register(AmountResource())
v1_api.register(CommentaryResource())
v1_api.register(CountryResource())
v1_api.register(CypherResource())
v1_api.register(DistributionResource())
v1_api.register(FundraisingRoundResource())
v1_api.register(OrganizationResource())
v1_api.register(PersonResource())
v1_api.register(PriceResource())
v1_api.register(ProductResource())
v1_api.register(ProjectResource())
v1_api.register(RevenueResource())
v1_api.register(SummaryResource())
v1_api.register(UserResource())
# TODO: Isolate
v1_api.register(EnergyProductResource())
v1_api.register(EnergyProjectResource())

admin.autodiscover()

scopes = "|".join(["energy", "health", "politic"])

urlpatterns = patterns('',
    url(r'^$', 				  		  'app.detective.views.home', name='home'),
    url(r'^login/$',	      		  'app.detective.views.home', name='login'),
    url(r'^signup/$',	      		  'app.detective.views.home', name='signup'),
    url(r'^node/$',		  		      'app.detective.views.home', name='overview'),
    url(r'^node/\w+/$',	  		      'app.detective.views.home', name='list'),
    url(r'^node/\w+/\d+/$',	  		  'app.detective.views.home', name='single'),
    url(r'^%s/$' % scopes, 		      'app.detective.views.home', name='explore'),
    url(r'^%s/contribute/$' % scopes, 'app.detective.views.home', name='contribute'),
    url(r'^admin/', 				   include(admin.site.urls)),    
    url(r'^api/',   				   include(v1_api.urls)),    
    url(r'^partial/(?P<partial_name>([a-zA-Z0-9_\-/]+))\.html$', 'app.detective.views.partial', name='partial'),
)

