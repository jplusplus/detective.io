from django.core.management       import call_command
from django.test                  import TestCase
from StringIO                     import StringIO 
from neo4django.auth.models import User
from ..models                     import Country
import sys
 

class CommandsTestCase(TestCase):

    def test_parseowl(self):
        # Catch output
        output = StringIO()
        sys.stdout = output
        # Must fail without argument
        with self.assertRaises(SystemExit):
            call_command('parseowl')

        args = "./app/data/ontology-v5.3.owl"
        call_command('parseowl', args)


    def test_createsuperuser(self):
        # Catch output
        output = StringIO()
        sys.stdout = output
        # Must fail without argument
        with self.assertRaises(SystemExit):
            call_command('createsuperuser', interactive=False)

        # Create the user
        call_command('createsuperuser', username="supertest", password="supersecret", email="super@email.com")
        # Check that it exists
        user = User.objects.get(username="supertest")
        self.assertEqual(user.is_superuser, True)


    def test_loadnodes(self):
        # Catch output
        output = StringIO()
        sys.stdout = output
        # Must fail without argument
        with self.assertRaises(SystemExit):
            call_command('loadnodes')
        # Import countries
        args = "./app/detective/apps/common/fixtures/countries.json"
        call_command('loadnodes', args)
        # Does France exists?
        self.assertGreater(len( Country.objects.filter(isoa3="FRA") ), 0)
        # Does USA exists?
        self.assertGreater(len( Country.objects.filter(isoa3="USA") ), 0)