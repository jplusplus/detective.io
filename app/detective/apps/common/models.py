# -*- coding: utf-8 -*-
# The ontology can be found in its entirety at http://www.semanticweb.org/nkb/ontologies/2013/6/impact-investment#
from neo4django.db import models
from neo4django.graph_auth.models import User

class Country(models.NodeModel):
	_description = u''
	_status = models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
	_author = models.IntArrayProperty(null=True, help_text=u'People that edited this entity.', verbose_name=u'author')
	name = models.StringProperty(null=True,help_text=u'')
	isoa3 = models.StringProperty(null=True,help_text=u'The 3-letter ISO code for the country or territory (e.g. FRA for France, DEU for Germany etc.)',verbose_name=u'ISO alpha-3 code')

	class Meta:
		verbose_name = u'Country'
		verbose_name_plural = u'Countries'

	def __unicode__(self):
		return self.name or u"Unkown"