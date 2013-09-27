# -*- coding: utf-8 -*-
from ..models              import Country
from ..neomatch            import Neomatch
from .utils                import get_model_node_id, get_model_fields
from django.core.paginator import Paginator, InvalidPage
from django.db.models      import get_app, get_models
from django.http           import Http404, HttpResponse
from forms                 import register_model_rules
from neo4django.db         import connection
from tastypie.exceptions   import ImmediateHttpResponse
from tastypie.resources    import Resource
from tastypie.serializers  import Serializer
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
        import time
        time.sleep(0.5) 
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
        # Get all detective's models        
        app = get_app('detective')
        for model in get_models(app):      
            # Do this ressource has a model?
            if model != None:
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
                    'scope'               : getattr(model, "_scope", None),
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

        limit = int(request.GET.get('limit', 20))
        match = bundle.request.GET["q"].lower()
        match = re.sub("\"|'|`|;|:|{|}|\|(|\|)|\|", '', match)
        # Query to get every result
        query = """
            START root=node(*)
            MATCH (root)<-[r:`<<INSTANCE>>`]-(type)
            WHERE HAS(root.name) 
            AND type.app_label = "detective"
            AND LOWER(root.name) =~ '.*(%s).*'
            RETURN ID(root) as id, root.name as name, type.model_name as model
        """ % match
        results   = connection.cypher(query).to_dicts()
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
                'q': match,
                'page': p,
                'limit': limit,
                'total_count': count
            }
        }

        self.log_throttled_access(request)
        return object_list

    def get_models_output(self):
        # Get all detective's models        
        app    = get_app('detective')
        # Select only some atribute
        output = lambda m: {'name': m.__name__, 'label': m._meta.verbose_name.title()}
        return [ output(m) for m in get_models(app) ]

    def summary_syntax(self, bundle):    
        syntax = {
            'subject': {
                'model':  self.get_models_output(),
                'entity': None
            },
            'predicate': {
                'relationship': [
                    {
                        "name": "fundraising_round_has_personal_payer+",
                        "subject": "FundraisingRound",
                        "label": "was financed by"
                    },
                    {
                        "name": "fundraising_round_has_payer+",
                        "subject": "FundraisingRound",
                        "label": "was financed by"
                    },
                    {
                        "name": "person_has_nationality+",
                        "subject": "Person",
                        "label": "is from"
                    },
                    {
                        "name": "person_has_activity_in_organization+",
                        "subject": "Person",
                        "label": "has activity in"
                    },
                    {
                        "name": "person_has_previous_activity_in_organization+",
                        "subject": "Person",
                        "label": "had previous activity in"
                    },
                    {
                        "name": "product_has_price+",
                        "subject": "Product",
                        "label": "is sell"
                    },
                    {
                        "name": "commentary_has_author+",
                        "subject": "Commentary",
                        "label": "was written by"
                    },
                    {
                        "name": "energy_product_has_distribution+",
                        "subject": "EnergyProduct",
                        "label": "is distributed in"
                    },
                    {
                        "name": "energy_product_has_operator+",
                        "subject": "EnergyProduct",
                        "label": "has operator"
                    },
                    {
                        "name": "energy_product_has_price+",
                        "subject": "EnergyProduct",
                        "label": "is sold"
                    },
                    {
                        "name": "organization_has_adviser+",
                        "subject": "Organization",
                        "label": "has adviser"
                    },
                    {
                        "name": "organization_has_key_person+",
                        "subject": "Organization",
                        "label": "has key person"
                    },
                    {
                        "name": "organization_has_partner+",
                        "subject": "Organization",
                        "label": "has a partnership with"
                    },
                    {
                        "name": "organization_has_fundraising_round+",
                        "subject": "Organization",
                        "label": "fundraised"
                    },
                    {
                        "name": "organization_has_monitoring_body+",
                        "subject": "Organization",
                        "label": "has monitoring body"
                    },
                    {
                        "name": "organization_has_litigation_against+",
                        "subject": "Organization",
                        "label": "has a litigation against"
                    },
                    {
                        "name": "organization_has_revenue+",
                        "subject": "Organization",
                        "label": "has revenue"
                    },
                    {
                        "name": "organization_has_board_member+",
                        "subject": "Organization",
                        "label": "has board member"
                    },
                    {
                        "name": "project_has_commentary+",
                        "subject": "Project",
                        "label": "has commentary/analysis"
                    },
                    {
                        "name": "project_has_owner+",
                        "subject": "Project",
                        "label": "is owned by"
                    },
                    {
                        "name": "project_has_partner+",
                        "subject": "Project",
                        "label": "has a partnership with"
                    },
                    {
                        "name": "project_has_activity_in_country+",
                        "subject": "Project",
                        "label": "has activity in"
                    },
                    {
                        "name": "distribution_has_activity_in_country+",
                        "subject": "Distribution",
                        "label": "has activity in"
                    },
                    {
                        "name": "energy_project_has_product+",
                        "subject": "EnergyProject",
                        "label": "has product"
                    },
                    {
                        "name": "energy_project_has_commentary+",
                        "subject": "EnergyProject",
                        "label": "has commentary/analysis"
                    },
                    {
                        "name": "energy_project_has_owner+",
                        "subject": "EnergyProject",
                        "label": "is owned by"
                    },
                    {
                        "name": "energy_project_has_partner+",
                        "subject": "EnergyProject",
                        "label": "has partnership with"
                    },
                    {
                        "name": "energy_project_has_activity_in_country+",
                        "subject": "EnergyProject",
                        "label": "has activity in"
                    }
                ]
            }
        }
        return syntax
