from ..modelrules     import ModelRules
from django.db.models import get_app, get_models

def register_model_rules():
	# ModelRules is a singleton that record every model rules
	rules = ModelRules()

	app = get_app('detective')
	# Register every model from detective with some extra rules
	for model in get_models(app):
		# If the current model has a name
		if "name" in rules.model(model).field_names:
			# Count the fields len
			fields_len = len(rules.model(model).field_names)
			# Put the highest priority to that name
			rules.model(model).field('name').add(priority=fields_len)

	return rules