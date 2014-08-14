from django.forms.forms     import pretty_name
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from random    import randint
from os.path   import isdir, join
from os        import listdir
import importlib
import inspect
import os
import re
import tempfile
import itertools
import logging
from django.db.models import signals
logger = logging.getLogger(__name__)

# for relative paths
here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

def create_node_model(name, fields=None, app_label='', module='', options=None):
    """
    Create specified model
    """
    from app.detective.models import update_topic_cache
    from neo4django.db            import models
    from django.db.models.loading import AppCache
    # Django use a cache by model
    cache = AppCache()
    # If we already create a model for this app
    if app_label in cache.app_models and name.lower() in cache.app_models[app_label]:
        # We just delete it quietly
        del cache.app_models[app_label][name.lower()]
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
    if fields: attrs.update(fields)
    # Create the class, which automatically triggers ModelBase processing
    cls = type(name, (models.NodeModel,), attrs)
    # for Model in topic.get_models():
    signals.post_save.connect(update_topic_cache, sender=cls)
    return cls

def create_model_resource(model, path=None, Resource=None, Meta=None):
    """
        Create specified model's api resource
    """
    from app.detective.individual import IndividualResource, IndividualMeta
    if Resource is None: Resource = IndividualResource
    if Meta is None: Meta = IndividualMeta
    class Meta(IndividualMeta):
        queryset = model.objects.all().select_related(depth=1)
     # Set up a dictionary to simulate declarations within a class
    attrs = {'Meta': Meta}
    name  = "%sResource" % model.__name__
    mr = type(name, (IndividualResource,), attrs)
    # Overide the default module
    if path is not None: mr.__module__ = path
    return mr

def import_class(path):
    components = path.split('.')
    klass      = components[-1:]
    mod_post   = ".".join(components[0:-1])
    mod        = __import__(mod_post, fromlist=klass)
    return getattr(mod, klass[0], None)

def get_topics(offline=True):
    if offline:
        # Load topics' names
        appsdir = here("topics")
        return [ name for name in listdir(appsdir) if isdir(join(appsdir, name)) ]
    else:
        from app.detective.models import Topic
        # Store topic object in a temporary attribute
        # to avoid SQL lazyness
        cache_key = "prefetched_topics"
        if cache.get(cache_key, None) is None:
            topics = Topic.objects.all()
            cache.set(cache_key, topics, 100)
        else:
            # Get all registered models
            topics = cache.get(cache_key)
        return [t.ontology_as_mod for t in topics]

def get_topics_modules():
    # Import the whole topics directory automaticly
    CUSTOM_APPS = tuple( "app.detective.topics.%s" % a for a in get_topics() )
    return CUSTOM_APPS

def get_topic_models(topic):
    import warnings
    warnings.warn("deprecated, you should use the get_models() method from the Topic model.", DeprecationWarning)
    from django.db.models import Model
    from app.detective.models import Topic
    # Models to collect
    models        = []
    models_path   = "app.detective.topics.%s.models" % topic
    try:
        if isinstance(topic, Topic):
            models_module = topic.get_models()
        elif hasattr(topic, '__str__'):
            # Models to collect
            models_path   = "app.detective.topics.%s.models" % topic
            models_module = importlib.import_module(models_path)
        else:
            return []
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
    from django.conf import settings
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

def get_topic_from_model(model):
    from app.detective.models import Topic
    return Topic.objects.get(ontology_as_mod=get_model_topic(model))


# storage middleware utilities
def get_topics_from_request(request):
    # see app.middleware.storage.StoreTopicList
    return getattr(request, 'topic_list', None)

def get_topic_from_request(request):
    # see app.middleware.storage.StoreTopic
    return getattr(request, 'current_topic', None)

