from .models     import *
from app.detective.individual import IndividualResource, IndividualMeta

class EnergyProductResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProduct.objects.all()

class EnergyProjectResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProject.objects.all()