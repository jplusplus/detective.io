#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.detective                      import register
from app.detective.neomatch             import Neomatch
from app.detective.utils                import import_class, to_underscores, get_model_topic, get_leafs_and_edges, get_topic_from_request
from app.detective.topics.common.models import FieldSource
from app.detective.models               import Topic
from django.conf.urls                   import url
from django.core.exceptions             import ObjectDoesNotExist
from django.core.paginator              import Paginator, InvalidPage
from django.core.urlresolvers           import reverse
from django.db.models.query             import QuerySet
from django.http                        import Http404
from neo4django.db                      import connection
from neo4django.db.models.properties    import DateProperty
from neo4django.db.models.relationships import MultipleNodes
from tastypie                           import fields
from tastypie.authentication            import Authentication, SessionAuthentication, BasicAuthentication, MultiAuthentication
from tastypie.authorization             import Authorization
from tastypie.constants                 import ALL
from tastypie.exceptions                import Unauthorized
from tastypie.resources                 import ModelResource
from tastypie.serializers               import Serializer
from tastypie.utils                     import trailing_slash
from datetime                           import datetime
import json
import re
import logging

logger = logging.getLogger(__name__)

DATETIME_FORMAT     = '%Y-%m-%dT%H:%M:%S'
DATETIME_FORMAT2    = '%Y-%m-%dT%H:%M:%S+00:00'
RFC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

class IndividualAuthorization(Authorization):
    def get_topic_from_bundle(self, bundle):
        topic = get_topic_from_request(bundle.request)
        if topic == None:
            topic = Topic.objects.get(ontology_as_mod=get_model_topic(bundle.obj)).public
        return topic

    def check_contribution_permission(self, object_list, bundle, operation):
        authorized = False
        user = bundle.request.user
        if user:
            perm_name  = "%s.contribute_%s" % (object_list._app_label, operation)
            authorized = user.is_staff or user.has_perm(perm_name)
        return authorized

    def read_detail(self, object_list, bundle):
        topic = self.get_topic_from_bundle(bundle)
        if not topic.public and not self.check_contribution_permission(object_list, bundle, 'read'):
            raise Unauthorized("Sorry, only staff or contributors can read resource.")
        return True

    def read_list(self, object_list, bundle):
        topic = self.get_topic_from_bundle(bundle)
        if not topic.public and not self.check_contribution_permission(object_list, bundle, 'read'):
            raise Unauthorized("Sorry, only staff or contributors can read resource.")
        return object_list

    def create_detail(self, object_list, bundle):
        if not self.check_contribution_permission(object_list, bundle, 'add'):
            raise Unauthorized("Sorry, only staff or contributors can create resource.")
        # check if user can add regarding to his plan
        topic         = get_topic_from_request(bundle.request)
        owner_profile = topic.author.detectiveprofileuser
        if owner_profile.nodes_max() > -1 and owner_profile.nodes_count()[topic.slug] >= owner_profile.nodes_max():
            raise Unauthorized("Sorry, you have to upgrade your plan.")
        return True

    def update_detail(self, object_list, bundle):
        if not self.check_contribution_permission(object_list, bundle, 'change'):
            raise Unauthorized("Sorry, only staff or contributors can update resource.")
        return True

    def delete_detail(self, object_list, bundle):
        if not self.check_contribution_permission(object_list, bundle, 'delete'):
            raise Unauthorized("Sorry, only staff or contributors can delete resource.")
        return True

    def delete_list(self, object_list, bundle):
        return False
        # if not self.check_contribution_permission(object_list, bundle, 'delete'):
        #     raise Unauthorized("Sorry, only staff or contributors can delete resource.")
        # return True

class IndividualMeta:
    list_allowed_methods   = ['get', 'post', 'put']
    detail_allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
    always_return_data     = True
    authorization          = IndividualAuthorization()
    authentication         = MultiAuthentication(Authentication(), BasicAuthentication(), SessionAuthentication())
    filtering              = {'name': ALL}
    ordering               = {'name': ALL}
    serializer             = Serializer(formats=['json', 'jsonp'])

