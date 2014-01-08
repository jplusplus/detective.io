# -*- coding: utf-8 -*-
from app.detective.models     import Topic
from app.detective.neomatch   import Neomatch
from app.detective.register   import topics_rules
from app.detective.utils      import get_model_fields, get_topic_models, uploaded_to_tempfile
from difflib                  import SequenceMatcher
from django.core.paginator    import Paginator, InvalidPage
from django.core.urlresolvers import resolve
from django.http              import Http404, HttpResponse
from neo4django.db            import connection
from tastypie                 import http
from tastypie.exceptions      import ImmediateHttpResponse
from tastypie.resources       import Resource
from tastypie.serializers     import Serializer
import json
import re
import csv
import logging

from .errors import *

# Get an instance of a logger
logger = logging.getLogger(__name__)

class SummaryResource(Resource):
    # Local serializer
    serializer = Serializer(formats=["json"]).serialize

    class Meta:
        allowed_methods = ['get', 'post']
        resource_name   = 'summary'
        object_class    = object

    def obj_get_list(self, request=None, **kwargs):
        # Nothing yet here!
        raise Http404("Sorry, not implemented yet!")

    def obj_get(self, request=None, **kwargs):
        content = {}
        # Get the current topic
        self.topic = self.get_topic_or_404(request=request)
        # Check for an optional method to do further dehydration.
        method = getattr(self, "summary_%s" % kwargs["pk"], None)
        if method:
            try:
                self.throttle_check(kwargs["bundle"].request)
                content = method(kwargs["bundle"], kwargs["bundle"].request)
                # Serialize content in json
                # @TODO implement a better format support
                content  = self.serializer(content, "application/json")
                # Create an HTTP response
                response = HttpResponse(content=content, content_type="application/json")
            except ForbiddenError as e:
                response = http.HttpForbidden(e)
            except UnauthorizedError as e:
                response = http.HttpUnauthorized(e)
        else:
            # Stop here, unkown summary type
            raise Http404("Sorry, not implemented yet!")
        # We force tastypie to render the response directly
        raise ImmediateHttpResponse(response=response)

    # TODO : factorize obj_get and post_detail methods
    def post_detail(self, request=None, **kwargs):
        content = {}
        # Get the current topic
        self.topic = self.get_topic_or_404(request=request)
        # Check for an optional method to do further dehydration.
        method = getattr(self, "summary_%s" % kwargs["pk"], None)
        if method:
            try:
                self.throttle_check(request)
                content = method(request, **kwargs)
                # Serialize content in json
                # @TODO implement a better format support
                content  = self.serializer(content, "application/json")
                # Create an HTTP response
                response = HttpResponse(content=content, content_type="application/json")
            except ForbiddenError as e:
                response = http.HttpForbidden(e)
            except UnauthorizedError as e:
                response = http.HttpUnauthorized(e)
        else:
            # Stop here, unkown summary type
            raise Http404("Sorry, not implemented yet!")
        raise ImmediateHttpResponse(response=response)

    def get_topic_or_404(self, request=None):
        try:
            if request is not None:
                return Topic.objects.get(module=resolve(request.path).namespace)
            else:
                return Topic.objects.get(module=self._meta.urlconf_namespace)
        except Topic.DoesNotExist:
            raise Http404()

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
        rulesManager = topics_rules()
        # Fetch every registered model
        # to print out its rules
        for model in get_topic_models(self.topic.module):
            name                = model.__name__.lower()
            rules               = rulesManager.model(model).all()
            fields              = get_model_fields(model)
            verbose_name        = getattr(model._meta, "verbose_name", name).title()
            verbose_name_plural = getattr(model._meta, "verbose_name_plural", verbose_name + "s").title()

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

            available_resources[name] = {
                'description'         : getattr(model, "_description", None),
                'topic'               : getattr(model, "_topic", self.topic.slug) or self.topic.slug,
                'model'               : getattr(model, "__name_", ""),
                'verbose_name'        : verbose_name,
                'verbose_name_plural' : verbose_name_plural,
                'name'                : name,
                'fields'              : fields,
                'rules'               : rules
            }

        return available_resources

    def summary_mine(self, bundle, request):
        app_label = self.topic.app_label()
        self.method_check(request, allowed=['get'])
        if not request.user.id:
            raise UnauthorizedError('This method require authentication')

        query = """
            START root=node(*)
            MATCH (type)-[`<<INSTANCE>>`]->(root)
            WHERE HAS(root.name)
            AND HAS(root._author)
            AND HAS(type.model_name)
            AND %s IN root._author
            AND type.app_label = '%s'
            RETURN DISTINCT ID(root) as id, root.name as name, type.name as model
        """ % ( int(request.user.id), app_label )

        matches      = connection.cypher(query).to_dicts()
        count        = len(matches)
        limit        = int(request.GET.get('limit', 20))
        paginator    = Paginator(matches, limit)

        try:
            p     = int(request.GET.get('page', 1))
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
                'total_count': count
            }
        }

        return object_list


    def summary_search(self, bundle, request):
        self.method_check(request, allowed=['get'])

        if not "q" in request.GET: raise Exception("Missing 'q' parameter")

        limit     = int(request.GET.get('limit', 20))
        query     = bundle.request.GET["q"].lower()
        results   = self.search(query)
        count     = len(results)
        paginator = Paginator(results, limit)

        try:
            p     = int(request.GET.get('page', 1))
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
                'page': p,
                'limit': limit,
                'total_count': count
            }
        }

        self.log_throttled_access(request)
        return object_list

    def summary_rdf_search(self, bundle, request):
        self.method_check(request, allowed=['get'])

        limit     = int(request.GET.get('limit', 20))
        query     = json.loads(request.GET.get('q', 'null'))
        subject   = query.get("subject", None)
        predicate = query.get("predicate", None)
        obj       = query.get("object", None)
        results   = self.rdf_search(subject, predicate, obj)
        count     = len(results)
        paginator = Paginator(results, limit)
        try:
            p     = int(request.GET.get('page', 1))
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
                'page': p,
                'limit': limit,
                'total_count': count
            }
        }

        self.log_throttled_access(request)
        return object_list

    def summary_human(self, bundle, request):
        self.method_check(request, allowed=['get'])

        if not "q" in request.GET:
            raise Exception("Missing 'q' parameter")

        query        = request.GET["q"]
        # Find the kown match for the given query
        matches      = self.find_matches(query)
        # Build and returns a list of proposal
        propositions = self.build_propositions(matches, query)
        # Build paginator
        count        = len(propositions)
        limit        = int(request.GET.get('limit', 20))
        paginator    = Paginator(propositions, limit)

        try:
            p     = int(request.GET.get('page', 1))
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
                'page': p,
                'limit': limit,
                'total_count': count
            }
        }

        self.log_throttled_access(request)
        return object_list

    def summary_bulk_upload(self, request, **kwargs):
        # only allow POST requests
        self.method_check(request, allowed=['post'])

        # check session
        if not request.user.id:
            raise UnauthorizedError('This method require authentication')

        entities = dict()
        relations = []

        # retrieve all models in current topic
        all_models = dict((model.__name__, model) for model in get_topic_models(self.topic.module))

        # flattern the list of files
        files = [file for sublist in request.FILES.lists() for file in sublist[1]]
        # TODO: Check headers
        # iterate over all files and dissociate entities .csv from relations .csv
        for file in files:
            # use .rstrip() to remove trailing \n
            file_header = file.readline().rstrip()
            if len(re.findall('_id;?$', file_header)) is 0:
                # extract the model name (match.group(1))
                match = re.match('^(\w+)_id;', file_header)
                if match.group(1) is not None:
                    model_name = match.group(1).capitalize()
                    # check that this model actually exists in the current topic
                    if model_name in all_models.keys():
                        entities[model_name] = file
            else:
                relations.append(file)

        id_mapping = dict()

        # first iterate over entities
        for entity, file in entities.items():
            tempfile = uploaded_to_tempfile(file)
            # create a csv reader
            csv_reader = csv.reader(tempfile, delimiter=';')
            # must check that all columns map to an existing model field
            field_names = [field['name'] for field in get_model_fields(all_models[entity])]
            columns = []
            for column in csv_reader.next():
                if column is not '':
                    if len(re.findall('_id$', column)) == 0 and not column in field_names:
                        break
                    columns.append(column)
            else:
                # here, we know that all columns are valid
                for row in csv_reader:
                    data = {}
                    for i in range(0, len(columns)):
                        if len(re.findall('_id$', columns[i])) == 0:
                            data[columns[i]] = str(row[i]).decode('utf-8')
                        else:
                            id = int(row[i])
                    # instanciate a model, save it and map it with the ID defined
                    # in the .csv
                    item = all_models[entity].objects.create(**data)
                    item.save()
                    id_mapping[id] = item
            # closing a tempfile deletes it
            tempfile.close()

        inserted_relations = 0
        # then iterate over relations
        for file in relations:
            tempfile = uploaded_to_tempfile(file)
            # create a csv reader
            csv_reader = csv.reader(tempfile, delimiter=';')
            csv_header = csv_reader.next()
            relation_name = csv_header[1]

            # check that the relation actually exists between the two objects
            model_from = re.match('(\w+)_id', csv_header[0]).group(1).capitalize()
            try:
                getattr(all_models[model_from], relation_name)

                for row in csv_reader:
                    id_from = int(row[0])
                    id_to = int(row[2])
                    if id_mapping[id_from] is not None and id_mapping[id_to] is not None:
                        getattr(id_mapping[id_from], relation_name).add(id_mapping[id_to])
                        inserted_relations += 1
            except AttributeError:
                logger.error("the attribute '{attribute}' doesn't exist for the model {model}. Check the header of the {file} file."
                    .format(attribute=relation_name, model=all_models[model_from], file=file))

            # closing a tempfile deletes it
            tempfile.close()

        # Save everything
        for item in id_mapping.values():
            item.save()

        self.log_throttled_access(request)
        return {
            'inserted' : {
                'objects' : len(id_mapping),
                'links' : inserted_relations
            }
        }

    def summary_syntax(self, bundle, request): return self.get_syntax(bundle, request)

    def search(self, query):
        match = str(query).lower()
        match = re.sub("\"|'|`|;|:|{|}|\|(|\|)|\|", '', match).strip()
        # Query to get every result
        query = """
            START root=node(*)
            MATCH (root)<-[r:`<<INSTANCE>>`]-(type)
            WHERE HAS(root.name)
            AND LOWER(root.name) =~ '.*(%s).*'
            AND type.app_label = '%s'
            RETURN ID(root) as id, root.name as name, type.model_name as model
        """ % (match, self.topic.app_label() )
        return connection.cypher(query).to_dicts()

    def rdf_search(self, subject, predicate, obj):
        # Query to get every result
        query = """
            START st=node(*)
            MATCH (st)<-[:`%s`]-(root)<-[:`<<INSTANCE>>`]-(type)
            WHERE HAS(root.name)
            AND HAS(st.name)
            AND type.name = "%s"
            AND st.name = "%s"
            AND type.app_label = '%s'
            RETURN DISTINCT ID(root) as id, root.name as name, type.model_name as model
        """ % ( predicate["name"], subject["name"], obj["name"], self.topic.app_label() )
        return connection.cypher(query).to_dicts()


    def get_models_output(self):
        # Select only some atribute
        output = lambda m: {'name': self.topic.slug + ":" + m.__name__, 'label': m._meta.verbose_name.title()}
        return [ output(m) for m in get_topic_models(self.topic.module) ]


    def ngrams(self, input):
        input = input.split(' ')
        output = []
        end = len(input)
        for n in range(1, end+1):
            for i in range(len(input)-n+1):
                output.append(input[i:i+n])
        return output

    def get_close_labels(self, token, lst, ratio=0.6):
        """
            Look for the given token into the list using labels
        """
        matches = []
        for item in lst:
            cpr = item["label"]
            if SequenceMatcher(None, token, cpr).ratio() >= ratio:
                matches.append(item)
        return matches

    def find_matches(self, query):
        # Group ngram by following string
        ngrams  = [' '.join(x) for x in self.ngrams(query) ]
        matches = []
        models  = self.get_syntax()["subject"]["model"]
        rels    = self.get_syntax()["predicate"]["relationship"]
        # Known models lookup for each ngram
        for token in ngrams:
            obj = {
                'models'       : self.get_close_labels(token, models),
                'relationships': self.get_close_labels(token, rels),
                'token'        : token
            }
            matches.append(obj)
        return matches

    def build_propositions(self, matches, query):
        """
            For now, a proposition follow the form
            <subject> <predicat> <object>
            Where a <subject>, is an "Named entity" or a Model
            a <predicat> is a relationship type
            and an <object> is a "Named entity" or a Model.
            Later, as follow RDF standard, an <object> could be any data.
        """
        def remove_duplicates(lst):
            seen = set()
            new_list = []
            for item in lst:
                # Create a hash of the dictionary
                obj = hash(frozenset(item.items()))
                if obj not in seen:
                    seen.add(obj)
                    new_list.append(item)
            return new_list

        def is_preposition(token=""):
            return str(token).lower() in ["aboard", "about", "above", "across", "after", "against",
            "along", "amid", "among", "anti", "around", "as", "at", "before", "behind", "below",
            "beneath", "beside", "besides", "between", "beyond", "but", "by", "concerning",
            "considering",  "despite", "down", "during", "except", "excepting", "excluding",
            "following", "for", "from", "in", "inside", "into", "like", "minus", "near", "of",
            "off", "on", "onto", "opposite", "outside", "over", "past", "per", "plus", "regarding",
            "round", "save", "since", "than", "through", "to", "toward", "towards", "under",
            "underneath", "unlike", "until", "up", "upon", "versus", "via", "with", "within", "without"]

        def previous_word(sentence="", base=""):
            if base == "" or sentence == "": return ""
            parts = sentence.split(base)
            return parts[0].strip().split(" ")[-1] if len(parts) else None

        predicates    = []
        subjects      = []
        objects       = []
        propositions  = []
        # Picks candidates for subjects and predicates
        for match in matches:
            subjects   += match["models"]
            predicates += match["relationships"]
            # Objects are detected when they start and end by double quotes
            if  match["token"].startswith('"') and match["token"].endswith('"'):
                # Remove the quote from the token
                token = match["token"].replace('"', '')
                # Store the token as an object
                objects += self.search(token)[:5]
            # Or if the previous word is a preposition
            elif is_preposition( previous_word(query, match["token"]) ):
                # Store the token as an object
                objects += self.search(match["token"])[:5]

        # No subject, no predicate, it might be a classic search
        if not len(subjects) and not len(predicates):
            results = self.search(query)
            for result in results:
                # Build the label
                label = result.get("name", None)
                propositions.append({
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
        # We find some subjects
        elif len(subjects) and not len(predicates):
            rels = self.get_syntax().get("predicate").get("relationship")
            for subject in subjects:
                # Gets all available relationship for these subjects
                predicates += [ rel for rel in rels if rel["subject"] == subject["name"] ]

        # Add a default and irrelevant object
        if not len(objects): objects = [""]

        # Generate proposition using RDF's parts
        for subject in remove_duplicates(subjects):
            for predicate in remove_duplicates(predicates):
                for obj in objects:
                    pred_sub = predicate.get("subject", None)
                    # If the predicate has a subject
                    # and this matches to the current one
                    if pred_sub == None or pred_sub == subject.get("name", None):
                        if type(obj) is dict:
                            obj_disp = obj["name"] or obj["label"]
                        else:
                            obj_disp = obj
                        # Value to inset into the proposition's label
                        values = (subject["label"], predicate["label"], obj_disp,)
                        # Build the label
                        label = '%s that %s %s' % values
                        propositions.append({
                            'label'    : label,
                            'subject'  : subject,
                            'predicate': predicate,
                            'object'   : obj
                        })

        # Remove duplicates proposition dicts
        return propositions

    def get_syntax(self, bundle=None, request=None):
        return {
            'subject': {
                'model':  self.get_models_output(),
                'entity': None
            },
            'predicate': {
                'relationship': []
            }
        }
