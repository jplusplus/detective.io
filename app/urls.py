# from app.detective.api.user        import UserResource
# from app.detective.api.summary     import SummaryResource
# from app.detective.api.cypher      import CypherResource
from django.conf.urls              import patterns, include, url
from neo4django                    import admin

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
    url(r'^api/base/',                 include('app.detective.apps.base.urls')),
    url(r'^api/energy/',               include('app.detective.apps.energy.urls')),
    url(r'^partial/(?P<partial_name>([a-zA-Z0-9_\-/]+))\.html$', 'app.detective.views.partial', name='partial'),
)

