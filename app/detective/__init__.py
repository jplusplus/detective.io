from django.conf   import settings
from .signals import bind
from .utils   import get_topics_modules

settings.INSTALLED_APPS += get_topics_modules()

import app.detective.topics # will init virtual modules
bind()

