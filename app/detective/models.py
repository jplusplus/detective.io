from neo4django.db          import models
from neo4django.auth.models import User

# from app.detective import fields
# The ontology can be found in its entirety at http://www.semanticweb.org/nkb/ontologies/2013/6/impact-investment#

class Individual(models.NodeModel):
    __status    = models.IntegerProperty(default=0)
    __author    = models.Relationship(User, rel_type='hasCreated')
    description = "" # Individual description provided by OWL file

    class Meta:
        abstract = True

class Amount(Individual):
    source = models.URLProperty(null=True)
    value = models.IntegerProperty(null=True)
    year = models.DateTimeProperty(null=True)

class Country(Individual):
    pass

class FundraisingRound(Amount):
    currency = models.StringProperty(null=True)
    raiseType = models.StringProperty(null=True)
    personalpayer = models.Relationship("Person",rel_type='hasPersonalPayer', null=True)
    payer = models.Relationship("Organization",rel_type='hasPayer', null=True)

class Organization(Individual):
    officeAddress = models.StringProperty(null=True)
    websiteUrl = models.URLProperty(null=True)
    address = models.StringProperty(null=True)
    name = models.StringProperty()
    image = models.URLProperty(null=True)
    source = models.URLProperty(null=True)
    twitterHandle = models.StringProperty(null=True)
    founded = models.DateTimeProperty(null=True)
    boardmember = models.Relationship("Person",rel_type='hasBoardMember', null=True)
    revenue = models.Relationship("Revenue",rel_type='hasRevenue', null=True)
    adviser = models.Relationship("Person",rel_type='hasAdviser', null=True)
    fundraisinground = models.Relationship("FundraisingRound",rel_type='hasFundraisingRound', null=True)
    partner = models.Relationship("self",rel_type='hasPartner', null=True)
    sponsor = models.Relationship("self",rel_type='hasSponsor', null=True)

    def __unicode__(self):
        return self.name

class Price(Amount):
    currency = models.StringProperty(null=True)

class Project(Individual):
    name = models.StringProperty()
    source = models.URLProperty(null=True)
    image = models.URLProperty(null=True)
    started = models.DateTimeProperty(null=True, blank=True)
    comment = models.StringProperty(null=True)
    ended = models.DateTimeProperty(null=True, blank=True)
    twitterHandle = models.StringProperty(verbose_name="Twitter Handle", null=True)
    activityin = models.Relationship("Country",rel_type='hasActivityIn', null=True)
    owner = models.Relationship("Organization",rel_type='hasOwner', null=True)
    commentary = models.Relationship("Commentary",rel_type='hasCommentary', null=True)
    partner = models.Relationship("Organization",rel_type='hasPartner', null=True)
    def __unicode__(self):
        return self.name

class Commentary(Individual):
    year = models.DateTimeProperty(null=True)
    articleUrl = models.URLProperty(null=True)
    title = models.StringProperty(null=True)
    author = models.Relationship("Person",rel_type='hasAuthor', null=True)

class Distribution(Amount):
    sold = models.StringProperty(null=True)

class EnergyProject(Project):
    product = models.Relationship("EnergyProduct",rel_type='hasProduct', null=True)

class InternationalOrganization(Organization):
    pass

class Person(Individual):
    name = models.StringProperty()
    source = models.URLProperty(null=True)
    websiteUrl = models.StringProperty(null=True)
    twitterHandle = models.StringProperty(null=True)
    image = models.URLProperty(null=True)
    hasActivityIn = models.Relationship("Organization",rel_type='hasActivityIn', null=True)
    nationality = models.Relationship("Country",rel_type='hasNationality', null=True)
    previousactivityin = models.Relationship("Organization",rel_type='hasPreviousActivityIn', null=True)
    def __unicode__(self):
        return self.name

class Revenue(Amount):
    currency = models.StringProperty(null=True)

class Company(Organization):
    companyType = models.StringProperty(null=True)
    companyRegisterLink = models.URLProperty(null=True)

class Fund(Organization):
    pass

class Product(Individual):
    name = models.StringProperty()
    source = models.URLProperty(null=True)
    image = models.URLProperty(null=True)
    price = models.Relationship("Price",rel_type='hasPrice', null=True)

class EnergyProduct(Product):
    powerGenerationPerUnitInWatt = models.IntegerProperty(null=True)
    distribution = models.Relationship("Distribution",rel_type='hasDistribution', null=True)
    operator = models.Relationship("Organization",rel_type='hasOperator', null=True)

class Ngo(Organization):
    pass
