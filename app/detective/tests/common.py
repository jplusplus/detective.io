#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Pierre Bellon
# @Date:   2014-08-21 17:04:11
# @Last Modified by:   toutenrab
# @Last Modified time: 2014-09-04 14:43:59
from django.test                import TestCase
from django.contrib.auth.models import User
from app.detective.models       import Topic

class CommonTestCase(TestCase):
    fixtures = [ 'app/detective/fixtures/default_skeletons.json', ]
    def default_user_args(self):
        return {
            'email'    : u'user.test@test.me',
            'username' : u'user-test',
            'password' : u'password',
            'is_active': True
        }
    def create_user(self, **kwargs):
        password = kwargs.get('password', 'default')
        if kwargs.has_key('password'):
            del kwargs['password']

        user = User.objects.create(**kwargs)
        user.set_password(password)
        user.save()
        return user

    def delete_user(self, instance=None):
        if instance: instance.delete()


    def test_user_delete(self):
        # Scenario: when we delete a user its topic should be deleted to
        user  = self.create_user(**self.default_user_args())
        topic = Topic.objects.create(title=u'title', author=user)
        self.delete_user(user)
        self.assertFalse(Topic.objects.filter(author=user).exists())


