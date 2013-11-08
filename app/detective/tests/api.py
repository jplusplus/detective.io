#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.detective.apps.common.models import Country
from app.detective.apps.energy.models import Organization, EnergyProject, Person
from django.contrib.auth.models       import User
from django.core.exceptions           import ObjectDoesNotExist
from tastypie.test                    import ResourceTestCase, TestApiClient
import json
import urllib


def find(function, iterable):
    for el in iterable:
        if function(el) is True:
            return el
    return None

class ApiTestCase(ResourceTestCase):

    def setUp(self):
        super(ApiTestCase, self).setUp()
        # Use custom api client
        self.api_client = TestApiClient()
        # Look for the test user
        self.username = u'tester'
        self.password = u'tester'
        try:
            self.user = User.objects.get(username=self.username)
            jpp       = Organization.objects.get(name=u"Journalism++")
            jg        = Organization.objects.get(name=u"Journalism Grant")
            fra       = Country.objects.get(name=u"France")
            self.pr = pr = Person.objects.get(name=u"Pierre Roméra")
            self.pb = pb = Person.objects.get(name=u"Pierre Bellon")

        except ObjectDoesNotExist:
            # Create the new user
            self.user = User.objects.create_user(self.username, 'tester@detective.io', self.password)
            self.user.is_staff = True
            self.user.is_superuser = True
            self.user.save()
            # Create related objects
            jpp = Organization(name=u"Journalism++")
            jpp.save()
            jg  = Organization(name=u"Journalism Grant")
            jg.save()
            fra = Country(name=u"France", isoa3=u"FRA")
            fra.save()

            self.pr = pr = Person(name=u"Pierre Roméra")
            pr.based_in.add(fra)
            pr.activity_in_organization.add(jpp)
            pr.save()

            self.pb = pb = Person(name=u"Pierre Bellon")
            pb.based_in.add(fra)
            pb.activity_in_organization.add(jpp)
            pb.save()

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
        self.rdf_jpp = {
            "label": u"Person that has activity in Journalism++",
            "object": {
                "id": 283,
                "model": u"common:Organization",
                "name": u"Journalism++"
            },
            "predicate": {
                "label": u"has activity in",
                "name": u"person_has_activity_in_organization+",
                "subject": u"energy:Person"
            },
            "subject": {
                "label": u"Person",
                "name": u"energy:Person"
            }
        }

    def get_credentials(self):
        return self.api_client.client.login(username=self.username, password=self.password)

    def test_user_login_succeed(self):
        auth = dict(username=u"tester", password=u"tester")
        resp = self.api_client.post('/api/common/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["success"], True)

    def test_user_login_failed(self):
        auth = dict(username=u"tester", password=u"wrong")
        resp = self.api_client.post('/api/common/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["success"], False)

    def test_user_logout_succeed(self):
        # First login
        auth = dict(username=u"tester", password=u"tester")
        self.api_client.post('/api/common/v1/user/login/', format='json', data=auth)
        # Then logout
        resp = self.api_client.get('/api/common/v1/user/logout/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["success"], True)

    def test_user_logout_failed(self):
        resp = self.api_client.get('/api/common/v1/user/logout/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["success"], False)

    def test_user_status_isnt_logged(self):
        resp = self.api_client.get('/api/common/v1/user/status/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["is_logged"], False)

    def test_user_status_is_logged(self):
        # Log in
        auth = dict(username=u"tester", password=u"tester")
        self.api_client.post('/api/common/v1/user/login/', format='json', data=auth)

        resp = self.api_client.get('/api/common/v1/user/status/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["is_logged"], True)

    def test_get_list_unauthorzied(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/energy/v1/energyproject/', format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get('/api/energy/v1/energyproject/?limit=20', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        # Number of element on the first page
        count = min(20, EnergyProject.objects.count() )
        self.assertEqual( len(self.deserialize(resp)['objects']), count)

    def test_post_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.post('/api/energy/v1/energyproject/', format='json', data=self.post_data_simple))

    def test_post_list(self):
        # Check how many are there first.
        count = EnergyProject.objects.count()
        self.assertHttpCreated(
            self.api_client.post('/api/energy/v1/energyproject/',
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
        resp  = self.api_client.post('/api/energy/v1/energyproject/',
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
        resp = self.api_client.get('/api/energy/v1/energyproject/mine/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(
            min(20, len(data["objects"])),
            EnergyProject.objects.filter(_author__contains=self.user.id).count()
        )

    def test_search_organization(self):
        resp = self.api_client.get('/api/energy/v1/organization/search/?q=Journalism', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # At least 2 results
        self.assertGreater( len(data.items()), 1 )

    def test_search_organization_wrong_page(self):
        resp = self.api_client.get('/api/energy/v1/organization/search/?q=Roméra&page=10000', format='json', authentication=self.get_credentials())
        self.assertHttpNotFound(resp)

    def test_cypher_detail(self):
        self.assertHttpNotFound(self.api_client.get('/api/common/v1/cypher/111/', format='json', authentication=self.get_credentials()))

    def test_cypher_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/common/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json'))

    def test_cypher_unauthorized(self):
        # Ensure the user isn't authorized to process cypher request
        self.user.is_staff = True
        self.user.is_superuser = False
        self.user.save()

        self.assertHttpUnauthorized(self.api_client.get('/api/common/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json', authentication=self.get_credentials()))

    def test_cypher_authorized(self):
        # Ensure the user IS authorized to process cypher request
        self.user.is_superuser = True
        self.user.save()

        self.assertValidJSONResponse(self.api_client.get('/api/common/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json', authentication=self.get_credentials()))

    def test_summary_list(self):
        self.assertHttpNotFound(self.api_client.get('/api/common/v1/summary/', format='json'))


    def test_countries_summary(self):
        resp = self.api_client.get('/api/common/v1/summary/countries/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # Only France is present
        self.assertGreater(len(data), 0)
        # We added 1 relation to France
        self.assertEqual("count" in data["FRA"], True)

    def test_forms_summary(self):
        resp = self.api_client.get('/api/common/v1/summary/forms/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # As many descriptors as models
        self.assertEqual( 11, len(data.items()) )

    def test_types_summary(self):
        resp = self.api_client.get('/api/common/v1/summary/types/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

    def test_search_summary(self):
        resp = self.api_client.get('/api/common/v1/summary/search/?q=Journalism', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # At least 2 results
        self.assertGreater( len(data.items()), 1 )

    def test_search_summary_wrong_page(self):
        resp = self.api_client.get('/api/common/v1/summary/search/?q=Journalism&page=-1', format='json', authentication=self.get_credentials())
        self.assertHttpNotFound(resp)

    def test_summary_human_search(self):
        query = "Person activity in Journalism"
        expected = "Person that has activity in Journalism++"
        expected2 = "Person that had activity previous in Journalism++"
        resp = self.api_client.get('/api/common/v1/summary/human/?q=%s' % query, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        data = json.loads(resp.content)
        self.assertGreater(len(data['objects']), 1)

    def test_rdf_search(self):
        # RDF object for persons that have activity in J++, we need to urlencode
        # the JSON string to avoid '+' loss
        rdf_str = urllib.quote(json.dumps(self.rdf_jpp))
        url = '/api/common/v1/summary/rdf_search/?limit=20&offset=0&q=%s' % rdf_str
        resp = self.api_client.get(url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        data = json.loads(resp.content)
        objects = data['objects']
        pr_t = find(lambda x: x['name'] == self.pr.name, objects)
        pb_t = find(lambda x: x['name'] == self.pb.name, objects)
        self.assertIsNotNone(pr_t)
        self.assertIsNotNone(pb_t)

