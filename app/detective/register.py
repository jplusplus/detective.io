from app.detective                       import parser, utils
from app.detective.modelrules            import ModelRules
from app.detective.models                import Topic
from django.conf.urls                    import url, include, patterns
from django.conf                         import settings
from django.core.cache                   import cache
from django.core.urlresolvers            import clear_url_caches
from tastypie.api                        import NamespacedApi

import importlib
import os
import sys
import imp

class TopicRegistor(object):
    __instance = None

    def __is_topic(self, topic):
        return isinstance(topic, Topic)

    def __get_topic_key(self, topic):
        key = topic
        if self.__is_topic(topic):
            key = topic.ontology_as_mod
        return key

    def __topic_models(self, topic):
        key = self.__get_topic_key(topic)
        return self.__registered_topics.get(key)

    def __new__(self, *args, **kwargs):
        if not self.__instance:
            self.__instance = super(TopicRegistor, self).__new__(self, *args, **kwargs)
            self.__registered_topics = {}
        return self.__instance

    def register_topic(self, topic):
        topic_key = self.__get_topic_key(topic)
        if not self.__topic_models(topic_key):
            self.__registered_topics[topic_key] = self.topic_models(topic_key)
            self.default_rules(topic) # register default rules for a topic
        return self.__topic_models(topic_key)

    def default_rules(self, topic):
        # ModelRules is a singleton that record every model rules
        rules = ModelRules()
        # We cant import this early to avoid bi-directional dependancies
        from app.detective.utils import import_class
        models = self.topic_models(topic)
        treated_models = []
        # Set "is_searchable" to true on every model with a name
        for model in models:
            # If the current model has a name
            if "name" in rules.model(model).field_names:
                field_names = rules.model(model).field_names
                # Count the fields len
                fields_len = len(field_names)
                # Put the highest priority to that name
                rules.model(model).field('name').add(priority=fields_len)
                rules.model(model).add(is_searchable=True)
            # This model isn't searchable
            else: rules.model(model).add(is_searchable=False)
            # since we use a generator for topics models we need to convert it
            # to a list to perform a 2nd loop.
            treated_models.append(model)

        # we need to pass a first time on every models to have the proper rules
        # and a second for their RelationShip fields
        for model in treated_models:
            # Check now that each "Relationship"
            # match with a searchable model
            for field in model._meta.fields:
                # Find related model for relation
                if hasattr(field, "target_model"):
                    target_model  = field.target_model
                    # Load class path
                    if type(target_model) is str: target_model = import_class(target_model)
                    # It's a searchable field !
                    modelRules = rules.model(target_model).all()
                    # Set it into the rules
                    rules.model(model).field(field.name).add(is_searchable=modelRules["is_searchable"])
                    # Entering relationship are not editable yet
                    is_editable = (False if hasattr(target_model, field.name) else False) \
                                  if field.direction == 'in' and target_model is model else modelRules["is_editable"]
                    rules.model(model).field(field.name).add(is_editable=is_editable)
        return rules

    def topic_models(self, topic):
        topic_key = self.__get_topic_key(topic)
        models    = self.__topic_models(topic_key)
        if not models:
            # Store topic object in a temporary attribute
            # to avoid SQL lazyness
            cache_key = "prefetched_topic_%s" % topic_key
            if cache.get(cache_key, None) == None:
                # Get all registered models for this topic
                if not self.__is_topic(topic):
                    topic = Topic.objects.get(ontology_as_mod=topic_key)
                models = topic.get_models()
                cache.set(cache_key, topic, 10)
            else:
                topic = cache.get(cache_key)
                # Get all registered models
                models = topic.get_models()
        return models

def topics_rules():
    """
        Auto-discover topic-related rules by looking into
        every topics' directories for forms.py files.
    """
    # Avoid bi-directional dependancy
    from app.detective.utils import get_topics
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    registor = TopicRegistor()
    # Each app module can defined a forms.py file that describe the model rules
    topics = get_topics()
    for topic in topics:
        registor.register_topic(topic)
        # Does this app contain a forms.py file?
        path = "app.detective.topics.%s.forms" % topic
        try:
            mod  = importlib.import_module(path)
        except ImportError:
            # Ignore absent forms.py
            continue
        func = getattr(mod, "topics_rules", None)
        # Simply call the function to register app's rules
        if func: rules = func()
    return rules


