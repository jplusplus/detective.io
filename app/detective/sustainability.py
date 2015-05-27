from django.core.exceptions import ValidationError
from neo4django.db import models

def dummy_model_to_ressource(model, get=False):
    from app.detective.utils import import_class
    path = model.__module__.split(".")
    # Remove last path part if need
    if path[-1] == 'models': path = path[0:-1]
    # Build the resource path
    path = ".".join(path + ["resources", model.__name__ + "Resource"])
    try:
        # Try to import the class
        resource = import_class(path)
        return resource if get else path
    except ImportError:
        return None

# This class of extend the model default model class to allow fluid definition
# of every model. This way data can be converted dynamicly.
class FluidNodeModel(models.NodeModel):
    class Meta:
        abstract = True

    @classmethod
    def _neo4j_instance(self, node):
        try:
            resource = dummy_model_to_ressource(self, True)()
            resource.validate(node.properties, model=self)
        # The given node properties don't validate with the resource model
        except ValidationError:
            node.properties = resource.convert(node.properties, model=self)
        # No resource given to make the convertion
        except NameError: pass
        return super(FluidNodeModel, self)._neo4j_instance(node)