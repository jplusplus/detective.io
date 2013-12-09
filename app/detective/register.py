from app.detective             import owl, utils
from app.detective.models      import Topic
from app.detective.modelrules  import ModelRules
from django.conf.urls          import url, include, patterns
from django.db                 import DatabaseError
from tastypie.api              import Api
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
    apps = get_topics()
    for app in apps:
        # Does this app contain a forms.py file?
        path = "app.detective.topics.%s.forms" % app
        try:
            mod  = importlib.import_module(path)
        except ImportError:
            # Ignore import error
            continue
        func = getattr(mod, "topics_rules", None)
        # Simply call the function to register app's rules
        if func: rules = func()
    # Register the rules
    topics_rules.rules = rules
    return rules

def import_or_create(path):
    try:
        # Import the models.py file
        module = importlib.import_module(path)
    # File dosen't exist, we create it virtually!
    except ImportError:
        module = types.ModuleType(str(path))
        # Register the virtual module
        sys.modules[path] = module
    return module

def topic_models(path, with_api=True):
    """
        Auto-discover topic-related model by looking into
        a topic package for an ontology file. This will also
        create all api resources and endpoints.
    """
    topic_name   = path.split(".")[-1]
    # Ensure that the topic's model exist
    import_or_create(path)
    try:
        topic_obj = Topic.objects.get(module=topic_name)
        app_label = topic_obj.app_label()
    except Topic.DoesNotExist:
        # Fails silently
        return []
    # Add '.models to the path if needed
    models_path = path if path.endswith(".models") else '%s.models' % path
    urls_path   = "%s.urls" % path
    # Import or create virtually the models.py file
    models_module = import_or_create(models_path)
    if topic_obj.ontology is None:
        directory     = os.path.dirname(os.path.realpath( models_module.__file__ ))
        # Path to the ontology file
        ontology = "%s/ontology.owl" % directory
    else:
        # Use the provided file
        ontology = topic_obj.ontology
    try:
        # Generates all model using the ontology file.
        # Also overides the default app label to allow data persistance
        models = owl.parse(ontology, path, app_label=app_label)
        # Makes every model available through this module
        for m in models: setattr(models_module, m, models[m])
    except TypeError:
        models = []
    # No API creation request!
    if not with_api: return models
    # Generates the API endpoints
    api = Api(api_name='v1')
    # Creates a resource for each model
    for name in models:
        Resource = utils.create_model_resource(models[name])
        # Register the virtual resource to by importa
        resource_path = "%s.resource.%sResource" % (path, name)
        sys.modules[resource_path] = Resource
        # And register it into the API instance
        api.register(Resource())
    # Create url patterns
    urlpatterns = patterns(path,
        url(r'', include(api.urls)),
    )
    # Import or create virtually the url path
    urls_modules = import_or_create(urls_path)
    # Merge the two url patterns if needed
    if hasattr(urls_modules, "urlpatterns"): urlpatterns += urls_modules.urlpatterns
    # Update the current url pattern
    urls_modules.urlpatterns = urlpatterns
    # API is now up and running,
    # we need to connect its url patterns to global one
    urls = importlib.import_module("app.urls")
    # Add api url pattern with the highest priority
    urls.urlpatterns = patterns(app_label,
        url(r'^api/%s/' % topic_obj.slug, include(urls_path, app_name=app_label)),
    # Merge with a filtered version of the urlpattern to avoid duplicates
    ) + [u for u in urls.urlpatterns if getattr(u, "app_name", None) != app_label ]

    return models

def init_topics():
    try:
        # Create all the application using database information
        for topic in Topic.objects.all():
            if topic.module not in ["common", "energy"]:
                topic_models("app.detective.topics.%s" % topic.module)
    except DatabaseError:
        # Database may not be ready yet (syncdb running),
        # we juste pass silently
        from django.db import transaction
        # Checks that we're in transaction-managed system
        if transaction.is_managed(): transaction.rollback()
        pass