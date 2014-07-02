#!/usr/bin/env python
# Encoding: utf-8

import os
import dj_database_url
from settings import *
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NEO4J_DATABASES['default']['OPTIONS'] = {
    'CLEANDB_URI': '/cleandb/supersecretdebugkey!',
}

NEO4J_TEST_DATABASES = NEO4J_DATABASES

DATABASES = {
    'default' : dj_database_url.config()
}

DEBUG = False

INSTALLED_APPS = list(INSTALLED_APPS)

# remove south an djrill to speed up the tests
INSTALLED_APPS.remove('south')
INSTALLED_APPS.remove('compressor')

NEO4DJANGO_PROFILE_REQUESTS = False
NEO4DJANGO_DEBUG_GREMLIN = False

# EOF
