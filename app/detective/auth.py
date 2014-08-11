#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Pierre Bellon
# @Date:   2014-08-06 12:21:55
# @Last Modified by:   toutenrab
# @Last Modified time: 2014-08-11 12:26:41
# took from https://djangosnippets.org/snippets/1368/

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None