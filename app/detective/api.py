from app.detective.models          import *
from django.conf.urls              import url
from django.conf.urls.defaults     import *
from django.contrib.auth           import authenticate, login, logout
from django.core.paginator         import Paginator, InvalidPage
from django.http                   import Http404, HttpResponse
from django.middleware.csrf        import _get_new_csrf_key as get_new_csrf_key
from neo4django.auth.models        import User
from tastypie                      import fields
from tastypie.api                  import Api
from tastypie.authentication       import SessionAuthentication
from tastypie.authorization        import DjangoAuthorization
from tastypie.resources            import ModelResource
from tastypie.utils                import trailing_slash
from tastypie.utils.mime           import determine_format, build_content_type



class DetailedApi(Api):
    def top_level(self, request, api_name=None):
        """
        A view that returns a serialized list of all resources registers
        to the ``Api``. Useful for discovery.
        """
        available_resources = {}

        if api_name is None: api_name = self.api_name

        for name in sorted(self._registry.keys()):                        
            resource      = self._registry[name]
            resourceModel = getattr(resource._meta.queryset, "model", {})      
            fields        = []
            verbose_name  = ""

            if hasattr(resourceModel, "_meta"):
                # Model berbose name
                verbose_name = getattr(resourceModel._meta, "verbose_name", name).title()
                # Create field object
                for f in resourceModel._meta.fields:
                    # Ignores field terminating by + or begining by _
                    if not f.name.endswith("+") and not f.name.endswith("_set") and not f.name.startswith("_"):             
                        # Find related model for relation
                        if hasattr(f, "target_model"):                            
                            related_model = f.target_model.__name__                
                        else:
                            related_model = None       
                        
                        # Create the field object
                        fields.append({
                            'name': f.name,
                            'type': f.get_internal_type(),
                            'help_text': getattr(f, "help_text", ""),
                            'verbose_name': getattr(f, "verbose_name", f.name).title(),
                            'related_model': related_model
                        })

            available_resources[name] = {
                'list_endpoint': self._build_reverse_url("api_dispatch_list", kwargs={
                    'api_name': api_name,
                    'resource_name': name,
                }),
                'schema': self._build_reverse_url("api_get_schema", kwargs={
                    'api_name': api_name,
                    'resource_name': name,
                }),
                'description' : getattr(resourceModel, "_description", None),
                'scope'       : getattr(resourceModel, "_scope", None),
                'model'       : getattr(resourceModel, "__name__", ""),
                'verbose_name': verbose_name,
                'name'        : name,
                'fields'      : fields
            }

        desired_format = determine_format(request, self.serializer)

        options = {}

        if 'text/javascript' in desired_format:
            callback = request.GET.get('callback', 'callback')

            if not is_valid_jsonp_callback_value(callback):
                raise BadRequest('JSONP callback name is invalid.')

            options['callback'] = callback

        serialized = self.serializer.serialize(available_resources, desired_format, options)
        return HttpResponse(content=serialized, content_type=build_content_type(desired_format))



class IndividualMeta:
    allowed_methods    = ['get', 'post', 'delete', 'put']    
    always_return_data = True         
    authorization      = DjangoAuthorization()     
    authentication     = SessionAuthentication()

