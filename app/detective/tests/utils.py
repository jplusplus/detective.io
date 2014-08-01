#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project: IDF-Quiz
# -----------------------------------------------------------------------------
# Author: Pierre Bellon                               <bellon.pierre@gmail.com>
# -----------------------------------------------------------------------------
# License: GNU General Public License
# -----------------------------------------------------------------------------
# Creation time:      2014-07-31 14:16:47
# Last Modified time: 2014-07-31 14:47:54
# -----------------------------------------------------------------------------
# This file is part of IDF-Quiz
#
#   IDF-Quiz is a narrative app promoting culture and tourism in Ile-De-France.
#   Copyright (C) 2014 Journalism++
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
from django.test          import TestCase
from app.detective.models import Topic
from app.detective.utils  import topic_cache
import json

class TopicCachierTestCase(TestCase):
    def setUp(self):
        ontology = """
        [
            {
                "name": "Person",
                "fields": [
                    { "name": "first_name","type": "string","verbose_name":"First Name" },
                    { "name": "last_name","type": "string","verbose_name":"Last Name" },
                    { "name": "employed_by", "type": "Relationship", "related_model": "Company" }
                ]
            },
            {
                "name": "Company",
                "fields": [
                    { "name": "name", "type": "string" },
                    {"name": "status", "type": "string"}
                ]
            }
        ]
        """
        try:
            self.topic = Topic.objects.create(
                title='Test investigation',
                ontology_as_json=json.loads(ontology),
                slug='test-investigation-fake'
            )

        except:
            self.topic = Topic.objects.get(slug='test-investigation-fake')

    def test_topic_update(self):
        # if we update a topic, its revision number should be incremented
        rev = topic_cache.version(self.topic)
        self.topic.title = "New title"
        self.topic.save()
        self.assertEqual(topic_cache.version(self.topic), rev+1)

    def test_topic_delete(self):
        self.topic.delete()
        self.assertIsNone(topic_cache.version(self.topic))

    def test_topic_model_update(self):
        import pdb; pdb.set_trace()
        models = self.topic.models()