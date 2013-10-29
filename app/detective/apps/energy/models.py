# -*- coding: utf-8 -*-
# The ontology can be found in its entirety at http://www.semanticweb.org/nkb/ontologies/2013/6/impact-investment#
from neo4django.db import models
from neo4django.graph_auth.models import User
from app.detective.apps.common.models import Country


class Amount(models.NodeModel):
	_scope = u'energy'
	_description = u''
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	year = models.DateTimeProperty(null=True,help_text=u'',verbose_name=u'Year')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	units = models.IntegerProperty(null=True,help_text=u'The value of the amount.',verbose_name=u'Value')
	_author = models.Relationship(User,null=True,rel_type='amount_amount_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')

	class Meta:
		pass

class FundraisingRound(models.NodeModel):	
	_scope = u'energy'
	_parent = u'Amount'
	_description = u''
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	currency = models.StringProperty(null=True,help_text=u'The currency of the amount, using its 3-letter ISO-4217 code, e.g. USD, EUR, GBP etc.',verbose_name=u'Currency')
	raise_type = models.StringProperty(null=True,help_text=u'Type of the transaction, e.g. equity contribution (cash), preproject expenses, loan.',verbose_name=u'Type of transaction')
	year = models.DateTimeProperty(null=True,help_text=u'',verbose_name=u'Year')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	units = models.IntegerProperty(null=True,help_text=u'The value of the amount.',verbose_name=u'Value')
	_author = models.Relationship(User,null=True,rel_type='fundraising_round_fundraising_round_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')
	payer = models.Relationship("Organization",null=True,rel_type='fundraising_round_has_payer+',help_text=u'The Organization that actually pays the amount or contributes the asset considered.',verbose_name=u'Payer')
	personal_payer = models.Relationship("Person",null=True,rel_type='fundraising_round_has_personal_payer+',help_text=u'The Person that contributes the amount or the asset considered.',verbose_name=u'Physical payer')

	class Meta:
		pass

class Person(models.NodeModel):
	_scope = u'energy'
	_description = u'A Person represents a physical man or woman that is involved in an Organization, a Project or a Commentary.'
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	position = models.StringProperty(null=True,help_text=u'Current position within the Organization (e.g. CEO, CFO, spokesperson etc.)',verbose_name=u'Position')
	twitter_handle = models.StringProperty(null=True,help_text=u'The Twitter name of the entity (without the @)',verbose_name=u'Twitter handle')
	name = models.StringProperty(null=True,help_text=u'')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	website_url = models.StringProperty(null=True,help_text=u'',verbose_name=u'Website URL')
	image = models.URLProperty(null=True,help_text=u'The URL (starting with http://) where the image is hosted.',verbose_name=u'Image URL')
	_author = models.Relationship(User,null=True,rel_type='person_person_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')
	previous_activity_in_organization = models.Relationship("Organization",null=True,rel_type='person_has_previous_activity_in_organization+',help_text=u'Has the entity been active in a specific Organization previsously?',verbose_name=u'Previous activity in')
	nationality = models.Relationship(Country,null=True,rel_type='person_has_nationality+',help_text=u'The list of nationalities (as appear on his/her passport) of a Person.',verbose_name=u'Nationality')
	activity_in_organization = models.Relationship("Organization",null=True,rel_type='person_has_activity_in_organization+',help_text=u'The Organization(s) this Person is active in.',verbose_name=u'Activity in Organizations')

	class Meta:
		verbose_name = u'Person'
		verbose_name_plural = u'Persons'

	def __unicode__(self):
		return self.name or u"Unkown"

class Revenue(models.NodeModel):
	_scope = u'energy'
	_parent = u'Amount'
	_description = u''
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	currency = models.StringProperty(null=True,help_text=u'The currency of the amount, using its 3-letter ISO-4217 code, e.g. USD, EUR, GBP etc.',verbose_name=u'Currency')
	year = models.DateTimeProperty(null=True,help_text=u'',verbose_name=u'Year')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	units = models.IntegerProperty(null=True,help_text=u'The value of the amount.',verbose_name=u'Value')
	_author = models.Relationship(User,null=True,rel_type='revenue_revenue_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')

	class Meta:
		pass

class Commentary(models.NodeModel):
	_scope = u'energy'
	_description = u''
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	year = models.DateTimeProperty(null=True,help_text=u'',verbose_name=u'Year')
	article_url = models.URLProperty(null=True,help_text=u'The URL (starting with http://) of the link.')
	title = models.StringProperty(null=True,help_text=u'Title of the article or report of this commentary.',verbose_name=u'Title')
	_author = models.Relationship(User,null=True,rel_type='commentary_commentary_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')
	author = models.Relationship("Person",null=True,rel_type='commentary_has_author+',help_text=u'The author or authors of the document.',verbose_name=u'Author')

	class Meta:
		pass

