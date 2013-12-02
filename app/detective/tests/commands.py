from app.detective.topics.common.models import Country
from django.core.management           import call_command
from django.core.management.base      import CommandError
from django.test                      import TestCase
from neo4django.graph_auth.models     import User as GraphUser
from django.contrib.auth.models       import User
from StringIO                         import StringIO
import sys

class CommandsTestCase(TestCase):
    def setUp(self):
        super(CommandsTestCase, self).setUp()
        try:
            self.toto = GraphUser.objects.get(email='toto@detective.io')
        except GraphUser.DoesNotExist:
            self.toto = GraphUser.objects.create(username='toto', email='toto@detective.io')
            self.toto.set_password('tttooo')
            self.toto.save()

    def tearDown(self):
        if self.toto:
            self.toto.delete()

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
        users = User.objects
        self.assertEqual(len(users.all()), len(GraphUser.objects.all()))
        self.assertIsNotNone(users.get(email=self.toto.email))

    def test_reindex(self):
        c = Country(name="France", isoa3="FRA")
        c.save()
        # Catch output
        output = StringIO()
        sys.stdout = output
        # Reindex countries
        args = 'common.Country'
        call_command('reindex', args)
