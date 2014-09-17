#!/usr/bin/env python
# Encoding: utf-8

import os
from settings import *
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NEO4J_DATABASES['default']['OPTIONS'] = {
    'CLEANDB_URI': '/cleandb/supersecretdebugkey!',
}

NEO4J_TEST_DATABASES = NEO4J_DATABASES

DEBUG = False

INSTALLED_APPS = list(INSTALLED_APPS)

# remove south an djrill to speed up the tests
INSTALLED_APPS.remove('south')
INSTALLED_APPS.remove('compressor')
INSTALLED_APPS.remove('debug_toolbar')

# Enable account activation in order to test it
ACCOUNT_ACTIVATION_ENABLED = True

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
MIDDLEWARE_CLASSES.remove('debug_toolbar.middleware.DebugToolbarMiddleware')
MIDDLEWARE_CLASSES.remove('app.middleware.debug_toolbar.JsonAsHTML')

NEO4DJANGO_PROFILE_REQUESTS = False
NEO4DJANGO_DEBUG_GREMLIN = False

CACHES = {
    'default': {
        # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/django_cache',
    }
}

from django.core.cache import cache
cache.clear()

# EOF
