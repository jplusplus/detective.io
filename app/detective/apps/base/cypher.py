from django.http             import Http404, HttpResponse
from tastypie.exceptions     import ImmediateHttpResponse
from tastypie.authentication import SessionAuthentication, MultiAuthentication, BasicAuthentication
from tastypie.authorization  import Authorization
from tastypie.resources      import Resource
from tastypie.serializers    import Serializer
from neo4django.db           import connection

class CypherResource(Resource):
    # Local serializer
    serializer = Serializer(formats=["json"]).serialize

    class Meta:
        authorization   = Authorization()
        authentication  = MultiAuthentication(SessionAuthentication(), BasicAuthentication())
        allowed_methods = ['get'] 
        resource_name   = 'cypher'
        object_class    = object

    def obj_get_list(self, request=None, **kwargs): 
        request = kwargs["bundle"].request if request == None else request 
        # Super user only
        if not request.user.is_superuser:
            # We force tastypie to render the response directly 
            raise ImmediateHttpResponse(response=HttpResponse('Unauthorized', status=401))            
        query = request.GET["q"];
        data  = connection.cypher(query).to_dicts()
        # Serialize content in json
        # @TODO implement a better format support
        content  = self.serializer(data, "application/json")
        # Create an HTTP response 
        response = HttpResponse(content=content, content_type="application/json")
        # We force tastypie to render the response directly 
        raise ImmediateHttpResponse(response=response)

    def obj_get(self, request=None, **kwargs):    
        # Nothing yet here!
        raise Http404("Sorry, no results on that page.") 
