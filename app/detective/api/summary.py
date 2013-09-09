from ..models             import Country
from .utils               import get_model_node_id
from django.http          import Http404, HttpResponse
from tastypie.exceptions  import ImmediateHttpResponse
from tastypie.resources   import Resource
from tastypie.serializers import Serializer
from neo4django.db        import connection


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
            MATCH (i)<-[]->(country)<-[r:`<<INSTANCE>>`]-(n)
            RETURN country.isoa3 as isoa3, ID(country) as id, count(i) as count
        """ % int(model_id)
        # Get the data and convert it to dictionnary
        return connection.cypher(query).to_dicts()

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
        return connection.cypher(query).to_dicts()