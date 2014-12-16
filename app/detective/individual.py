#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.detective                      import register, graph
from app.detective.neomatch             import Neomatch
from app.detective.utils                import import_class, to_underscores, get_model_topic, \
                                                get_leafs_and_edges, get_topic_from_request, \
                                                iterate_model_fields, topic_cache, \
                                                without, download_url, \
                                                get_image, is_local
from app.detective.topics.common.models import FieldSource
from app.detective.topics.common.user   import UserNestedResource
from app.detective.models               import Topic
from app.detective.exceptions           import UnavailableImage, NotAnImage, OversizedFile
from django.conf                        import settings
from django.conf.urls                   import url
from django.contrib.auth.models         import User
from django.core.exceptions             import ObjectDoesNotExist, ValidationError
from django.core.paginator              import Paginator, InvalidPage
from django.core.urlresolvers           import reverse
from django.core.files.storage          import default_storage
from django.db.models.query             import QuerySet
from django.http                        import Http404
from neo4jrestclient                    import client
from neo4jrestclient.request            import TransactionException
from neo4django.db                      import connection
from neo4django.db.models               import NodeModel
from neo4django.db.models.properties    import DateProperty, BoundProperty
from neo4django.db.models.relationships import MultipleNodes
from tastypie                           import fields
from tastypie.authentication            import Authentication, SessionAuthentication, BasicAuthentication, MultiAuthentication
from tastypie.authorization             import DjangoAuthorization
from tastypie.constants                 import ALL
from tastypie.exceptions                import Unauthorized
from tastypie.resources                 import ModelResource
from tastypie.serializers               import Serializer
from tastypie.utils                     import trailing_slash
from datetime                           import datetime
from easy_thumbnails.exceptions         import InvalidImageFormatError
from easy_thumbnails.files              import get_thumbnailer
import json
import re
import logging
import bleach
import os

logger = logging.getLogger(__name__)


