from app.detective.apps.energy.models   import *
from app.detective.modelrules           import ModelRules
from app.detective.neomatch             import Neomatch
from app.detective.models               import *
from django.db.models                   import get_app, get_models

def register_model_rules():
    # Singleton
    if hasattr(register_model_rules, "rules"): return register_model_rules.rules
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()
    # Disable editing on some model
    rules.model(Country).add(is_editable=False)    
    # Records "invisible" fields
    rules.model(EnergyProduct).field("operator").add(is_visible=False)
    rules.model(EnergyProject).field("ended").add(is_visible=False)
    rules.model(EnergyProject).field("partner").add(is_visible=False)
    rules.model(FundraisingRound).field("personal_payer").add(is_visible=False)
    rules.model(Organization).field("adviser").add(is_visible=False)
    rules.model(Organization).field("board_member").add(is_visible=False)
    rules.model(Organization).field("company_register_link").add(is_visible=False)
    rules.model(Organization).field("litigation_against").add(is_visible=False)
    rules.model(Organization).field("monitoring_body").add(is_visible=False)
    rules.model(Organization).field("partner").add(is_visible=False)
    rules.model(Organization).field("website_url").add(is_visible=False)
    rules.model(Person).field("previous_activity_in_organization").add(is_visible=False)
    rules.model(Person).field("website_url").add(is_visible=False)
    rules.model(Project).field("partner").add(is_visible=False)

    rules.model(Country).add(product_set= Neomatch(
        title="Energy products distributed in this country",
        target_model=EnergyProduct,
        match="""
            (root)<--()<-[:`energy_product_has_distribution+`]-({select})
        """
    ))

    rules.model(Country).add(person_set=Neomatch(
        title="Persons from this country",
        target_model=Person,
        match="""
            (root)-[:`person_has_nationality+`]-({select})
        """
    ))

    rules.model(Country).add(project_set=Neomatch(
        title="Energy projects active in this country",
        target_model=EnergyProject,
        match="""
            (root)-[:`energy_project_has_activity_in_country+`]-({select})
        """
    ))

    rules.model(EnergyProduct).add(country_set= Neomatch(
        title="Countries where this product is distributed",
        target_model=Country,
        match="""
            (root)-[:`energy_product_has_distribution+`]-()-[:`distribution_has_activity_in_country+`]-({select})
        """
    ))
    
    rules.model(Organization).add(energyproject_set=Neomatch(
        title="Energy projects this organization owns",
        target_model=EnergyProject,
        match="""
            (root)-[:`energy_project_has_owner+`]-({select})
        """
    ))
    
    rules.model(EnergyProject).add(energyproduct_set=Neomatch(
        title="Energy project this product belongs to",
        target_model=EnergyProduct,
        match="""
            (root)-[:`energy_project_has_product+`]-({select})
        """
    ))



    rules.model(Person).add(organizationkey_set=Neomatch(
        title="Organizations this person has a key position in",
        target_model=Organization,
        match="""
            (root)-[:`organization_has_key_person+`]-({select})
        """
    ))

    rules.model(Person).add(organizationadviser_set=Neomatch(
        title="Organizations this person is an adviser to",
        target_model=Organization,
        match="""
            (root)-[:`organization_has_adviser+`]-({select})
        """
    ))

    rules.model(Person).add(organizationboard_set=Neomatch(
        title="Organizations this person is a board member of",
        target_model=Organization,
        match="""
            (root)-[:`organization_has_board_member+`]-({select})
        """
    ))

    rules.model(Person).add(fundraisinground_set=Neomatch(
        title="Fundraising rounds this person has contributed to",
        target_model=FundraisingRound,
        match="""
            (root)-[:`fundraising_round_has_personal_payer+`]-({select})
        """
    ))



    # Add now some generic rules
    app = get_app('detective')
    # Set "is_searchable" to true on every model with a name
    for model in get_models(app):
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
    for model in get_models(app):
        for field in model._meta.fields:         
            # Find related model for relation
            if hasattr(field, "target_model"):                       
                target_model  = field.target_model         
                # It's a searchable field !
                modelRules = rules.model(target_model).all()
                # Set it into the rules
                rules.model(model).field(field.name).add(is_searchable=modelRules["is_searchable"])
                rules.model(model).field(field.name).add(is_editable=modelRules["is_editable"])                            

    # Register the rules
    register_model_rules.rules = rules
    return rules