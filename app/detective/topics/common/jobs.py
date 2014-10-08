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
# Last mod : 02-Oct-2014
# -----------------------------------------------------------------------------
from tastypie.resources                 import Resource
from django.core.exceptions             import ObjectDoesNotExist
from tastypie                           import fields
from rq.job                             import Job
from django.contrib.auth.models         import User
from rq                                 import get_current_job
from rq.exceptions                      import NoSuchJobError
from django.utils.timezone              import utc
from neo4django.db                      import connection
from django.conf                        import settings
from django.core.paginator              import InvalidPage
from django.core.files.storage          import default_storage
from django.core.files.base             import ContentFile
from cStringIO                          import StringIO
from app.detective.topics.common.models import FieldSource
import app.detective.utils              as utils
import django_rq
import json
import time
import datetime
import logging
import re
import zipfile
import csv
import tempfile
import os
import base64

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
#
#    JOB - EXPORT AS CSV
#
# -----------------------------------------------------------------------------
def render_csv_zip_file(topic, model_type=None, query=None, cache_key=None):

    def write_all_in_zip(objects, columns, zip_file, model_name=None):
        """
        Write the csv file from `objects` and `columns` and add it into the `zip_file` file.
        If given, `model_name` will be the name of the csv file.
        If `cache_key` is defined, will put the generated file name in the default cache with the given key.
        """
        # set a getattr function depending of the type of `objects`
        if isinstance(objects[0], dict):
            def _getattr(o, prop): return o.get(prop, "")
        else:
            def _getattr(o, prop): return getattr(o, prop)
        all_ids    = []
        csv_file   = StringIO()
        model_name = model_name or objects[0].__class__.__name__
        spamwriter = csv.writer(csv_file)
        spamwriter.writerow(["%s_id" % (model_name)] + columns) # header
        for obj in objects:
            all_ids.append(_getattr(obj, 'id'))
            obj_columns = []
            for column in columns:
                val = _getattr(obj, column)
                if val:
                    val = unicode(val).encode('utf-8')
                obj_columns.append(val)
            spamwriter.writerow([_getattr(obj, 'id')] + obj_columns)
        zip_file.writestr("{0}.csv".format(model_name), csv_file.getvalue())
        csv_file.close()
        return all_ids

    def get_columns(model):
        edges   = dict()
        columns = []
        for field in utils.iterate_model_fields(model):
            if field['type'] != 'Relationship':
                if field['name'] not in ['id']:
                    columns.append(field['name'])
            else:
                edges[field['rel_type']] = [field['model'], field['name'], field['related_model']]
        return (columns, edges)

    buffer   = StringIO()
    zip_file = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
    models   = topic.get_models()
    if not query:
        export_edges = not model_type
        for model in models:
            if model_type and model.__name__.lower() != model_type:
                continue
            (columns, edges) = get_columns(model)
            objects = model.objects.all()
            if objects.count() > 0:
                all_ids = write_all_in_zip(objects, columns, zip_file)
                if export_edges:
                    for key in edges.keys():
                        rows = connection.cypher("""
                            START root=node({nodes})
                            MATCH (root)-[r:`{rel}`]->(leaf)
                            RETURN id(root) as id_from, id(leaf) as id_to
                        """.format(nodes=','.join([str(id) for id in all_ids]), rel=key)).to_dicts()
                        csv_file = StringIO()
                        spamwriter = csv.writer(csv_file)
                        spamwriter.writerow(["%s_id" % (edges[key][0]), edges[key][1], "%s_id" % (edges[key][2])]) # header
                        for row in rows:
                            spamwriter.writerow([row['id_from'], None, row['id_to']])
                        zip_file.writestr("{0}_{1}.csv".format(edges[key][0], edges[key][1]), csv_file.getvalue())
                        csv_file.close()
    else:
        page        = 1
        limit       = 1
        objects     = []
        total       = -1
        while len(objects) != total:
            try:
                result   = topic.rdf_search(query=query, offset=(page - 1) * limit)
                objects += result['objects']
                total    = result['meta']['total_count']
                page    += 1
            except KeyError:
                break
            except InvalidPage:
                break
        for model in models:
            if model.__name__ == objects[0]['model']:
                break
        (columns, _) = get_columns(model)
        write_all_in_zip(objects, columns, zip_file, model.__name__)
    zip_file.close()
    buffer.flush()
    # save the zip in `base_dir`
    base_dir  = "csv-exports"
    file_name = "%s/d.io-export-%s.zip" % (base_dir, topic.slug)
    # name can be changed by default storage if previous exists
    file_name = default_storage.save(file_name, ContentFile(buffer.getvalue()))
    buffer.close()
    file_name = "%s%s" % (settings.MEDIA_URL, file_name)
    # save in cache if cache_key is defined
    if cache_key:
        utils.topic_cache.set(topic, cache_key, file_name, 60*60*24)
    return dict(file_name=file_name)

# -----------------------------------------------------------------------------
#
#    JOB - BULK UPLOAD
#
# -----------------------------------------------------------------------------
def unzip_and_process_bulk_parsing_and_save_as_model(topic, zip_content):
    start_time = time.time()

    try:
        (fd, zip_file) = tempfile.mkstemp()
        with open(zip_file, 'w') as tmp:
            tmp.write(base64.b64decode(zip_content))

        # Create a tempdir
        extraction_dir = tempfile.mkdtemp()

        # We extract everything in the tempdir
        with zipfile.ZipFile(zip_file, 'r') as opened_zip_file:
            opened_zip_file.extractall(extraction_dir)
        os.close(fd)

        # Get all lines from all .csv in big nested arrays
        opened_files = [open(os.path.join(extraction_dir, f), 'r') for f in os.listdir(extraction_dir)]
        files = [(opened_file.name, opened_file.readlines()) for opened_file in opened_files]

        # Close and delete every tmp file / dir
        for opened_file in opened_files:
            opened_file.close()
            os.remove(os.path.join(extraction_dir, opened_file.name))
        os.rmdir(extraction_dir)
        os.remove(zip_file)

        # Process!
        process_bulk_parsing_and_save_as_model(topic, files, start_time)
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

