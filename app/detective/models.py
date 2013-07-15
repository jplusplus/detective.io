from django.db import models
from neo4django.db import models

# The ontology can be found in its entirety at http://www.semanticweb.org/nkb/ontologies/2013/6/impact-investment#

class Amount(models.NodeModel):
	year = models.DateTimeProperty()
	value = models.IntegerProperty()

class Distribution(Amount):
	pass

class Price(Amount):
	pass

class Revenue(Amount):
	pass

class Fundraising_round(Amount):
	pass

class Organization(models.NodeModel):
	pass

class Company(Organization):
	pass

class Fund(Organization):
	pass
	
class NGO(Organization):
	pass


class Product(models.NodeModel):
	pass

class Energy_product(Product):
	pass

class Project(models.NodeModel):
	pass

class Energy_project(Project):
	pass

class International_Organization(Organization):
	pass

class Country(models.NodeModel):
	pass

class Person(models.NodeModel):
	pass

class Commentary(models.NodeModel):
	author = models.Relationship(Person, rel_type='hasAuthor')
