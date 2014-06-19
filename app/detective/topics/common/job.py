#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Detective.io
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU GENERAL PUBLIC LICENSE v3
# -----------------------------------------------------------------------------
# Creation : 20-Jan-2014
# Last mod : 20-Jan-2014
# -----------------------------------------------------------------------------
from tastypie.resources import Resource
from tastypie           import fields
from rq.job             import Job
import django_rq
import json

class Document(object):
    def __init__(self, *args, **kwargs):
        self._id = None
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        if hasattr(self,'meta') and self.meta:
            self.meta = json.dumps(self.meta)
        if hasattr(self,'_result') and self._result:
            self._result = json.dumps(self._result)

class JobResource(Resource):
    id         = fields.CharField(attribute="_id")
    result     = fields.CharField(attribute="_result"    , null=True)
    meta       = fields.CharField(attribute="meta"       , null=True)
    status     = fields.CharField(attribute="_status"    , null=True)
    created_at = fields.CharField(attribute="created_at" , null=True)
    timeout    = fields.CharField(attribute="timeout"    , null=True)
    exc_info   = fields.CharField(attribute="exc_info"   , null=True)

    def obj_get(self, bundle, **kwargs):
        """
        Returns redis document from provided id.
        """
        queue = django_rq.get_queue('default')
        job = Job.fetch(kwargs['pk'], connection=queue.connection)
        return Document(**job.__dict__)

    def obj_update(self, bundle, **kwargs):
        queue = django_rq.get_queue('default')
        job = Job.fetch(kwargs['pk'], connection=queue.connection)
        if "email" in bundle.data:
            job.meta["email"] = bundle.data["email"]
            job.save()

    class Meta:
        resource_name          = "jobs"
        include_resource_uri   = False
        list_allowed_methods   = []
        detail_allowed_methods = ["get", "put"]

# EOF
