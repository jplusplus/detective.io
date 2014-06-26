# -*- coding: utf-8 -*-
"""
Django Heroku settings for Detective.io project.
Packages required:
    * boto
    * django-storages
"""
from settings import *
from urlparse import urlparse
import os
import dj_database_url

ALLOWED_HOSTS = [".detective.io"]

DATABASES = {
    'default' : dj_database_url.config()
}

# Turn on database level autocommit
# Otherwise db can raise a "current transaction is aborted,
# commands ignored until end of transaction block"
DATABASES['default']['OPTIONS'] = {'autocommit': True,}

# Parse url given into environment variable
NEO4J_URL  = urlparse( os.getenv('NEO4J_URL', '') )
NEO4J_OPTIONS = {}

# Determines the hostname
if NEO4J_URL.username and NEO4J_URL.password:
    NEO4J_OPTIONS = {
        'username': NEO4J_URL.username,
        'password': NEO4J_URL.password
    }

NEO4J_DATABASES = {
    'default' : {
        # Concatenates username, password and hostname
        'HOST': NEO4J_URL.hostname,
        'PORT': int(NEO4J_URL.port),
        'ENDPOINT':'/db/data',
        'OPTIONS': NEO4J_OPTIONS
    }
}

# AWS ACCESS
AWS_ACCESS_KEY_ID          = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY      = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME    = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_AUTH       = False
AWS_S3_FILE_OVERWRITE      = os.getenv('AWS_S3_FILE_OVERWRITE') == "True" and True or False

# Enable debug for minfication
DEBUG                      = bool(os.getenv('DEBUG', False))
# Configure static files for S3
STATIC_URL                 = os.getenv('STATIC_URL')
STATIC_ROOT                = here('staticfiles')
STATICFILES_DIRS          += (here('static'),)
INSTALLED_APPS            += ('storages',)
DEFAULT_FILE_STORAGE       = 'storages.backends.s3boto.S3BotoStorage'
# Static storage
STATICFILES_STORAGE        = DEFAULT_FILE_STORAGE
ADMIN_MEDIA_PREFIX         = STATIC_URL + 'admin/'

# JS/CSS compressor settings
COMPRESS_ENABLED           = True
COMPRESS_ROOT              = STATIC_ROOT
COMPRESS_URL               = STATIC_URL
COMPRESS_STORAGE           = STATICFILES_STORAGE
COMPRESS_OFFLINE           = True

# Activate CSS minifier
COMPRESS_CSS_FILTERS       = (
    "app.detective.compress_filter.CustomCssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
    "compressor.filters.template.TemplateFilter",
)

COMPRESS_JS_FILTERS = (
    "compressor.filters.jsmin.JSMinFilter",
    "compressor.filters.template.TemplateFilter",
)

COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': STATIC_URL
}

COMPRESS_TEMPLATE_FILTER_CONTEXT = {
    'STATIC_URL': STATIC_URL
}

# Activate the cache, for true
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

EMAIL_BACKEND    = "djrill.mail.backends.djrill.DjrillBackend"
MANDRILL_API_KEY = os.getenv("MANDRILL_APIKEY")
INSTALLED_APPS  += ('djrill',)

# EOF
