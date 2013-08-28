from app.detective.models          import *
from django.conf.urls              import url
from django.contrib.auth           import authenticate, login, logout
from django.core.paginator         import Paginator, InvalidPage
from django.http                   import Http404
from django.middleware.csrf        import _get_new_csrf_key as get_new_csrf_key
from neo4django.auth.models        import User
from tastypie                      import fields
from tastypie.authentication       import SessionAuthentication
from tastypie.authorization        import DjangoAuthorization
from tastypie.constants            import ALL
from tastypie.resources            import ModelResource
from tastypie.utils                import trailing_slash


class IndividualMeta:
    allowed_methods    = ['get', 'post', 'delete', 'put']    
    always_return_data = True         
    authorization      = DjangoAuthorization()     
    authentication     = SessionAuthentication()
    filtering          = {'name': ALL}

class IndividualResource(ModelResource):

    _author = fields.ToManyField("app.detective.api.resources.UserResource", "_author", full=False, null=True, use_in="detail")

    def build_schema(self):  
        """
        Description and scope for each Resource
        """
        schema = super(IndividualResource, self).build_schema()        
        model  = self._meta.queryset.model

        additionals = {
            "description": getattr(model, "_description", None),
            "scope"      : getattr(model, "_scope", None)
        }
        return dict(additionals.items() + schema.items())

    def dehydrate(self, bundle):
        # Control that every relationship fields are list        
        # and that we didn't send hidden field
        for field in bundle.data:
            # Is this an "hidden field" ?
            if field.endswith("_set"):
                # Set the field to None 'cause we cant change the size 
                # of the data's bundle
                bundle.data[field] = None
                continue
            # Find the model's field 
            modelField = getattr(bundle.obj, field, False) 
            # The current field is a relationship
            if modelField and hasattr(modelField, "_rel"): 
                # Wrong type given, relationship field must ouput a list
                if type(bundle.data[field]) is not list:
                    # We remove the field from the ouput
                    bundle.data[field] = []                    

        return bundle



    def hydrate(self, bundle):         
        # By default, every individual from staff are validated
        bundle.data["_status"] = 1*bundle.request.user.is_staff
        bundle.data["_author"] = [bundle.request.user.id]

        for field in bundle.data:   
            # Find the model's field 
            modelField = getattr(bundle.obj, field, False) 
            # The current field is a relationship
            if modelField and hasattr(modelField, "_rel"):
                # Model associated to that field
                model = modelField._rel.relationship.target_model                
                # Wrong type given
                if type(bundle.data[field]) is not list:                         
                    # Empty the field that contain bad
                    bundle.data[field] = []
                # Transform list field to be more flexible
                elif len(bundle.data[field]):   
                    rels = []                     
                    # For each relation...
                    for rel in bundle.data[field]:  
                        # Keeps the string
                        if type(rel) is str:
                            rels.append(rel)
                        # Convert object with id to uri
                        elif type(rel) is int:
                            obj = model.objects.get(id=rel)                                  
                        elif "id" in rel:
                            obj = model.objects.get(id=rel["id"])
                        else:                                 
                            obj = False
                        # Associated the existing object 
                        if obj: rels.append(obj)

                    bundle.data[field] = rels   

        return bundle

    def save_m2m(self, bundle): 
        for field in bundle.data: 
            # Find the model's field 
            modelField = getattr(bundle.obj, field, False) 
            # The field doesn't exist
            if not modelField: setattr(bundle.obj, field, None)
            # Transform list field to be more flexible
            elif type(bundle.data[field]) is list:                   
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
                    if hasattr(rel, "obj"):
                        attr.add(rel.obj)
                    else:
                        attr.add(rel)

        # Save the object with it new relations
        bundle.obj.save()

        return super(IndividualResource, self).save_m2m(bundle)

    def prepend_urls(self):
        params = (self._meta.resource_name, trailing_slash())
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % params, self.wrap_view('get_search'), name="api_get_search"),
            url(r"^(?P<resource_name>%s)/mine%s$" % params, self.wrap_view('get_mine'), name="api_get_mine"),
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
            bundle = self.full_dehydrate(bundle, for_list=True)        
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

    def get_mine(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        
        # Do the query.        
        limit     = int(request.GET.get('limit', 20))
        results   = self._meta.queryset.filter(_author__id=request.user.id)
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
            bundle = self.full_dehydrate(bundle, for_list=True)        
            objects.append(bundle) 

        object_list = {
            'objects': objects,
            'meta': {
                'author': request.user,
                'page': p,
                'limit': limit,
                'total_count': count
            }
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)     


class UserResource(IndividualResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['first_name', 'last_name', 'username', 'is_staff']
        allowed_methods = ['get', 'post']
        resource_name = 'user'

    def prepend_urls(self):
        params = (self._meta.resource_name, trailing_slash())
        return [
            url(r"^(?P<resource_name>%s)/login%s$"  % params, self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' % params, self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/status%s$' % params, self.wrap_view('status'), name='api_status'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

        username    = data.get('username', '')
        password    = data.get('password', '')
        remember_me = data.get('remember_me', False)

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                
                # Remember me opt-in
                if not remember_me: request.session.set_expiry(0)

                response = self.create_response(request, {
                    'success': True
                })
                # Create CSRF token
                response.set_cookie("csrftoken", get_new_csrf_key())

                return response
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'Account disabled.',
                })
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'Incorrect password or username.',
                })

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
            return self.create_response(request, { 'is_logged': False, 'username': '' })  


class AmountResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Amount.objects.all()

class CountryResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Country.objects.all()

class FundraisingRoundResource(IndividualResource):
    payer = fields.ToManyField("app.detective.api.resources.OrganizationResource", "payer", full=True, null=True, use_in="detail")
    personalpayer = fields.ToManyField("app.detective.api.resources.PersonResource", "personalpayer", full=True, null=True, use_in="detail")

    class Meta(IndividualMeta):
        queryset = FundraisingRound.objects.all()

class OrganizationResource(IndividualResource):
    partner = fields.ToManyField("app.detective.api.resources.OrganizationResource", "partner", full=True, null=True, use_in="detail")
    adviser = fields.ToManyField("app.detective.api.resources.PersonResource", "adviser", full=True, null=True, use_in="detail")
    litigation_against = fields.ToManyField("app.detective.api.resources.OrganizationResource", "litigation_against", full=True, null=True, use_in="detail")
    fundraising_round = fields.ToManyField("app.detective.api.resources.FundraisingRoundResource", "fundraising_round", full=True, null=True, use_in="detail")
    board_member = fields.ToManyField("app.detective.api.resources.PersonResource", "board_member", full=True, null=True, use_in="detail")
    revenue = fields.ToManyField("app.detective.api.resources.RevenueResource", "revenue", full=True, null=True, use_in="detail")

    class Meta(IndividualMeta):
        queryset = Organization.objects.all()

class PriceResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Price.objects.all()

class ProjectResource(IndividualResource):
    activity_in = fields.ToManyField("app.detective.api.resources.CountryResource", "activity_in", full=True, null=True, use_in="detail")
    owner = fields.ToManyField("app.detective.api.resources.OrganizationResource", "owner", full=True, null=True, use_in="detail")
    commentary = fields.ToManyField("app.detective.api.resources.CommentaryResource", "commentary", full=True, null=True, use_in="detail")
    partner = fields.ToManyField("app.detective.api.resources.OrganizationResource", "partner", full=True, null=True, use_in="detail")

    class Meta(IndividualMeta):
        queryset = Project.objects.all()

class CommentaryResource(IndividualResource):
    author = fields.ToManyField("app.detective.api.resources.PersonResource", "author", full=True, null=True, use_in="detail")

    class Meta(IndividualMeta):
        queryset = Commentary.objects.all()

class DistributionResource(IndividualResource):    
    activity_in = fields.ToManyField("app.detective.api.resources.CountryResource", "activity_in", full=True, null=True, use_in="detail")

    class Meta(IndividualMeta):
        queryset = Distribution.objects.all()

class EnergyProjectResource(IndividualResource):
    product = fields.ToManyField("app.detective.api.resources.EnergyProductResource", "product", full=True, null=True, use_in="detail")
  
    class Meta(IndividualMeta):
        queryset = EnergyProject.objects.all()

class InternationalOrganizationResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = InternationalOrganization.objects.all()

class PersonResource(IndividualResource):    
    activity_in = fields.ToManyField("app.detective.api.resources.OrganizationResource", "activity_in", full=True, null=True, use_in="detail")
    nationality = fields.ToManyField("app.detective.api.resources.CountryResource", "nationality", full=True, null=True, use_in="detail")
    previous_activity_in = fields.ToManyField("app.detective.api.resources.OrganizationResource", "previous_activity_in", full=True, null=True, use_in="detail")

    class Meta(IndividualMeta):
        queryset = Person.objects.all()

class RevenueResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Revenue.objects.all()

class CompanyResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Company.objects.all()

class GovernmentOrganizationResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = GovernmentOrganization.objects.all()

class ProductResource(IndividualResource):

    price = fields.ToManyField("app.detective.api.resources.PriceResource", "price", full=True, null=True, use_in="detail")

    class Meta(IndividualMeta):
        queryset = Product.objects.all()

class EnergyProductResource(IndividualResource):
    
    distribution = fields.ToManyField("app.detective.api.resources.DistributionResource", "distribution", full=True, null=True, use_in="detail")
    operator = fields.ToManyField("app.detective.api.resources.OrganizationResource", "operator", full=True, null=True, use_in="detail")
    price = fields.ToManyField("app.detective.api.resources.PriceResource", "price", full=True, null=True, use_in="detail")

    class Meta(IndividualMeta):
        queryset = EnergyProduct.objects.all()

class NgoResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Ngo.objects.all()
