#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Pierre Bellon
# @Date:   2014-08-21 17:04:11
# @Last Modified by:   pbellon
# @Last Modified time: 2014-08-28 15:37:40
from django.test                import TestCase
from django.contrib.auth.models import User
from app.detective.models       import TopicSkeleton, TopicFactory

class CommonTestCase(TestCase):
    fixtures = [ 'app/detective/fixtures/default_skeletons.json' ]
    def setUp(self):
        self.contrib_username = 'contrib_user_common'
        self.contrib_userpass = 'contrib_password'
        self.contrib_email    = 'random@email.com'
        contrib_user = User.objects.create(
            username=self.contrib_username,
            email=self.contrib_userpass,
            )
        contrib_user.set_password(self.contrib_userpass)
        contrib_user.save()
        self.contrib_user = contrib_user

        skeleton = TopicSkeleton.objects.get(title="Body Count")
        self.body_skeleton = skeleton


    def test_topic_skeleton_list_selected_plans(self):
        selected_plans = self.body_skeleton.selected_plans()
        self.assertEqual(len(selected_plans), 4)


    def test_topic_factory_with_skeleton(self):
        skeleton = self.body_skeleton
        data = {
            'title': u'random',
            'author': self.contrib_user,
            'topic_skeleton': skeleton
        }
        topic = TopicFactory.create_topic(**data)
        self.assertEqual(topic.background,       skeleton.picture)
        self.assertEqual(topic.ontology_as_json, skeleton.ontology)
        self.assertIsNotNone(topic.ontology_as_json)

    def test_topic_create_with_bacground_url(self):
        skeleton = self.body_skeleton
        data = {
            'title':          u'random',
            'author':         self.contrib_user,
            'topic_skeleton': skeleton,
            'background_url': "http://i.imgur.com/cK1QyLU.jpg"
        }
        topic = TopicFactory.create_topic(**data)
        self.assertIsNotNone(topic.background)
        self.assertNotEqual(topic.background.url, skeleton.picture.url)
