from app.detective             import owl
from app.detective             import utils
from app.detective.modelrules  import ModelRules
from django.conf.urls          import url, include, patterns
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


def topic_models(path, with_api=True):
    """
        Auto-discover topic-related model by looking into
        a topic package for an ontology file. This will also
        create all api resources and endpoints.
    """
    topic_name  = path.split(".")[-1]
    # Add '.models to the path if needed
    models_path = path if path.endswith(".models") else '%s.models' % path
    urls_path   = "%s.urls" % path
    # Import the models.py file
    models_module = importlib.import_module(models_path)
    directory     = os.path.dirname(os.path.realpath( models_module.__file__ ))
    # Path to the ontology file
    ontology = "%s/ontology.owl" % directory
    # Generates all model using the ontology file
    models = owl.parse(ontology, path)
    # API creation request!
    if with_api:
        # Generates the API endpoints
        api = Api(api_name='v1')
        # Creates a resource for each model
        for name in models:
            model =  models[name]
            Resource = utils.create_model_resource(model)
            # Register the virtual resource to by importa
            resource_path = "%s.resource.%sResource" % (path, name)
            sys.modules[resource_path] = Resource
            # And register it into the API instance
            api.register(Resource())
        # Create url patterns
        urlpatterns = patterns(path,
            url(r'', include(api.urls)),
        )
        try:
            urls_modules = importlib.import_module(urls_path)
            # Merge the two url patterns if needed
            if hasattr(urls_modules, "urlpatterns"): urlpatterns += urls_modules.urlpatterns
            # Update the current url pattern
            urls_modules.urlpatterns = urlpatterns
        # If urls.py doesn't exist, we create a virtual one
        except ImportError:
            # Creates a virtual 'urls' module inside the current path
            urls_modules = types.ModuleType(urls_path)
            # Add a urlpatterns
            urls_modules.urlpatterns = urlpatterns
            # Register the virtual module
            sys.modules[urls_path] = urls_modules
        # API is now up and running,
        # we need to connect its url patterns to global one
        urls = importlib.import_module("app.urls")
        # Add api url pattern with the highest priority
        urls.urlpatterns = patterns('api',
            url(r'^api/%s/' % topic_name, include(urls_path)),
        ) + urls.urlpatterns
    return models