class IndividualResource(ModelResource):

    _author = fields.ToManyField("app.detective.api.UserResource", "_author", full=False, null=True)

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

    def obj_create(self, bundle, **kwargs):
        # Add per-user resource
        return super(IndividualResource, self).obj_create(bundle, _author=bundle.request.user)

    def hydrate(self, bundle): 
        # By default, every individual from staff are validated
        bundle.data["_status"] = 1*bundle.request.user.is_staff

        for field in bundle.data:                        
            # Transform list field to be more flexible
            if type(bundle.data[field]) is list and len(bundle.data[field]):   
                rels = [] 
                # Model associated to that field
                model = getattr(bundle.obj, field)._rel.relationship.target_model
                # For each relation...
                for rel in bundle.data[field]:   
                    # Keeps the string
                    if type(rel) is str:
                        rels.append(rel)
                    # Convert object with id to uri
                    elif type(rel) is dict and "id" in rel:                                                
                        obj = model.objects.get(id=rel["id"])                
                        # Associated the existing object 
                        if obj: rels.append(obj)

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

        return super(IndividualResource, self).save_m2m(bundle)

    def override_urls(self):
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

    def get_mine(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        limit     = int(request.GET.get('limit', 20))
        # Do the query.        
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
            bundle = self.full_dehydrate(bundle)
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
    payer = fields.ToManyField("app.detective.api.OrganizationResource", "payer", full=True, null=True)
    personalpayer = fields.ToManyField("app.detective.api.PersonResource", "personalpayer", full=True, null=True)

    class Meta(IndividualMeta):
        queryset = FundraisingRound.objects.all()

class OrganizationResource(IndividualResource):
    partner = fields.ToManyField("app.detective.api.OrganizationResource", "partner", full=True, null=True)
    adviser = fields.ToManyField("app.detective.api.PersonResource", "adviser", full=True, null=True)
    litigation_against = fields.ToManyField("app.detective.api.OrganizationResource", "litigation_against", full=True, null=True)
    fundraising_round = fields.ToManyField("app.detective.api.FundraisingRoundResource", "fundraising_round", full=True, null=True)
    board_member = fields.ToManyField("app.detective.api.PersonResource", "board_member", full=True, null=True)
    revenue = fields.ToManyField("app.detective.api.RevenueResource", "revenue", full=True, null=True)

    class Meta(IndividualMeta):
        queryset = Organization.objects.all()

class PriceResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Price.objects.all()

class ProjectResource(IndividualResource):
    activity_in = fields.ToManyField("app.detective.api.CountryResource", "activity_in", full=True, null=True)
    owner = fields.ToManyField("app.detective.api.OrganizationResource", "owner", full=True, null=True)
    commentary = fields.ToManyField("app.detective.api.CommentaryResource", "commentary", full=True, null=True)
    partner = fields.ToManyField("app.detective.api.OrganizationResource", "partner", full=True, null=True)

    class Meta(IndividualMeta):
        queryset = Project.objects.all()

class CommentaryResource(IndividualResource):
    author = fields.ToManyField("app.detective.api.PersonResource", "author", full=True, null=True)

    class Meta(IndividualMeta):
        queryset = Commentary.objects.all()

class DistributionResource(IndividualResource):    
    activity_in = fields.ToManyField("app.detective.api.CountryResource", "activity_in", full=True, null=True)

    class Meta(IndividualMeta):
        queryset = Distribution.objects.all()

class EnergyProjectResource(IndividualResource):
    product = fields.ToManyField("app.detective.api.EnergyProductResource", "product", full=True, null=True)
  
    class Meta(IndividualMeta):
        queryset = EnergyProject.objects.all()

class InternationalOrganizationResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = InternationalOrganization.objects.all()

class PersonResource(IndividualResource):    
    activity_in = fields.ToManyField("app.detective.api.OrganizationResource", "activity_in", full=True, null=True)
    nationality = fields.ToManyField("app.detective.api.CountryResource", "nationality", full=True, null=True)
    previous_activity_in = fields.ToManyField("app.detective.api.OrganizationResource", "previous_activity_in", full=True, null=True)

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

    price = fields.ToManyField("app.detective.api.PriceResource", "price", full=True, null=True)

    class Meta(IndividualMeta):
        queryset = Product.objects.all()

class EnergyProductResource(IndividualResource):
    
    distribution = fields.ToManyField("app.detective.api.DistributionResource", "distribution", full=True, null=True)
    operator = fields.ToManyField("app.detective.api.OrganizationResource", "operator", full=True, null=True)

    class Meta(IndividualMeta):
        queryset = EnergyProduct.objects.all()

class NgoResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Ngo.objects.all()