def get_model_fields(model, order_by='name'):
    from app.detective           import register
    from django.db.models.fields import FieldDoesNotExist
    fields       = []
    models_rules = register.topics_rules().model(model)
    # Create field object
    for f in model._meta.fields:
        # Ignores field terminating by + or begining by _
        if not f.name.endswith("+") and not f.name.endswith("_set") and not f.name.startswith("_"):

            try:
                # Get the rules related to this model
                field_rules = models_rules.field(f.name).all()
            except FieldDoesNotExist:
                # No rules
                field_rules = []

            field_type = f.get_internal_type()
            # Find related model for relation
            if field_type.lower() == "relationship":
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

            verbose_name = getattr(f, "verbose_name", None)

            if verbose_name is None:
                # Use the name as verbose_name fallback
                verbose_name = pretty_name(f.name)

            field = {
                'name'         : f.name,
                'type'         : field_type,
                'direction'    : getattr(f, "direction", ""),
                'rel_type'     : getattr(f, "rel_type", ""),
                'help_text'    : getattr(f, "help_text", ""),
                'verbose_name' : verbose_name,
                'related_model': related_model,
                'model'        : model.__name__,
                'rules'        : field_rules
            }
            fields.append(field)

    if hasattr(model, '__fields_order__'):
        _len = len(fields)
        fields = sorted(fields, key=lambda x: model.__fields_order__.index(x['name']) if x['name'] in model.__fields_order__ else _len)
    else:
        get_key=lambda el: el[order_by]
        fields = sorted(fields, key=get_key)

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

def get_leafs_and_edges(topic, depth, root_node="*"):
    def _get_leafs_and_edges(topic, depth, root_node):
        from neo4django.db import connection
        leafs = {}
        edges = []
        leafs_related = []
        ###
        # First we retrieve every leaf in the graph
        query = """
            START root=node({root})
            MATCH p = (root)-[*1..{depth}]-(leaf)<-[:`<<INSTANCE>>`]-(type)
            WHERE HAS(leaf.name)
            AND type.app_label = '{app_label}'
            AND length(filter(r in relationships(p) : type(r) = "<<INSTANCE>>")) = 1
            RETURN leaf, ID(leaf) as id_leaf, type
        """.format(root=root_node, depth=depth, app_label=topic.app_label())
        rows = connection.cypher(query).to_dicts()

        if root_node != "*":
            # We need to retrieve the root in another request
            # TODO : enhance that
            query = """
                START root=node({root})
                MATCH (root)<-[:`<<INSTANCE>>`]-(type)
                RETURN root as leaf, ID(root) as id_leaf, type
            """.format(root=root_node)
            for row in connection.cypher(query).to_dicts():
                rows.append(row)
        # filter rows using the models in ontology
        # FIXME: should be in the cypher query
        models_in_ontology = map(lambda m: m.__name__.lower(), topic.get_models())
        rows = filter(lambda r: r['type']['data']['model_name'].lower() in models_in_ontology, rows)

        for row in rows:
            row['leaf']['data']['_id'] = row['id_leaf']
            row['leaf']['data']['_type'] = row['type']['data']['model_name']
            leafs[row['id_leaf']] = row['leaf']['data']
        if len(leafs) == 0:
            return ([], [])

        # Then we retrieve all edges
        query = """
            START A=node({leafs})
            MATCH (A)-[rel]-(B)
            WHERE type(rel) <> "<<INSTANCE>>"
            RETURN ID(A) as head, type(rel) as relation, id(B) as tail
        """.format(leafs=','.join([str(id) for id in leafs.keys()]))
        rows = connection.cypher(query).to_dicts()
        for row in rows:
            try:
                if (leafs[row['head']] and leafs[row['tail']]):
                    leafs_related.extend([row['head'], row['tail']])
                    edges.append([row['head'], row['relation'], row['tail']])
            except KeyError:
                pass
        # filter edges with relations in ontology
        models_fields         = itertools.chain(*map(get_model_fields, topic.get_models()))
        relations_in_ontology = set(map(lambda _: _.get("rel_type"), models_fields))
        edges                 = [e for e in edges if e[1] in relations_in_ontology]
        # filter leafts without relations
        # FIXME: should be in the cypher query
        leafs_related = set(leafs_related)
        leafs = dict((k, v) for k, v in leafs.iteritems() if k in leafs_related)
        return (leafs, edges)

    cache_key = "leafs_and_nodes_%s_%s" % (depth, root_node)
    topic_cache = TopicCachier()
    leafs_and_edges = topic_cache.get(topic, cache_key)
    if leafs_and_edges != None:
        return leafs_and_edges
    else:
        leafs_and_edges = _get_leafs_and_edges(topic=topic, depth=depth, root_node=root_node)
        topic_cache.set(topic, cache_key, leafs_and_edges)
        return leafs_and_edges

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
    return model._meta.app_label or model.__module__.split(".")[-2]

