# -*- coding: utf-8 -*-
from neo4django.db import models

class FieldSource(models.NodeModel):
    url        = models.URLProperty()
    individual = models.IntegerProperty()
    field      = models.StringProperty()

    class Meta:
        verbose_name = u'Source'
        verbose_name_plural = u'Sources'

    def __unicode__(self):
        return self.url or u"Unkown"
