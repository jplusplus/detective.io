from .models                  import *
from .user                    import UserResource as ParentUserResource
from app.detective.individual import IndividualResource, IndividualMeta

# Ugly patch
# See also ./individual.py -> IndividualResource -> get_to_many_field()
class UserResource(ParentUserResource):
    pass

class AmountResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Amount.objects.all()

class CountryResource(IndividualResource): 
    class Meta(IndividualMeta):
        queryset = Country.objects.all()
    
class FundraisingRoundResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = FundraisingRound.objects.all()
    
class PersonResource(IndividualResource):        
    class Meta(IndividualMeta):
        queryset = Person.objects.all()

class ProductResource(IndividualResource):        
    class Meta(IndividualMeta):
        queryset = Product.objects.all()
        
class RevenueResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Revenue.objects.all()

class CommentaryResource(IndividualResource): 
    class Meta(IndividualMeta):
        queryset = Commentary.objects.all()

class OrganizationResource(IndividualResource):   
    class Meta(IndividualMeta):
        queryset = Organization.objects.all()

class ProjectResource(IndividualResource):        
    class Meta(IndividualMeta):
        queryset = Project.objects.all()

class DistributionResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Distribution.objects.all()

class PriceResource(IndividualResource):    
    class Meta(IndividualMeta):
        queryset = Price.objects.all()
