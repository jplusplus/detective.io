#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Detective.io
# -----------------------------------------------------------------------------
# Author : Pierre Bellon
#          Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU GENERAL PUBLIC LICENSE v3
# -----------------------------------------------------------------------------
# Creation : 22-Jan-2014
# Last mod : 22-Jan-2014
# -----------------------------------------------------------------------------
"""
Creates permissions for all installed topics that need permissions.
"""
from .models                    import AppPermission
from django.db                  import DEFAULT_DB_ALIAS, IntegrityError
from django.db.models           import signals
from django.contrib.auth.models import Group, Permission

OPERATIONS = (
    ('add'   , 'Add an individual to {app_name}'),
    ('delete', 'Delete an individual from {app_name}'),
    ('change', 'Edit an individual of {app_name}'),
    ('read', 'Read {app_name}')
)

GROUPS = (dict(
    name        = '{app_name}_contributor',
    description = 'Contributors of an application, can create',
    permissions = ('change', 'add', 'delete', 'read')),
)

def _create_groups(app_label):
    groups = []
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
        groups.append(group)
    return groups

def _remove_groups(app_label):
    for group_dict in GROUPS:
        group_name = group_dict['name'].format(app_name=app_label)
        try:
            group = Group.objects.get(name = group_name)
            group.delete()
        except Group.DoesNotExist:
            pass

def _create_permission(app_label, permission_args):
    """
    Create or get a single permission based on its application label, its name
    and codename

    @see: _get_permission_args(app_label, operation)
    """
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
        "name"    :  operation[1].format(app_name=app_label),
    }

def _remove_permission(app_label, permission_args):
    try:
        perm = AppPermission.objects.get(**permission_args)
        perm.delete()
    except AppPermission.DoesNotExist:
        pass

def create_permissions(app, app_label=None, created_models=None, verbosity=False, db=DEFAULT_DB_ALIAS, **kwargs):
    """
    Entry point for permission creation. Will be called after DB synchronisation
    for every installed app (see settings.INSTALLED_APPS)
    """
    app_name = app.__name__

    if app_label is None:
        # FIXME: why -2 ?
        app_label = app_name.split('.')[-2]
    # we check if the received signal come from a local installed application
    if app_name.startswith("app.detective.topics"):
        for op in OPERATIONS:
            perm_args = _get_permission_args(app_label, op)
            _create_permission(app_label, perm_args)
        _create_groups(app_label)

def remove_permissions(sender, instance, using, **kwargs):
    app_label = instance.slug
    for op in OPERATIONS:
        perm_args = _get_permission_args(app_label, op)
        _remove_permission(app_label, perm_args)
    _remove_groups(app_label)

# -----------------------------------------------------------------------------
#
#    SIGNALS
#
# -----------------------------------------------------------------------------
# will be trigger for each created app

signals.post_syncdb.connect(create_permissions,
    dispatch_uid="app.detective.permissions.create_permissions")

#EOF
