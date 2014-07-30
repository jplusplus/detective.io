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
# Last mod : 30-Jul-2014
# -----------------------------------------------------------------------------
from tastypie.resources         import Resource
from tastypie                   import fields
from rq.job                     import Job
from django.contrib.auth.models import User
from rq                         import get_current_job
from django.utils.timezone      import utc
from django.conf                import settings
import app.detective.utils      as utils
import django_rq
import json
import time
import datetime
import logging
import re

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
#
#    JOBS - BULK UPLOAD
#
# -----------------------------------------------------------------------------
def process_bulk_parsing_and_save_as_model(topic, files):
    """
    Job which parses uploaded content, validates and saves them as model
    """

    start_time               = time.time()
    entities                 = {}
    relations                = []
    errors                   = []
    id_mapping               = {}
    nb_lines                 = 0
    file_reading_progression = 0
    job                      = get_current_job()

    # Define Exceptions
    class Error (Exception):
        """
        Generic Custom Exception for this endpoint.
        Include the topic.
        """
        def __init__(self, **kwargs):
            """ set the topic and add all the parameters as attributes """
            self.topic = topic.title
            for key, value in kwargs.items():
                setattr(self, key, value)
        def __str__(self):
            return self.__dict__

    class WarningCastingValueFail     (Error): pass
    class WarningValidationError      (Error): pass
    class WarningKeyUnknown           (Error): pass
    class WarningInformationIsMissing (Error): pass
    class AttributeDoesntExist        (Error): pass
    class WrongCSVSyntax              (Error): pass
    class ColumnUnknow                (Error): pass
    class ModelDoesntExist            (Error): pass
    class RelationDoesntExist         (Error): pass

    try:
        assert type(files) in (tuple, list)
        assert len(files) > 0, "You need to upload at least one file."
        assert type(files[0]) in (tuple, list)
        assert len(files[0]) == 2

        # retrieve all models in current topic
        all_models = dict((model.__name__, model) for model in topic.get_models())
        # iterate over all files and dissociate entities .csv from relations .csv
        for file in files:
            if type(file) is tuple:
                file_name = file[0]
                file      = file[1]
            else:
                raise Exception()
            csv_reader = utils.open_csv(file)
            header     = csv_reader.next()
            assert len(header) > 1, "header should have at least 2 columns"
            assert header[0].endswith("_id"), "First column should begin with a header like <model_name>_id"
            if len(header) >=3 and header[0].endswith("_id") and header[2].endswith("_id"):
                # this is a relationship file
                relations.append((file_name, file))
            else:
                # this is an entities file
                model_name = utils.to_class_name(header[0].replace("_id", ""))
                if model_name in all_models.keys():
                    entities[model_name] = (file_name, file)
                else:
                    raise ModelDoesntExist(model=model_name, file=file_name, models_availables=all_models.keys())
            nb_lines += len(file) - 1 # -1 removes headers

        # first iterate over entities
        logger.debug("BulkUpload: creating entities")
        for entity, (file_name, file) in entities.items():
            csv_reader = utils.open_csv(file)
            header     = csv_reader.next()
            # must check that all columns map to an existing model field
            fields       = utils.get_model_fields(all_models[entity])
            fields_types = {}
            for field in fields:
                fields_types[field['name']] = field['type']
            field_names = [field['name'] for field in fields]
            columns = []
            for column in header[1:]:
                column = utils.to_underscores(column)
                if column is not '':
                    if not column in field_names:
                        raise ColumnUnknow(file=file_name, column=column, model=entity, attributes_available=field_names)
                        break
                    column_type = fields_types[column]
                    columns.append((column, column_type))
            else:
                # here, we know that all columns are valid
                for row in csv_reader:
                    data = {}
                    id   = row[0]
                    for i, (column, column_type) in enumerate(columns):
                        value = str(row[i+1]).decode('utf-8')
                        # cast value if needed
                        if value:
                            try:
                                if "Integer" in column_type:
                                    value = int(value)
                                # TODO: cast float
                                if "Date" in column_type:
                                    value = datetime.datetime(*map(int, re.split('[^\d]', value)[:-1])).replace(tzinfo=utc)
                            except Exception as e:
                                e = WarningCastingValueFail(
                                    column_name = column,
                                    value       = value,
                                    type        = column_type,
                                    data        = data, model=entity,
                                    file        = file_name,
                                    line        = csv_reader.line_num,
                                    error       = str(e)
                                )
                                errors.append(e)
                                break
                            data[column] = value
                    else:
                        # instanciate a model
                        try:
                            item = all_models[entity].objects.create(**data)
                            # map the object with the ID defined in the .csv
                            id_mapping[(entity, id)] = item
                            file_reading_progression += 1
                            # FIXME: job can be accessed somewhere else (i.e detective/topics/common/job.py)
                            # Concurrent access are not secure here.
                            # For now we refresh the job just before saving it.
                            job.refresh()
                            job.meta["file_reading_progression"] = (float(file_reading_progression) / float(nb_lines)) * 100
                            job.meta["file_reading"] = file_name
                            job.save()
                        except Exception as e:
                            errors.append(
                                WarningValidationError(
                                    data  = data,
                                    model = entity,
                                    file  = file_name,
                                    line  = csv_reader.line_num,
                                    error = str(e)
                                )
                            )

        inserted_relations = 0
        # then iterate over relations
        logger.debug("BulkUpload: creating relations")
        for file_name, file in relations:
            # create a csv reader
            csv_reader    = utils.open_csv(file)
            csv_header    = csv_reader.next()
            relation_name = utils.to_underscores(csv_header[1])
            model_from    = utils.to_class_name(csv_header[0].replace("_id", ""))
            model_to      = utils.to_class_name(csv_header[2].replace("_id", ""))
            # check that the relation actually exists between the two objects
            try:
                getattr(all_models[model_from], relation_name)
            except Exception as e:
                raise RelationDoesntExist(
                    file             = file_name,
                    model_from       = model_from,
                    model_to         = model_to,
                    relation_name    = relation_name,
                    fields_available = [field['name'] for field in utils.get_model_fields(all_models[model_from])],
                    error            = str(e))
            for row in csv_reader:
                id_from = row[0]
                id_to   = row[2]
                if id_to and id_from:
                    try:
                        getattr(id_mapping[(model_from, id_from)], relation_name).add(id_mapping[(model_to, id_to)])
                        inserted_relations += 1
                        file_reading_progression += 1
                        job.refresh()
                        job.meta["file_reading_progression"] = (float(file_reading_progression) / float(nb_lines)) * 100
                        job.meta["file_reading"] = file_name
                        job.save()
                    except KeyError as e:
                        errors.append(
                            WarningKeyUnknown(
                                file             = file_name,
                                line             = csv_reader.line_num,
                                model_from       = model_from,
                                id_from          = id_from,
                                model_to         = model_to,
                                id_to            = id_to,
                                relation_name    = relation_name,
                                error            = str(e)
                            )
                        )
                    except Exception as e:
                        # Error unknown, we break the process to alert the user
                        raise Error(
                            file             = file_name,
                            line             = csv_reader.line_num,
                            model_from       = model_from,
                            id_from          = id_from,
                            model_to         = model_to,
                            id_to            = id_to,
                            relation_name    = relation_name,
                            error            = str(e))
                else:
                    # A key is missing (id_from or id_to) but we don't want to stop the parsing.
                    # Then we store the wrong line to return it to the user.
                    errors.append(
                        WarningInformationIsMissing(
                            file=file_name, row=row, line=csv_reader.line_num, id_to=id_to, id_from=id_from
                        )
                    )

        # Save everything
        saved = 0
        logger.debug("BulkUpload: saving %d objects" % (len(id_mapping)))
        job.refresh()
        job.meta["objects_to_save"] = len(id_mapping)
        for item in id_mapping.values():
            item.save()
            saved += 1
            job.refresh()
            job.meta["saving_progression"] = saved
            job.save()
        job.refresh()
        if "track" in job.meta:
            from django.core.mail import send_mail
            user = User.objects.get(pk=job.meta["user"])
            send_mail("upload finished", "your upload just finished", settings.DEFAULT_FROM_EMAIL, (user.email,))
        return {
            'duration' : (time.time() - start_time),
            'inserted' : {
                'objects' : saved,
                'links'   : inserted_relations
            },
            "errors" : sorted([dict([(e.__class__.__name__, str(e.__dict__))]) for e in errors])
        }

    except Exception as e:
        import traceback
        logger.error(traceback.format_exc())
        if e.__dict__:
            message = str(e.__dict__)
        else:
            message = e.message
        return {
            "errors" : [{e.__class__.__name__ : message}]
        }

# -----------------------------------------------------------------------------
#
#    API RESOURCE
#
# -----------------------------------------------------------------------------
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
        job.meta["user"] = bundle.request.user.pk
        job.save()
        return Document(**job.__dict__)

    def obj_update(self, bundle, **kwargs):
        queue = django_rq.get_queue('default')
        job = Job.fetch(kwargs['pk'], connection=queue.connection)
        if "track" in bundle.data:
            job.meta["track"] = bundle.data["track"]
            job.save()

    class Meta:
        resource_name          = "jobs"
        include_resource_uri   = False
        list_allowed_methods   = []
        detail_allowed_methods = ["get", "put"]

# EOF
