from .resources       import *
from django.conf.urls import patterns, include, url
from tastypie.api     import Api

api = Api(api_name='v1')
api.register(EnergyProductResource())
api.register(EnergyProjectResource())

urlpatterns = patterns('app.detective.apps.energy',
    url(r'', include(api.urls)),    
)