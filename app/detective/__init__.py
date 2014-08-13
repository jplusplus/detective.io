from app.detective import topics # will init virtual modules
from app.detective import signals, utils

from django.conf   import settings
settings.INSTALLED_APPS += utils.get_topics_modules()

signals.bind()

