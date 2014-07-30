from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
# -*- coding: utf-8 -*-
import os, re
# for relative paths
here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TASTYPIE_FULL_DEBUG = DEBUG

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Custom data directory
DATA_ROOT = here('data')

ADMINS = (
    ('Pierre Romera', 'hello@pirhoo.com')
)

DEFAULT_FROM_EMAIL = 'Detective.io <contact@detective.io>'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db'
    }
}

NEO4J_DATABASES = {
    'default' : {
        'HOST': "127.0.0.1",
        'PORT': 7474,
        'ENDPOINT':'/db/data'
    }
}

DATABASE_ROUTERS        = ['neo4django.utils.Neo4djangoIntegrationRouter']
SESSION_ENGINE          = "django.contrib.sessions.backends.db"
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = here('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/public/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = here('staticfiles')

LOGIN_URL = "/admin"
# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Bower components
    ('components', here('static/components') ),
    ('custom_d3', here('static/custom_d3') ),
    here("detective/static"),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.getenv('SECRET_KEY', '#_o0^tt=lv1k8k-h=n%^=e&amp;vnvcxpnl=6+%&amp;+%(2!qiu!vtd9%')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

MIDDLEWARE_CLASSES = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'app.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'app.middleware.debug_toolbar.JsonAsHTML',
    'app.middleware.crossdomainxhr.XsSharing',
    # add urlmiddleware after all other middleware.
    'urlmiddleware.URLMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

]


TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

SUIT_CONFIG = {
    'ADMIN_NAME': 'Detective.io',
    'MENU_EXCLUDE': ('registration', 'tastypie'),
}

ROOT_URLCONF = 'app.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'app.wsgi.application'

TEMPLATE_DIRS = (
    here('detective/templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# JS/CSS COMPRESSOR SETTINGS
COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio --bare'),
    ('text/less', 'lessc --include-path="%s" {infile} {outfile}' % here('static') ),
)

# Activate CSS minifier
COMPRESS_CSS_FILTERS = (
    "app.detective.compress_filter.CustomCssAbsoluteFilter",
)

COMPRESS_JS_FILTERS = ()

COMPRESS_TEMPLATE_FILTER_CONTEXT = {
    'STATIC_URL': STATIC_URL
}

# Remove BeautifulSoup requirement
COMPRESS_PARSER = 'compressor.parser.HtmlParser'
COMPRESS_ENABLED = False
#INTERNAL_IPS = ('127.0.0.1',)

TASTYPIE_DEFAULT_FORMATS = ['json', 'jsonp']


INSTALLED_APPS = (
    # 'suit' must be added before 'django.contrib.admin'
    'suit',
    'neo4django.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    # Allow CORS
    'corsheaders',
    # Thumbnails generator
    'easy_thumbnails',
    # Sign up activation
    'registration',
    # Compresses linked and inline JavaScript or CSS into a single cached file.
    'compressor',
    # API generator
    'tastypie',
    # Email backend
    'password_reset',
    # Manage migrations
    'south',
    # Rich text editor
    'tinymce',
    # Redis queue backend
    "django_rq",
    # Debug utilities
    "debug_toolbar",
    # Internal
    'app.detective',
    'app.detective.permissions',
)

SOUTH_MIGRATION_MODULES = {
    'easy_thumbnails': 'easy_thumbnails.south_migrations',
}

# Add customs app to INSTALLED_APPS
from app.detective.utils import get_topics_modules
INSTALLED_APPS = INSTALLED_APPS + get_topics_modules()

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# One-week activation window
ACCOUNT_ACTIVATION_DAYS = 7

CACHES = {
    'default': {
        # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/django_cache',
    }
}

# Redis Queues
# RQ_SHOW_ADMIN_LINK will override the default admin template so it may interfere
# with other apps that modifies the default admin template.
RQ_SHOW_ADMIN_LINK = True
RQ_CONFIG = {
    'URL'  : os.getenv('REDISTOGO_URL', None) or os.getenv('REDISCLOUD_URL', None) or 'redis://localhost:6379',
    'DB'   : 0,
    'ASYNC': True
}
RQ_QUEUES = {
    'default': RQ_CONFIG,
    'high'   : RQ_CONFIG,
    'low'    : RQ_CONFIG
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
         'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters' : ['require_debug_true'],
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'app.detective': {
            'handlers': ['mail_admins', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}


if DEBUG:
    # INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', '::1')
    DEBUG_TOOLBAR_PATCH_SETTINGS = False 
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'neo4j_panel.Neo4jPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
    )
    DEBUG_TOOLBAR_CONFIG = { 
        'SHOW_TOOLBAR_CALLBACK': 'app.detective.utils.should_show_debug_toolbar'
    }
