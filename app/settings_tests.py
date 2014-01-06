#!/usr/bin/env python
# Encoding: utf-8

import os
from settings import *
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NEO4J_DATABASES['default']['OPTIONS'] = {
    'CLEANDB_URI': '/cleandb/supersecretdebugkey!',
}

NEO4J_TEST_DATABASES = NEO4J_DATABASES

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db'
    }
}

DEBUG = False

INSTALLED_APPS = list(INSTALLED_APPS)

INSTALLED_APPS.remove('south')
INSTALLED_APPS.remove('djrill')

NEO4DJANGO_PROFILE_REQUESTS = False
NEO4DJANGO_DEBUG_GREMLIN = False

# EOF
