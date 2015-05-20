from tastypie.paginator import Paginator as TastypiePaginator
from .sustainability import convertible_objects

# We use a custom Paginator embeded into a close that receive a resource class.
# That way we can pass to tastypie's resource a Paginator awares of the resource
# it might have to use. Since Detective implements models with field types that
# can change over time, it is important to be able to convert old data types into
# the new one during runtime.
def resource_paginator(resource=None, base=TastypiePaginator):
    class Paginator(base):
        # Override the get_slice method of the paginator to allow
        # dynamic node convertion. Since every model instance is sent to the user
        # using the paginator, we use it an interface to convert data.
        def get_slice(self, limit, offset):
            # Override the query function that transforms node into neo4django model.
            # We pass the current model through a closure.
            self.objects = convertible_objects(self.objects, resource)
            # No limit parameter,  we return the whole subset from the given offset
            if limit == 0: return self.objects[offset:]
            return self.objects[offset:offset + limit]
    return Paginator

# Allows paginator exportation without auto convertion
Paginator = resource_paginator()
