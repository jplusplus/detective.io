from .models import *
from app.detective.individual import IndividualResource, IndividualMeta


class AmountResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Amount.objects.all()
    
class FundraisingRoundResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = FundraisingRound.objects.all()
    
class PersonResource(IndividualResource):        
    class Meta(IndividualMeta):
        queryset = Person.objects.all()
        
class RevenueResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Revenue.objects.all()

class CommentaryResource(IndividualResource): 
    class Meta(IndividualMeta):
        queryset = Commentary.objects.all()

class OrganizationResource(IndividualResource):   
    class Meta(IndividualMeta):
        queryset = Organization.objects.all()

class DistributionResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Distribution.objects.all()

class PriceResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Price.objects.all()

class EnergyProductResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProduct.objects.all()

class EnergyProjectResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProject.objects.all()

