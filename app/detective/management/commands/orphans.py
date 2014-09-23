#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Detective.io
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU GENERAL PUBLIC LICENSE v3
# -----------------------------------------------------------------------------
# Creation : 04-09-2014
# Last mod : 04-09-2014
# -----------------------------------------------------------------------------
from django.core.management.base import BaseCommand, CommandError
import json
from django.db.models.loading import get_model
from optparse import make_option
from app.detective.models import Topic
from app.detective import utils
import traceback

class Command(BaseCommand):
    help = "Detect orphans in the graph."    
    option_list = BaseCommand.option_list + (
        make_option('--fix',
            action='store_true',
            dest='fix',
            default=False,
            help='Delete orphans'),
        )

    def handle(self, *args, **options):
        total_orphans_count = 0
        for topic in Topic.objects.all():
            # escape common & energy as usual
            if topic.slug in ["common", "energy"]: continue
            self.stdout.write("Topic: %s" % (topic))
            orphans_count = 0
            try:
                for Model in topic.get_models():
                    try:
                        fields = utils.get_model_fields(Model)
                        for field in fields:
                            if field["rel_type"] and field["direction"] == "out" and "through" in field["rules"]:
                                ids= []
                                for entity in Model.objects.all():
                                    ids.extend([_.id for _ in entity.node.relationships.all()])
                                Properties = field["rules"]["through"]
                                for info in Properties.objects.all():
                                    if info._relationship not in ids:
                                        self.stdout.write("\t%s is an orphelin property of the model %s." % (info._NodeModel__node, Model))
                                        orphans_count += 1
                                        total_orphans_count += 1
                                        if options["fix"]:
                                            self.stdout.write("\tremoving %s" % (info))
                                            info.delete()
                    except Exception as e:
                        self.stderr.write("\tError with fields of %s (%s)" % (entity, e))
                if orphans_count > 0:
                    self.stdout.write("\tfound %d orphans" % (orphans_count))
            except Exception as e:
                self.stderr.write("\tError with model %s (%s)" % (Model.__class__.__name__, e))
        self.stdout.write("TOTAL: found %d orphans" % (total_orphans_count))

# EOF
