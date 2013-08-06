from app.detective.models      import Amount, Country, FundraisingRound, Organization, Price, Project, Commentary, Distribution, EnergyProject, InternationalOrganization, Person, Revenue, Company, Fund, Product, EnergyProduct, Ngo
from django.conf.urls          import url
from django.conf.urls.defaults import *
from django.contrib.auth       import authenticate, login, logout
from django.core.paginator     import Paginator, InvalidPage
from django.http               import Http404
from neo4django.auth.models    import User
from tastypie                  import fields
from tastypie.authorization    import Authorization
from tastypie.http             import HttpUnauthorized, HttpForbidden
from tastypie.resources        import ModelResource
from tastypie.utils            import trailing_slash

class CommonMeta:
    allowed_methods = ['get', 'post', 'delete', 'put']    
    always_return_data = True         
    authorization = Authorization()     

class SearchableResource(ModelResource):    
    
    def hydrate(self, bundle): 
        for field in bundle.data:                        
            # Transform list field to be more flexible
            if type(bundle.data[field]) is list:   
                rels = [] 
                # For each relation...
                for rel in bundle.data[field]:   
                    # Keeps the string
                    if type(rel) is str:
                        rels.append(rel)
                    # Convert object with id to uri
                    elif type(rel) is dict and "id" in rel:                                                                        
                        rels.append( Organization.objects.get(id=rel["id"]) )

                bundle.data[field] = rels                                        
        return bundle

    def save_m2m(self, bundle): 
        for field in bundle.data:                        
            # Transform list field to be more flexible
            if type(bundle.data[field]) is list:                   
                rels = bundle.data[field]
                # Empties the bundle to avoid insert data twice
                bundle.data[field] = []
                # Get the field
                attr = getattr(bundle.obj, field)                                    
                if attr.count() > 0:
                    # Clean the field to avoid duplicates
                    attr.clear()
                # For each relation...
                for rel in rels:        
                    # Add the received obj
                    attr.add(rel.obj)

        # Save the object with it new relations
        bundle.obj.save()

        return super(SearchableResource, self).save_m2m(bundle)

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


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['first_name', 'last_name', 'email']
        allowed_methods = ['get', 'post']
        resource_name = 'user'

    def override_urls(self):
        params = (self._meta.resource_name, trailing_slash())
        return [
            url(r"^(?P<resource_name>%s)/login%s$"  % params, self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' % params, self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/status%s$' % params, self.wrap_view('status'), name='api_status'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                    }, HttpForbidden )
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
                }, HttpUnauthorized )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized)  

    def status(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            return self.create_response(request, { 'is_logged': True,  'username': request.user.username })
        else:
            return self.create_response(request, { 'is_logged': False, 'username': '' }, HttpUnauthorized)  


class AmountResource(ModelResource):    
    class Meta(CommonMeta):
        queryset = Amount.objects.all()                    

class CountryResource(SearchableResource):
    class Meta(CommonMeta):
        queryset = Country.objects.all()              

class FundraisingRoundResource(ModelResource):
    class Meta(CommonMeta):
        queryset = FundraisingRound.objects.all()              

class OrganizationResource(SearchableResource):
    class Meta(CommonMeta):
        queryset = Organization.objects.all()         

class PriceResource(ModelResource):
    class Meta(CommonMeta):
        queryset = Price.objects.all()   

class ProjectResource(SearchableResource):
    activityin = fields.ToManyField("app.detective.api.CountryResource", "activityin", full=True, null=True)
    owner = fields.ToManyField("app.detective.api.OrganizationResource", "owner", full=True, null=True)
    commentary = fields.ToManyField("app.detective.api.CommentaryResource", "commentary", full=True, null=True)
    partner = fields.ToManyField("app.detective.api.OrganizationResource", "partner", full=True, null=True)

    class Meta(CommonMeta):
        queryset = Project.objects.all()        

class CommentaryResource(ModelResource):
    class Meta(CommonMeta):
        queryset = Commentary.objects.all()              

class DistributionResource(ModelResource):
    class Meta(CommonMeta):
        queryset = Distribution.objects.all()              

class EnergyProjectResource(SearchableResource):
    class Meta(CommonMeta):
        queryset = EnergyProject.objects.all()              

class InternationalOrganizationResource(SearchableResource):
    class Meta(CommonMeta):
        queryset = InternationalOrganization.objects.all()              

class PersonResource(SearchableResource):
    organization_set = fields.ToManyField(OrganizationResource, "organization_set", full=False)
    class Meta(CommonMeta):
        queryset = Person.objects.all()              

class RevenueResource(ModelResource):
    class Meta(CommonMeta):
        queryset = Revenue.objects.all()              

class CompanyResource(SearchableResource):
    class Meta(CommonMeta):
        queryset = Company.objects.all()              

class FundResource(ModelResource):
    class Meta(CommonMeta):
        queryset = Fund.objects.all()              

class ProductResource(SearchableResource):
    class Meta(CommonMeta):
        queryset = Product.objects.all()              

class EnergyProductResource(SearchableResource):
    class Meta(CommonMeta):
        queryset = EnergyProduct.objects.all()              

class NgoResource(SearchableResource):
    class Meta(CommonMeta):
        queryset = Ngo.objects.all()              
