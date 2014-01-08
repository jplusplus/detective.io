from .models                             import *
from app.detective.individual            import IndividualResource, IndividualMeta
from app.detective.topics.common.summary import SummaryResource

class SummaryResource(SummaryResource):
    class Meta(SummaryResource.Meta):
        pass

    def get_syntax(self, bundle=None, request=None):
        return {
            'subject': {
                'model':  self.get_models_output(),
                'entity': None
            },
            'predicate': {
                'relationship': [
                    {
                        "name": "fundraising_round_has_personal_payer+",
                        "subject": "energy:FundraisingRound",
                        "label": "was financed by"
                    },
                    {
                        "name": "fundraising_round_has_payer+",
                        "subject": "energy:FundraisingRound",
                        "label": "was financed by"
                    },
                    {
                        "name": "person_has_educated_in+",
                        "subject": "energy:Person",
                        "label": "was educated in"
                    },
                    {
                        "name": "person_has_based_in+",
                        "subject": "energy:Person",
                        "label": "is based in"
                    },
                    {
                        "name": "person_has_activity_in_organization+",
                        "subject": "energy:Person",
                        "label": "has activity in"
                    },
                    {
                        "name": "person_has_previous_activity_in_organization+",
                        "subject": "energy:Person",
                        "label": "had previous activity in"
                    },
                    {
                        "name": "energy_product_has_price+",
                        "subject": "energy:EnergyProduct",
                        "label": "is sold at"
                    },
                    {
                        "name": "commentary_has_author+",
                        "subject": "energy:Commentary",
                        "label": "was written by"
                    },
                    {
                        "name": "energy_product_has_distribution+",
                        "subject": "energy:EnergyProduct",
                        "label": "is distributed in"
                    },
                    {
                        "name": "energy_product_has_operator+",
                        "subject": "energy:EnergyProduct",
                        "label": "is operated by"
                    },
                    {
                        "name": "energy_product_has_price+",
                        "subject": "energy:EnergyProduct",
                        "label": "is sold at"
                    },
                    {
                        "name": "organization_has_adviser+",
                        "subject": "energy:Organization",
                        "label": "is advised by"
                    },
                    {
                        "name": "organization_has_key_person+",
                        "subject": "energy:Organization",
                        "label": "is staffed by"
                    },
                    {
                        "name": "organization_has_partner+",
                        "subject": "energy:Organization",
                        "label": "has a partnership with"
                    },
                    {
                        "name": "organization_has_fundraising_round+",
                        "subject": "energy:Organization",
                        "label": "was financed by"
                    },
                    {
                        "name": "organization_has_monitoring_body+",
                        "subject": "energy:Organization",
                        "label": "is monitored by"
                    },
                    {
                        "name": "organization_has_litigation_against+",
                        "subject": "energy:Organization",
                        "label": "has a litigation against"
                    },
                    {
                        "name": "organization_has_revenue+",
                        "subject": "energy:Organization",
                        "label": "has revenue of"
                    },
                    {
                        "name": "organization_has_board_member+",
                        "subject": "energy:Organization",
                        "label": "has board of directors with"
                    },
                    {
                        "name": "energy_project_has_commentary+",
                        "subject": "energy:EnergyProject",
                        "label": "is analyzed by"
                    },
                    {
                        "name": "energy_project_has_owner+",
                        "subject": "energy:EnergyProject",
                        "label": "is owned by"
                    },
                    {
                        "name": "energy_project_has_partner+",
                        "subject": "energy:EnergyProject",
                        "label": "has a partnership with"
                    },
                    {
                        "name": "energy_project_has_activity_in_country+",
                        "subject": "energy:EnergyProject",
                        "label": "has activity in"
                    },
                    {
                        "name": "distribution_has_activity_in_country+",
                        "subject": "energy:Distribution",
                        "label": "has activity in"
                    },
                    {
                        "name": "energy_project_has_product+",
                        "subject": "energy:EnergyProject",
                        "label": "has product of"
                    },
                    {
                        "name": "energy_project_has_commentary+",
                        "subject": "energy:EnergyProject",
                        "label": "is analyzed by"
                    },
                    {
                        "name": "energy_project_has_owner+",
                        "subject": "energy:EnergyProject",
                        "label": "is owned by"
                    },
                    {
                        "name": "energy_project_has_partner+",
                        "subject": "energy:EnergyProject",
                        "label": "has partnership with"
                    },
                    {
                        "name": "energy_project_has_activity_in_country+",
                        "subject": "energy:EnergyProject",
                        "label": "has activity in"
                    }
                ]
            }
        }


class CountryResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Country.objects.all().select_related(depth=1)

class AmountResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Amount.objects.all().select_related(depth=1)

class FundraisingRoundResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = FundraisingRound.objects.all().select_related(depth=1)

class PersonResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Person.objects.all().select_related(depth=1)

class RevenueResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Revenue.objects.all().select_related(depth=1)

class CommentaryResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Commentary.objects.all().select_related(depth=1)

class OrganizationResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Organization.objects.all().select_related(depth=1)

class DistributionResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Distribution.objects.all().select_related(depth=1)

class PriceResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = Price.objects.all().select_related(depth=1)

class EnergyProductResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProduct.objects.all().select_related(depth=1)

class EnergyProjectResource(IndividualResource):
    class Meta(IndividualMeta):
        queryset = EnergyProject.objects.all().select_related(depth=1)

