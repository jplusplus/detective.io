"""
Creates permissions for all installed apps that need permissions.
"""
from .models                    import AppPermission
from app.detective              import apps 
from django.db                  import DEFAULT_DB_ALIAS, IntegrityError
from django.db.models           import signals
from django.contrib.auth.models import Group, Permission


OPERATIONS = (
    ('add', 'Add an individual to {app_name}'),
    ('delete', 'Delete an individual from {app_name}'),
    ('change', 'Edit an individual of {app_name}'),
)
GROUPS = (
    dict(name='{app_name}_contributor', description='Contributors of an application, can create', permissions=('change', 'add', 'delete')),
)

def _create_groups(app_label):
    for group_dict in GROUPS:
        group_name = group_dict['name'].format(app_name=app_label)
        try:
            group = Group.objects.create(name=group_name)
        except IntegrityError:
            group = Group.objects.get(name=group_name)
            group.permissions.clear()
        for permission in group_dict['permissions']:
            perm = Permission.objects.filter(content_type__app_label=app_label, codename="contribute_%s" % permission)
            if perm:
                group.permissions.add(perm[0])

        group.save()


def _create_permission(app_label, permission_args):
    try:
        perm = AppPermission(**permission_args)
        perm.app_label(app_label)
        perm.save()
    except IntegrityError:
        perm = AppPermission.objects.get(**permission_args)
    return perm


def _get_permission_args(app_label, operation):
    return {
        "codename": "contribute_%s" % operation[0],
        "name":  operation[1].format(app_name=app_label),
    }

def create_permissions(app, created_models, verbosity, db=DEFAULT_DB_ALIAS, **kwargs):
    app_name  = app.__name__
    app_label = app_name.split('.')[-2]
    if apps.__name__ in app_name:
        for op in OPERATIONS:
            perm_args = _get_permission_args(app_label, op)
            _create_permission(app_label, perm_args)
        _create_groups(app_label)


# will be trigger for each created app
signals.post_syncdb.connect(create_permissions,
    dispatch_uid="app.detective.permissions.create_permissions")

