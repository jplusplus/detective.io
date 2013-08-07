# -*- coding: utf-8 -*-
from neo4django.db          import models
from neo4django.auth.models import User
# from app.detective import fields
# The ontology can be found in its entirety at http://www.semanticweb.org/nkb/ontologies/2013/6/impact-investment#


# This model should beabstract but neo4django doesn't like it...
class Individual(models.NodeModel):
    # Admin fields
    _status     = models.IntegerProperty(default=1, editable=False)
    _author     = models.Relationship(User, rel_type='hasCreated', related_name="hasCreated+", editable=False)
    # A common field that every entity must integrate
    name        = models.StringProperty(default="No name")
    # Individual description provided by OWL file
    description = ""

    def __unicode__(self):
        return unicode(self.name) or u''

class Amount(Individual):
    description = u''
    source = models.URLProperty(null=True,help_text=u'')
    units = models.IntegerProperty(null=True,help_text=u'')
    year = models.DateTimeProperty(null=True,help_text=u'')

    class Meta:
        pass

class Country(Individual):
    description = u''
    isoa3 = models.StringProperty(null=True,help_text=u'')

    class Meta:
        verbose_name = u'Country'
        verbose_name_plural = u'Countries'

class FundraisingRound(Amount):
    description = u''
    currency = models.StringProperty(null=True,help_text=u'')
    raise_type = models.StringProperty(null=True,help_text=u'')
    payer = models.Relationship("Organization",null=True,rel_type='hasPayer',help_text=u'The Organization that actually pays the amount or contributes the asset considered.')
    personal_payer = models.Relationship("Person",null=True,rel_type='hasPersonalPayer',help_text=u'The Person that contributes the amount or the asset considered.')

    class Meta:
        pass

class Organization(Individual):
    description = u'An Organization represents a social entity that implements, funds, takes part in or helps a Project. It can be an NGO, a for-profit company or an international organization.'
    office_address = models.StringProperty(null=True,help_text=u'')
    image = models.URLProperty(null=True,help_text=u'')
    twitter_handle = models.StringProperty(null=True,help_text=u'')
    website_url = models.URLProperty(null=True,help_text=u'')
    founded = models.DateTimeProperty(null=True,help_text=u'')
    source = models.URLProperty(null=True,help_text=u'')
    address = models.StringProperty(null=True,help_text=u'')
    partner = models.Relationship("self",null=True,rel_type='hasPartner',help_text=u'An entity can have Partners, i.e. Organizations that help without making a financial contribution (if financial or substancial help is involved, use Fundraising Round instead).')
    adviser = models.Relationship("Person",null=True,rel_type='hasAdviser',help_text=u'The list of persons that help the entity.')
    litigation_against = models.Relationship("self",null=True,rel_type='hasLitigationAgainst',help_text=u'An entity is said to litigate against another when it is involved in a lawsuit or an out-of-court settlement with the other.')
    fundraising_round = models.Relationship("FundraisingRound",null=True,rel_type='hasFundraisingRound',help_text=u'A Fundraising Round represents an event when an Organization was able to raise cash or another asset.')
    board_member = models.Relationship("Person",null=True,rel_type='hasBoardMember',help_text=u'The list of board members of the Organization, if any.')
    revenue = models.Relationship("Revenue",null=True,rel_type='hasRevenue',help_text=u'A Revenue represents the quantity of cash that the Organization was able to gather in any given year. It doesn\'t have to be equal to the net sales but can take into account subsidies as well.')

    class Meta:
        verbose_name = u'Organization'
        verbose_name_plural = u'Organizations'

class Price(Amount):
    description = u''
    currency = models.StringProperty(null=True,help_text=u'')

    class Meta:
        pass

class Project(Individual):
    description = u''
    image = models.URLProperty(null=True,help_text=u'')
    started = models.DateTimeProperty(null=True,help_text=u'')
    source = models.URLProperty(null=True,help_text=u'')
    ended = models.DateTimeProperty(null=True,help_text=u'')
    twitter_handle = models.StringProperty(null=True,help_text=u'')
    comment = models.StringProperty(null=True,help_text=u'')
    partner = models.Relationship("Organization",null=True,rel_type='hasPartner',help_text=u'An entity can have Partners, i.e. Organizations that help without making a financial contribution (if financial or substancial help is involved, use Fundraising Round instead).')
    activity_in = models.Relationship("Country",null=True,rel_type='hasActivityIn',help_text=u'The list of countries or territories the entity is active in. ')
    owner = models.Relationship("Organization",null=True,rel_type='hasOwner',help_text=u'The formal Owner of the entity.')
    commentary = models.Relationship("Commentary",null=True,rel_type='hasCommentary',help_text=u'A Commentary is an article, a blog post or a report that assesses the quality of the Project.')

    class Meta:
        pass