class Organization(models.NodeModel):
	_scope = u'energy'
	_description = u'An Organization represents a social entity that implements, funds, takes part in or helps a Project. It can be an NGO, a university, a governement organization, a for-profit company or an international organization.'
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	founded = models.DateTimeProperty(null=True,help_text=u'The date when the organization was created.',verbose_name=u'Date founded')
	company_type = models.StringProperty(null=True,help_text=u'If the organization is a company, type of company (e.g. limited liability company, public corporation, unlimited company etc.)',verbose_name=u'Company type')
	company_register_link = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to the official company register where the organization is registered.',verbose_name=u'Company register link')
	twitter_handle = models.StringProperty(null=True,help_text=u'The Twitter name of the entity (without the @)',verbose_name=u'Twitter handle')
	website_url = models.URLProperty(null=True,help_text=u'',verbose_name=u'Website URL')
	name = models.StringProperty(null=True,help_text=u'')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	address = models.StringProperty(null=True,help_text=u'The official address of the organization.',verbose_name=u'Address')
	organization_type = models.StringProperty(null=True,help_text=u'Type of organization. Can be Company, Government Organization, International Organization, University or NGO',verbose_name=u'Organization type')
	image = models.URLProperty(null=True,help_text=u'The URL (starting with http://) where the image is hosted.',verbose_name=u'Image URL')
	office_address = models.StringProperty(null=True,help_text=u'The address or addresses where this organization does business. Do add the country at the end of the address, e.g. Grimmstraße 10A, 10967 Berlin, Germany.',verbose_name=u'Office address')
	_author = models.Relationship(User,null=True,rel_type='organization_organization_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')
	adviser = models.Relationship("Person",null=True,rel_type='organization_has_adviser+',help_text=u'The list of persons that help the entity.',verbose_name=u'Adviser')
	revenue = models.Relationship("Revenue",null=True,rel_type='organization_has_revenue+',help_text=u'A Revenue represents the quantity of cash that the Organization was able to gather in any given year. It doesn\'t have to be equal to the net sales but can take into account subsidies as well.',verbose_name=u'Revenue')
	board_member = models.Relationship("Person",null=True,rel_type='organization_has_board_member+',help_text=u'The list of board members of the Organization, if any.',verbose_name=u'Board member')
	partner = models.Relationship("self",null=True,rel_type='organization_has_partner+',help_text=u'An entity can have Partners, i.e. Organizations that help without making a financial contribution (if financial or substancial help is involved, use Fundraising Round instead).',verbose_name=u'Partner')
	key_person = models.Relationship("Person",null=True,rel_type='organization_has_key_person+',help_text=u'A Key Person is an executive-level individual within an Organization, such as a CEO, CFO, spokesperson etc.',verbose_name=u'Key Person')
	litigation_against = models.Relationship("self",null=True,rel_type='organization_has_litigation_against+',help_text=u'An entity is said to litigate against another when it is involved in a lawsuit or an out-of-court settlement with the other.',verbose_name=u'Litigation against')
	fundraising_round = models.Relationship("FundraisingRound",null=True,rel_type='organization_has_fundraising_round+',help_text=u'A Fundraising Round represents an event when an Organization was able to raise cash or another asset.',verbose_name=u'Fundraising round')
	monitoring_body = models.Relationship("self",null=True,rel_type='organization_has_monitoring_body+',help_text=u'The Monitoring Body is the organization that is responsible for overseeing the project. In the case of electricity projects, it is often the national electricity regulator.',verbose_name=u'Monitoring body')

	class Meta:
		verbose_name = u'Organization'
		verbose_name_plural = u'Organizations'

	def __unicode__(self):
		return self.name or u"Unkown"


class Distribution(models.NodeModel):
	_scope = u'energy'
	_parent = u'Amount'
	_description = u''
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	sold = models.StringProperty(null=True,help_text=u'The type of distribution can be donated, sold, loaned.',verbose_name=u'Type of distribution')
	year = models.DateTimeProperty(null=True,help_text=u'',verbose_name=u'Year')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	units = models.IntegerProperty(null=True,help_text=u'The value of the amount.',verbose_name=u'Value')
	_author = models.Relationship(User,null=True,rel_type='distribution_distribution_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')
	activity_in_country = models.Relationship(Country,null=True,rel_type='distribution_has_activity_in_country+',help_text=u'The list of countries or territories the entity is active in. ',verbose_name=u'Active in countries')

	class Meta:
		pass

