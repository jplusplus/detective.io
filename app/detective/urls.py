from django.conf.urls import patterns, include, url

urlpatterns = patterns('api',
    # Energy and Common are the 2 first topics and are threat with attentions
    url(r'^common/', include('app.detective.topics.common.urls', app_name='common')),
    url(r'^energy/', include('app.detective.topics.energy.urls', app_name='energy')),
)