from app.detective.models      import Amount, Country, FundraisingRound, Organization, Price, Project, Commentary, Distribution, EnergyProject, InternationalOrganization, Person, Revenue, Company, Fund, Product, EnergyProduct, Ngo
from django.conf.urls.defaults import *
from django.core.paginator     import Paginator, InvalidPage
from django.http               import Http404
from tastypie                  import fields
from tastypie.authorization    import DjangoAuthorization, Authorization
from tastypie.resources        import ModelResource
from tastypie.resources        import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils            import trailing_slash

class IndividualResource(ModelResource):
    class Meta:
        allowed_methods = ['get', 'post', 'delete', 'put']    
        always_return_data = True

class AmountResource(ModelResource):    
    class Meta:
        queryset = Amount.objects.all()                    

class CountryResource(ModelResource):
    class Meta:
        queryset = Country.objects.all()              

class FundraisingRoundResource(ModelResource):
    class Meta:
        queryset = FundraisingRound.objects.all()              

class OrganizationResource(ModelResource):
    class Meta:
        queryset = Organization.objects.all()   
        
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        query     = request.GET.get('q', '')
        limit     = int(request.GET.get('limit', 20))
        # Do the query.        
        results   = self._meta.queryset.filter(name__icontains=query)
        count     = len(results)
        paginator = Paginator(results, limit)

        try:
            p     = int(request.GET.get('page', 1))
            page  = paginator.page(p)
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        objects = []

        for result in page.object_list:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
            'meta': {
                'q': query,
                'page': p,
                'limit': limit,
                'total_count': count
            }
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)           

class PriceResource(ModelResource):
    class Meta:
        queryset = Price.objects.all()   

class ProjectResource(ModelResource):
    activityin = fields.ToManyField("app.detective.api.CountryResource", "activityin", full=True, null=True)
    owner = fields.ToManyField("app.detective.api.OrganizationResource", "owner", full=True, null=True)
    commentary = fields.ToManyField("app.detective.api.CommentaryResource", "commentary", full=True, null=True)
    partner = fields.ToManyField("app.detective.api.OrganizationResource", "partner", full=True, null=True)

    class Meta:
        queryset = Project.objects.all()              
        authorization = Authorization()        

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
