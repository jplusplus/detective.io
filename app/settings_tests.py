import os
from settings import *
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

DEBUG = False

NEO4DJANGO_PROFILE_REQUESTS = False
NEO4DJANGO_DEBUG_GREMLIN = False

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
    'password_reset',
    'app.detective',
    'app.detective.permissions',
)

# Add customs app to INSTALLED_APPS
INSTALLED_APPS = INSTALLED_APPS + get_topics_modules()
