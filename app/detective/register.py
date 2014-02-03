from app.detective                       import owl, utils
from app.detective.modelrules            import ModelRules
from app.detective.models                import Topic
from django.conf.urls                    import url, include, patterns
from django.conf                         import settings
from django.core.urlresolvers            import clear_url_caches
from tastypie.api                        import NamespacedApi

import importlib
import os
import sys
import types

def topics_rules():
    """
        Auto-discover topic-related rules by looking into
        evry topics' directories for forms.py files.
    """
    # Singleton
    if hasattr(topics_rules, "rules"): return topics_rules.rules
    # Avoid bi-directional dependancy
    from app.detective.utils import get_topics
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    # Each app can defined a forms.py file that describe the model rules
    topcis = get_topics(offline=False)
    for topic in topcis:
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
    # Register the rules
    topics_rules.rules = rules
    return rules

def default_rules(topic):
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    # We cant import this early to avoid bi-directional dependancies
    from app.detective.utils import import_class
    # Get all registered models
    models = Topic.objects.get(module=topic).get_models()
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
                rules.model(model).field(field.name).add(is_editable=modelRules["is_editable"])
    return rules

def import_or_create(path, register=True):
    try:
        # Import the models.py file
        module = importlib.import_module(path)
    # File dosen't exist, we create it virtually!
    except ImportError:
        path_parts = path.split(".")
        module     = types.ModuleType(str(path))
        # Register the new module in the global scope
        if register:
            # Get the parent module
            parent      = import_or_create( ".".join( path_parts[0:-1]) )
            # Register this module as attribute of its parent
            setattr( parent, path_parts[-1], module)
            # Register the virtual module
            sys.modules[path] = module
    return module


def reload_urlconf(urlconf=None):
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])

def topic_models(path, with_api=True):
    """
        Auto-discover topic-related model by looking into
        a topic package for an ontology file. This will also
        create all api resources and endpoints.
    """
    topic_module = import_or_create(path)
    topic_name   = path.split(".")[-1]
    # Ensure that the topic's model exist
    topic = Topic.objects.get(module=topic_name)
    app_label = topic.app_label()
    # Add '.models to the path if needed
    models_path = path if path.endswith(".models") else '%s.models' % path
    urls_path   = "%s.urls" % path
    # Import or create virtually the models.py file
    models_module = import_or_create(models_path)
    if topic.ontology is None:
        directory     = os.path.dirname(os.path.realpath( models_module.__file__ ))
        # Path to the ontology file
        ontology = "%s/ontology.owl" % directory
    else:
        # Use the provided file
        ontology = topic.ontology
    try:
        # Generates all model using the ontology file.
        # Also overides the default app label to allow data persistance
        models = owl.parse(ontology, path, app_label=app_label)
        # Makes every model available through this module
        for m in models: setattr(models_module, m, models[m])
    except TypeError:
        models = []
    # No API creation request!
    if not with_api: return topic_module
    # Generates the API endpoints
    api = NamespacedApi(api_name='v1', urlconf_namespace=app_label)
    # Create resources root if needed
    resources = import_or_create("%s.resources" % path)
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
    summary_module = import_or_create(summary_path)
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
    urls_modules = import_or_create(urls_path)
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