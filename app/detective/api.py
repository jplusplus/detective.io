from app.detective.models   import Amount, Country, FundraisingRound, Organization, Price, Project, Commentary, Distribution, EnergyProject, InternationalOrganization, Person, Revenue, Company, Fund, Product, EnergyProduct, Ngo
from tastypie               import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources     import ModelResource

class AmountResource(ModelResource):    
    class Meta:
        queryset = Amount.objects.all()   
        authorization = DjangoAuthorization()     
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']

class CountryResource(ModelResource):
    class Meta:
        queryset = Country.objects.all()

class FundraisingRoundResource(ModelResource):
    class Meta:
        queryset = FundraisingRound.objects.all()

class OrganizationResource(ModelResource):
    class Meta:
        queryset = Organization.objects.all()

class PriceResource(ModelResource):
    class Meta:
        queryset = Price.objects.all()

class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()

class CommentaryResource(ModelResource):
    class Meta:
        queryset = Commentary.objects.all()

class DistributionResource(ModelResource):
    class Meta:
        queryset = Distribution.objects.all()

class EnergyProjectResource(ModelResource):
    class Meta:
        queryset = EnergyProject.objects.all()

class InternationalOrganizationResource(ModelResource):
    class Meta:
        queryset = InternationalOrganization.objects.all()

class PersonResource(ModelResource):
    organization_set = fields.ToManyField(OrganizationResource, "organization_set", full=False)
    class Meta:
        queryset = Person.objects.all()

class RevenueResource(ModelResource):
    class Meta:
        queryset = Revenue.objects.all()

class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()

class FundResource(ModelResource):
    class Meta:
        queryset = Fund.objects.all()

class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.all()

class EnergyProductResource(ModelResource):
    class Meta:
        queryset = EnergyProduct.objects.all()

class NgoResource(ModelResource):
    class Meta:
        queryset = Ngo.objects.all()
