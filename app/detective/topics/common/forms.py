from app.detective.topics.common.models import Country
from app.detective.modelrules           import ModelRules

def topics_rules():
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    # Disable editing on some model
    rules.model(Country).add(is_editable=False)
    return rules