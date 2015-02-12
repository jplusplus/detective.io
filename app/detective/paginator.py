from tastypie.paginator import Paginator as TastypiePaginator
from django.core.exceptions import ValidationError

# We use a custom Paginator embeded into a close that receive a resource class.
# That way we can pass to tastypie's resource a Paginator awares of the resource
# it might have to use. Since Detective implements models with field types that
# can change over time, it is important to be able to convert old data types into
# the new one during runtime.
def resource_paginator(resource=None, base=TastypiePaginator):
    class Paginator(base):
        # Closure function to receive the model used to convert a node to an instance
        def get_converter(self, model):
            def neo4j_instance(node):
                try:
                    resource.validate(node.properties, model=model)
                # The given node properties don't validate with the resource model
                except ValidationError as e:
                    node.properties = resource.convert(node.properties, model=model)
                # No resource given to make the convertion
                except NameError: pass
                # Return the model instance
                return model._neo4j_instance(node)
            return neo4j_instance
        # Override the get_slice method of the paginator to allow
        # dynamic node convertion. Since every model instance is sent to the user
        # using the paginator, we use it an interface to convert data.
        def get_slice(self, limit, offset):
            # Override the query function that transforms node into neo4django model.
            # We pass the current model through a closure.
            self.objects.query.model_from_node = self.get_converter(self.objects.model)
            # Iterate over the objects using the modified query
            subset = [o for o in self.objects.query.execute(self.objects.db) ]
            # No limit parameter,  we return the whole subset from the given offset
            if limit == 0: return subset[offset:]
            return subset[offset:offset + limit]
    return Paginator

# Allows paginator exportation without auto convertion
Paginator = resource_paginator()