# -*- coding: utf-8 -*-
from neo4django.db import models

class FieldSource(models.NodeModel):
    # binding to entity
    individual = models.IntegerProperty()
    # actual source value
    reference  = models.StringProperty()
    field      = models.StringProperty()

    class Meta:
        verbose_name = u'Source'
        verbose_name_plural = u'Sources'

    def __unicode__(self):
        return self.reference or "Unkown"
