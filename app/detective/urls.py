from django.conf.urls import patterns, include, url

urlpatterns = patterns('api',
    # Energy and Common are the 2 first topics and are threat with attentions
    url(r'^detective/common/', include('app.detective.topics.common.urls', namespace='common')),
    url(r'^detective/energy/', include('app.detective.topics.energy.urls', namespace='energy')),
)