class Price(models.NodeModel):
	_scope = u'energy'
	_parent = u'Amount'
	_description = u''
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	currency = models.StringProperty(null=True,help_text=u'The currency of the amount, using its 3-letter ISO-4217 code, e.g. USD, EUR, GBP etc.',verbose_name=u'Currency')
	year = models.DateTimeProperty(null=True,help_text=u'',verbose_name=u'Year')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	units = models.IntegerProperty(null=True,help_text=u'The value of the amount.',verbose_name=u'Value')
	_author = models.Relationship(User,null=True,rel_type='price_price_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')

	class Meta:
		pass


class EnergyProduct(models.NodeModel):
	_scope = u'energy'
	_description = u'An energy Product represents the concrete emanation of an energy Project. It can be a mass-produced device or a power plant.'
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	power_generation_per_unit_in_watt = models.IntegerProperty(null=True,help_text=u'The amount of energy, in watts, that can be generated by each unit of the product.',verbose_name=u'Power generation per unit (in watts)')
	households_served = models.IntegerProperty(null=True,help_text=u'The number of households that can use the product. E.g. an oven is for 1 household, a lamp is for 0.25 households, a power plant is for (power / average household consumption in the region) households. Leave blank if you\'re unsure.',verbose_name=u'Households served')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	name = models.StringProperty(null=True,help_text=u'')
	image = models.URLProperty(null=True,help_text=u'The URL (starting with http://) where the image is hosted.',verbose_name=u'Image URL')
	_author = models.Relationship(User,null=True,rel_type='energy_product_energy_product_has_admin_author+',help_text=u'People that edited this entity.',verbose_name=u'author')
	distribution = models.Relationship("Distribution",null=True,rel_type='energy_product_has_distribution+',help_text=u'A Distribution represents the batch sales or gift of a product. Companies often communicate in terms of "in year X, Y units of Product Z were sold/distributed in Country A".',verbose_name=u'Distribution')
	operator = models.Relationship("Organization",null=True,rel_type='energy_product_has_operator+',help_text=u'Products, especially large ones such as power plants, have an Operator, usually a company.',verbose_name=u'Operator')
	price = models.Relationship("Price",null=True,rel_type='energy_product_has_price+',help_text=u'The price (use only digits, i.e. 8.99) of the Product at the date considered.',verbose_name=u'Price')

	class Meta: 
		verbose_name = u'Energy product'
		verbose_name_plural = u'Energy products'

	def __unicode__(self):
		return self.name or u"Unkown"


class EnergyProject(models.NodeModel):
	_scope = u'energy'
	_description = u'An energy Project represents an endeavor to reach a particular aim (e.g. improve access to electricity, produce electricity in a certain way, improve energy efficiency, etc.). A project is the child of an Organization and takes its concrete form most often through Products.'
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	source = models.URLProperty(null=True,help_text=u'The URL (starting with http://) to your source. If the source is a book, enter the URL to the book at Google Books or Amazon.',verbose_name=u'Source')
	twitter_handle = models.StringProperty(null=True,help_text=u'The Twitter name of the entity (without the @)',verbose_name=u'Twitter handle')
	ended = models.DateTimeProperty(null=True,help_text=u'The date when the project or organization ended.',verbose_name=u'End date')
	started = models.DateTimeProperty(null=True,help_text=u'Date when the project was started. Can be anterior to the date when the parent organization was created.',verbose_name=u'Start date')
	comment = models.StringProperty(null=True,help_text=u'Enter a short comment to the entity you are reporting on (max. 500 characters).',verbose_name=u'Comment')
	image = models.URLProperty(null=True,help_text=u'The URL (starting with http://) where the image is hosted.',verbose_name=u'Image URL')
	name = models.StringProperty(null=True,help_text=u'')
	_author = models.Relationship(User,null=True,rel_type='energy_project_energy_project_has_admin_author+',help_text=u'People that edited this entity.')
	product = models.Relationship("EnergyProduct",null=True,rel_type='energy_project_has_product+',help_text=u'A Product represents the concrete emanation of an energy Project. It can be a mass-produced device or a power plant.')
	partner = models.Relationship("Organization",null=True,rel_type='energy_project_has_partner+',help_text=u'An entity can have Partners, i.e. Organizations that help without making a financial contribution (if financial or substancial help is involved, use Fundraising Round instead).')
	commentary = models.Relationship("Commentary",null=True,rel_type='energy_project_has_commentary+',help_text=u'A Commentary is an article, a blog post or a report that assesses the quality of the Project.')
	activity_in_country = models.Relationship(Country,null=True,rel_type='energy_project_has_activity_in_country+',help_text=u'The list of countries or territories the entity is active in. ')
	owner = models.Relationship("Organization",null=True,rel_type='energy_project_has_owner+',help_text=u'The formal Owner of the entity.')

	class Meta:
		verbose_name = u'Energy project'
		verbose_name_plural = u'Energy projects'

	def __unicode__(self):
		return self.name or u"Unkown"

