# -*- coding: utf-8 -*-
from app.detective.models import Topic
from app.detective import register
# Create all the application using database information
for topic in Topic.objects.exclude(module="common"):
    register.topic_models("app.detective.topics.%s" % topic.module)