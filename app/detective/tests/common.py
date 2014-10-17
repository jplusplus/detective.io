#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Pierre Bellon
# @Date:   2014-08-21 17:04:11
# @Last Modified by:   toutenrab
# @Last Modified time: 2014-09-04 14:43:59
from django.test                import TestCase
from django.contrib.auth.models import User
from app.detective.models       import Topic
from app.detective.utils        import where, findwhere, without

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

    def test_where(self):
        arr = [
            {'a': 0, 'test': 'ok'},
            {'b': 1, 'test': 'ok'},
            {'c': 2, 'test': 'notok'}
        ]

        els = where(arr, {'test': 'ok'})
        self.assertTrue(arr[0] in els)
        self.assertTrue(arr[1] in els)

    def test_findwhere(self):
        arr = [
            {'a': 0, 'test': 'ok'},
            {'b': 1, 'test': 'ok'},
            {'c': 2, 'test': 'notok'}
        ]

        res = findwhere(arr, {'test': 'ok'})
        self.assertTrue(res == arr[0])


    def test_without_simple(self):
        coll = [ 1, 2 , 3]
        without_el = 3
        new_coll = without(coll, without_el)
        self.assertTrue(without not in new_coll)

    def test_without_lambda(self):
        # lambda to filter every odd number
        coll = [1, 2, 3, 4]
        l_odd = lambda el: el % 2 != 0
        new_coll = without(coll, l_odd)
        self.assertTrue(1 not in new_coll)
        self.assertTrue(3 not in new_coll)







