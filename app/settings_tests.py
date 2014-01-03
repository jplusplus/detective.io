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

# By default, South’s syncdb command will also apply migrations if it’s run in non-interactive mode, 
# which includes when you’re running tests - it will run every migration every time you run your tests.
# See http://south.readthedocs.org/en/latest/unittests.html#unit-test-integration
SOUTH_TESTS_MIGRATE = False

# EOF
