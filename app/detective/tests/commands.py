from django.core.management           import call_command
from django.core.management.base      import CommandError
from django.test                      import TestCase
from StringIO                         import StringIO
from django.contrib.auth.models       import User
from neo4django.graph_auth.models     import User as GraphUser
from app.detective.apps.common.models import Country

import sys

class CommandsTestCase(TestCase):

    def test_parseowl_fail(self):
        # Catch output
        output = StringIO()
        sys.stdout = output
        # Must fail without argument
        with self.assertRaises(CommandError):
            call_command('parseowl')

    def test_parseowl(self):
        # Catch output
        output = StringIO()
        sys.stdout = output
        args = "./app/data/ontology-v5.3.owl"
        call_command('parseowl', args)

    def test_loadnodes_fail(self):
        # Catch output
        output = StringIO()
        sys.stdout = output
        # Must fail without argument
        with self.assertRaises(CommandError):
            call_command('loadnodes')

    def test_loadnodes(self):
        # Catch output
        output = StringIO()
        sys.stdout = output
        # Import countries
        args = "./app/detective/apps/common/fixtures/countries.json"
        call_command('loadnodes', args)
        # Does France exists?
        self.assertGreater(len( Country.objects.filter(isoa3="FRA") ), 0)

    def test_importusers(self):
        # Catch output
        output = StringIO()
        sys.stdout = output
        # Import users
        call_command('importusers')
