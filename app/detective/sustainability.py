from django.core.exceptions import ValidationError
from app.detective.utils import import_class

def dummy_model_to_ressource(model):
    module = model.__module__.split(".")
    # Remove last path part if need
    if module[-1] == 'models': module = module[0:-1]
    # Build the resource path
    module = ".".join(module + ["resources", model.__name__ + "Resource"])
    try:
        # Try to import the class
        import_class(module)
        return module
    except ImportError:
        return None

def convertible_objects(objects, resource=None):
    # Closure function to receive the model used to convert a node to an instance
    def get_converter(model, resource):
        def neo4j_instance(node):
            try:
                resource.validate(node.properties, model=model)
            # The given node properties don't validate with the resource model
            except ValidationError:
                node.properties = resource.convert(node.properties, model=model)
            # No resource given to make the convertion
            except NameError: pass
            # Return the model instance
            return model._neo4j_instance(node)
        return neo4j_instance
    # Retreive the resource for this model
    if resource is None: resource = dummy_model_to_ressource(objects.model)
    # Override the query function that transforms node into neo4django model.
    # We pass the current model through a closure.
    objects.query.model_from_node = get_converter(objects.model, resource)
    return objects
