import os
from settings import *
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AUTHENTICATION_BACKENDS = ('neo4django.graph_auth.backends.NodeModelBackend',)

NEO4J_DATABASES = {
    'default' : {
        'HOST':'localhost',
        'PORT':7474,
        'ENDPOINT':'/db/data',
        'OPTIONS':{
            'CLEANDB_URI': '/cleandb/supersecretdebugkey!',
        },
    }
}

NEO4J_TEST_DATABASES = {
    'default' : {
        'HOST':'localhost',
        'PORT':7474,
        'ENDPOINT':'/db/data',
        'OPTIONS':{
            'CLEANDB_URI': '/cleandb/supersecretdebugkey!',
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db'
    }
}

DATABASE_ROUTERS = ['neo4django.utils.Neo4djangoIntegrationRouter']

USE_TZ = True

INSTALLED_APPS = (
    'neo4django.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'compressor',
    'tastypie',
    'registration',
    'app.detective',
    'app.detective.apps.common',
    'app.detective.apps.energy'
)

SECRET_KEY="<SET A SECRET KEY HERE>"

DEBUG = True

NEO4DJANGO_PROFILE_REQUESTS = False
NEO4DJANGO_DEBUG_GREMLIN = False