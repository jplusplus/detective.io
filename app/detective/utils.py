from django.core.cache         import cache
from django.core.exceptions    import ValidationError, SuspiciousOperation
from django.core.files         import File
from django.core.files.storage import default_storage
from django.core.files.temp    import NamedTemporaryFile
from django.core.validators    import validate_email
from django.db.models          import signals
from django.forms.forms        import pretty_name
from os                        import listdir
from os.path                   import isdir, join
from random                    import randint
from app.detective.exceptions  import UnavailableImage, NotAnImage, OversizedFile
from urlparse                  import urlparse
import importlib
import inspect
import itertools
import logging
import os
import re
import tempfile
import urllib2
import magic
logger = logging.getLogger(__name__)

# for relative paths
here = lambda x: join(os.path.abspath(os.path.dirname(__file__)), x)

def without(coll, val):
    def _check_not_val(el):
        if callable(val):
            return val(el) == True
        else:
            return el == val
    l_without = lambda el: not _check_not_val(el)
    return filter(l_without, coll)

def where(coll, cond_dict):
    def get_el_val(el, k):
        if callable(k):
            return k(el)
        else:
            if type(el) is type({}):
                return el.get(k)

    l_find   = lambda el: all(
        v() == get_el_val(el, k) if callable(v) else get_el_val(el, k) == v for k,v in cond_dict.items()
    )
    return filter(l_find, coll)

def findwhere(coll, cond_dict):
    return where(coll, cond_dict)[0]

def create_node_model(name, fields=None, app_label='', module='', options=None):
    """
    Create specified model
    """
    from app.detective.models import update_topic_cache, delete_entity
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
    signals.post_save.connect(update_topic_cache, sender=cls)
    signals.post_delete.connect(delete_entity, sender=cls)
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
        # Turning offline mode to false is now deprecated
        from warnings import warn
        warn("Turning offline mode to false is now deprecated with 'utils.get_topics'.")
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
            models_module = topic.get_models_module()
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

def get_topic_model(topic, model_type):
    model  = None
    models = get_topic_models(topic)
    if len(models) > 0:
        models = map(
            lambda klass: (klass.__name__.lower(), klass),
            models
        )
        results = filter(lambda el: el[0] == model_type, models)
        if len(results) > 0:
            model = results[0][1]
    return model

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
    return list(iterate_model_fields(model, order_by))

