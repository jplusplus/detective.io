#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Detective.io
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU GENERAL PUBLIC LICENSE v3
# -----------------------------------------------------------------------------
# Creation : 05-09-2014
# Last mod : 05-09-2014
# -----------------------------------------------------------------------------
from django.core.management.base import BaseCommand
from optparse import make_option
from django.contrib.auth.models import User
from app.detective.models import DetectiveProfileUser, Topic

class Command(BaseCommand):
    help = "Detect orphans in the graph."    
    option_list = BaseCommand.option_list + (
        make_option('--fix',
            action='store_true',
            dest='fix',
            default=False,
            help='upgrade the plan'),
        )

    def handle(self, *args, **options):
        from django.conf import settings
        for user in User.objects.all():
            profile                = DetectiveProfileUser.objects.get(user=user)
            user_topics            = Topic.objects.filter(author=user)
            number_of_topic        = user_topics.count()
            max_number_of_entities = 0
            for topic in user_topics:
                max_number_of_entities = max(max_number_of_entities, topic.entities_count())
            for plan in settings.PLANS:
                best_plan, proprs = plan.items()[0]
                if proprs.get("max_investigation") != -1 and number_of_topic        > proprs.get("max_investigation"): continue
                if proprs.get("max_entities")      != -1 and max_number_of_entities > proprs.get("max_entities")     : continue
                break
            self.stdout.write("%s : %s ---> %s" % (user.username, profile.plan, best_plan))
            if options["fix"]:
                profile.plan = best_plan
                profile.save()

# EOF
