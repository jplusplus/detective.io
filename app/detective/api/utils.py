from tastypie.utils.mime           import determine_format, build_content_type
from django.http                   import HttpResponse
from tastypie.api                  import Api
from django.conf.urls.defaults     import *
from django.forms.forms            import pretty_name
from forms                         import register_model_rules

def get_model_fields(model):
    fields      = []
    modelsRules = register_model_rules().model(model)
    if hasattr(model, "_meta"):          
        # Create field object
        for fieldRules in modelsRules.fields():
            f = model._meta.get_field(fieldRules.name)
            # Ignores field terminating by + or begining by _
            if not f.name.endswith("+") and not f.name.endswith("_set") and not f.name.startswith("_"):             
                # Find related model for relation
                if hasattr(f, "target_model"):                            
                    target_model  = f.target_model                     
                    related_model = target_model.__name__
                else:
                    related_model = None     
                
                field = {
                    'name'         : f.name,
                    'type'         : f.get_internal_type(),
                    'help_text'    : getattr(f, "help_text", ""),
                    'verbose_name' : getattr(f, "verbose_name", pretty_name(f.name)),
                    'related_model': related_model,
                    'rules'        : fieldRules.all()
                }
                
                fields.append(field)


    return fields

class DetailedApi(Api):
    def top_level(self, request, api_name=None):
        """
        A view that returns a serialized list of all resources registers
        to the ``Api``. Useful for discovery.
        """
        available_resources = {}

        if api_name is None: api_name = self.api_name

        # Get the model's rules manager
        rulesManager = register_model_rules()

        for name in sorted(self._registry.keys()):                        
            resource      = self._registry[name]
            resourceModel = getattr(resource._meta.queryset, "model", None)  
            # Do this ressource has a model?
            if resourceModel != None:
                fields        = get_model_fields(resourceModel)
                verbose_name  = getattr(resourceModel._meta, "verbose_name", name).title()      

                available_resources[name] = {
                    'list_endpoint': self._build_reverse_url("api_dispatch_list", kwargs={
                        'api_name': api_name,
                        'resource_name': name,
                    }),
                    'schema': self._build_reverse_url("api_get_schema", kwargs={
                        'api_name': api_name,
                        'resource_name': name,
                    }),
                    'description'  : getattr(resourceModel, "_description", None),
                    'scope'        : getattr(resourceModel, "_scope", None),
                    'model'        : getattr(resourceModel, "__name__", ""),
                    'verbose_name' : verbose_name,
                    'name'         : name,
                    'fields'       : fields,
                    'rules'        : rulesManager.model(resourceModel).all()
                }
            # Default description
            else:                
                available_resources[name] = {
                    'list_endpoint': self._build_reverse_url("api_dispatch_list", kwargs={
                        'api_name': api_name,
                        'resource_name': name,
                    }),
                    'schema': self._build_reverse_url("api_get_schema", kwargs={
                        'api_name': api_name,
                        'resource_name': name,
                    }),
                    'name': name
                }

        desired_format = determine_format(request, self.serializer)

        options = {}

        if 'text/javascript' in desired_format:
            callback = request.GET.get('callback', 'callback')

            if not is_valid_jsonp_callback_value(callback):
                raise BadRequest('JSONP callback name is invalid.')

            options['callback'] = callback

        serialized = self.serializer.serialize(available_resources, desired_format, options)
        return HttpResponse(content=serialized, content_type=build_content_type(desired_format))

