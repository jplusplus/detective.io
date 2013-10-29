from .models import *
from app.detective.individual import IndividualResource, IndividualMeta

class CountryResource(IndividualResource): 
    class Meta(IndividualMeta):
        queryset = Country.objects.all()    