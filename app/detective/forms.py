from app.detective.modelrules  import ModelRules
import importlib

def register_model_rules():
    # Singleton
    if hasattr(register_model_rules, "rules"): return register_model_rules.rules        
    # Avoid bi-directional dependancy
    from app.detective.utils import get_apps
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    # Each app can defined a forms.py file that describe the model rules
    apps = get_apps()
    for app in apps:
        # Does this app contain a forms.py file?
        path = "app.detective.apps.%s.forms" % app
        try:
            mod  = importlib.import_module(path)              
        except ImportError:
            # Ignore import error
            continue
        func = getattr(mod, "register_model_rules", None)        
        # Simply call the function to register app's rules
        if func: rules = func()
    # Register the rules
    register_model_rules.rules = rules
    return rules