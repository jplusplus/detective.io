#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.detective.apps.common.user     import UserResource
from app.detective.forms                import register_model_rules
from app.detective.neomatch             import Neomatch
from app.detective.utils                import import_class
from django.conf.urls                   import url
from django.core.paginator              import Paginator, InvalidPage
from django.db.models.query             import QuerySet
from django.http                        import Http404
from neo4django.db.models.relationships import MultipleNodes
from tastypie                           import fields
from tastypie.authentication            import SessionAuthentication
from tastypie.authorization             import Authorization
from tastypie.constants                 import ALL
from tastypie.resources                 import ModelResource
from tastypie.serializers               import Serializer
from tastypie.utils                     import trailing_slash
from tastypie.exceptions                import Unauthorized
import re

class IndividualAuthorization(Authorization):
    def read_detail(self, object_list, bundle):
        return True
        
    def create_detail(self, object_list, bundle):   
        if not (bundle.request.user and bundle.request.user.is_staff): 
            raise Unauthorized("Sorry, only staff is authorized to create resource.")
        return True
        
    def update_detail(self, object_list, bundle):     
        if not (bundle.request.user and bundle.request.user.is_staff): 
            raise Unauthorized("Sorry, only staff is authorized to update resource.")
        return True

    def delete_detail(self, object_list, bundle):   
        if not (bundle.request.user and bundle.request.user.is_staff): 
            raise Unauthorized("Sorry, only staff is authorized to delete resource.")
        return True             
        
    def delete_list(self, object_list, bundle):           
        if not (bundle.request.user and bundle.request.user.is_staff): 
            raise Unauthorized("Sorry, only staff is authorized to delete resource.")             

class IndividualMeta:
    list_allowed_methods   = ['get', 'post', 'put']
    detail_allowed_methods = ['get', 'post', 'delete', 'put', 'patch']    
    always_return_data     = True         
    authorization          = IndividualAuthorization()     
    authentication         = SessionAuthentication()
    filtering              = {'name': ALL}    
    ordering               = {'name': ALL}
    serializer             = Serializer(formats=['json', 'jsonp', 'xml', 'yaml'])

class IndividualResource(ModelResource):

    # All individual resource have authors
    _author = fields.ToManyField(UserResource, "_author", full=True, null=True, use_in="detail")

    def __init__(self, api_name=None):        
        super(IndividualResource, self).__init__(api_name)  
        # Register relationships fields automaticly            
        self.generate_to_many_fields(True)     

    def apply_sorting(self, obj_list, options=None):        
        options_copy = options.copy()
        # No failling sorting, 
        if "order_by" in options and not options["order_by"] in self.fields:
            # remove invalid order_by key
            options_copy.pop("order_by", None)
        return super(IndividualResource, self).apply_sorting(obj_list, options_copy)
        

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

    def get_queryset(self):        
        # Resource must implement a queryset!
        queryset = getattr(self._meta, "queryset", None)
        if not isinstance(queryset, QuerySet):
            raise Exception("The given resource must define a queryset.")
        return queryset

    def get_model(self):      
        return self.get_queryset().model

    def get_model_fields(self):
        # Find fields of the queryset's model        
        return self.get_model()._meta.fields  

    def need_to_many_field(self, field):        
        # Limit the definition of the new fields
        # to the relationships
        if isinstance(field, MultipleNodes) and not field.name.endswith("_set"):
            # The resource already define a field for this one
            # resource_field = self.fields[field.name]
            # But it's probably still a charfield !
            # And it's so bad.
            # if isinstance(resource_field, fields.CharField):                               
            return True
        # Return false if not needed
        return False

    def dummy_class_to_ressource(self, klass):
        module = klass.__module__.split(".")[0:-1]
        module = ".".join(module + ["resources", klass.__name__ + "Resource"])
        try:
            # Try to import the class
            import_class(module)
            return module
        except ImportError:
            return None

    def get_to_many_field(self, field, full=False):
        if type(field.target_model) == str:
            target_model = import_class(field.target_model)
        else:
            target_model = field.target_model        
        resource = self.dummy_class_to_ressource(target_model)
        # Do not create a relationship with an empty resource (not resolved)
        if resource: return fields.ToManyField(resource, field.name, full=full, null=True, use_in=self.use_in)
        else: return None

    def generate_to_many_fields(self, full=False):
        # For each model field
        for field in self.get_model_fields():
            # Limit the definition of the new fields
            # to the relationships
            if self.need_to_many_field(field):   
                f = self.get_to_many_field(field, full=bool(full))
                # Get the full relationship                                           
                if f: self.fields[field.name] = f

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

    def alter_detail_data_to_serialize(self, request, bundle):
        # Show additional field following the model's rules
        rules = register_model_rules().model(self.get_model()).all()
        # All additional relationships        
        for key in rules:
            # Filter rules to keep only Neomatch
            if isinstance(rules[key], Neomatch):
                bundle.data[key] = rules[key].query(bundle.obj.id)
        
        return bundle

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

    def hydrate(self, bundle):
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
        self.throttle_check(request)

        query     = request.GET.get('q', '').lower()
        query     = re.sub("\"|'|`|;|:|{|}|\|(|\|)|\|", '', query).strip()        
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