class Commentary(Individual):
    description = u''
    article_url = models.URLProperty(null=True,help_text=u'')
    title = models.StringProperty(null=True,help_text=u'')
    year = models.DateTimeProperty(null=True,help_text=u'')
    author = models.Relationship("Person",null=True,rel_type='hasAuthor',help_text=u'The author or authors of the document.')

    class Meta:
        pass

class Distribution(Amount):
    description = u''
    sold = models.StringProperty(null=True,help_text=u'')
    activity_in = models.Relationship("Country",null=True,rel_type='hasActivityIn',help_text=u'The list of countries or territories the entity is active in. ')

    class Meta:
        pass

class EnergyProject(Project):
    description = u'An energy Project represents an endeavor to reach a particular aim (e.g. improve access to electricity, produce electricity in a certain way, improve energy efficiency, etc.). A project is the child of an Organization and takes its concrete form most often through Products.'
    product = models.Relationship("EnergyProduct",null=True,rel_type='hasProduct',help_text=u'A Product represents the concrete emanation of an energy Project. It can be a mass-produced device or a power plant.')

    class Meta:
        verbose_name = u'Energy project'
        verbose_name_plural = u'Energy projects'

class InternationalOrganization(Organization):
    description = u'An International Organization is a transnational body with links to governments, whose primary goal is usually not to turn in a profit. Examples of International Organizations include the World Bank, the United Nations and its agencies etc.'

    class Meta:
        verbose_name = u'International organization'
        verbose_name_plural = u'International organizations'

class Person(Individual):
    description = u'A Person represents a physical man or woman that is involved in an Organization, a Project or a Commentary.'
    image = models.URLProperty(null=True,help_text=u'')
    twitter_handle = models.StringProperty(null=True,help_text=u'')
    website_url = models.StringProperty(null=True,help_text=u'')
    source = models.URLProperty(null=True,help_text=u'')
    activity_in = models.Relationship("Organization",null=True,rel_type='hasActivityIn',help_text=u'The list of countries or territories the entity is active in. ')
    nationality = models.Relationship("Country",null=True,rel_type='hasNationality',help_text=u'The list of nationalities (as appear on his/her passport) of a Person.')
    previous_activity_in = models.Relationship("Organization",null=True,rel_type='hasPreviousActivityIn',help_text=u'Has the entity been active in a specific country or Organization previsously?')

    class Meta:
        verbose_name = u'Person'
        verbose_name_plural = u'Persons'

class Revenue(Amount):
    description = u''
    currency = models.StringProperty(null=True,help_text=u'')

    class Meta:
        pass

class Company(Organization):
    description = u'A Company is an Organization whose primary goal is to break even or make a profit. It can be a corporation, a limited liability company etc.'
    company_register_link = models.URLProperty(null=True,help_text=u'')
    company_type = models.StringProperty(null=True,help_text=u'')

    class Meta:
        verbose_name = u'Company'
        verbose_name_plural = u'Companies'

class GovernmentOrganization(Organization):
    description = u'A Government Organization is an emanation of a national or local government, such as an Administration, an Authority, a Ministry etc.'

    class Meta:
        verbose_name = u'Government Organization'
        verbose_name_plural = u'Government Organizations'

class Product(Individual):
    description = u''
    source = models.URLProperty(null=True,help_text=u'')
    image = models.URLProperty(null=True,help_text=u'')
    price = models.Relationship("Price",null=True,rel_type='hasPrice',help_text=u'The price (use only digits, i.e. 8.99) of the Product at the date considered.')

    class Meta:
        pass

class EnergyProduct(Product):
    description = u'An energy Product represents the concrete emanation of an energy Project. It can be a mass-produced device or a power plant.'
    power_generation_per_unit_in_watt = models.IntegerProperty(null=True,help_text=u'')
    distribution = models.Relationship("Distribution",null=True,rel_type='hasDistribution',help_text=u'A Distribution represents the batch sales or gift of a product. Companies often communicate in terms of "in year X, Y units of Product Z were sold/distributed in Country A".')
    operator = models.Relationship("Organization",null=True,rel_type='hasOperator',help_text=u'Products, especially large ones such as power plants, have an Operator, usually a company.')

    class Meta:
        verbose_name = u'Energy product'
        verbose_name_plural = u'Energy products'

class Ngo(Organization):
    description = u'A Non-Government Organization is a not-for-profit Organization that can be local or global in scope, usually aiming at fulfilling a goal (ex: Greenpeace, Local Energy Network) or managing an asset (ex: the Bill & Melinda Gates Foundation).'

    class Meta:
        verbose_name = u'NGO'
        verbose_name_plural = u'NGOs'