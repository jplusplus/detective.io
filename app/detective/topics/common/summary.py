# -*- coding: utf-8 -*-
from .errors                  import ForbiddenError, UnauthorizedError
from app.detective.models     import Topic
from app.detective.search     import Search
from app.detective.neomatch   import Neomatch
from app.detective.parser     import schema
from app.detective.individual import IndividualAuthorization
from app.detective            import graph, utils
from difflib                  import SequenceMatcher
from django.core.paginator    import Paginator, InvalidPage
from django.http              import Http404, HttpResponse
from neo4django.db            import connection
from tastypie                 import http
from tastypie.exceptions      import ImmediateHttpResponse
from tastypie.resources       import Resource
from tastypie.serializers     import Serializer
from .jobs                    import process_bulk_parsing_and_save_as_model, render_csv_zip_file
import json
import re
import logging
import django_rq
import inspect
import hashlib

# Get an instance of a logger
logger = logging.getLogger(__name__)

class SummaryResource(Resource):
    # Local serializer
    serializer = Serializer(formats=["json", "jsonp"]).serialize

    class Meta:
        allowed_methods = ['get', 'post']
        authorization   = IndividualAuthorization()
        resource_name   = 'summary'
        object_class    = object

    @staticmethod
    def get_page_number(offset=0, limit=20):
        if offset < 0:
            return -1
        else:
            return int(round(offset / limit)) +  1

    def obj_get_list(self, request=None, **kwargs):
        # Nothing yet here!
        raise Http404("Sorry, not implemented yet!")

    def discover_method(self, request=None, **kwargs):
        content = {}
        # Deduces request from bundle
        if request is None and "bundle" in kwargs: request = kwargs["bundle"].request
        # Refresh syntax cache at each request
        if hasattr(self, "syntax"): delattr(self, "syntax")
        # Get the current topic
        self.topic = self.get_topic_or_404(request=request)
        # Create a search instance
        self.search = Search(topic=self.topic)
        # Check for an optional method to do further dehydration.
        method = getattr(self, "summary_%s" % kwargs["pk"], None)
        if method:
            try:
                self.throttle_check(request)
                content = method(kwargs["bundle"], request)
                if isinstance(content, HttpResponse):
                    response = content
                else:
                    # Create an HTTP response
                    response = self.create_response(data=content, request=request)
            except ForbiddenError as e:
                response = http.HttpForbidden(e)
            except UnauthorizedError as e:
                response = http.HttpUnauthorized(e)
        else:
            # Stop here, unkown summary type
            raise Http404("Sorry, not implemented yet!")
        # We force tastypie to render the response directly
        raise ImmediateHttpResponse(response=response)

    def obj_get(self, request=None, **kwargs):
        # User must be allow to see this topic
        self.authorized_read_list(None, kwargs["bundle"])
        return self.discover_method(request, **kwargs)

    def post_detail(self, request=None, **kwargs):
        kwargs["bundle"] = self.build_bundle(request=request)
         # User must be allow to edit this topic
        self.authorized_create_detail(None, kwargs["bundle"])
        return self.discover_method(request, **kwargs)

    def get_topic_or_404(self, request=None):
        try:
            if request is not None:
                topic = utils.get_topic_from_request(request)
                if topic == None:
                    raise Topic.DoesNotExist()
                return topic
            else:
                return Topic.objects.get(ontology_as_mod=self._meta.urlconf_namespace)
        except Topic.DoesNotExist:
            raise Http404()

    def summary_jsonschema(self, bundle, request):
        return schema.ontology

    def summary_countries(self, bundle, request):
        app_label = self.topic.app_label()
        # Query to aggreagte relationships count by country
        query = """
            START n=node(*)
            MATCH (m)-[:`<<INSTANCE>>`]->(i)<-[*0..1]->(country)<-[r:`<<INSTANCE>>`]-(n)
            WHERE HAS(country.isoa3)
            AND HAS(n.model_name)
            AND n.model_name = 'Country'
            AND n.app_label = '%s'
            AND HAS(country.isoa3)
            RETURN country.isoa3 as isoa3, ID(country) as id, count(i)-1 as count
        """ % app_label
        # Get the data and convert it to dictionnary
        countries = connection.cypher(query).to_dicts()
        obj       = {}
        for country in countries:
            # Use isoa3 as identifier
            obj[ country["isoa3"] ] = country
            # ISOA3 is now useless
            del country["isoa3"]
        return obj

    def summary_types(self, bundle, request):
        app_label = self.topic.app_label()
        # Query to aggreagte relationships count by country
        query = """
            START n=node(*)
            MATCH (c)<-[r:`<<INSTANCE>>`]-(n)
            WHERE HAS(n.model_name)
            AND n.app_label = '%s'
            RETURN ID(n) as id, n.model_name as name, count(c) as count
        """ % app_label
        # Get the data and convert it to dictionnary
        types = connection.cypher(query).to_dicts()
        obj   = {}
        for t in types:
            # Use name as identifier
            obj[ t["name"].lower() ] = t
            # name is now useless
            del t["name"]
        return obj

    def summary_forms(self, bundle, request):
        available_resources = {}
        # Get the model's rules manager
        rulesManager = request.current_topic.get_rules()
        # Fetch every registered model
        # to print out its rules
        for model in self.topic.get_models():
            name                = model.__name__.lower()
            rules               = rulesManager.model(model).all()
            fields              = utils.get_model_fields(model)
            verbose_name        = getattr(model._meta, "verbose_name", name)
            verbose_name_plural = getattr(model._meta, "verbose_name_plural", verbose_name + "s")

            for key in rules:
                # Filter rules to keep only Neomatch
                if isinstance(rules[key], Neomatch):
                    fields.append({
                        "name"         : key,
                        "type"         : "ExtendedRelationship",
                        "verbose_name" : rules[key].title,
                        "rules"        : {},
                        "related_model": rules[key].target_model.__name__
                    })

            for field in fields:
                # Create a copy of the rule to avoid compromize the rules singleton
                field["rules"] = field["rules"].copy()
                for key, rule in field["rules"].items():
                    # Convert class to model name
                    if inspect.isclass(rule):
                        field["rules"][key] = getattr(rule, "__name__", rule)

            try:
                idx = model.__idx__
            except AttributeError:
                idx = 0
            available_resources[name] = {
                'description'         : getattr(model, "_description", None),
                'topic'               : getattr(model, "_topic", self.topic.slug) or self.topic.slug,
                'model'               : getattr(model, "__name__", ""),
                'verbose_name'        : verbose_name,
                'verbose_name_plural' : verbose_name_plural,
                'name'                : name,
                'fields'              : fields,
                'rules'               : rules,
                'index'               : idx
            }

        return available_resources

    def summary_mine(self, bundle, request):
        app_label = self.topic.app_label()
        self.method_check(request, allowed=['get'])

        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        if request.user.id is None:
            object_list = {
                'objects': [],
                'meta': {
                    'page': 1,
                    'limit': limit,
                    'total_count': 0
                }
            }
        else:
            query = """
                START root=node(0)
                MATCH (node)<-[r:`<<INSTANCE>>`]-(type)<-[`<<TYPE>>`]-(root)
                WHERE HAS(node.name)
                AND HAS(node._author)
                AND HAS(type.model_name)
                AND %s IN node._author
                AND type.app_label = '%s'
                RETURN DISTINCT ID(root) as id, node.name as name, type.model_name as model
            """ % ( int(request.user.id), app_label )

            matches      = connection.cypher(query).to_dicts()
            paginator    = Paginator(matches, limit)

            try:
                p     = self.get_page_number(offset, limit)
                page  = paginator.page(p)
            except InvalidPage:
                raise Http404("Sorry, no results on that page.")

            objects = []
            for result in page.object_list:
                label = result.get("name", None)
                objects.append({
                    'label': label,
                    'subject': {
                        "name": result.get("id", None),
                        "label": label
                    },
                    'predicate': {
                        "label": "is instance of",
                        "name": "<<INSTANCE>>"
                    },
                    'object': result.get("model", None)
                })

            object_list = {
                'objects': objects,
                'meta': {
                    'page': p,
                    'limit': limit,
                    'total_count': paginator.count
                }
            }

        return object_list


    def summary_search(self, bundle, request):
        self.method_check(request, allowed=['get'])

        if not "q" in request.GET: raise Exception("Missing 'q' parameter")

        limit     = int(request.GET.get('limit', 20))
        offset    = int(request.GET.get('offset', 0))
        query     = bundle.request.GET["q"].lower()
        results   = self.search.by_name(query)
        paginator = Paginator(results, limit)

        try:
            p     = self.get_page_number(offset, limit )
            page  = paginator.page(p)
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        objects = []
        for result in page.object_list:
            objects.append(result)

        object_list = {
            'objects': objects,
            'meta': {
                'q': query,
                'limit': limit,
                'total_count': paginator.count
            }
        }

        self.log_throttled_access(request)
        return object_list

    def summary_rdf_search(self, bundle, request):
        self.method_check(request, allowed=['get'])
        limit     = int(request.GET.get('limit', 20))
        offset    = int(request.GET.get('offset', 0))
        query     = json.loads(request.GET.get('q', 'null'))
        if query == None:
            return []
        try:
            object_list = self.topic.rdf_search(query, limit, offset)
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")
        self.log_throttled_access(request)
        return object_list

    def summary_human(self, bundle, request):
        self.method_check(request, allowed=['get'])

        if not "q" in request.GET: raise Exception("Missing 'q' parameter")

        query        = request.GET["q"]
        query        = query.strip()
        # Find the kown match for the given query
        matches      = self.search.find_matches(query)
        # Build and returns a list of proposal
        propositions = self.search.build_propositions(matches, query)

        # Build paginator
        limit        = int(request.GET.get('limit', 20))
        offset       = int(request.GET.get('offset', 0))
        paginator    = Paginator(propositions, limit)

        try:
            p     = self.get_page_number(offset, limit )
            page  = paginator.page(p)
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        objects = []
        for result in page.object_list:
            objects.append(result)

        object_list = {
            'objects': objects,
            'meta': {
                'q': query,
                'limit': limit,
                'offset': offset,
                'total_count': paginator.count
            }
        }

        self.log_throttled_access(request)
        return object_list

    def summary_graph(self, bundle, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        depth     = int(request.GET['depth']) if 'depth' in request.GET.keys() else 1
        leafs, edges  = utils.get_leafs_and_edges(
            topic     = self.topic,
            depth     = depth,
            root_node = "0")
        self.log_throttled_access(request)
        return self.create_response(request, {'leafs': leafs, 'edges' : edges})

    def summary_bulk_upload(self, bundle, request):
        # only allow POST requests
        self.method_check(request, allowed=['post'])
        # check session
        if not request.user.id:
            raise UnauthorizedError('This method require authentication')
        # flattern the list of files
        files = [file for sublist in request.FILES.lists() for file in sublist[1]]
        # reads the files
        files = [(f.name, f.readlines()) for f in files]
        # enqueue the parsing job
        queue = django_rq.get_queue('default', default_timeout=7200)
        job   = queue.enqueue(process_bulk_parsing_and_save_as_model, self.topic, files)
        # return a quick response
        self.log_throttled_access(request)
        return {
            "status" : "enqueued",
            "token"  : job.get_id()
        }

    def summary_export(self, bundle, request):
        self.method_check(request, allowed=['get'])
        # check from cache
        cache_key = "summary_export_{type}_{query}" \
            .format( type  = request.GET.get("type", "all"),
                     query = hashlib.md5(request.GET.get("q", "null")).hexdigest())
        response_in_cache = utils.topic_cache.get(self.topic, cache_key)
        if response_in_cache: # could be empty or str("<filename>")
            logger.debug("export already exist from cache")
            response = dict(status="ok", file_name=response_in_cache)
        else:
            # return a quick response
            response = dict(
                status = "enqueued")
            # check if a job already exist
            for job in django_rq.get_queue('high').jobs:
                if job.meta["cache_key"] == cache_key:
                    response["token"] = job.id
                    logger.debug("job_already_exist")
                    break
            else:
                # enqueue the job
                queue = django_rq.get_queue('high', default_timeout=360)
                job = queue.enqueue(render_csv_zip_file,
                                    topic      = self.topic,
                                    model_type = request.GET.get("type"),
                                    query      = json.loads(request.GET.get('q', 'null')),
                                    cache_key  = cache_key)
                # save the cache_key in the meta data in order to check if a job already exist for this key later
                job.meta["cache_key"] = cache_key
                job.save()
                response['token'] = job.id
        self.log_throttled_access(request)
        return response

    def summary_syntax(self, bundle, request): return self.search.get_syntax()

# EOF
