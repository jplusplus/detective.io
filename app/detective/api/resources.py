from app.detective.models               import *
from django.conf.urls                   import url
from django.contrib.auth                import authenticate, login, logout
from django.core.paginator              import Paginator, InvalidPage
from django.db.models.query             import QuerySet
from django.http                        import Http404, HttpResponse
from django.middleware.csrf             import _get_new_csrf_key as get_new_csrf_key
from neo4django.auth.models             import User
from neo4django.db.models.relationships import MultipleNodes
from tastypie                           import fields
from tastypie.authentication            import SessionAuthentication
from tastypie.authorization             import DjangoAuthorization
from tastypie.constants                 import ALL
from tastypie.exceptions                import ImmediateHttpResponse
from tastypie.resources                 import ModelResource, Resource
from tastypie.serializers               import Serializer
from tastypie.utils                     import trailing_slash


class SummaryResource(Resource):
    # Local serializer
    serializer = Serializer(formats=["json"]).serialize

    class Meta:
        allowed_methods = ['get'] 
        resource_name   = 'summary'
        object_class    = object

    def obj_get_list(self, request=None, **kwargs):
        # Nothing yet here!
        raise Http404("Sorry, no results on that page.") 

    def obj_get(self, request=None, **kwargs):    
        content = {}
        # Summary for the country
        if kwargs["pk"] == "countries": 
            content["test"] = 1
        else: 
            # Stop here, unkown summary type
            raise Http404("Sorry, no results on that page.")        
        # Serialize content in json
        # @TODO implement a better format support
        content  = self.serializer(content, "application/json")
        # Create an HTTP response 
        response = HttpResponse(content=content, content_type="application/json")
        # We force tastypie to render the response directly 
        raise ImmediateHttpResponse(response=response)


class IndividualMeta:
    allowed_methods    = ['get', 'post', 'delete', 'put']    
    always_return_data = True         
    authorization      = DjangoAuthorization()     
    authentication     = SessionAuthentication()
    filtering          = {'name': ALL}

class IndividualResource(ModelResource):

    def __init__(self, api_name=None):        
        super(IndividualResource, self).__init__(api_name)    
        # Register relationships fields automaticly            
        self.generate_to_many_fields(True)

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

    def get_model_fields(self):
        # Resource must implement a queryset!
        queryset = getattr(self._meta, "queryset", None)
        if not isinstance(queryset, QuerySet):
            raise Exception("The given resource must define a queryset.")
        # Find fields of the queryset's model        
        return queryset.model._meta.fields  

    def need_to_many_field(self, field):        
        # Limit the definition of the new fields
        # to the relationships
        if isinstance(field, MultipleNodes):
            # The resource already define a field for this one
            # resource_field = self.fields[field.name]
            # But it's probably still a charfield !
            # And it's so bad.
            # if isinstance(resource_field, fields.CharField):                               
            return True
        # Return false if not needed
        return False

    def get_to_many_field(self, field, full=False):
        resource = "app.detective.api.resources.%sResource" % (field.target_model.__name__, )        
        return fields.ToManyField(resource, field.name, full=full, null=True, use_in=self.use_in)

    def generate_to_many_fields(self, full=False):
        # For each model field
        for field in self.get_model_fields():
            # Limit the definition of the new fields
            # to the relationships
            if self.need_to_many_field(field):         
                # Get the full relationship                           
                self.fields[field.name] = self.get_to_many_field(field, full=bool(full))

    def use_in(self, bundle=None):
        # Use in post/put
        if bundle.request.method in ['POST', 'PUT']:
            return bundle.request.path == self.get_resource_uri()
        else:
            # Use in detail
            return self.get_resource_uri(bundle) == bundle.request.path

    def get_detail(self, request, **kwargs):  
        # Register relationships fields automaticly with full detail            
        self.generate_to_many_fields(True)
        return super(IndividualResource, self).get_detail(request, **kwargs)

    def get_list(self, request, **kwargs):
        # Register relationships fields automaticly with full detail
        self.generate_to_many_fields(False)
        return super(IndividualResource, self).get_list(request, **kwargs)

    def dehydrate(self, bundle):
        # Control that every relationship fields are list        
        # and that we didn't send hidden field
        for field in bundle.data:
            # Find the model's field 
            modelField = getattr(bundle.obj, field, False) 
            # The current field is a relationship
            if modelField and hasattr(modelField, "_rel"): 
                # Wrong type given, relationship field must ouput a list
                if type(bundle.data[field]) is not list:
                    # We remove the field from the ouput
                    bundle.data[field] = []         
        return bundle

    def hydrate_m2m(self, bundle):         
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
                # Avoid working on empty relationships set
                if len(rels) > 0:
                    # Empties the bundle to avoid insert data twice
                    bundle.data[field] = []                                      
                    # Get the field
                    attr = getattr(bundle.obj, field)
                    # Clean the field to avoid duplicates            
                    if attr.count() > 0: attr.clear()
                    # For each relation...
                    for rel in rels:   
                        # Add the received obj
                        if hasattr(rel, "obj"):
                            attr.add(rel.obj)
                        else:
                            attr.add(rel)

        # Save the object now to avoid duplicated relations 
        bundle.obj.save()

        return bundle

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

class UserResource(ModelResource):    
    
    class Meta(IndividualMeta):
        queryset = User.objects.all()
        fields = ['first_name', 'last_name', 'username', 'is_staff']
        allowed_methods = ['get', 'post']
        resource_name = 'user'
        always_return_data = True         
        authorization      = DjangoAuthorization()     
        authentication     = SessionAuthentication()
        filtering          = {'name': ALL}

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

class EnergyProductResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProduct.objects.all()

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

class EnergyProjectResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProject.objects.all()
