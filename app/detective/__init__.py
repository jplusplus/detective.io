# Warning: Edit this file with caution. It is highly sensitive and could cause
# detective.io misbehavior and many API endpoints could produce errors and
# failures
from django.conf   import settings
from .signals import bind
from .utils   import get_topics_modules

# first we add topics as modules to our installed apps
settings.INSTALLED_APPS += get_topics_modules()
# we now import topics file which will wrap topics as modules
import app.detective.topics
# then we bind application signals
bind()

