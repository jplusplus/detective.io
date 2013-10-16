from app.detective.apps.common.models import *
from app.detective.apps.energy.models import *
from app.detective.modelrules         import ModelRules
from app.detective.neomatch           import Neomatch
from app.detective.models             import *

def register_model_rules():
    # ModelRules is a singleton that record every model rules
    rules = ModelRules()   
    # Records "invisible" fields
    rules.model(EnergyProduct).field("operator").add(is_visible=False)
    rules.model(EnergyProject).field("ended").add(is_visible=False)
    rules.model(EnergyProject).field("partner").add(is_visible=False)

    rules.model(Country).add(product_set= Neomatch(
        title="Energy products distributed in this country",
        target_model=EnergyProduct,
        match="""
            (root)<--()<-[:`energy_product_has_distribution+`]-({select})
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

    return rules