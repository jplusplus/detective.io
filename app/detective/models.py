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
    source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
    units = models.IntegerProperty(null=True,help_text=u'The value of the amount.',verbose_name=u'Value')
    year = models.DateTimeProperty(null=True,help_text=u'',verbose_name=u'Year')

    class Meta:
        pass

class Country(Individual):
    description = u''
    isoa3 = models.StringProperty(null=True,help_text=u'The 3-letter ISO code for the country or territory (e.g. FRA for France, DEU for Germany etc.)',verbose_name=u'ISO alpha-3 code')

    class Meta:
        verbose_name = u'Country'
        verbose_name_plural = u'Countries'

class FundraisingRound(Amount):
    description = u''
    currency = models.StringProperty(null=True,help_text=u'The currency of the amount, using its 3-letter ISO-4217 code, e.g. USD, EUR, GBP etc.',verbose_name=u'Currency')
    raise_type = models.StringProperty(null=True,help_text=u'Type of the transaction, e.g. equity contribution (cash), preproject expenses, loan.',verbose_name=u'Type of transaction')
    payer = models.Relationship("Organization",null=True,rel_type='hasPayer',help_text=u'The Organization that actually pays the amount or contributes the asset considered.',verbose_name=u'Payer')
    personal_payer = models.Relationship("Person",null=True,rel_type='hasPersonalPayer',help_text=u'The Person that contributes the amount or the asset considered.',verbose_name=u'Physical payer')

    class Meta:
        pass

class Organization(Individual):
    description = u'An Organization represents a social entity that implements, funds, takes part in or helps a Project. It can be an NGO, a for-profit company or an international organization.'
    office_address = models.StringProperty(null=True,help_text=u'The address or addresses where this organization does business. Do add the country at the end of the address, e.g. Grimmstraße 10A, 10967 Berlin, Germany.',verbose_name=u'Office address')
    image = models.URLProperty(null=True,help_text=u'The URL (starting with http://) where the image is hosted.',verbose_name=u'Image URL')
    twitter_handle = models.StringProperty(null=True,help_text=u'The Twitter name of the entity (without the @)',verbose_name=u'Twitter handle')
    website_url = models.URLProperty(null=True,help_text=u'',verbose_name=u'Website URL')
    founded = models.DateTimeProperty(null=True,help_text=u'The date when the organization was created.',verbose_name=u'Date founded')
    source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
    address = models.StringProperty(null=True,help_text=u'The official address of the organization.',verbose_name=u'Address')
    partner = models.Relationship("self",null=True,rel_type='hasPartner',help_text=u'An entity can have Partners, i.e. Organizations that help without making a financial contribution (if financial or substancial help is involved, use Fundraising Round instead).',verbose_name=u'Partner')
    adviser = models.Relationship("Person",null=True,rel_type='hasAdviser',help_text=u'The list of persons that help the entity.',verbose_name=u'Adviser')
    litigation_against = models.Relationship("self",null=True,rel_type='hasLitigationAgainst',help_text=u'An entity is said to litigate against another when it is involved in a lawsuit or an out-of-court settlement with the other.',verbose_name=u'Litigation against')
    fundraising_round = models.Relationship("FundraisingRound",null=True,rel_type='hasFundraisingRound',help_text=u'A Fundraising Round represents an event when an Organization was able to raise cash or another asset.',verbose_name=u'Fundraising round')
    board_member = models.Relationship("Person",null=True,rel_type='hasBoardMember',help_text=u'The list of board members of the Organization, if any.',verbose_name=u'Board member')
    revenue = models.Relationship("Revenue",null=True,rel_type='hasRevenue',help_text=u'A Revenue represents the quantity of cash that the Organization was able to gather in any given year. It doesn\'t have to be equal to the net sales but can take into account subsidies as well.',verbose_name=u'Revenue')

    class Meta:
        verbose_name = u'Organization'
        verbose_name_plural = u'Organizations'

class Price(Amount):
    description = u''
    currency = models.StringProperty(null=True,help_text=u'The currency of the amount, using its 3-letter ISO-4217 code, e.g. USD, EUR, GBP etc.',verbose_name=u'Currency')

    class Meta:
        pass

class Project(Individual):
    description = u''
    image = models.URLProperty(null=True,help_text=u'The URL (starting with http://) where the image is hosted.',verbose_name=u'Image URL')
    started = models.DateTimeProperty(null=True,help_text=u'Date when the project was started. Can be anterior to the date when the parent organization was created.',verbose_name=u'Start date')
    source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
    ended = models.DateTimeProperty(null=True,help_text=u'The date when the project or organization ended.',verbose_name=u'End date')
    twitter_handle = models.StringProperty(null=True,help_text=u'The Twitter name of the entity (without the @)',verbose_name=u'Twitter handle')
    comment = models.StringProperty(null=True,help_text=u'Enter a short comment to the entity you are reporting on (max. 500 characters).',verbose_name=u'Comment')
    partner = models.Relationship("Organization",null=True,rel_type='hasPartner',help_text=u'An entity can have Partners, i.e. Organizations that help without making a financial contribution (if financial or substancial help is involved, use Fundraising Round instead).',verbose_name=u'Partner')
    activity_in = models.Relationship("Country",null=True,rel_type='hasActivityIn',help_text=u'The list of countries or territories the entity is active in. ',verbose_name=u'Active in')
    owner = models.Relationship("Organization",null=True,rel_type='hasOwner',help_text=u'The formal Owner of the entity.',verbose_name=u'Owner')
    commentary = models.Relationship("Commentary",null=True,rel_type='hasCommentary',help_text=u'A Commentary is an article, a blog post or a report that assesses the quality of the Project.',verbose_name=u'Commentary')

    class Meta:
        pass

