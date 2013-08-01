from neo4django.db import models
# from app.detective import fields
# The ontology can be found in its entirety at http://www.semanticweb.org/nkb/ontologies/2013/6/impact-investment#

class Amount(models.NodeModel):
	source = models.URLProperty()
	value = models.IntegerProperty()
	year = models.DateTimeProperty()

class Country(models.NodeModel):
	pass

class FundraisingRound(Amount):
	currency = models.StringProperty()
	raiseType = models.StringProperty()
	personalpayer = models.Relationship("Person",rel_type='hasPersonalPayer')
	payer = models.Relationship("Organization",rel_type='hasPayer')

class Organization(models.NodeModel):
	officeAddress = models.StringProperty()
	websiteUrl = models.URLProperty()
	address = models.StringProperty()
	name = models.StringProperty()
	image = models.URLProperty()
	source = models.URLProperty()
	twitterHandle = models.StringProperty()
	founded = models.DateTimeProperty()
	boardmember = models.Relationship("Person",rel_type='hasBoardMember')
	revenue = models.Relationship("Revenue",rel_type='hasRevenue')
	adviser = models.Relationship("Person",rel_type='hasAdviser')
	fundraisinground = models.Relationship("FundraisingRound",rel_type='hasFundraisingRound')
	partner = models.Relationship("self",rel_type='hasPartner')
	sponsor = models.Relationship("self",rel_type='hasSponsor')
	def __unicode__(self):
		return self.name

class Price(Amount):
	currency = models.StringProperty()

class Project(models.NodeModel):
	name = models.StringProperty()
	source = models.URLProperty()
	image = models.URLProperty()
	started = models.DateTimeProperty()
	comment = models.StringProperty()
	ended = models.DateTimeProperty()
	twitterHandle = models.StringProperty(verbose_name="Twitter Handle")
	activityin = models.Relationship("Country",rel_type='hasActivityIn')
	owner = models.Relationship("Organization",rel_type='hasOwner')
	commentary = models.Relationship("Commentary",rel_type='hasCommentary')
	partner = models.Relationship("Organization",rel_type='hasPartner', help_text="COUCU")
	def __unicode__(self):
		return self.name

class Commentary(models.NodeModel):
	year = models.DateTimeProperty()
	articleUrl = models.URLProperty()
	title = models.StringProperty()
	author = models.Relationship("Person",rel_type='hasAuthor')

class Distribution(Amount):
	sold = models.StringProperty()

class EnergyProject(Project):
	product = models.Relationship("EnergyProduct",rel_type='hasProduct')

class InternationalOrganization(Organization):
	pass

class Person(models.NodeModel):
	name = models.StringProperty()
	source = models.URLProperty()
	websiteUrl = models.StringProperty()
	twitterHandle = models.StringProperty()
	image = models.URLProperty()
	hasActivityIn = models.Relationship("Organization",rel_type='hasActivityIn')
	nationality = models.Relationship("Country",rel_type='hasNationality')
	previousactivityin = models.Relationship("Organization",rel_type='hasPreviousActivityIn')
	def __unicode__(self):
		return self.name

class Revenue(Amount):
	currency = models.StringProperty()

class Company(Organization):
	companyType = models.StringProperty()
	companyRegisterLink = models.URLProperty()

class Fund(Organization):
	pass

class Product(models.NodeModel):
	name = models.StringProperty()
	source = models.URLProperty()
	image = models.URLProperty()
	price = models.Relationship("Price",rel_type='hasPrice')

class EnergyProduct(Product):
	powerGenerationPerUnitInWatt = models.IntegerProperty()
	distribution = models.Relationship("Distribution",rel_type='hasDistribution')
	operator = models.Relationship("Organization",rel_type='hasOperator')

class Ngo(Organization):
	pass