def to_class_name(value=""):
    """
    Class name must:
        - begin by an uppercase
        - use camelcase
    """
    value = value.replace("_", " ")
    return ''.join(x for x in str(value).title() if not x.isspace())


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
    # Space to underscore
    value = value.replace(" ", "_")

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def uploaded_to_tempfile(uploaded_file):
    # reset uploaded file's cusor
    cursor_pos = uploaded_file.tell()
    uploaded_file.seek(0)
    # create a new tempfile
    temporary = tempfile.TemporaryFile()
    # write the uploaded content
    temporary.write(uploaded_file.read())
    # reset cusors
    temporary.seek(0)
    uploaded_file.seek(cursor_pos)

    return temporary

def open_csv(csv_file):
    """
    Return a csv reader for the reading the given file.
    Deduce the format of the csv file.
    """
    import csv
    if hasattr(csv_file, 'read'):
        sample = csv_file.read(1024)
        csv_file.seek(0)
    elif type(csv_file) in (tuple, list):
        sample = "\n".join(csv_file[:5])
    dialect = csv.Sniffer().sniff(sample)
    dialect.doublequote = True
    reader = csv.reader(csv_file, dialect)
    return reader

# @src: http://stackoverflow.com/a/3218128/797941
def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def should_show_debug_toolbar(request):
    return re.match(r'^/api/', request.path) != None

class TopicCachier(object):
    __instance = None
    # dict of cache key definitions / formats
    __KEYS = {
        # general prefix for every key
        'topic_prefix'   : 'topic_{module}',
        # specific version cache key
        'version_number' : '{topic_prefix}_version',
        # topic's related cache key prefix
        'cache_prefix'   : '{topic_prefix}_{suffix}',
    }

    __TIMEOUTS = {
        'default': 60 * 60 # 3600 secondes = 1h
    }

    def __keys(self):
        return self.__KEYS

    def __timeout(self, key='default'):
        return self.__TIMEOUTS[key]

    def __version_key(self, topic):
        return self.__keys()['version_number'].format(
            topic_prefix=self.__topic_prefix(topic))

    def __topic_prefix(self, topic):
        return self.__keys()['topic_prefix'].format(
            module=topic.module)

    def __get_key(self, topic, suffix):
        return self.__keys()['cache_prefix'].format(
            topic_prefix=self.__topic_prefix(topic),
            suffix=suffix
        )

    def init_version(self, topic):
        cache.set(
            self.__version_key(topic), 0, self.__timeout()
        )

    def version(self, topic):
        cache_key = self.__version_key(topic)
        return cache.get(cache_key)

    def incr_version(self, topic):
        cache_key = self.__version_key(topic)
        if cache.get(cache_key) == None:
            self.init_version(topic)
        else:
            cache.incr(cache_key)

    def delete_version(self, topic):
        cache_key = self.__version_key(topic)
        cache.delete(cache_key)

    def get(self, topic, suffix_key):
        rev       = self.version(topic)
        cache_key = self.__get_key(topic, suffix_key)
        return cache.get(cache_key, version=rev)

    def set(self, topic, suffix_key, value, timeout=None):
        rev = self.version(topic)
        if timeout == None:
            timeout = self.__timeout()
        cache_key = self.__get_key(topic, suffix_key)
        cache.set(cache_key, value, timeout, version=rev)

    def delete(self, topic, suffix_key):
        cache_key = self.__get_key(topic, suffix_key)
        rev = self.version(topic)
        cache.delete(cache_key, version=rev)

    def debug(self, msg):
        print "\nDEBUG - TopicCachier %s\n" % msg

    def __new__(self):
        # singleton instanciation
        if self.__instance == None:
            self.__instance = super(TopicCachier, self).__new__(self)
        return self.__instance

topic_cache = TopicCachier()
# EOF
