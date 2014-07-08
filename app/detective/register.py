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


def topics_rules():
    """
        Auto-discover topic-related rules by looking into
        evry topics' directories for forms.py files.
    """
    # Avoid bi-directional dependancy
    from app.detective.utils import get_topics
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    # Each app can defined a forms.py file that describe the model rules
    topics = get_topics(offline=False)
    for topic in topics:
        # Add default rules
        default_rules(topic)
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

def default_rules(topic):
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    # We cant import this early to avoid bi-directional dependancies
    from app.detective.utils import import_class
    # Store topic object in a temporary attribute
    # to avoid SQL lazyness
    cache_key = "prefetched_topic_%s" % topic
    if cache.get(cache_key, None) is None:
        # Get all registered models for this topic
        topic  = Topic.objects.get(ontology_as_mod=topic)
        models = topic.get_models()
        cache.set(cache_key, topic, 10)
    else:
        # Get all registered models
        models = cache.get(cache_key).get_models()

    # Set "is_searchable" to true on every model with a name
    for model in models:
        # If the current model has a name
        if "name" in rules.model(model).field_names:
            field_names = rules.model(model).field_names
            # Count the fields len
            fields_len = len(field_names)
            # Put the highest priority to that name
            rules.model(model).field('name').add(priority=fields_len)
        # This model isn't searchable
        else: rules.model(model).add(is_searchable=False)
    # Check now that each "Relationship"
    # match with a searchable model
    for model in models:
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
                is_editable = False if field.direction == 'in' and target_model is model else modelRules["is_editable"]
                rules.model(model).field(field.name).add(is_editable=is_editable)
    return rules

def import_or_create(path, register=True, force=False):
    try:
        # For the new module to be written
        if force:
            if path in sys.modules: del( sys.modules[path] )
            raise ImportError
        # Import the models.py file
        module = importlib.import_module(path)
    # File dosen't exist, we create it virtually!
    except ImportError:
        path_parts      = path.split(".")
        module          = imp.new_module(path)
        module.__name__ = path
        name            = path_parts[-1]
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
    except TypeError as e:
        if settings.DEBUG: print 'TypeError:', e
        models = []
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
        url(r'^%s/' % topic.slug, include(urls_path, namespace=app_label) ),
    )
    if hasattr(urls, "urlpatterns"):
        # Merge with a filtered version of the urlpattern to avoid duplicates
        new_patterns += [u for u in urls.urlpatterns if getattr(u, "namespace", None) != topic.slug ]
    # Then update url pattern
    urls.urlpatterns = new_patterns
    # At last, force the url resolver to reload (because we update it)
    clear_url_caches()
    reload_urlconf()
    return topic_module