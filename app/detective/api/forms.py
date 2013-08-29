from ..modelrules     import ModelRules
from ..models         import *
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

	# Records "invisible" fields	
	# Organization
	rules.model(EnergyProduct).field("operator").add(visible=False)
	rules.model(EnergyProject).field("ended").add(visible=False)
	rules.model(EnergyProject).field("partner").add(visible=False)
	rules.model(FundraisingRound).field("personal_payer").add(visible=False)
	rules.model(Organization).field("adviser").add(visible=False)
	rules.model(Organization).field("board_member").add(visible=False)
	rules.model(Organization).field("company_register_link").add(visible=False)
	rules.model(Organization).field("litigation_against").add(visible=False)
	rules.model(Organization).field("monitoring_body").add(visible=False)
	rules.model(Organization).field("partner").add(visible=False)
	rules.model(Organization).field("website_url").add(visible=False)
	rules.model(Person).field("previous_activity_in_organization").add(visible=False)
	rules.model(Person).field("website_url").add(visible=False)
	rules.model(Project).field("partner").add(visible=False)

	return rules