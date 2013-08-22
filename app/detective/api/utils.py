from tastypie.utils.mime           import determine_format, build_content_type
from django.http                   import HttpResponse
from tastypie.api                  import Api
from django.conf.urls.defaults     import *
from django.forms.forms            import pretty_name

class DetailedApi(Api):
    def top_level(self, request, api_name=None):
        """
        A view that returns a serialized list of all resources registers
        to the ``Api``. Useful for discovery.
        """
        available_resources = {}

        if api_name is None: api_name = self.api_name

        for name in sorted(self._registry.keys()):                        
            resource      = self._registry[name]
            resourceModel = getattr(resource._meta.queryset, "model", {})      
            fields        = []
            verbose_name  = ""

            if hasattr(resourceModel, "_meta"):
                # Model berbose name
                verbose_name = getattr(resourceModel._meta, "verbose_name", name).title()                
                # Create field object
                for f in resourceModel._meta.fields:
                    # Ignores field terminating by + or begining by _
                    if not f.name.endswith("+") and not f.name.endswith("_set") and not f.name.startswith("_"):             
                        # Find related model for relation
                        if hasattr(f, "target_model"):                            
                            target_model  = f.target_model
                            modelFields   = target_model._meta.get_all_field_names()                            
                            related_model = target_model.__name__         
                            is_searchable = "name" in modelFields
                        else:
                            related_model = None     
                            is_searchable  = False
                        
                        # Create the field object
                        fields.append({
                            'name': f.name,
                            'type': f.get_internal_type(),
                            'help_text': getattr(f, "help_text", ""),
                            'verbose_name': getattr(f, "verbose_name", pretty_name(f.name)),
                            'related_model': related_model,
                            'is_searchable': is_searchable
                        })

            available_resources[name] = {
                'list_endpoint': self._build_reverse_url("api_dispatch_list", kwargs={
                    'api_name': api_name,
                    'resource_name': name,
                }),
                'schema': self._build_reverse_url("api_get_schema", kwargs={
                    'api_name': api_name,
                    'resource_name': name,
                }),
                'description' : getattr(resourceModel, "_description", None),
                'scope'       : getattr(resourceModel, "_scope", None),
                'model'       : getattr(resourceModel, "__name__", ""),
                'verbose_name': verbose_name,
                'name'        : name,
                'fields'      : fields
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

