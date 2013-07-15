from django.conf.urls import patterns, include, url
from neo4django import admin

# Uncomment the next two lines to enable the admin:
admin.autodiscover()


urlpatterns = patterns('',	
    url(r'^admin/', include(admin.site.urls)),
)