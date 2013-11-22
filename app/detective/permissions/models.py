# took from http://stackoverflow.com/questions/13932774/how-can-i-use-django-permissions-without-defining-a-content-type-or-model/13952198#13952198
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
 
class AppPermissionManager(models.Manager):
    def get_query_set(self):
        return super(AppPermissionManager, self).\
            get_query_set().filter(content_type__name='global_permission')

class AppPermission(Permission):
    """A global permission, not attached to a model"""
 
    objects = AppPermissionManager()

    class Meta:
        proxy = True
    
    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            name="global_permission", app_label=self.app_label()
        )
        self.content_type = ct
        super(AppPermission, self).save(*args, **kwargs)

    def app_label(self, label=None):
        if label:
            self._app_label = label
        return self._app_label