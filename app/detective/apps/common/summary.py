# -*- coding: utf-8 -*-
from .models                import Country
from .forms                 import register_model_rules
from app.detective.neomatch import Neomatch
from app.detective.utils    import get_model_node_id, get_model_fields, get_registered_models, get_model_scope
from difflib                import SequenceMatcher
from django.core.paginator  import Paginator, InvalidPage
from django.http            import Http404, HttpResponse
from neo4django.db          import connection
from tastypie.exceptions    import ImmediateHttpResponse
from tastypie.resources     import Resource
from tastypie.serializers   import Serializer
import json
import re

class SummaryResource(Resource):
    # Local serializer
    serializer = Serializer(formats=["json"]).serialize

    class Meta:
        allowed_methods = ['get'] 
        resource_name   = 'summary'
        object_class    = object

    def obj_get_list(self, request=None, **kwargs):
        # Nothing yet here!
        raise Http404("Sorry, not implemented yet!") 

    def obj_get(self, request=None, **kwargs):   
        content = {}
        # Check for an optional method to do further dehydration.
        method = getattr(self, "summary_%s" % kwargs["pk"], None)
        if method:
            content = method(kwargs["bundle"])
        else: 
            # Stop here, unkown summary type
            raise Http404("Sorry, not implemented yet!")        
        # Serialize content in json
        # @TODO implement a better format support
        content  = self.serializer(content, "application/json")
        # Create an HTTP response 
        response = HttpResponse(content=content, content_type="application/json")
        # We force tastypie to render the response directly 
        raise ImmediateHttpResponse(response=response)

    def summary_countries(self, bundle):    
        model_id = get_model_node_id(Country)
        # The Country isn't set yet in neo4j
        if model_id == None: raise Http404()
        # Query to aggreagte relationships count by country
        query = """
            START n=node(%d)
            MATCH (i)<-[*0..1]->(country)<-[r:`<<INSTANCE>>`]-(n)
            WHERE HAS(country.isoa3)
            RETURN country.isoa3 as isoa3, ID(country) as id, count(i)-1 as count 
        """ % int(model_id)
        # Get the data and convert it to dictionnary
        countries = connection.cypher(query).to_dicts()
        obj       = {}
        for country in countries:
            # Use isoa3 as identifier
            obj[ country["isoa3"] ] = country
            # ISOA3 is now useless
            del country["isoa3"]            
        return obj

    def summary_types(self, bundle):    
        # Query to aggreagte relationships count by country
        query = """
            START n=node(*)
            MATCH (c)<-[r:`<<INSTANCE>>`]-(n)
            WHERE HAS(n.model_name) 
            RETURN ID(n) as id, n.model_name as name, count(c) as count
        """
        # Get the data and convert it to dictionnary
        types = connection.cypher(query).to_dicts()
        obj       = {}
        for t in types:
            # Use name as identifier
            obj[ t["name"] ] = t
            # name is now useless
            del t["name"]
        return obj

    def summary_forms(self, bundle):        
        available_resources = {}
        # Get the model's rules manager
        rulesManager = register_model_rules()     
        # Fetch every registered model  
        # to print out its rules
        for model in get_registered_models():                                      
            # Do this ressource has a model?
            # Do this ressource is a part of apps?
            if model != None and model.__module__.startswith("app.detective.apps"):
                name                = model.__name__.lower()
                rules               = rulesManager.model(model).all()
                fields              = get_model_fields(model)
                verbose_name        = getattr(model._meta, "verbose_name", name).title()      
                verbose_name_plural = getattr(model._meta, "verbose_name_plural", verbose_name + "s").title()      
                # Extract the model parent to find its scope
                scope               = model.__module__.split(".")[-2]

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
                    'scope'               : getattr(model, "_scope", scope),
                    'model'               : getattr(model, "__name_", ""),
                    'verbose_name'        : verbose_name,
                    'verbose_name_plural' : verbose_name_plural,
                    'name'                : name,
                    'fields'              : fields,
                    'rules'               : rules
                }

        return available_resources


    def summary_search(self, bundle):        
        request = bundle.request
        self.method_check(request, allowed=['get'])        
        self.throttle_check(request)

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

    def summary_rdf_search(self, bundle):       
        request = bundle.request
        self.method_check(request, allowed=['get'])        
        self.throttle_check(request)

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

    def summary_human(self, bundle):         
        request = bundle.request
        self.method_check(request, allowed=['get'])        
        self.throttle_check(request)
   
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

    def summary_syntax(self, bundle): return self.get_syntax()

    def search(self, query):
        match = str(query).lower()
        match = re.sub("\"|'|`|;|:|{|}|\|(|\|)|\|", '', match).strip()        
        # Query to get every result
        query = """
            START root=node(*)
            MATCH (root)<-[r:`<<INSTANCE>>`]-(type)
            WHERE HAS(root.name) 
            AND LOWER(root.name) =~ '.*(%s).*'
            RETURN ID(root) as id, root.name as name, type.name as model
        """ % match
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
            RETURN DISTINCT ID(root) as id, root.name as name, type.name as model
        """ % ( predicate["name"], subject["name"], obj["name"], )      
        return connection.cypher(query).to_dicts()


    def get_models_output(self):        
        # Select only some atribute
        output = lambda m: {'name': get_model_scope(m) + ":" + m.__name__, 'label': m._meta.verbose_name.title()}
        return [ output(m) for m in get_registered_models() if m.__module__.startswith("app.detective.apps") ]


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

    def get_syntax(self):    
        return {
            'subject': {
                'model':  self.get_models_output(),
                'entity': None
            },
            'predicate': {
                'relationship': [
                    {
                        "name": "fundraising_round_has_personal_payer+",
                        "subject": "energy:FundraisingRound",
                        "label": "was financed by"
                    },
                    {
                        "name": "fundraising_round_has_payer+",
                        "subject": "energy:FundraisingRound",
                        "label": "was financed by"
                    },
                    {
                        "name": "person_has_nationality+",
                        "subject": "energy:Person",
                        "label": "is from"
                    },
                    {
                        "name": "person_has_activity_in_organization+",
                        "subject": "energy:Person",
                        "label": "has activity in"
                    },
                    {
                        "name": "person_has_previous_activity_in_organization+",
                        "subject": "energy:Person",
                        "label": "had previous activity in"
                    },
                    {
                        "name": "energy_product_has_price+",
                        "subject": "energy:EnergyProduct",
                        "label": "is sold at"
                    },
                    {
                        "name": "commentary_has_author+",
                        "subject": "energy:Commentary",
                        "label": "was written by"
                    },
                    {
                        "name": "energy_product_has_distribution+",
                        "subject": "energy:EnergyProduct",
                        "label": "is distributed in"
                    },
                    {
                        "name": "energy_product_has_operator+",
                        "subject": "energy:EnergyProduct",
                        "label": "is operated by"
                    },
                    {
                        "name": "energy_product_has_price+",
                        "subject": "energy:EnergyProduct",
                        "label": "is sold at"
                    },
                    {
                        "name": "organization_has_adviser+",
                        "subject": "energy:Organization",
                        "label": "is advised by"
                    },
                    {
                        "name": "organization_has_key_person+",
                        "subject": "energy:Organization",
                        "label": "is staffed by"
                    },
                    {
                        "name": "organization_has_partner+",
                        "subject": "energy:Organization",
                        "label": "has a partnership with"
                    },
                    {
                        "name": "organization_has_fundraising_round+",
                        "subject": "energy:Organization",
                        "label": "was financed by"
                    },
                    {
                        "name": "organization_has_monitoring_body+",
                        "subject": "energy:Organization",
                        "label": "is monitored by"
                    },
                    {
                        "name": "organization_has_litigation_against+",
                        "subject": "energy:Organization",
                        "label": "has a litigation against"
                    },
                    {
                        "name": "organization_has_revenue+",
                        "subject": "energy:Organization",
                        "label": "has revenue of"
                    },
                    {
                        "name": "organization_has_board_member+",
                        "subject": "energy:Organization",
                        "label": "has board of directors with"
                    },
                    {
                        "name": "energy_project_has_commentary+",
                        "subject": "energy:EnergyProject",
                        "label": "is analyzed by"
                    },
                    {
                        "name": "energy_project_has_owner+",
                        "subject": "energy:EnergyProject",
                        "label": "is owned by"
                    },
                    {
                        "name": "energy_project_has_partner+",
                        "subject": "energy:EnergyProject",
                        "label": "has a partnership with"
                    },
                    {
                        "name": "energy_project_has_activity_in_country+",
                        "subject": "energy:EnergyProject",
                        "label": "has activity in"
                    },
                    {
                        "name": "distribution_has_activity_in_country+",
                        "subject": "energy:Distribution",
                        "label": "has activity in"
                    },
                    {
                        "name": "energy_project_has_product+",
                        "subject": "energy:EnergyProject",
                        "label": "has product of"
                    },
                    {
                        "name": "energy_project_has_commentary+",
                        "subject": "energy:EnergyProject",
                        "label": "is analyzed by"
                    },
                    {
                        "name": "energy_project_has_owner+",
                        "subject": "energy:EnergyProject",
                        "label": "is owned by"
                    },
                    {
                        "name": "energy_project_has_partner+",
                        "subject": "energy:EnergyProject",
                        "label": "has partnership with"
                    },
                    {
                        "name": "energy_project_has_activity_in_country+",
                        "subject": "energy:EnergyProject",
                        "label": "has activity in"
                    }
                ]
            }
        }
