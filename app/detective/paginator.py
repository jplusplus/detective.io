from tastypie.paginator import Paginator as TastypiePaginator

# @DEPRECATED
def resource_paginator(resource=None, base=TastypiePaginator):
    class Paginator(base):
        pass
    return Paginator

# Allows paginator exportation without auto convertion
Paginator = resource_paginator()
