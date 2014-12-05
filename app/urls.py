from app.middleware.virtualapi import VirtualApi
from app.middleware.storage    import StoreTopic
from app.middleware.storage    import StoreTopicList
from django.conf               import settings
from django.conf.urls          import patterns, include, url
from django.contrib            import admin
from urlmiddleware.conf        import middleware, mpatterns

admin.autodiscover()

# This will catch the api calls with a virtual api middleware.
# If needed, this middleware will create the API endpoints and resources
# that match to the given slug.
middlewarepatterns = mpatterns('',
    middleware(r'^api/([a-zA-Z0-9_\-.]+)/([a-zA-Z0-9_\-]+)/', StoreTopic),
    middleware(r'^api/([a-zA-Z0-9_\-.]+)/([a-zA-Z0-9_\-]+)/', StoreTopicList),
    middleware(r'^api/([a-zA-Z0-9_\-.]+)/([a-zA-Z0-9_\-]+)/', VirtualApi),
)

urlpatterns = patterns('',
    url(r'^api/', include('app.detective.urls')),
    url(r'^$', 'app.detective.views.main', name='main'),
    url(r'^embed/(.*/?)$', 'app.detective.views.embed', name='embed'),
    url(r'^404/$', 'app.detective.views.main', name='404'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('registration.backends.default.urls')),
    url(r'^account/activate/$', 'app.detective.views.main', name='registration_activate'),
    url(r'^account/reset-password-confirm/$', 'app.detective.views.main', name='reset_password_confirm'),
    url(r'^account/reset-password/$', 'app.detective.views.main', name='reset_password'),
    url(r'^page/$', 'app.detective.views.main', name='page-list'),
    url(r'^page/\w+/$', 'app.detective.views.main', name='page-single'),
    url(r'^login/$', 'app.detective.views.main', name='login'),
    url(r'^search/$', 'app.detective.views.main', name='search'),
    url(r'^signup/$', 'app.detective.views.main', name='signup'),
    url(r'^subscribe/$', 'app.detective.views.main', name='subscribe'),
    url(r'^signup/(?P<name>(\w+))/$', 'app.detective.views.main', name='signup-invitation'),
    url(r'^contact-us/$', 'app.detective.views.main', name='contact-us'),
    url(r'^plans/$', 'app.detective.views.main', name='subscriptions'),
    url(r'^job-runner/', include('django_rq.urls')),
    url(r'^proxy/(?P<name>([a-zA-Z0-9_\-/.]+))', 'app.detective.views.proxy',name='proxy'),
    url(r'^(?P<user>[\w\-\.]+)/$', 'app.detective.views.profile', name='user'),
    url(r'^(?P<user>[\w\-\.]+)/create-investigation/$', 'app.detective.views.profile', name='topic-create'),
    url(r'^(?P<user>[\w\-\.]+)/(?P<topic>[\w\-]+)/$', 'app.detective.views.topic', name='explore'),
    url(r'^(?P<user>[\w\-\.]+)/(?P<topic>[\w\-]+)/graph/$', 'app.detective.views.topic', name='explore'),
    url(r'^(?P<user>[\w\-\.]+)/(?P<topic>[\w\-]+)/(?P<type>[\w-]+)/$', 'app.detective.views.entity_list', name='list'),
    url(r'^(?P<user>[\w\-\.]+)/(?P<topic>[\w\-]+)/(?P<type>\w+)/(?P<pk>\d+)/$', 'app.detective.views.entity_details', name='single'),
    url(r'^(?P<user>[\w\-\.]+)/(?P<topic>[\w\-]+)/(?P<type>\w+)/(?P<pk>\d+)/network/$', 'app.detective.views.entity_details', name='single_network'),
    url(r'^(?P<user>[\w\-\.]+)/(?P<topic>[\w\-]+)/contribute/$','app.detective.views.topic', name='contribute'),
    url(r'^(?P<user>[\w\-\.]+)/(?P<topic>[\w\-]+)/contribute/upload/$', 'app.detective.views.topic', name='contribute'),
    url(r'^(?P<user>[\w\-\.]+)/(?P<topic>[\w\-]+)/invite/$', 'app.detective.views.topic', name='invite'),
    url(r'^partial/topic.explore.(?P<topic>([\w\-\.]+))\.html$', 'app.detective.views.partial_explore', name='partial_explore'),
    url(r'^partial/(?P<partial_name>([\w\-\./]+))\.html$', 'app.detective.views.partial', name='partial'),
    url(r'^tinymce/', include('tinymce.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^public/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    ) + urlpatterns

    if getattr(settings, 'USE_DEBUG_TOOLBAR', False):
        import debug_toolbar
        urlpatterns = patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ) + urlpatterns

# Handle 404 with the main page
handler404 = "app.detective.views.not_found"
