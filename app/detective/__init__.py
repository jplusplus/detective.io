from app.detective import utils
from django.conf   import settings

settings.INSTALLED_APPS += utils.get_topics_modules()
