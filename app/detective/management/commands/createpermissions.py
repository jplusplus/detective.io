from app.detective.permissions.models import AppPermission
from django.conf                      import settings
from django.db                        import IntegrityError
from django.core.management.base      import BaseCommand

class Command(BaseCommand):

    help = "Create local application"
    args = ''

    def handle(self, *args, **options):
        creation_count = 0
        for app in settings.INSTALLED_APPS:
            if "app.detective.apps" in app:
                app_name = app.split('.').pop()
                try:
                    perm = AppPermission(codename='contribute', name='Contribute to %s application' % app_name)
                    perm.app_label(app_name)
                    perm.save()
                    creation_count += 1
                    print "%s.contribute permission have been created" % app_name
                except IntegrityError:
                    print "%s.contribute permission is already created" % app_name

        print "%d permission have been created"

                


