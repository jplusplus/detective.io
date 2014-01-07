from app.middleware.virtualapi import VirtualApi
from django.conf               import settings
from django.conf.urls          import patterns, include, url
from django.contrib            import admin
from urlmiddleware.conf        import middleware, mpatterns

admin.autodiscover()

# This will catch the api calls with a virtual api middleware.
# If needed, this middleware will create the API endpoints and resources
# that match to the given slug.
middlewarepatterns = mpatterns('',
    middleware(r'^api/([a-zA-Z0-9_\-]+)/', VirtualApi),
)

urlpatterns = patterns('',
    url(r'^api/',                             include('app.detective.urls')),
    url(r'^$',                                'app.detective.views.home', name='home'),
    url(r'^404/$',                            'app.detective.views.home', name='404'),
    url(r'^admin/',                            include(admin.site.urls)),
    url(r'^account/',                          include('registration.backends.default.urls')),
    url(r'^account/activate/$',               'app.detective.views.home', name='registration_activate'),
    url(r'^account/reset-password/$',         'app.detective.views.home', name='reset_password'),
    url(r'^account/reset-password-confirm/$', 'app.detective.views.home', name='reset_password_confirm'),
    url(r'^page/$',                           'app.detective.views.home', name='page-list'),
    url(r'^page/\w+/$',                       'app.detective.views.home', name='page-single'),
    url(r'^login/$',                          'app.detective.views.home', name='login'),
    url(r'^search/$',                         'app.detective.views.home', name='search'),
    url(r'^signup/$',                         'app.detective.views.home', name='signup'),
    url(r'^contact-us/$',                     'app.detective.views.home', name='contact-us'),
    url(r'^bulk_upload/$',                    'app.detective.views.home', name='bulk_upload'),
    url(r'^[a-zA-Z0-9_\-/]+/$',               'app.detective.views.home', name='explore'),
    url(r'^[a-zA-Z0-9_\-/]+/\w+/$',           'app.detective.views.home', name='list'),
    url(r'^[a-zA-Z0-9_\-/]+/\w+/\d+/$',       'app.detective.views.home', name='single'),
    url(r'^\w+/contribute/$',                 'app.detective.views.home', name='contribute'),
    url(r'^partial/explore-(?P<topic>([a-zA-Z0-9_\-/]+))\.html$', 'app.detective.views.partial_explore', name='partial_explore'),
    url(r'^partial/(?P<partial_name>([a-zA-Z0-9_\-/]+))\.html$',  'app.detective.views.partial', name='partial'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^public/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

# Handle 404 with the homepage
handler404 = "app.detective.views.not_found"
