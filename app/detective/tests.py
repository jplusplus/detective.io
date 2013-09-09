from .models                import EnergyProject, Organization, Country
from django.core.exceptions import ObjectDoesNotExist
from django.db.models       import get_app, get_models
from neo4django.auth.models import User
from tastypie.test          import ResourceTestCase
import json

class ApiTestCase(ResourceTestCase):

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.detective = get_app("detective")
        self.models    = get_models(self.detective)
        # Look for the test user
        self.username  = 'tester'
        self.password  = 'tester'
        try:
            self.user = User.objects.get(username=self.username)  
            jpp       = Organization.objects.get(name="Journalism++")             
            jg        = Organization.objects.get(name="Journalism Grant")             
            fra       = Country.objects.get(name="France")             
        except ObjectDoesNotExist:            
            # Create the new user
            self.user = User.objects.create_user(self.username, 'tester@detective.io', self.password)
            self.user.is_staff = False
            self.user.is_superuser = False
            self.user.save()    
            # Create related objects
            jpp = Organization(name="Journalism++")
            jpp.save()
            jg  = Organization(name="Journalism Grant")
            jg.save()
            fra = Country(name="France", isoa3="FRA")
            fra.save()

        self.post_data_simple = {
            "name": "Lorem ispum TEST",
            "twitter_handle": "loremipsum"
        }

        self.post_data_related = {
            "name": "Lorem ispum TEST RELATED",
            "owner": [
                { "id": jpp.id },
                { "id": jg.id }
            ],
            "activity_in_country": [
                { "id": fra.id }
            ]
        }

    def get_credentials(self):        
        return self.create_basic(username=self.username, password=self.password)

    def test_user_login_succeed(self):
        auth = dict(username="tester", password="tester")
        resp = self.api_client.post('/api/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)       
        self.assertEqual(data["success"], True)

    def test_user_login_failed(self):
        auth = dict(username="tester", password="wrong")
        resp = self.api_client.post('/api/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)       
        self.assertEqual(data["success"], False)

    def test_user_logout_succeed(self):
        # First login
        auth = dict(username="tester", password="tester")
        self.api_client.post('/api/v1/user/login/', format='json', data=auth)
        # Then logout
        resp = self.api_client.get('/api/v1/user/logout/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)       
        self.assertEqual(data["success"], True)

    def test_user_logout_failed(self):
        resp = self.api_client.get('/api/v1/user/logout/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)       
        self.assertEqual(data["success"], False)

    def test_get_list_unauthorzied(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/v1/energyproject/', format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/energyproject/?limit=20', format='json', authentication=self.get_credentials())   
        self.assertValidJSONResponse(resp)
        # Number of element on the first page
        count = min(20, EnergyProject.objects.count() )        
        self.assertEqual( len(self.deserialize(resp)['objects']), count)

    def test_post_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.post('/api/v1/energyproject/', format='json', data=self.post_data_simple))

    def test_post_list(self):
        # Check how many are there first.
        count = EnergyProject.objects.count()
        self.assertHttpCreated(
            self.api_client.post('/api/v1/energyproject/', 
                format='json',
                data=self.post_data_simple,
                authentication=self.get_credentials()
            )
        )
        # Verify a new one has been added.
        self.assertEqual(EnergyProject.objects.count(), count+1)

    def test_post_list_related(self):
        # Check how many are there first.
        count = EnergyProject.objects.count()
        # Record API response to extract data
        resp  = self.api_client.post('/api/v1/energyproject/', 
            format='json',
            data=self.post_data_related,
            authentication=self.get_credentials()
        )
        # Vertify the request status
        self.assertHttpCreated(resp)        
        # Verify a new one has been added.
        self.assertEqual(EnergyProject.objects.count(), count+1)
        # Are the data readable?
        self.assertValidJSON(resp.content)
        # Parse data to verify relationship
        data = json.loads(resp.content)
        self.assertEqual(len(data["owner"]), len(self.post_data_related["owner"]))
        self.assertEqual(len(data["activity_in_country"]), len(self.post_data_related["activity_in_country"]))

    def test_mine(self):
        resp = self.api_client.get('/api/v1/energyproject/mine/', format='json', authentication=self.get_credentials())                   
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)        
        self.assertEqual(
            min(20, len(data["objects"])), 
            EnergyProject.objects.filter(_author__username="tester").count()
        )

    def test_cypher_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json'))

    def test_cypher_unauthorized(self):
        # Ensure the user isn't authorized to process cypher request
        self.user.is_staff = True
        self.user.is_superuser = False
        self.user.save() 

        self.assertHttpUnauthorized(self.api_client.get('/api/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json', authentication=self.get_credentials()))

    def test_cypher_authorized(self):
        # Ensure the user IS authorized to process cypher request
        self.user.is_superuser = True
        self.user.save()

        self.assertValidJSONResponse(self.api_client.get('/api/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json', authentication=self.get_credentials()))

    def test_countries_summary(self):
        resp = self.api_client.get('/api/v1/summary/countries/', format='json', authentication=self.get_credentials())  
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # Only France is present
        self.assertGreater(len(data), 0)
        # We added 1 relation to France 
        self.assertEqual("count" in data["FRA"], True)

    def test_forms_summary(self):
        resp = self.api_client.get('/api/v1/summary/forms/', format='json', authentication=self.get_credentials())  
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # As many descriptors as models
        self.assertEqual( len(self.models), len(data.items()) )
