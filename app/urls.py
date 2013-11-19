from django.conf.urls    import patterns, include, url
from django.contrib      import admin
from app.detective.utils import get_apps

admin.autodiscover()
apps = "|".join( get_apps() )

urlpatterns = patterns('',
    url(r'^admin/', 				   include(admin.site.urls)),
    url(r'^$',                        'app.detective.views.home', name='home'),
    url(r'^404/$',                    'app.detective.views.home', name='404'),
    url(r'^login/$',                  'app.detective.views.home', name='login'),
    url(r'^account/activate/$',       'app.detective.views.home', name='registration_activate'),
    url(r'^search/$',                 'app.detective.views.home', name='search'),
    url(r'^signup/$',                 'app.detective.views.home', name='signup'),
    url(r'^page/$',                   'app.detective.views.home', name='page-list'),
    url(r'^page/\w+/$',               'app.detective.views.home', name='page-single'),
    url(r'^reset_password/$',         'app.detective.views.home', name='reset_password'),
    url(r'^reset_password_confirm/$', 'app.detective.views.home', name='reset_password_confirm'),
    url(r'^%s/$' % apps,              'app.detective.views.home', name='explore'),
    url(r'^%s/\w+/$' % apps,          'app.detective.views.home', name='list'),
    url(r'^%s/\w+/\d+/$' % apps,      'app.detective.views.home', name='single'),
    url(r'^%s/contribute/$' % apps,   'app.detective.views.home', name='contribute'),
    url(r'^api/common/',               include('app.detective.apps.common.urls')),
    url(r'^api/energy/',               include('app.detective.apps.energy.urls')),
    url(r'^partial/(?P<partial_name>([a-zA-Z0-9_\-/]+))\.html$', 'app.detective.views.partial', name='partial'),
    url(r'^account/',                  include('registration.backends.default.urls')),
)

