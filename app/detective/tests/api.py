#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.detective.apps.common.message import SaltMixin
from app.detective.apps.common.models  import Country
from app.detective.apps.energy.models  import Organization, EnergyProject, Person
from datetime                          import datetime
from django.contrib.auth.models        import User
from django.core                       import signing
from tastypie.utils                    import timezone
from django.core.exceptions            import ObjectDoesNotExist
from registration.models               import RegistrationProfile
from tastypie.test                     import ResourceTestCase, TestApiClient
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
        self.email    = u'tester@detective.io'
        self.salt     = SaltMixin.salt
        try:
            self.user = User.objects.get(username=self.username)
            self.jpp  = jpp = Organization.objects.get(name=u"Journalism++")
            self.jg   = jg  = Organization.objects.get(name=u"Journalism Grant")
            self.fra  = fra = Country.objects.get(name=u"France")
            self.pr   = pr  = Person.objects.get(name=u"Pierre Roméra")
            self.pb   = pb  = Person.objects.get(name=u"Pierre Bellon")

        except ObjectDoesNotExist:
            # Create the new user
            self.user = User.objects.create_user(self.username, self.email, self.password)
            self.user.is_staff = True
            self.user.is_superuser = True
            self.user.save()
            # Create related objects
            self.jpp = jpp = Organization(name=u"Journalism++")
            jpp._author = [self.user.pk]
            jpp.founded = datetime(2011, 4, 3)
            jpp.website_url = 'http://jplusplus.com'
            jpp.save()

            self.jg = jg  = Organization(name=u"Journalism Grant")
            jg._author = [self.user.pk]
            jg.save()

            self.fra = fra = Country(name=u"France", isoa3=u"FRA")
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

    def tearDown(self):
        if self.user:
            self.user.delete()
        if self.jpp:
            self.jpp.delete()
        if self.jg:
            self.jg.delete()
        if self.fra:
            self.fra.delete()
        if self.pr:
            self.pr.delete()
        if self.pb:
            self.pb.delete()

    # Utility functions (Auth, operation etc.)
    def get_credentials(self):
        return self.api_client.client.login(username=self.username, password=self.password)

    def signup_user(self, user_dict):
        """ Utility method to signup through API """
        return self.api_client.post('/api/common/v1/user/signup/', format='json', data=user_dict)

    def patch_individual(self, scope=None, model_name=None, model_id=None,
                         patch_data=None, auth=None, skipAuth=False):
        if not skipAuth and not auth:
            auth = self.get_credentials()
        url = '/api/%s/v1/%s/%d/patch/' % (scope, model_name, model_id)
        return self.api_client.post(url, format='json', data=patch_data, authentication=auth)

    # All test functions
    def test_user_signup_succeed(self):
        """
        Test with proper data to signup user
        Expected: HTTT 201 (Created)
        """
        user_dict = dict(username=u"newuser", password=u"newuser", email=u"newuser@detective.io")
        resp = self.signup_user(user_dict)
        self.assertHttpCreated(resp)

    def test_user_signup_empty_data(self):
        """
        Test with empty data to signup user
        Expected: HTTP 400 (BadRequest)
        """
        user_dict = dict(username=u"", password=u"", email=u"")
        resp = self.signup_user(user_dict)
        self.assertHttpBadRequest(resp)

    def test_user_signup_no_data(self):
        resp = self.api_client.post('/api/common/v1/user/signup/', format='json')
        self.assertHttpBadRequest(resp)

    def test_user_signup_existing_user(self):
        user_dict = dict(username=self.username, password=self.password, email=self.email)
        resp = self.signup_user(user_dict)
        self.assertHttpForbidden(resp)

    def test_user_activate_succeed(self):
        user_dict = dict(username='myuser', password='mypassword', email='myuser@mywebsite.com')
        self.assertHttpCreated(self.signup_user(user_dict))
        innactive_user = User.objects.get(email=user_dict.get('email'))
        activation_profile = RegistrationProfile.objects.get(user=innactive_user)
        activation_key = activation_profile.activation_key
        resp_activate = self.api_client.get('/api/common/v1/user/activate/?token=%s' % activation_key)
        self.assertHttpOK(resp_activate)
        user = User.objects.get(email=user_dict.get('email'))
        self.assertTrue(user.is_active)

    def test_user_activate_fake_token(self):
        resp = self.api_client.get('/api/common/v1/user/activate/?token=FAKE')
        self.assertHttpForbidden(resp)

    def test_user_activate_no_token(self):
        resp = self.api_client.get('/api/common/v1/user/activate/')
        self.assertHttpBadRequest(resp)

    def test_user_activate_empty_token(self):
        resp = self.api_client.get('/api/common/v1/user/activate/?token')
        self.assertHttpBadRequest(resp)

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

    def test_reset_password_success(self):
        email = dict(email="tester@detective.io")
        resp = self.api_client.post('/api/common/v1/user/reset_password/', format='json', data=email)
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertTrue(data['success'])

    def test_reset_password_wrong_email(self):
        email = dict(email="wrong_email@detective.io")
        resp = self.api_client.post('/api/common/v1/user/reset_password/', format='json', data=email)
        self.assertEqual(resp.status_code in [302, 404])

    def test_reset_password_no_data(self):
        resp = self.api_client.post('/api/common/v1/user/reset_password/', format='json')
        self.assertHttpBadRequest(resp)

    def test_reset_password_empty_email(self):
        resp = self.api_client.post('/api/common/v1/user/reset_password/', format='json', data=dict(email=''))
        self.assertHttpBadRequest(resp)

    def test_reset_password_confirm_succes(self):
        """
        Test to successfuly reset a password with a new one.
        Expected:
            HTTP 200 - OK
        """
        token = signing.dumps(self.user.pk, salt=self.salt)
        password = "testtest"
        auth = dict(password=password, token=token)
        resp = self.api_client.post(
                '/api/common/v1/user/reset_password_confirm/',
                format='json',
                data=auth
            )
        self.assertValidJSON(resp.content)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        # we query users to get the latest user object (updated with password)
        user = User.objects.get(email=self.user.email)
        self.assertTrue(user.check_password(password))

    def test_reset_password_confirm_no_data(self):
        """
        Test on reset_password_confirm API endpoint without any data.
        Expected response:
            HTTP 400 (BadRequest).
        Explanation:
            Every request on /reset_password_confirm/ must have a JSON data payload.
            {
                password: ... // the password to reset"
                token:    ... // the reset password token (received by emai)
            }
        """
        resp = self.api_client.post('/api/common/v1/user/reset_password_confirm/', format='json')
        self.assertHttpBadRequest(resp)
        self.assertIsNotNone(resp.content)

    def test_reset_password_confirm_empty_data(self):
        """
        Test on reset_password_confirm API endpoint with empty data:
        {
            password: ""
            token: ""
        }
        Expected result:
            HTTP 400 (BadRequest)
        Explanation:
            A reset_password_confirm request must have a password and should be
            authenticated with a token.
        """
        auth = dict(password='', token='')
        resp = self.api_client.post('/api/common/v1/user/reset_password_confirm/', format='json', data=auth)
        self.assertHttpBadRequest(resp)

    def test_reset_password_confirm_fake_token(self):
        """
        Test on reset_password_confirm API endpoint with empty data:
        {
            password: ""
            token: ""
        }
        Expected result:
            HTTP 403 (Forbidden)
        Explanation:
            A reset_password_confirm request should be authenticated with a valid
            token.
        """
        fake_token = 'f4k:t0k3N'
        auth = dict(password='newpassword', token=fake_token)
        resp = self.api_client.post(
                '/api/common/v1/user/reset_password_confirm/',
                format='json',
                data=auth
            )
        self.assertHttpForbidden(resp)

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
        self.assertEqual(resp.status_code in [302, 404])

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

    def test_summary_mine_success(self):
        resp = self.api_client.get('/api/common/v1/summary/mine/', authentication=self.get_credentials(), format='json')
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        objects = data['objects']
        jpp_t = find(lambda x: x['label'] == self.jpp.name, objects)
        jg_t  = find(lambda x: x['label'] == self.jg.name,  objects)
        self.assertIsNotNone(jpp_t)
        self.assertIsNotNone(jg_t)

    def test_summary_mine_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/common/v1/summary/mine/', format='json'))

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
        self.assertEqual(resp.status_code in [302, 404])

    def test_summary_human_search(self):
        query = "Person activity in Journalism"
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

    def test_patch_individual_date(self):
        """
        Test a patch request on an invidividual's date attribute.
        Request: /api/energy/v1/organization/
        Expected: HTTP 200 (OK)
        """
        # date are subject to special process with patch method.
        new_date  = datetime(2011, 4, 1, 0, 0, 0, 0)
        data = {
            'founded': new_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }
        args = {
            'scope'      : 'energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data
        }
        resp = self.patch_individual(**args)
        self.assertHttpOK(resp)
        self.assertValidJSONResponse(resp)
        updated_jpp = Organization.objects.get(name=self.jpp.name)
        self.assertEqual(timezone.make_naive(updated_jpp.founded), new_date)



    def test_patch_individual_website(self):

        jpp_url  = 'http://jplusplus.org'
        data = {
            'website_url': jpp_url,
        }
        args = {
            'scope'      : 'energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data
        }
        resp = self.patch_individual(**args)
        self.assertHttpOK(resp)
        self.assertValidJSONResponse(resp)
        updated_jpp = Organization.objects.get(name=self.jpp.name)
        self.assertEqual(updated_jpp.website_url, jpp_url)

    def test_patch_individual_unauthorized(self):
        jpp_url  = 'http://jplusplus.org'
        data = {
            'website_url': jpp_url,
        }
        args = {
            'scope'      : 'energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data,
            'skipAuth'   : True,
        }
        resp = self.patch_individual(**args)
        self.assertHttpUnauthorized(resp)

    def test_patch_individual_not_found(self):
        jpp_url  = 'http://jplusplus.org'
        data = {
            'website_url': jpp_url,
        }
        args = {
            'scope'      : 'energy',
            'model_id'   : 1337,
            'model_name' : 'organization',
            'patch_data' : data,
        }
        resp = self.patch_individual(**args)
        self.assertEqual(resp.status_code in [302, 404])