def import_or_create(path, register=True, force=False):
    try:
        # Import the module once
        module = importlib.import_module(path)
        # If it doesn't raise an Importerror,
        # we may need to reload it
        if force:
            # The module isn't a file
            if getattr(module, "__file__", None) is None and path in sys.modules:
                del( sys.modules[path] )
                # Reimport the module
                raise ImportError
    # File dosen't exist, we create it virtually!
    except ImportError:
        path_parts         = path.split(".")
        module             = imp.new_module(path)
        module.__name__    = path
        name               = path_parts[-1]
        # Register the new module in the global scope
        if register:
            # Get the parent module
            parent = import_or_create( ".".join( path_parts[0:-1]) )
            # Avoid memory leak
            if force and hasattr(parent, name):
                delattr(parent, name)
            # Register this module as attribute of its parent
            setattr(parent, name, module)
            # Register the virtual module
            sys.modules[path] = module
    return module


def reload_urlconf(urlconf=None):
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])

def topic_models(path, force=False):
    """
        Auto-discover topic-related model by looking into
        a topic package for an ontology file. This will also
        create all api resources and endpoints.

        This will create the following modules:
            {path}
            {path}.models
            {path}.resources
            {path}.summary
            {path}.urls
    """
    topic_module = import_or_create(path, force=force)
    topic_name   = path.split(".")[-1]
    # Ensure that the topic's model exist
    topic = Topic.objects.get(ontology_as_mod=topic_name)
    app_label = topic.app_label()
    # Add '.models to the path if needed
    models_path = path if path.endswith(".models") else '%s.models' % path
    urls_path   = "%s.urls" % path
    # Import or create virtually the models.py file
    models_module = import_or_create(models_path, force=force)
    try:
        # Generates all model using the ontology file.
        # Also overides the default app label to allow data persistance
        if topic.ontology_as_json is not None:
            # JSON ontology
            models = parser.json.parse(topic.ontology_as_json, path, app_label=app_label)
        elif topic.ontology_as_owl is not None:
            # OWL ontology
            models = parser.owl.parse(topic.ontology_as_owl, path, app_label=app_label)
        else:
            models = []
    # except TypeError as e:
    #    if settings.DEBUG: print 'TypeError:', e
    #    models = []
    except ValueError as e:
        if settings.DEBUG: print 'ValueError:', e
        models = []
    # Makes every model available through this module
    for m in models:
        # Record the model
        setattr(models_module, m, models[m])
    # Generates the API endpoints
    api = NamespacedApi(api_name='v1', urlconf_namespace=app_label)
    # Create resources root if needed
    resources = import_or_create("%s.resources" % path, force=force)
    # Creates a resource for each model
    for name in models:
        Resource = utils.create_model_resource(models[name])
        resource_name = "%sResource" % name
        # Register the virtual resource to by importa
        resource_path = "%s.resources.%s" % (path, resource_name)
        # This resource is now available everywhere:
        #  * as an attribute of `resources`
        #  * as a module
        setattr(resources, resource_name, Resource)
        sys.modules[resource_path] = Resource
        # And register it into the API instance
        api.register(Resource())
    # Every app have to instance a SummaryResource class
    summary_path   = "%s.summary" % path
    summary_module = import_or_create(summary_path, force=force)
    # Take the existing summary resource
    if hasattr(summary_module, 'SummaryResource'):
        SummaryResource = summary_module.SummaryResource
    # We create one if it doesn't exist
    else:
        from app.detective.topics.common.summary import SummaryResource as CommonSummaryResource
        attrs           = dict(meta=CommonSummaryResource.Meta)
        SummaryResource = type('SummaryResource', (CommonSummaryResource,), attrs)
    # Register the summary resource
    api.register(SummaryResource())
    # Create url patterns
    urlpatterns = patterns(path, url('', include(api.urls)), )
    # Import or create virtually the url path
    urls_modules = import_or_create(urls_path, force=force)
    # Merge the two url patterns if needed
    if hasattr(urls_modules, "urlpatterns"): urlpatterns += urls_modules.urlpatterns
    # Update the current url pattern
    urls_modules.urlpatterns = urlpatterns
    # API is now up and running,
    # we need to connect its url patterns to global one
    urls = importlib.import_module("app.detective.urls")
    # Add api url pattern with the highest priority
    new_patterns = patterns(app_label,
        url(r'^{0}/{1}/'.format(topic.author, topic.slug), include(urls_path, namespace=app_label) ),
    )
    if hasattr(urls, "urlpatterns"):
        # Merge with a filtered version of the urlpattern to avoid duplicates
        new_patterns += [u for u in urls.urlpatterns if getattr(u, "namespace", None) != app_label ]
    # Then update url pattern
    urls.urlpatterns = new_patterns
    # At last, force the url resolver to reload (because we update it)
    clear_url_caches()
    reload_urlconf()
    return topic_module