class FieldSourceResource(ModelResource):
    class Meta:
        queryset = FieldSource.objects.all()
        resource_name = 'auth/user'
        excludes = ['individual', 'id']

    def dehydrate(self, bundle):
        del bundle.data["resource_uri"]
        return bundle

class IndividualResource(ModelResource):


    field_sources = fields.ToManyField(
        FieldSourceResource,
        attribute=lambda bundle: FieldSource.objects.filter(individual=bundle.obj.id),
        full=True,
        null=True,
        use_in='detail'
    )

    def __init__(self, api_name=None):
        super(IndividualResource, self).__init__(api_name)
        # Register relationships fields automaticly
        self.generate_to_many_fields(True)
        # By default, tastypie detects detail mode globally: it means that
        # even into an embeded resource (through a relationship), Tastypie will
        # serialize it as if we are in it's detail view.
        # We overide 'use_in' for every field with the value "detail"
        for field_name, field_object in self.fields.items():
            if field_object.use_in == 'detail':
                # We use a custom method
                field_object.use_in = self.use_in

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

    def get_model_fields(self, name=None):
        if name is None:
            # Find fields of the queryset's model
            return self.get_model()._meta.fields
        else:
            fields = [f for f in self.get_model()._meta.fields if f.name == name]
            return fields[0] if len(fields) else None


    def get_model_field(self, name):
        target = None
        for field in self.get_model_fields():
            if field.name == name:
                target = field
        return target

    def need_to_many_field(self, field):
        # Limit the definition of the new fields
        # to the relationships
        return isinstance(field, MultipleNodes) and not field.name.endswith("_set")

    # TODO: Find another way!
    def dummy_class_to_ressource(self, klass):
        module = klass.__module__.split(".")
        # Remove last path part if need
        if module[-1] == 'models': module = module[0:-1]
        # Build the resource path
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
        if resource: return fields.ToManyField(resource, field.name, full=full, null=True, use_in='detail')
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

    def _build_reverse_url(self, name, args=None, kwargs=None):
        # This ModelResource respects Django namespaces.
        # @see tastypie.resources.NamespacedModelResource
        # @see tastypie.api.NamespacedApi
        namespaced = "%s:%s" % (self._meta.urlconf_namespace, name)
        return reverse(namespaced, args=args, kwargs=kwargs)

    def use_in(self, bundle=None):
        if bundle.request.method in ['POST', 'PUT']:
            return bundle.request.path == self.get_resource_uri()
        # Use in detail
        else:
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
        rules = request.current_topic.get_rules().model(self.get_model()).all()
        # All additional relationships
        for key in rules:
            # Filter rules to keep only Neomatch
            if isinstance(rules[key], Neomatch):
                bundle.data[key] = rules[key].query(bundle.obj.id)
        return bundle

    def dehydrate(self, bundle):
        # Show additional field following the model's rules
        rules = bundle.request.current_topic.get_rules().model( self.get_model() )
        # Get the output transformation for this model
        transform = rules.get("transform")
        # This is just a string
        # For complex formating use http://docs.python.org/2/library/string.html#formatspec
        if type(transform) is str:
            transform = transform.format(**bundle.data)
        # We can also receive a function
        elif callable(transform):
            transform = transform(bundle.data)

        bundle.data["_transform"] = transform or getattr(bundle.data, 'name', None)
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
            # The field is a list of literal values
            elif type(modelField) in (list, tuple):
                # For tuple serialization
                bundle.data[field] = modelField
            # Get the output transformation for this field
            transform = rules.field(field).get("transform")
            # This is just a string
            # For complex formating use http://docs.python.org/2/library/string.html#formatspec
            if type(transform) is str:
                bundle.data[field] = transform.format(**bundle.data)
            # We can also receive a function
            elif callable(transform):
                bundle.data[field] = transform(bundle.data, field)

        return bundle

    def hydrate(self, bundle):
        # Convert author to set to avoid duplicate
        bundle.obj._author = set(bundle.obj._author)
        bundle.obj._author.add(bundle.request.user.id)
        bundle.obj._author = list(bundle.obj._author)
        # Avoid try to insert automatic relationship
        for name in bundle.data:
            if name.endswith("_set"): bundle.data[name] = []
        return bundle

    def hydrate_m2m(self, bundle):
        # By default, every individual from staff are validated
        bundle.data["_status"] = 1*bundle.request.user.is_staff

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
            # Skip admmin field
            elif field.startswith("_"): continue
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
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/patch%s$" % params, self.wrap_view('get_patch'), name="api_get_patch"),
            url(r"^(?P<resource_name>%s)/bulk_upload%s$" % params, self.wrap_view('bulk_upload'), name="api_bulk_upload"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/graph%s$" % params, self.wrap_view('get_graph'), name="api_get_graph"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/relationships%s$" % params, self.wrap_view('get_relationships'), name="api_get_relationships"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/relationships/(?P<field>\w[\w-]*)%s$" % params, self.wrap_view('get_relationships'), name="api_get_relationships_field"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/relationships/(?P<field>\w[\w-]*)/(?P<end>\w[\w-]*)%s$" % params, self.wrap_view('get_relationships'), name="api_get_relationships_field_end"),
        ]


    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        query     = request.GET.get('q', '').lower()
        query     = re.sub("\"|'|`|;|:|{|}|\|(|\|)|\|", '', query).strip()
        limit     = int(request.GET.get('limit', 20))
        # Do the query.
        results   = self._meta.queryset.filter(name__icontains=query)
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
                'total_count': paginator.count
            }
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def get_mine(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        limit = int(request.GET.get('limit', 20))

        if request.user.id is None:
            object_list = {
                'objects': [],
                'meta': {
                    'author': request.user,
                    'page': 1,
                    'limit': limit,
                    'total_count': 0
                }
            }
        else:
            # Do the query.
            results   = self._meta.queryset.filter(_author__contains=request.user.id)
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
                    'total_count': paginator.count
                }
            }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def patch_sources(self, sources, node):
        def arr_no_dict_dup(in_arr):
            out_arr = []
            for el in in_arr:
                existing = len(
                        filter(
                            lambda t: t['field'] == el['field'] and el['reference'] == t['reference'],
                            out_arr
                        )
                    ) > 0
                if not existing:
                    out_arr.append(el)
            return out_arr

        # remove source duplicates
        all_filtered_sources_data = arr_no_dict_dup(sources)
        # remove empty references
        all_filtered_sources_data = filter(lambda el: el['reference'] not in [None, ''], sources)

        # dump patching: remove all old field_sources and put the new ones
        [ source.delete() for source in  FieldSource.objects.filter(individual=node.id)]
        for source_data in all_filtered_sources_data:
            FieldSource.objects.create(individual=node.id, **source_data)

    def get_patch(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.throttle_check(request)
        self.is_authenticated(request)
        bundle = self.build_bundle(request=request)
        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        model = self.get_model()
        try:
            node = model.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            raise Http404("Sorry, unknown node.")
        # Parse only body string
        body = json.loads(request.body) if type(request.body) is str else request.body
        # Copy data to allow dictionary resizing
        data = body.copy()
        for field in body:
            if field == "field_sources":
                self.patch_sources( data[field], node )
                # Continue to not deleted the field
                continue
            # If the field exists into our model
            elif hasattr(node, field) and not field.startswith("_"):
                value = data[field]
                # Get the field
                attr = getattr(node, field)
                # It's a relationship
                if hasattr(attr, "_rel"):
                    related_model = attr._rel.relationship.target_model
                    # Load the json-formated relationships
                    data[field] = rels = value
                    # For each relationship...
                    for idx, rel in enumerate(rels):
                        if type(rel) in [str, int]:
                            rel = dict(id=rel)
                        # We receied an object with an id
                        if rel.has_key("id"):
                            # Get the related object
                            try:
                                related = related_model.objects.get(id=rel["id"])
                            except ObjectDoesNotExist:
                                del data[field][idx]
                                # Too bad! Go to the next related object
                                continue
                            else:
                                # skip for existing relationships
                                if any(r.id == rel["id"] for r in attr.all()):
                                    continue
                                attr.add(related)
                    # removing unused relationship
                    rel_type = self.get_model_field(field).rel_type
                    for relationship in node.node.relationships.all(types=[rel_type]):
                        if relationship.end.id not in rels:
                            relationship.delete()
                # It's a literal value and not the ID
                elif field != 'id':
                    field_prop = self.get_model_field(field)._property
                    if isinstance(field_prop, DateProperty) and value != None:
                        try:
                            # It's a date and therefor `value` should be converted as it
                            value = datetime.strptime(value, RFC_DATETIME_FORMAT)
                        except ValueError:
                            # Try a second format
                            try:
                                value = datetime.strptime(value, DATETIME_FORMAT)
                            except ValueError:
                                # Try a third format
                                try:
                                    value = datetime.strptime(value, DATETIME_FORMAT2)
                                except ValueError as e:
                                    raise Exception("the date `%s` has an unknown format (%s)." % (value, e))
                    # Set the new value
                    setattr(node, field, value)
                # Continue to not deleted the field
                continue
            # Remove the field
            del data[field]

        if len(data) > 0:
            # Convert author to set to avoid duplicate
            node._author = set(node._author)
            node._author.add(request.user.id)
            node._author = list(node._author)
            # Save the node
            node.save()
        return self.create_response(request, data)


    def get_relationships(self, request, **kwargs):
        # Extract node id from given node uri
        def node_id(uri)       : return re.search(r'(\d+)$', uri).group(1)
        # Get the end of the given relationship
        def rel_from(rel, side): return node_id(rel.__dict__["_dic"][side])
        def connected(rel, idx): return rel_from(rel, "end") == idx or rel_from(rel, "start") == idx

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        pk = kwargs['pk']
        node = connection.nodes.get(pk)
        # Only the relationships for a given field
        if "field" in kwargs:
            field = self.get_model_fields(kwargs["field"])
            # Unkown type
            if field is None: raise Http404("Unkown relationship field.")
            reltype = getattr(field, "rel_type", None)
            # Not a relationship
            if reltype is None: raise Exception("The given field is not a relationship.")
            rels = node.relationships.all(types=[reltype])
            # We want to filter the relationships with an other node
            if "end" in kwargs:
                end = kwargs["end"]
                # Then filter the relations
                ids = [ rel.id for rel in rels if connected(rel, end) ]
                if len(ids):
                    # Show additional field following the model's rules
                    rules  = request.current_topic.get_rules()
                    # Model that manages properties
                    though = rules.model( self.get_model() ).field(kwargs["field"]).get("through")
                    # Get the properties for this relationship
                    try:
                        properties = though.objects.get(_relationship=ids[0])
                        # Get the module for this model
                        module = self.dummy_class_to_ressource(though)
                        # Instanciate the resource
                        resource = import_class(module)()
                        # Create a bundle with this resource
                        bundle = resource.build_bundle(obj=properties, request=request)
                        bundle = resource.full_dehydrate(bundle, for_list=True)
                        # We ask for relationship properties
                        return resource.create_response(request, bundle)
                    except though.DoesNotExist:
                        endnodes = [ int(pk), int(end) ]
                        # We ask for relationship properties
                        return self.create_response(request, {
                            "_relationship": ids[0],
                            "_endnodes": endnodes
                        })
                else:
                    # No relationship
                    return self.create_response(request, { "_relationship": None })
        # All relationship
        else:
            rels = node.relationships.all()
        # Only returns IDS
        ids = [ rel.id for rel in rels ]
        return self.create_response(request, ids)

    def get_graph(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        depth = int(request.GET['depth']) if 'depth' in request.GET.keys() else 1
        topic = Topic.objects.get(ontology_as_mod=get_model_topic(self.get_model()))
        leafs, edges = get_leafs_and_edges(
            topic     = topic,
            depth     = depth,
            root_node = kwargs['pk'])
        self.log_throttled_access(request)
        return self.create_response(request, {'leafs': leafs, 'edges' : edges})

# EOF