def process_bulk_parsing_and_save_as_model(topic, files, start_time=None):
    """
    Job which parses uploaded content, validates and saves them as model
    """

    start_time               = start_time != None and start_time or time.time()
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
        assert type(files) in (tuple, list), type(files)
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
            assert len(header) > 1, "{file_name} header should have at least 2 columns"
            assert header[0].endswith("_id"), "{file_name} : First column should begin with a header like <model_name>_id. Actually {first_col}".format(file_name=file_name, first_col=header[0])
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
            columns        = []
            for column in header[1:]:
                column = utils.to_underscores(column)
                if not column in field_names and not column.endswith("__sources__"):
                    raise ColumnUnknow(file=file_name, column=column, model=entity, attributes_available=field_names)
                    break
                if column.endswith("__sources__"):
                    column_type = "__sources__"
                    column = column[:-len("__sources__")]
                    if not column in field_names:
                        raise ColumnUnknow(file=file_name, column=column, model=entity, attributes_available=field_names)
                        break
                else:
                    column_type = fields_types.get(column, None)
                columns.append((column, column_type))
            else:
                # here, we know that all columns are valid
                for row in csv_reader:
                    data      = {}
                    sources   = {}
                    entity_id = row[0]
                    for i, (column, column_type) in enumerate(columns):
                        value = str(row[i+1]).decode('utf-8')
                        # cast value if needed
                        if value:
                            try:
                                if "Integer" in column_type:
                                    value = int(value)
                                # TODO: cast float
                                if "Date" in column_type:
                                    value = datetime.datetime(*map(int, re.split('[^\d]', value)[:3])).replace(tzinfo=utc)

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
                            if column_type == "__sources__":
                                sources[column] = value
                            else:
                                data[column] = value
                    else:
                        # instanciate a model
                        try:
                            item = all_models[entity].objects.create(**data)
                            # map the object with the ID defined in the .csv
                            id_mapping[(entity, entity_id)] = item
                            # create sources
                            for sourced_field, reference in sources.items():
                                for ref in reference.split("||"):
                                    FieldSource.objects.create(individual=item.id, field=sourced_field, reference=ref)
                            # FIXME: job can be accessed somewhere else (i.e detective/topics/common/jobs.py:JobResource)
                            # Concurrent access are not secure here.
                            # For now we refresh the job just before saving it.
                            file_reading_progression += 1
                            if job:
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
            csv_reader      = utils.open_csv(file)
            csv_header      = csv_reader.next()
            relation_name   = utils.to_underscores(csv_header[1])
            model_from      = utils.to_class_name(csv_header[0].replace("_id", ""))
            model_to        = utils.to_class_name(csv_header[2].replace("_id", ""))
            properties_name = csv_header[3:]
            # retrieve ModelProperties from related model
            ModelProperties = topic.get_rules().model(all_models[model_from]).field(relation_name).get("through")
            # check that the relation actually exists between the two objects
            try:
                getattr(all_models[model_from], relation_name)
            except Exception as e:
                raise RelationDoesntExist(
                    file             = file_name,
                    model_from       = model_from,
                    model_to         = model_to,
                    relation_name    = relation_name,
                    fields_available = [field['name'] for field in utils.iterate_model_fields(all_models[model_from])],
                    error            = str(e))
            for row in csv_reader:
                id_from    = row[0]
                id_to      = row[2]
                properties = [p.decode('utf-8') for p in row[3:]]
                if id_to and id_from:
                    try:
                        instance_from = id_mapping[(model_from, id_from)]
                        instance_to   = id_mapping[(model_to, id_to)]
                        getattr(instance_from, relation_name).add(instance_to)
                        # add properties if needed
                        if ModelProperties and properties_name and properties:
                            # save the relationship to create an id
                            instance_from.save()
                            # retrieve this id
                            relation_id = next(rel.id for rel in instance_from.node.relationships.outgoing() if rel.end.id == instance_to.id)
                            # properties of the relationship
                            relation_args = {
                                "_endnodes"     : [id_mapping[(model_from, id_from)].id, instance_to.id],
                                "_relationship" : relation_id,
                            }
                            # Pairwise the properties with their names 
                            relation_args.update(zip(properties_name, properties))
                            try:
                                ModelProperties.objects.create(**relation_args)
                            except TypeError as e:
                                errors.append(
                                    AttributeDoesntExist(
                                        file             = file_name,
                                        line             = csv_reader.line_num,
                                        model_from       = model_from,
                                        id_from          = id_from,
                                        model_to         = model_to,
                                        id_to            = id_to,
                                        relation_args    = relation_args,
                                        error            = str(e)
                                    )
                        )
                        # update the job
                        inserted_relations += 1
                        file_reading_progression += 1
                        if job:
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
        if job:
            job.refresh()
            job.meta["objects_to_save"] = len(id_mapping)
            job.save()
        for item in id_mapping.values():
            item.save()
            saved += 1
            if job:
                job.refresh()
                job.meta["saving_progression"] = saved
                job.save()
        if job: job.refresh()
        if job and "track" in job.meta:
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
        try:
            job = Job.fetch(kwargs['pk'], connection=queue.connection)
        except NoSuchJobError:
            raise ObjectDoesNotExist()
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
