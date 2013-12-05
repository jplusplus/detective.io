from app.detective.topics.common.models import Country
from app.detective.modelrules         import ModelRules

def topics_rules():
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    # Disable editing on some model
    rules.model(Country).add(is_editable=False)
    # We can import this early to avoid bi-directional dependancies
    from app.detective.utils import get_registered_models, import_class
    # Get all registered models
    models = get_registered_models()
    # Them filter the list to the detective's apps
    models = [m for m in models if m.__module__.startswith("app.detective.topics")]
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