from .models import *
from app.detective.individual import IndividualResource, IndividualMeta


class AmountResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Amount.objects.all().select_related(depth=1)
    
class FundraisingRoundResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = FundraisingRound.objects.all().select_related(depth=1)
    
class PersonResource(IndividualResource):        
    class Meta(IndividualMeta):
        queryset = Person.objects.all().select_related(depth=1)
        
class RevenueResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Revenue.objects.all().select_related(depth=1)

class CommentaryResource(IndividualResource): 
    class Meta(IndividualMeta):
        queryset = Commentary.objects.all().select_related(depth=1)

class OrganizationResource(IndividualResource):   
    class Meta(IndividualMeta):
        queryset = Organization.objects.all().select_related(depth=1)

class DistributionResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Distribution.objects.all().select_related(depth=1)

class PriceResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Price.objects.all().select_related(depth=1)

class EnergyProductResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProduct.objects.all().select_related(depth=1)

class EnergyProjectResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProject.objects.all().select_related(depth=1)

