from django.http          import Http404, HttpResponse
from tastypie.exceptions  import ImmediateHttpResponse
from tastypie.resources   import Resource
from tastypie.serializers import Serializer

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
