#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Pierre Bellon
# @Date:   2014-09-08 11:45:45
# @Last Modified by:   pbellon
# @Last Modified time: 2014-09-08 12:03:03
from django.core.management.base import BaseCommand
from app.detective.models        import Topic
from optparse import make_option

class Command(BaseCommand):
    help = "Detect topics that don't consider their own author as contributor"
    option_list = BaseCommand.option_list + (
        make_option('--fix',
            action='store_true',
            dest='fix',
            default=False,
            help='Fix anomalies (add back the author as contributor)'),
    )


    def handle(self, *args, **kwargs):
        abnormal_topics = self.get_anomalies()
        print "Detected %s abnormal topics" % len(abnormal_topics)
        for topic in abnormal_topics:

            msg = "{title}({module}) by {author}".format(
                title=topic.title,
                module=topic.ontology_as_mod,
                author=topic.author.username
            )

            if kwargs['fix']:
                contributors = topic.get_contributor_group()
                contributors.user_set.add(topic.author)
                contributors.save()
                msg += ' - FIXED'

            print msg


    def get_anomalies(self):
        anomalies = []
        for topic in Topic.objects.all():
            contributors = topic.get_contributor_group().user_set.all()
            if topic.author not in contributors:
                anomalies.append(topic)
        return anomalies









