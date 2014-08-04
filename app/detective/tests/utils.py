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
        ontology_str = """
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
        self.ontology = json.loads(ontology_str)


    def create_topic(self, args=None):
        default_kwargs = {
            'title': 'Test investigation',
            'ontology_as_json':  self.ontology,
            'slug': 'test-investigation-fake'
        }
        if args == None:
            kwargs = default_kwargs
        else:
            kwargs = args
        try:
            return Topic.objects.create(**kwargs)
        except:
            return Topic.objects.get(
                slug=kwargs.get('slug', default_kwargs.get('slug'))
            )
    def test_topic_creation(self):
        topic = self.create_topic()
        rev = topic_cache.version(topic)
        self.assertEqual(rev, 0)


    def test_topic_update(self):
        # if we update a topic, its revision number should be incremented
        topic = self.create_topic()
        rev = topic_cache.version(topic)
        topic.title = "New title"
        topic.save()
        self.assertEqual(topic_cache.version(topic), rev+1)


    def test_topic_delete(self):
        topic = self.create_topic()
        topic.delete()
        self.assertIsNone(topic_cache.version(topic))

    def test_topic_model_update(self):
        topic = self.create_topic()
        rev_origin = topic_cache.version(topic)
        Person = topic.get_models_module().Person
        p = Person.objects.create(first_name='Pierre', last_name='Bellon')
        rev_target = topic_cache.version(topic)
        self.assertEqual(rev_target, rev_origin + 1)