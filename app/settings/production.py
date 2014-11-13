# -*- coding: utf-8 -*-
"""
Django Heroku settings for Detective.io project.
Packages required:
    * boto
    * django-storages
"""
from .common  import *
from urlparse import urlparse
from datetime import date, timedelta
import os
import dj_database_url

ADMINS = (
    ('Pierre Romera', 'hello@pirhoo.com'),
)

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

# Expires 10 years in the future at 13:37 GMT
tenyrs = date.today() + timedelta(days=365*10)
oneweek= 3600 * 24 * 7

# AWS ACCESS
AWS_ACCESS_KEY_ID          = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY      = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME    = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_AUTH       = False
AWS_S3_FILE_OVERWRITE      = os.getenv('AWS_S3_FILE_OVERWRITE') == "True" and True or False
AWS_IS_GZIPPED             = False

GZIP_CONTENT_TYPES         = (
    'text/css',
    'text/csv',
    'text/html',
    'text/javascript',
    'text/plain',
    'text/xml',
    'text/x-markdown',
    'application/javascript',
    'application/x-javascript',
    'application/json',
    'application/pdf',
    'application/font-woff',
    'application/octet-stream',
    'font/opentype',
    'application/xml',
    'image/png',
    'image/jpeg',
    'image/pjpeg',
    'image/svg+xml',
    'image/gif',
    'image/jpg',
)
AWS_HEADERS                = {
    'Expires': tenyrs.strftime('%a, %d %b %Y 13:37:00 GMT'),
    'Cache-Control': "public, max-age={week}".format(week=oneweek) # one week max-age.
}

# Enable debug for minfication
DEBUG                      = bool(os.getenv('DEBUG', False))
# Configure static files for S3
STATIC_URL                 = os.getenv('STATIC_URL')
MEDIA_URL                  = STATIC_URL
STATIC_ROOT                = here('../staticfiles')
INSTALLED_APPS            += ('storages', )
DEFAULT_FILE_STORAGE       = 'storages.backends.s3boto.S3BotoStorage'
THUMBNAIL_DEFAULT_STORAGE  = DEFAULT_FILE_STORAGE
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
)

COMPRESS_JS_FILTERS = (
    "compressor.filters.jsmin.JSMinFilter",
)

COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': STATIC_URL
}

COMPRESS_TEMPLATE_FILTER_CONTEXT = {
    'STATIC_URL': STATIC_URL
}


EMAIL_BACKEND    = "djrill.mail.backends.djrill.DjrillBackend"
MANDRILL_API_KEY = os.getenv("MANDRILL_APIKEY")
INSTALLED_APPS  += ('djrill',)

# https only
MIDDLEWARE_CLASSES.insert(0, 'sslify.middleware.SSLifyMiddleware') # need to be the first middleware
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SSLIFY_DISABLE          = os.getenv('SSLIFY_DISABLE', "True") == "True" # default: True

# LOGGIN
RAVEN_API = os.getenv('RAVEN_API')
if RAVEN_API:
    INSTALLED_APPS += ('raven.contrib.django.raven_compat', )
    RAVEN_CONFIG = {'dsn': RAVEN_API,}
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console':{
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            },
            'null': {
                'class': 'django.utils.log.NullHandler',
            },
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['sentry', 'console'],
            },
            'django.request': {
                'handlers': ['sentry', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'py.warnings': {
                'handlers': ['console'],
            },
            'app.detective': {
                'handlers': ['sentry', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'rq.worker': {
                'handlers': ['sentry', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        }
    }
# EOF
