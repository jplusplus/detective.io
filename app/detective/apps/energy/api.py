from app.detective.apps.energy.models  import *
from app.detective.api.individual 	   import IndividualResource, IndividualMeta

class EnergyProductResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProduct.objects.all()

class EnergyProjectResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProject.objects.all()