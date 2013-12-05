from django.forms.forms       import pretty_name
from random                   import randint
from os                       import listdir
from os.path                  import isdir, join
from neo4django.db            import models
import importlib
import inspect
import re


def create_node_model(name, fields=None, app_label='', module='', options=None, base_class=models.NodeModel):
    """
    Create specified model
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass
    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)
    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)
    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}
    # Add in any fields that were provided
    if fields:
        attrs.update(fields)
    # Create the class, which automatically triggers ModelBase processing
    return type(name, (base_class,), attrs)

def create_model_resource(model):
    """
        Create specified model's api resource
    """
    from app.detective.individual import IndividualResource, IndividualMeta
    class Meta(IndividualMeta):
        queryset = model.objects.all().select_related(depth=1)
     # Set up a dictionary to simulate declarations within a class
    attrs = {'Meta': Meta}
    name  = "%sResource" % model.__name__
    return type(name, (IndividualResource,), attrs)

def import_class(path):
    components = path.split('.')
    klass      = components[-1:]
    mod        = ".".join(components[0:-1])
    return getattr(__import__(mod, fromlist=klass), klass[0], None)

def get_topics():
    # Load topics' names
    appsdir = "./app/detective/topics"
    return [ name for name in listdir(appsdir) if isdir(join(appsdir, name)) ]

def get_topics_modules():
    # Import the whole topics directory automaticly
    CUSTOM_APPS = tuple( "app.detective.topics.%s" % a for a in get_topics() )
    return CUSTOM_APPS

def get_topic_models(topic):
    from django.db.models import Model
    # Models to collect
    models        = []
    models_path   = "app.detective.topics.%s.models" % topic
    try:
        models_module = importlib.import_module(models_path)
        for i in dir(models_module):
            cls = getattr(models_module, i)
            # Collect every Django's model subclass
            if inspect.isclass(cls) and issubclass(cls, Model): models.append(cls)
    except ImportError:
        # Fail silently if the topic doesn't exist
        pass
    return models

def get_registered_models():
    from django.db import models
    import app.settings as settings
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
    from app.detective           import register
    from django.db.models.fields import FieldDoesNotExist
    fields      = []
    modelsRules = register.topics_rules().model(model)
    if hasattr(model, "_meta"):
        # Create field object
        for fieldRules in modelsRules.fields():
            try:
                f = model._meta.get_field(fieldRules.name)
            except FieldDoesNotExist:
                # This is rule field. Ignore it!
                continue
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
    from neo4django.db import connection
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
        app  = get_model_topic(model)
        name = model.__name__
        # Search for the node with the good name
        model_node  = next(n for n in nodes if n["name"] == "%s:%s" % (app, name) )
        return model_node["id"] or None
    # We didn't found the node id
    except StopIteration:
        return None

def get_model_topic(model):
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