class IndividualAuthorization(DjangoAuthorization):

    def get_topic_from_bundle(self, bundle):
        topic = get_topic_from_request(bundle.request)
        if topic == None:
            topic = Topic.objects.get(ontology_as_mod=get_model_topic(bundle.obj)).public
        return topic

    def check_contribution_permission(self, bundle, operation):
        authorized = False
        user = bundle.request.user
        app_label = bundle.request.current_topic.app_label()
        if user:
            perm_name  = "%s.contribute_%s" % (app_label, operation)
            authorized = user.is_staff or user.has_perm(perm_name)
        return authorized

    def read_detail(self, object_list, bundle):
        topic = self.get_topic_from_bundle(bundle)
        if not topic.public and not self.check_contribution_permission(bundle, 'read'):
            raise Unauthorized("Sorry, only staff or contributors can read resource.")
        return True

    def read_list(self, object_list, bundle):
        topic = self.get_topic_from_bundle(bundle)
        if not topic.public and not self.check_contribution_permission(bundle, 'read'):
            raise Unauthorized("Sorry, only staff or contributors can read resource.")
        return object_list

    def create_detail(self, object_list, bundle):
        if not self.check_contribution_permission(bundle, 'add'):
            raise Unauthorized("Sorry, only staff or contributors can create resource.")
        # check if user can add regarding to his plan
        topic         = get_topic_from_request(bundle.request)
        owner_profile = topic.author.detectiveprofileuser
        if owner_profile.nodes_max() > -1 and owner_profile.nodes_count()[topic.slug] >= owner_profile.nodes_max():
            raise Unauthorized("Sorry, you have to upgrade your plan.")
        return True

    def update_detail(self, object_list, bundle):
        if not self.check_contribution_permission(bundle, 'change'):
            raise Unauthorized("Sorry, only staff or contributors can update resource.")
        return True

    def delete_detail(self, object_list, bundle):
        if not self.check_contribution_permission(bundle, 'delete'):
            raise Unauthorized("Sorry, only staff or contributors can delete resource.")
        return True

    def delete_list(self, object_list, bundle):
        return False

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
        excludes = ['individual',]

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
        # By default, tastypie detects detail mode globally: it means that
        # even into an embeded resource (through a relationship), Tastypie will
        # serialize it as if we are in it's detail view.
        # We overide 'use_in' for every field with the value "detail"
        for field_name, field_object in self.fields.items():
            if field_object.use_in == 'detail':
                # We use a custom method
                field_object.use_in = self.use_in

    def prepend_urls(self):
        params = (self._meta.resource_name, trailing_slash())
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % params, self.wrap_view('get_search'), name="api_get_search"),
            url(r"^(?P<resource_name>%s)/mine%s$" % params, self.wrap_view('get_mine'), name="api_get_mine"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/patch%s$" % params, self.wrap_view('get_patch'), name="api_get_patch"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/patch/sources%s$" % params, self.wrap_view('get_patch_source'), name="api_get_create_source"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/patch/sources/(?P<source_pk>[0-9]*)%s$" % params, self.wrap_view('get_patch_source'), name="api_get_patch_source"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/authors%s$" % params, self.wrap_view('get_authors'), name="api_get_authors"),
            url(r"^(?P<resource_name>%s)/bulk_upload%s$" % params, self.wrap_view('bulk_upload'), name="api_bulk_upload"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/graph%s$" % params, self.wrap_view('get_graph'), name="api_get_graph"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/relationships%s$" % params, self.wrap_view('get_relationships'), name="api_get_relationships"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/relationships/(?P<field>\w[\w-]*)%s$" % params, self.wrap_view('get_relationships'), name="api_get_relationships_field"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/relationships/(?P<field>\w[\w-]*)/(?P<end>\w[\w-]*)%s$" % params, self.wrap_view('get_relationships'), name="api_get_relationships_field_end"),
        ]

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

    def get_topic(self, bundle=None):
        model = self.get_model()
        topic = None
        # Bundle given
        if bundle != None:
            # The topic may be set by a middleware
            topic = get_topic_from_request(bundle.request)
        # No topic found
        if topic == None:
            # We found the topic according to the current model
            topic = Topic.objects.get(ontology_as_mod=get_model_topic(model))
        return topic

    @property
    def topic(self):
        return self.get_topic()

    def get_model_fields(self, name=None, model=None):
        if model is None: model = self.get_model()
        if name is None:
            # Find fields of the queryset's model
            return model._meta.fields
        else:
            fields = [f for f in model._meta.fields if f.name == name]
            return fields[0] if len(fields) else None

    def get_model_field(self, name, model=None):
        if model is None: model = self.get_model()
        target = None
        for field in self.get_model_fields(model=model):
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
        # Use in detail
        return self.get_resource_uri(bundle) == bundle.request.path

    def dehydrate(self, bundle):
        # Get the request from the bundle
        request = bundle.request
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

        to_add = dict()
        for field in bundle.data:
            # Image field
            if field == 'image':
                # Get thumbnails
                try:
                    url_or_path = bundle.data[field]
                    # Remove host for local url
                    if is_local(request, url_or_path or ''):
                        # By removing the host, we'll force django
                        # to read the file instead of downloading it
                        url_or_path = url_or_path.split( request.get_host() )[1]
                        url_or_path = url_or_path.replace(settings.MEDIA_URL, '/')
                    try:
                        #  Use a file instance and download external only
                        #  on detail view (to avoid heavy loading)
                        image = get_image(url_or_path, download_external=self.use_in(bundle))
                    # The given url is not a valid image
                    except (NotAnImage, OversizedFile):
                        # Save the new URL to avoid reloading it
                        setattr(bundle.obj, field, None)
                        bundle.obj.save()
                        continue
                    # The image might be temporary unvailable
                    except UnavailableImage: continue
                    # Skip none value
                    if image is None: continue
                    # Build the media url using the request
                    media_url = request.build_absolute_uri(settings.MEDIA_URL)
                    # Extract public name
                    public_name = lambda i: os.path.join(media_url,  i.replace(settings.MEDIA_ROOT, '').strip('/') )
                    # Return the public url
                    bundle.data[field] = public_name(image.name)
                    # The image url changed...
                    if getattr(bundle.obj, field) != public_name(image.name):
                        # Save the new URL to avoid reloading it
                        setattr(bundle.obj, field, public_name(image.name))
                        bundle.obj.save()
                    # Create thumbnailer with the file
                    thumbnailer = get_thumbnailer(image.name)

                    to_add[field + '_thumbnail'] = {
                        key : public_name(thumbnailer.get_thumbnail({
                            'size': size,
                            'crop': True
                        }).name)
                        for key, size in settings.THUMBNAIL_SIZES.items()
                    }
                except InvalidImageFormatError as e:
                    print e
                    to_add[field + '_thumbnail'] = ''

            # Convert tuple to array for better serialization
            if type( getattr(bundle.obj, field, None) ) is tuple:
                bundle.data[field] = list( getattr(bundle.obj, field) )
            # Get the output transformation for this field
            transform = rules.field(field).get("transform", None)
            # This is just a string
            # For complex formating use http://docs.python.org/2/library/string.html#formatspec
            if type(transform) is str:
                bundle.data[field] = transform.format(**bundle.data)
            # We can also receive a function
            elif callable(transform):
                bundle.data[field] = transform(bundle.data, field)

        for key in to_add.keys():
            bundle.data[key] = to_add[key]

        return bundle


    def get_model_node(self):
        # Wraps the graph method with the model of this ressource
        return graph.get_model_node( self.get_model() )

    def obj_create(self, bundle, **kwargs):
        # Feed request object with the bundle
        request = bundle.request
        # Since we are not using the native save method
        # we need to check autorization here
        self.authorized_create_detail(self.get_object_list(request), bundle)
        # The only field allowed during creation is "name"
        data = dict(name=bundle.data.get("name", None), _author=[request.user.id])
        data = self.validate(data)
        # Model class
        model = self.get_model()
        # Find the node associate to this model
        model_node = self.get_model_node()
        # Start a transaction to batch insert values
        with connection.transaction(commit=False) as tx:
            # Create a brand new node
            node = connection.nodes.create(**data)
            # Instanciate its type
            rel_type = connection.relationships.create(model_node, "<<INSTANCE>>", node)
        # Commit the transaction
        tx.commit()
        # Create an object to build the bundle
        obj = node.properties
        obj["id"] = node.id
        # update the cache
        topic_cache.incr_version(request.current_topic)
        # Return a new bundle
        return self.build_bundle(obj=model._neo4j_instance(node), data=obj, request=request)

    def obj_get(self, **kwargs):
        pk      = kwargs["pk"]
        bundle  = kwargs["bundle"]
        request = bundle.request
        # Current model
        model = self.get_model()

        # Get the node's data using the rest API
        try: node = connection.nodes.get(pk)
        # Node not found
        except client.NotFoundError: raise Http404("Not found.")
        # Create a model istance from the node
        return model._neo4j_instance(node)

    def get_detail(self, request, **kwargs):
        basic_bundle = self.build_bundle(request=request)
        kwargs["bundle"] = basic_bundle
        obj    = self.obj_get(**kwargs)
        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle, True)
        return self.create_response(request, bundle)

    def alter_detail_data_to_serialize(self, request, bundle, nested=False):
        model = self.get_model()
        # Get relationships fields
        fields = [ f for f in model._meta.fields if f.get_internal_type() == 'Relationship']
        node_rels = bundle.obj.node.relationships.all()
        # If the nested parameter is True, this set
        node_to_retreive = set()
        # Resolve relationships manualy
        for field in fields:
            # Get relationships for this fields
            field_rels = [ rel for rel in node_rels[:] if rel.type == field._type]
            # Filter relationships to keep only the well oriented relationships
            # get the related field informations
            related_field = [f for f in iterate_model_fields(model) if "rel_type" in f and f["rel_type"] == field._type and "name" in f and f["name"] == field._BoundRelationship__attname]
            if related_field:
                # Note (edouard): check some assertions in case I forgot something
                assert len(related_field) == 1, related_field
                assert related_field[0]["direction"]
                # choose the end point to check
                end_point_side = "start" if related_field[0]["direction"] == "out" else "end"
                # filter the relationship
                field_rels = [rel for rel in field_rels if getattr(rel, end_point_side).id == bundle.obj.id]
            # Get node ids for those relationships
            field_oposites = [ graph.opposite(rel, bundle.obj.id) for rel in field_rels ]
            # Save the list into properities
            bundle.data[field.name] = field_oposites
            # Nested mode to true: we need to retreive every node
            if nested: node_to_retreive = set(list(node_to_retreive) + field_oposites)
        # There is node to extract for the graph
        if len(node_to_retreive):
            # Build the query to get all node in one request
            query = "start n=node(%s) RETURN ID(n), n" % ",".join(map(str, node_to_retreive))
            # Get all nodes as raw values to avoid unintended request to the graph
            nodes = connection.query(query, returns=(int, dict))
            # Helper lambda to retreive a node
            retreive_node = lambda idx: next(n[1]["data"] for n in nodes if n[0] == idx)
            # Populate the relationships field with there node instance
            for field in fields:
                # Retreive the list of ids
                for i, idx in enumerate(bundle.data[field.name]):
                    rel_node = retreive_node(idx)
                    # Save the id which is not a node property
                    rel_node["id"] = idx
                    # Update value
                    bundle.data[field.name][i] = self.validate(rel_node, field.target_model, allow_missing=True)
        # Show additional field following the model's rules
        rules = request.current_topic.get_rules().model(self.get_model()).all()
        # All additional relationships
        for key in rules:
            # Filter rules to keep only Neomatch instance.
            # Neomatch is a class to create programmaticly a search related to
            # this node.
            if isinstance(rules[key], Neomatch):
                bundle.data[key] = rules[key].query(bundle.obj.id)
        return bundle

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        query     = request.GET.get('q', '').lower()
        query     = re.sub("\"|'|`|;|:|{|}|\|(|\|)|\|", '', query).strip()
        limit     = int( request.GET.get('limit', 20))
        exclude   = int( request.GET.get('exclude', -1) )
        # Do the query.
        results   = self._meta.queryset.filter(name__icontains=query)
        # Quicker than query exclude
        results   = [r for r in results if r.id != exclude]
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

    def validate(self, data, model=None, allow_missing=False):
        if model is None: model = self.get_model()
        cleaned_data = {}
        for field_name in data:
            field = self.get_model_field(field_name, model)
            if field is not None:
                # Boolean field must be validate manually
                if field.get_internal_type() == 'BooleanField':
                    if type(data[field_name]) is not bool:
                        raise ValidationError({field_name: 'Must be a boolean value'})
                        if not allow_missing:
                            raise ValidationError({field_name: 'Must be a boolean value'})
                        # Skip this field
                        else: continue
                    cleaned_data[field_name] = data[field_name]
                # Only literal values have a _property attribute
                elif hasattr(field, "_property"):
                    try:
                        try:
                            # Get a single field validator
                            formfield = field._property.formfield()
                            # Validate and clean data
                            cleaned_data[field_name] = formfield.clean(data[field_name])
                        except TypeError:
                            validators = getattr(field._property, "validators", [])
                            # This field has several validators
                            for validator in field._property.validators:
                                # Process validation with every validator
                                validator(data[field_name])
                            # @warning: this will validate the data for
                            # array of values but not clean them
                            cleaned_data[field_name] = data[field_name]
                    except ValidationError as e:
                        # Raise the same error the field name as key
                        if not allow_missing: raise ValidationError({field_name: e.messages})
                # The given value is a relationship
                elif hasattr(field, "target_model") and type(data[field_name]) is list:
                    # The validation method will collect targets ID
                    cleaned_data[field_name] = []
                    # Relationships can be added using to ways:
                    # * a list of numeric id
                    # * a list of objects containing an id key (final formatspec)
                    for rel in data[field_name]:
                        # Common error message
                        error = "Bad relationship value"
                        # Evaluate the relation as a string:
                        if type(rel) is str:
                            # it must be a numeric value
                            if rel.isnumeric():
                                # We can add the value to the list.
                                # We take care of casting it to integer.
                                cleaned_data[field_name].append( int(rel) )
                            elif not allow_missing:
                                raise ValidationError({field_name: error})
                        # This is an integer, we're just passing
                        elif type(rel) is int:
                            # We can add the value to the list
                            cleaned_data[field_name].append(rel)
                        # This is an object
                        elif type(rel) is dict:
                            # The given object as no ID
                            if "id" not in rel:
                                raise ValidationError({field_name: error})
                            elif not allow_missing:
                                # Add and cast the value
                                cleaned_data[field_name].append( int(rel["id"]) )
                # Treat id
                elif field.name == "id": cleaned_data[field_name] = int(data[field_name])

        return cleaned_data


    def obj_delete(self, bundle, **kwargs):
        super(IndividualResource, self).obj_delete(bundle, **kwargs)
        # update the cache
        topic_cache.incr_version(bundle.request.current_topic)

    def get_patch(self, request, **kwargs):
        pk = kwargs["pk"]
        # This should be a POST request
        self.method_check(request, allowed=['post'])
        self.throttle_check(request)
        # User must be authentication
        self.is_authenticated(request)
        bundle = self.build_bundle(request=request)
        # User allowed to update this model
        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        # Get the node's data using the rest API
        try: node = connection.nodes.get(pk)
        # Node not found
        except client.NotFoundError: raise Http404("Not found.")
        # Load every relationship only when we need to update a relationship
        node_rels = None
        # Parse only body string
        body = json.loads(request.body) if type(request.body) is str else request.body
        # Copy data to allow dictionary resizing
        data = body.copy()
        # Received per-field sources
        if "field_sources" in data:
            # field_sources must not be treated here, see patch_source method
            field_sources = data.pop("field_sources")
        # Validate data.
        # If it fails, it will raise a ValidationError
        data = self.validate(data)
        # Get author list (or a new array if )
        author_list = node.properties.get("_author", [])
        # This is the first time the current user edit this node
        if int(request.user.id) not in author_list:
            # Add the author to the author list
            data["_author"] = author_list + [request.user.id]
        # @TODO check that 'node' is an instance of 'model'
        # Set new values to the node
        for field_name in data:
            field       = self.get_model_field(field_name)
            field_value = data[field_name]
            # The value can be a list of ID for relationship
            if field.get_internal_type() is 'Relationship':
                # Pluck id from the list
                field_ids = [ value for value in field_value if value is not int(pk) ]
                # Prefetch all relationship
                if node_rels is None: node_rels = node.relationships.all()
                # Get relationship name
                rel_type = self.get_model_field(field_name)._type
                # We don't want to add this relation twice so we extract
                # every node connected to the current one through this type
                # of relationship. "existing_rels_id" will contain the ids of
                # every node related to this one.
                existing_rels = [ rel for rel in node_rels if rel.type == rel_type ]
                existing_rels_id = [ graph.opposite(rel, pk) for rel in existing_rels ]
                # Get every ids from "field_ids" that ain't not in
                # the list of existing relationship "existing_rel_id".
                new_rels_id = set(field_ids).difference(existing_rels_id)
                # Get every ids from "existing_rels_id" that ain't no more
                # in the new list of relationships "field_ids".
                old_rels_id = set(existing_rels_id).difference(field_ids)
                # Start a transaction to batch import values
                with connection.transaction(commit=False) as tx:
                    # Convert ids or related node to *node* instances
                    new_rels_node = [ connection.nodes.get(idx) for idx in new_rels_id ]
                    # Convert ids or unrelated node to *relationships* instances
                    old_rels    = []
                    # Convert ids list into relationship instances
                    for idx in old_rels_id:
                        # Find the relationship that match with this id
                        matches = [ rel for rel in existing_rels if graph.connected(rel, idx) ]
                        # Merge the list of relationships
                        old_rels = old_rels + matches
                # Commit change when every field was treated
                tx.commit()
                # Start a transaction to batch insert/delete values
                with connection.transaction(commit=False) as tx:
                    # Then create the new relationships (using nodes instances)
                    # Outcoming relationship
                    if field.direction == 'out':
                        [ connection.relationships.create(node, rel_type, n) for n in new_rels_node ]
                    # Incoming relationship
                    elif field.direction == 'in':
                        [ connection.relationships.create(n, rel_type, node) for n in new_rels_node ]
                    # Then delete the old relationships (using relationships instance)
                    [ rel.delete() for rel in old_rels ]
                # Commit change when every field was treated
                tx.commit()
            # Or a literal value
            # (integer, date, url, email, etc)
            else:
                # Current model
                model = self.get_model()
                # Fields
                fields = { x['name'] : x for x in iterate_model_fields(model) }
                # Remove the values
                if field_value in [None, '']:
                    if field_name == 'image' and fields[field_name]['type'] == 'URLField':
                        self.remove_node_file(node, field_name, True)
                    # The field may not exists (yet)
                    try:
                        node.delete(field_name)
                    # It's OK, it just means we don't have to remove it
                    except client.NotFoundError: pass
                # We simply update the node property
                # (the value is already validated)
                else:
                    if field_name in fields:
                        if 'is_rich' in fields[field_name]['rules'] and fields[field_name]['rules']['is_rich']:
                            data[field_name] = field_value = bleach.clean(field_value,
                                                                          tags=("br", "blockquote", "ul", "ol",
                                                                                "li", "b", "i", "u", "a", "p"),
                                                                          attributes={
                                                                              '*': ("class",),
                                                                              'a': ("href", "target")
                                                                          })
                        if field_name == 'image' and fields[field_name]['type'] == 'URLField':
                            self.remove_node_file(node, field_name, True)
                            try:
                                image_file = download_url(data[field_name])
                                path = default_storage.save(os.path.join(settings.UPLOAD_ROOT, image_file.name) , image_file)
                                data[field_name] = field_value = path.replace(settings.MEDIA_ROOT, "")
                            except UnavailableImage:
                                data[field_name] = field_value = ""
                            except NotAnImage:
                                data[field_name] = field_value = ""
                            except OversizedFile:
                                data[field_name] = field_value = ""
                    node.set(field_name, field_value)
        # update the cache
        topic_cache.incr_version(request.current_topic)
        # And returns cleaned data
        return self.create_response(request, data)

    def get_patch_source(self, request, **kwargs):
        import time
        start_time = time.time()

        def delete_source(source_id):
            node = connection.nodes.get(source_id)
            rels = node.relationships.all()
            [ rel.delete() for rel in rels ]
            deleted = node.delete()
            return None

        def update_source(individual, source_id, data):
            res = {}
            src_node = connection.nodes.get(source_id)
            src_node['reference'] = data['reference']
            res = data
            return res

        def create_source(individual, data):
            res = {}
            # took from neo4django.db.base.NodeModel._save_node_model
            type_hier_props = [{'app_label': t._meta.app_label,
                                'model_name': t.__name__} for t in FieldSource._concrete_type_chain()]
            type_hier_props = list(reversed(type_hier_props))
            #get all the names of all types, including abstract, for indexing
            type_names_to_index = [t._type_name() for t in FieldSource.mro()
                                   if (issubclass(t, NodeModel) and t is not NodeModel)]
            create_groovy = '''
            node = Neo4Django.createNodeWithTypes(types)
            Neo4Django.indexNodeAsTypes(node, indexName, typesToIndex)
            node.field = field
            node.individual = individual
            node.reference = reference
            results = node
            '''
            data.update({'individual': individual.id})
            node = connection.gremlin_tx(create_groovy, types=type_hier_props,
                                          indexName=FieldSource.index_name(),
                                          typesToIndex=type_names_to_index, **data)

            # for field, val in data.items():
            #     node.set(field, val)

            res['id'] = node.id
            res.update(data)

            # tx.commit()
            # remove added individual
            if res.get('individual'):
                del res['individual']
            return res

        pk = kwargs["pk"]
        individual = None
        source_id = kwargs.get('source_pk')
        # This should be a POST request
        self.method_check(request, allowed=['post', 'delete'])
        self.throttle_check(request)
        # User must be authentication
        self.is_authenticated(request)
        bundle = self.build_bundle(request=request)
        # User allowed to update this model
        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        # Get the node's data using the rest API
        try: individual = connection.nodes.get(pk)
        # Node not found
        except client.NotFoundError: raise Http404("Not found.")

        source = None
        if request.method == 'POST':
            body = json.loads(request.body)
            data = body.copy()
            if source_id != None:
                if data.get('reference') in ['', None]:
                    source = delete_source(source_id)
                else:
                    source = update_source(individual, source_id, data)
            else:
                source = create_source(individual, data)
        elif request.method == 'DELETE':
            delete_source(source_id)

        print "Took %f to patch sources" % (time.time() - start_time)
        return self.create_response(request, source)

    def get_authors(self, request, **kwargs):
        pk = kwargs["pk"]
        # This should be a POST request
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        # User must be authentication
        self.is_authenticated(request)
        bundle = self.build_bundle(request=request)
        # Resource to returns
        resource = UserNestedResource()
        # User must be the author of the topic
        if not request.user.is_staff and request.user.id != self.get_topic(bundle).author.id:
            # Returns an empty set of authors
            return resource.create_response(request, [])
        # Get the node's data using the rest API
        try: node = connection.nodes.get(pk)
        # Node not found
        except client.NotFoundError: raise Http404("Not found.")
        # Get the authors ids
        authors_ids = node.properties.get("_author", [])
        # Find them in the database
        authors = User.objects.filter(id__in=authors_ids).select_related("profile")
        # Create a bundle with each resources
        bundles = [resource.build_bundle(obj=a, request=request) for a in authors]
        data = [resource.full_dehydrate(bundle) for bundle in bundles]
        # We ask for relationship properties
        return resource.create_response(request, data)

    def get_relationships(self, request, **kwargs):
        # Extract node id from given node uri
        def node_id(uri)       : return re.search(r'(\d+)$', uri).group(1)
        # Get the end of the given relationship
        def rel_from(rel, side): return node_id(rel.__dict__["_dic"][side])
        # Is the given relation connected to the given uri
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
                    if though:
                        # Get the properties for this relationship
                        try:
                            properties = though.objects.get(_relationship=ids[0])
                        except though.DoesNotExist:
                            endnodes = [ int(pk), int(end) ]
                            # We ask for relationship properties
                            return self.create_response(request, {
                                "_relationship": ids[0],
                                "_endnodes": endnodes
                            })
                        else:
                            # Get the module for this model
                            module = self.dummy_class_to_ressource(though)
                            # Instanciate the resource
                            resource = import_class(module)()
                            # Create a bundle with this resource
                            bundle = resource.build_bundle(obj=properties, request=request)
                            bundle = resource.full_dehydrate(bundle, for_list=True)
                            # We ask for relationship properties
                            return resource.create_response(request, bundle)
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
        depth = int(request.GET['depth']) if 'depth' in request.GET.keys() else 2
        topic = Topic.objects.get(ontology_as_mod=get_model_topic(self.get_model()))
        leafs, edges = get_leafs_and_edges(
            topic     = topic,
            depth     = depth,
            root_node = kwargs['pk'])
        self.log_throttled_access(request)
        return self.create_response(request, {'leafs': leafs, 'edges' : edges})

    def remove_node_file(self, node, field_name, thumbnails=False):
        try:
            file_name = os.path.join(settings.MEDIA_ROOT, node.get(field_name).strip('/'))
            default_storage.delete(file_name)

            if thumbnails:
                extension = file_name.split('.')[-1].lower().replace('jpeg', 'jpg')
                suffixes = [".{0}x{1}_q85_crop.".format(size[0], size[1]) for size in settings.THUMBNAIL_SIZES.values()]
                for suffix in suffixes:
                    full_file_name = "{0}{1}{2}".format(file_name, suffix, extension)
                    if default_storage.exists(full_file_name):
                        default_storage.delete(full_file_name)
        except:
            pass

# EOF