class Commentary(Individual):
    description = u''
    article_url = models.URLProperty(null=True,help_text=u'The URL (starting with http://) of the link.')
    title = models.StringProperty(null=True,help_text=u'Title of the article or report of this commentary.',verbose_name=u'Title')
    year = models.DateTimeProperty(null=True,help_text=u'',verbose_name=u'Year')
    author = models.Relationship("Person",null=True,rel_type='hasAuthor',help_text=u'The author or authors of the document.',verbose_name=u'Author')

    class Meta:
        pass

class Distribution(Amount):
    description = u''
    sold = models.StringProperty(null=True,help_text=u'The type of distribution can be donated, sold, loaned.',verbose_name=u'Type of distribution')
    activity_in = models.Relationship("Country",null=True,rel_type='hasActivityIn',help_text=u'The list of countries or territories the entity is active in. ',verbose_name=u'Active in')

    class Meta:
        pass

class EnergyProject(Project):
    scope = u'energy'
    description = u'An energy Project represents an endeavor to reach a particular aim (e.g. improve access to electricity, produce electricity in a certain way, improve energy efficiency, etc.). A project is the child of an Organization and takes its concrete form most often through Products.'
    product = models.Relationship("EnergyProduct",null=True,rel_type='hasProduct',help_text=u'A Product represents the concrete emanation of an energy Project. It can be a mass-produced device or a power plant.',verbose_name=u'Product')

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
    image = models.URLProperty(null=True,help_text=u'The URL (starting with http://) where the image is hosted.',verbose_name=u'Image URL')
    twitter_handle = models.StringProperty(null=True,help_text=u'The Twitter name of the entity (without the @)',verbose_name=u'Twitter handle')
    website_url = models.StringProperty(null=True,help_text=u'',verbose_name=u'Website URL')
    source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
    activity_in = models.Relationship("Organization",null=True,rel_type='hasActivityIn',help_text=u'The list of countries or territories the entity is active in. ',verbose_name=u'Active in')
    nationality = models.Relationship("Country",null=True,rel_type='hasNationality',help_text=u'The list of nationalities (as appear on his/her passport) of a Person.',verbose_name=u'Nationality')
    previous_activity_in = models.Relationship("Organization",null=True,rel_type='hasPreviousActivityIn',help_text=u'Has the entity been active in a specific country or Organization previsously?',verbose_name=u'Previous activity in')

    class Meta:
        verbose_name = u'Person'
        verbose_name_plural = u'Persons'

class Revenue(Amount):
    description = u''
    currency = models.StringProperty(null=True,help_text=u'The currency of the amount, using its 3-letter ISO-4217 code, e.g. USD, EUR, GBP etc.',verbose_name=u'Currency')

    class Meta:
        pass

class Company(Organization):
    description = u'A Company is an Organization whose primary goal is to break even or make a profit. It can be a corporation, a limited liability company etc.'
    company_register_link = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to the official company register where the organization is registered.',verbose_name=u'Company register link')
    company_type = models.StringProperty(null=True,help_text=u'Type of company (e.g. limited liability company, public corporation, unlimited company etc.)',verbose_name=u'Company type')

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
    source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
    image = models.URLProperty(null=True,help_text=u'The URL (starting with http://) where the image is hosted.',verbose_name=u'Image URL')
    price = models.Relationship("Price",null=True,rel_type='hasPrice',help_text=u'The price (use only digits, i.e. 8.99) of the Product at the date considered.',verbose_name=u'Price')

    class Meta:
        pass

class EnergyProduct(Product):
    scope = u'energy'
    description = u'An energy Product represents the concrete emanation of an energy Project. It can be a mass-produced device or a power plant.'
    power_generation_per_unit_in_watt = models.IntegerProperty(null=True,help_text=u'The amount of energy, in watts, that can be generated by each unit of the product.',verbose_name=u'Power generation per unit (in watts)')
    distribution = models.Relationship("Distribution",null=True,rel_type='hasDistribution',help_text=u'A Distribution represents the batch sales or gift of a product. Companies often communicate in terms of "in year X, Y units of Product Z were sold/distributed in Country A".',verbose_name=u'Distribution')
    operator = models.Relationship("Organization",null=True,rel_type='hasOperator',help_text=u'Products, especially large ones such as power plants, have an Operator, usually a company.',verbose_name=u'Operator')

    class Meta:
        verbose_name = u'Energy product'
        verbose_name_plural = u'Energy products'

class Ngo(Organization):
    description = u'A Non-Government Organization is a not-for-profit Organization that can be local or global in scope, usually aiming at fulfilling a goal (ex: Greenpeace, Local Energy Network) or managing an asset (ex: the Bill & Melinda Gates Foundation).'

    class Meta:
        verbose_name = u'NGO'
        verbose_name_plural = u'NGOs'