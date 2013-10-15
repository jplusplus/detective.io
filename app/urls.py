from django.conf.urls              import patterns, include, url
from neo4django                    import admin
from os                            import listdir
from os.path                       import isdir, join

admin.autodiscover()

# Load apps' names 
appsdir = "./app/detective/apps"
apps    = [ name for name in listdir(appsdir) if isdir(join(appsdir, name)) ]
apps    = "|".join(apps)

urlpatterns = patterns('',
    url(r'^admin/', 				   include(admin.site.urls)),    
    url(r'^$',                        'app.detective.views.home', name='home'),
    url(r'^404/$',                    'app.detective.views.home', name='404'),
    url(r'^login/$',                  'app.detective.views.home', name='login'),
    url(r'^search/$',                 'app.detective.views.home', name='search'),
    url(r'^signup/$',                 'app.detective.views.home', name='signup'),
    url(r'^%s/$' % apps,              'app.detective.views.home', name='explore'),
    url(r'^%s/\w+/$' % apps,          'app.detective.views.home', name='list'),
    url(r'^%s/\w+/\d+/$' % apps,      'app.detective.views.home', name='single'),
    url(r'^%s/contribute/$' % apps,   'app.detective.views.home', name='contribute'),
    url(r'^api/common/',               include('app.detective.apps.common.urls')),
    url(r'^api/energy/',               include('app.detective.apps.energy.urls')),
    url(r'^partial/(?P<partial_name>([a-zA-Z0-9_\-/]+))\.html$', 'app.detective.views.partial', name='partial'),
)