def iterate_model_fields(model, order_by='name'):
    from app.detective           import register
    from django.db.models.fields import FieldDoesNotExist
    models_rules = register.topics_rules().model(model)
    if hasattr(model, '__fields_order__'):
        _len = len(model._meta.fields)
        model_fileds = sorted(model._meta.fields, key=lambda x: model.__fields_order__.index(x.name) if x.name in model.__fields_order__ else _len)
    else:
        model_fileds = sorted(model._meta.fields, key=lambda el: getattr(el, order_by))
    for f in model_fileds:
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
                verbose_name = pretty_name(f.name).lower()
            yield {
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

def get_model_nodes():
    from neo4django.db import connection
    # Return buffer values
    if hasattr(get_model_nodes, "buffer"):
        results = get_model_nodes.buffer
        # Refresh the buffer ~ 1/10 calls
        if randint(0,10) == 10: del get_model_nodes.buffer
        return results
    query = """
        START n=node(0)
        MATCH n-[r:`<<TYPE>>`]->t
        WHERE HAS(t.name)
        RETURN t.name as name, ID(t) as id
    """
    # Bufferize the result
    get_model_nodes.buffer = connection.cypher(query).to_dicts()
    return get_model_nodes.buffer

def get_leafs_and_edges(topic, depth, root_node="0"):
    def _get_leafs_and_edges(topic, depth, root_node):
        from neo4django.db import connection
        leafs = {}
        edges = []
        leafs_related = []
        ###
        # First we retrieve every leaf in the graph
        if root_node == "0":
            query = """
                START root = node({root})
                MATCH root-[`<<TYPE>>`]->(type)--> leaf
                WHERE type.app_label = '{app_label}'
                AND not(has(leaf._relationship))
                RETURN leaf, ID(leaf) as id_leaf, type
            """.format(root=root_node, depth=depth, app_label=topic.app_label())
        else:
            query = """
                START root=node({root})
                MATCH p = (root)-[*1..{depth}]-(leaf)<-[:`<<INSTANCE>>`]-(type)
                WHERE HAS(leaf.name)
                AND type.app_label = '{app_label}'
                AND length(filter(r in relationships(p) : type(r) = "<<INSTANCE>>")) = 1
                RETURN leaf, ID(leaf) as id_leaf, type
            """.format(root=root_node, depth=depth, app_label=topic.app_label())
        rows = connection.cypher(query).to_dicts()

        if root_node != "0":
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
            MATCH (A)-[rel]->(B)
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
        models_fields         = itertools.chain(*map(iterate_model_fields, topic.get_models()))
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


def is_member_of(user, group):
    if not user or not group:
        membership = False
    membership = user.groups.filter(name=group.name).count() > 0
    return membership

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

    def __new__(self, *args, **kwargs):
        if not self.__instance:
            self.__instance = super(TopicCachier, self).__new__(self, *args, **kwargs)
        return self.__instance

    def __keys(self):
        return self.__KEYS

    def __timeout(self, key='default'):
        return self.__TIMEOUTS[key]

    def __version_key(self, topic):
        return self.__keys()['version_number'].format(
            topic_prefix=self.__topic_prefix(topic))

    def is_topic(self, topic):
        from app.detective.models import Topic
        return isinstance(topic, Topic)

    def get_topic(self, topic_module):
        topic = self.get(topic_module, 'topic_obj')
        if not topic:
            from app.detective.models import Topic
            topic = Topic.objects.get(ontology_as_mod=topic_module)
            self.set(topic_module, 'topic_obj', topic)
        return topic

    def __topic_prefix(self, topic):
        # topic can be a topic instance or a string representing topic.module
        module = topic
        if self.is_topic(topic):
            module = topic.module
        return self.__keys()['topic_prefix'].format(
            module=module)

    def __get_key(self, topic, suffix):
        return self.__keys()['cache_prefix'].format(
            topic_prefix=self.__topic_prefix(topic),
            suffix=suffix
        )

    def init_version(self, topic):
        cache.set(
            self.__version_key(topic), 1, self.__timeout()
        )

    def version(self, topic):
        cache_key = self.__version_key(topic)
        version = cache.get(cache_key)
        if version is None:
            return 0
        else:
            return int(version)

    def incr_version(self, topic):
        cache_key = self.__version_key(topic)
        if cache.get(cache_key) == None:
            self.init_version(topic)
        else:
            cache.incr(cache_key)

    def get(self, topic, suffix_key):
        rev       = self.version(topic)
        cache_key = self.__get_key(topic, suffix_key)
        return cache.get(cache_key, version=rev)

    def set(self, topic, suffix_key, value, timeout=None):
        rev = self.version(topic)
        if rev is None:
            self.incr_version(topic)
        if timeout == None:
            timeout = self.__timeout()
        cache_key = self.__get_key(topic, suffix_key)
        cache.set(cache_key, value, timeout, version=rev)

    def delete(self, topic, suffix_key):
        cache_key = self.__get_key(topic, suffix_key)
        rev = self.version(topic)
        cache.delete(cache_key, version=rev)

class DumbProfiler(object):
    __instance = None

    def __new__(self, *args, **kwargs):
        import time
        if not self.__instance:
            self.__instance = super(DumbProfiler, self).__new__(self, *args, **kwargs)
            self.__instance.time = time.time()
        return self.__instance

    def new(self):
        class Dumb(object): pass
        for attr in dir(self):
            if attr not in dir(Dumb()) + ['new'] and not attr.endswith('__instance'):
                delattr(self, attr)


topic_cache   = TopicCachier()
dumb_profiler = DumbProfiler()

def download_url(url):
    tmp_file = None
    def is_image(tmp):
        mimetype = magic.from_file(tmp.name, True)
        return mimetype.startswith('image')

    def is_oversized(tmp, url):
        max_size_in_bytes = 1 * 1024 ** 2 # 1MB
        file_size = os.stat(tmp.name).st_size
        oversized = file_size > max_size_in_bytes
        return oversized

    if url == None:
        return None
    try:
        name = urlparse(url).path.split('/')[-1]
        tmp_file = NamedTemporaryFile(delete=True)
        tmp_file.write(urllib2.urlopen(url).read())
        tmp_file.flush()
        if not is_image(tmp_file):
            raise NotAnImage()
        if is_oversized(tmp_file, url):
            raise OversizedFile()
        return File(tmp_file, name)
    except urllib2.HTTPError:
        raise UnavailableImage()
    except urllib2.URLError:
        raise UnavailableImage()



def get_image(url_or_path):
    from django.conf import settings
    if not isinstance(url_or_path, str) and \
       not isinstance(url_or_path, unicode):
        return None
    # It's an url
    elif url_or_path.startswith("http"):
        # From file storage?
        try:
            image = download_url(url_or_path)
        except UnavailableImage:
            return None
        path = join(settings.UPLOAD_ROOT, image.name)
        # And load it from the path
        return get_image(path)
    # It's a path
    elif url_or_path.startswith(settings.MEDIA_ROOT):
        try:
            # Load the file from the file storage
            if default_storage.exists(url_or_path):
                return default_storage.open(url_or_path)
            else:
                return None
        except SuspiciousOperation:
            return None
    # It's a path
    elif url_or_path.startswith("/"):
        return get_image( join( settings.MEDIA_ROOT, url_or_path.strip('/') ) )
    else:
        return None