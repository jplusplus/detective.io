from django.conf.urls     import patterns, include, url
from django.contrib       import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/common/',                       include('app.detective.topics.common.urls', app_name='common')),
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
    url(r'^\w+/$',                            'app.detective.views.home', name='explore'),
    url(r'^\w+/\w+/$',                        'app.detective.views.home', name='list'),
    url(r'^\w+/\w+/\d+/$',                    'app.detective.views.home', name='single'),
    url(r'^\w+/contribute/$',                 'app.detective.views.home', name='contribute'),
    url(r'^partial/(?P<partial_name>([a-zA-Z0-9_\-/]+))\.html$', 'app.detective.views.partial', name='partial'),
)


# Handle 404 with the homepage
handler404 = "app.detective.views.not_found"
