# -*- coding: utf-8 -*-
from django.core.management.base  import BaseCommand
from neo4django.graph_auth.models import User as GraphUser
from django.contrib.auth.models   import User

class Command(BaseCommand):
    help = "Import users from graph into current user's collection."
    args = ''

    def handle(self, *args, **options):
        imported = 0

        newusers = [u.__dict__["_prop_values"] for u in GraphUser.objects.all()]
        for u in newusers:
            try:
                User.objects.get(username=u["username"])
                print "%s already exists!" % u["username"]
            # User doesn't exist
            except User.DoesNotExist:
                # Avoid integrity error
                if u["first_name"] == None: u["first_name"] = u["username"]
                if u["last_name"] == None:  u["last_name"] = ""
                user = User(**u)
                user.save()
                # Count imported user
                imported += 1

        if imported <= 1:
            print "%s user imported!" % imported
        else:
            print "%s users imported!" % imported