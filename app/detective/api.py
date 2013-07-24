from app.detective.models   import Amount, Country, FundraisingRound, Organization, Price, Project, Commentary, Distribution, EnergyProject, InternationalOrganization, Person, Revenue, Company, Fund, Product, EnergyProduct, Ngo
from tastypie               import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources     import ModelResource, ALL, ALL_WITH_RELATIONS

class AmountResource(ModelResource):    
    class Meta:
        queryset = Amount.objects.all()            
        allowed_methods = ['get']    

class CountryResource(ModelResource):
    class Meta:
        queryset = Country.objects.all()      
        allowed_methods = ['get']    

class FundraisingRoundResource(ModelResource):
    class Meta:
        queryset = FundraisingRound.objects.all()      
        allowed_methods = ['get']    

class OrganizationResource(ModelResource):
    class Meta:
        filtering = {
            'name': ALL,
            'twitterHandle': ALL
        }
        queryset = Organization.objects.all()      
        allowed_methods = ['get']    

class PriceResource(ModelResource):
    class Meta:
        queryset = Price.objects.all()      
        allowed_methods = ['get']    

class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()      
        allowed_methods = ['get']    

class CommentaryResource(ModelResource):
    class Meta:
        queryset = Commentary.objects.all()      
        allowed_methods = ['get']    

class DistributionResource(ModelResource):
    class Meta:
        queryset = Distribution.objects.all()      
        allowed_methods = ['get']    

class EnergyProjectResource(ModelResource):
    class Meta:
        queryset = EnergyProject.objects.all()      
        allowed_methods = ['get']    

class InternationalOrganizationResource(ModelResource):
    class Meta:
        queryset = InternationalOrganization.objects.all()      
        allowed_methods = ['get']    

class PersonResource(ModelResource):
    organization_set = fields.ToManyField(OrganizationResource, "organization_set", full=False)
    class Meta:
        queryset = Person.objects.all()      
        allowed_methods = ['get']    

class RevenueResource(ModelResource):
    class Meta:
        queryset = Revenue.objects.all()      
        allowed_methods = ['get']    

class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()      
        allowed_methods = ['get']    

class FundResource(ModelResource):
    class Meta:
        queryset = Fund.objects.all()      
        allowed_methods = ['get']    

class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.all()      
        allowed_methods = ['get']    

class EnergyProductResource(ModelResource):
    class Meta:
        queryset = EnergyProduct.objects.all()      
        allowed_methods = ['get']    

class NgoResource(ModelResource):
    class Meta:
        queryset = Ngo.objects.all()      
        allowed_methods = ['get']    
