from app.detective.forms       import register_model_rules
from django.conf.urls.defaults import *
from django.db                 import models
from django.forms.forms        import pretty_name
from neo4django.db             import connection
from random                    import randint
import re
import app.settings as settings


def import_class(path):
    components = path.split('.')
    klass      = components[-1:]
    mod        = ".".join(components[0:-1])
    return getattr(__import__(mod, fromlist=klass), klass[0], None)

def get_registered_models():
    mdls = []
    for app in settings.INSTALLED_APPS:
        models_name = app + ".models"
        try:
            models_module = __import__(models_name, fromlist=["models"])            
            attributes = dir(models_module)
            for attr in attributes:
                try:
                    attrib = models_module.__getattribute__(attr)
                    if issubclass(attrib, models.Model) and attrib.__module__== models_name:                        
                        mdls.append(attrib)
                except TypeError:
                    pass
        except ImportError:
            pass
    return mdls

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
                    # We received a model as a string
                    if type(f.target_model) is str:
                        # Extract parts of the module path
                        module_path  = f.target_model.split(".")
                        # Import models as a module
                        module       = __import__( ".".join(module_path[0:-1]), fromlist=["class"])
                        # Import the target_model from the models module
                        target_model = getattr(module, module_path[-1], {__name__: None})
                    else:                        
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

def get_model_nodes():
    # Return buffer values
    if hasattr(get_model_nodes, "buffer"): 
        results = get_model_nodes.buffer
        # Refresh the buffer ~ 1/10 calls
        if randint(0,10) == 10: del get_model_nodes.buffer
        return results
    query = """
        START n=node(*)
        MATCH n-[r:`<<TYPE>>`]->t
        WHERE HAS(t.name)
        RETURN t.name as name, ID(t) as id
    """
    # Bufferize the result
    get_model_nodes.buffer = connection.cypher(query).to_dicts()    
    return get_model_nodes.buffer
    

def get_model_node_id(model):
    # All node from neo4j that are have ascending <<TYPE>> relationship
    nodes = get_model_nodes()
    try:
        app  = get_model_scope(model)
        name = model.__name__
        # Search for the node with the good name
        model_node  = next(n for n in nodes if n["name"] == "%s:%s" % (app, name) )
        return model_node["id"] or None
    # We didn't found the node id
    except StopIteration:
        return None

def get_model_scope(model):
    return model.__module__.split(".")[-2]

def to_class_name(value=""):
    """
    Class name must:
        - begin by an uppercase
        - use camelcase
    """
    value = to_camelcase(value)
    value = list(value)
    if len(value) > 0:
        value[0] = value[0].capitalize()

    return "".join(value)


def to_camelcase(value=""):

    def camelcase(): 
        yield str.lower
        while True:
            yield str.capitalize            

    value =  re.sub(r'([a-z])([A-Z])', r'\1_\2', value)
    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))

def to_underscores(value=""):    
    # Lowercase of the first letter
    value = list(value)
    if len(value) > 0:
        value[0] = value[0].lower()
    value = "".join(value)

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()