#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.detective.models                import Topic, TopicSkeleton, PLANS_CHOICES
from app.detective.topics.common.message import SaltMixin
from app.detective.topics.energy.models  import Organization, EnergyProject, Person, Country
from app.detective                       import utils
from datetime                            import datetime
from django.conf                         import settings
from django.contrib.auth.models          import User, Group
from django.core                         import management, signing
from django.core.files                   import File
from registration.models                 import RegistrationProfile
from tastypie.test                       import ResourceTestCase, TestApiClient
from tastypie.utils                      import timezone
from neo4django.db                       import connection as gdb
import json
import urllib

def find(function, iterable):
    for el in iterable:
        if function(el) is True:
            return el
    return None

class ApiTestCase(ResourceTestCase):

    fixtures = ['app/detective/fixtures/default_topics.json',
                'app/detective/fixtures/default_skeletons.json',
                'app/detective/fixtures/tests_topics.json',
                'app/detective/fixtures/tests_pillen.json',
                'app/detective/fixtures/tests_double_entities.json',
                'app/detective/fixtures/search_terms.json',]

    def setUp(self):
        super(ApiTestCase, self).setUp()
        # Use custom api client
        self.api_client = TestApiClient()
        self.salt       = SaltMixin.salt

        self.super_username = 'super_user'
        self.super_password = 'super_user'
        self.super_email    = 'super_user@detective.io'

        self.contrib_username = 'contrib_user'
        self.contrib_password = 'contrib_user'
        self.contrib_email    = 'contrib_user@detective.io'

        self.lambda_username = 'lambda_user'
        self.lambda_password = 'lambda_user'
        self.lambda_email    = 'lambda_user@detective.io'

        contributors = Group.objects.get(name='energy_contributor')

        test_contributors = Topic.objects.get(slug='test-topic').get_contributor_group()

        # Create the new user users
        super_user = User.objects.create(
            username=self.super_username,
            email=self.super_email,
            is_staff=True,
            is_superuser = True
        )

        super_user.set_password(self.super_password)
        super_user.save()
        self.super_user = super_user

        contrib_user = User.objects.create(
            username=self.contrib_username,
            email=self.contrib_email,
            is_active=True
        )
        # put the user in the best plan
        profile = contrib_user.detectiveprofileuser
        profile.plan = PLANS_CHOICES[-1][0]
        profile.save()
        contrib_user.groups.add(contributors)
        contrib_user.groups.add(test_contributors)
        contrib_user.set_password(self.contrib_password)
        contrib_user.save()
        self.contrib_user = contrib_user

        lambda_user = User.objects.create(
            username=self.lambda_username,
            email=self.lambda_email,
        )

        lambda_user.set_password(self.lambda_password)
        lambda_user.save()
        self.lambda_user = lambda_user

        # Create related objects
        self.jpp = Organization(name=u"Journalism++")
        self.jpp._author = [super_user.pk]
        self.jpp.founded = datetime(2011, 4, 3)
        self.jpp.website_url = 'http://jplusplus.com'
        self.jpp.save()

        self.jg  = Organization(name=u"Journalism Grant")
        self.jg._author = [super_user.pk]
        self.jg.save()

        self.fra = Country(name=u"France", isoa3=u"FRA")
        self.fra.save()

        self.pr = Person(name=u"Pierre Roméra")
        self.pr.based_in.add(self.fra)
        self.pr.activity_in_organization.add(self.jpp)
        self.pr.save()

        self.pb = Person(name=u"Pierre Bellon")
        self.pb.based_in.add(self.fra)
        self.pb.activity_in_organization.add(self.jpp)
        self.pb.save()
        # Creates Christmas topic
        ontology = File(open(settings.DATA_ROOT + "/ontology-v5.7.owl"))
        self.christmas = Topic(slug=u"christmas", title="It's christmas!", ontology_as_owl=ontology, author=super_user)
        self.christmas.save()
        # Creates Thanksgiving topic
        self.thanksgiving = Topic(slug=u"thanksgiving", title="It's thanksgiving!", ontology_as_owl=ontology, author=super_user)
        self.thanksgiving.save()

        self.post_data_simple = {
            "name": "Lorem ispum TEST",
            "twitter_handle": "loremipsum"
        }

        self.post_data_related = {
            "name": "Lorem ispum TEST RELATED",
            "owner": [
                { "id": self.jpp.id },
                { "id": self.jg.id }
            ],
            "activity_in_country": [
                { "id": self.fra.id }
            ]
        }

        self.rdf_jpp = {
            "label": u"Person that has activity in Journalism++",
            "object": {
                "id": self.jpp.id,
                "model": u"Organization",
                "name": u"Journalism++"
            },
            "predicate": {
                "label": u"has activity in",
                "name": u"activity_in_organization",
                "subject": u"Person"
            },
            "subject": {
                "label": u"Person",
                "name": u"Person"
            }
        }

    def cleanModel(self, model_instance):
        if model_instance:
            model_instance.delete()

    def tearDown(self):
        # Clean & delete generated data
        # individuals
        self.cleanModel(self.jpp) # organization
        self.cleanModel(self.jg) # organization
        self.cleanModel(self.fra) # country
        self.cleanModel(self.pr) # people
        self.cleanModel(self.pb) # people
        # Simply flush the database
        management.call_command('flush', verbosity=0, interactive=False)

    def create_user(self, username='default', password=None, email=None, plan=None):
        if not email:
            email = "%s@test.me" % username

        if not plan:
            plan = PLANS_CHOICES[-1][0]

        if not password:
            password = username

        user = User.objects.create(
            username=username,
            email=email,
            is_active=True
        )
        # put the user in the best plan
        profile = user.detectiveprofileuser
        profile.plan = plan
        profile.save()
        user.set_password(password)
        user.save()
        return user

    # Utility functions (Auth, operation etc.)
    def login(self, username, password):
        return self.api_client.client.login(username=username, password=password)

    def logout(self):
        return self.api_client.client.logout()

    def get_super_credentials(self):
        return self.login(self.super_username, self.super_password)

    def get_contrib_credentials(self):
        return self.login(self.contrib_username, self.contrib_password)

    def get_lambda_credentials(self):
        return self.login(self.lambda_username, self.lambda_password)

    def signup_user(self, user_dict):
        """ Utility method to signup through API """
        return self.api_client.post('/api/detective/common/v1/user/signup/', format='json', data=user_dict)

    def patch_individual(self, scope, model_name, model_id,
                         patch_data=None, auth=None, skip_auth=False):
        if not skip_auth and not auth:
            auth = self.get_super_credentials()
        url = '/api/%s/v1/%s/%d/patch/' % (scope, model_name, model_id)
        return self.api_client.post(url, format='json', data=patch_data, authentication=auth)

    def check_permissions(self, permissions=None, user=None):
        user_permissions = list(user.get_all_permissions())
        self.assertEqual(len(user_permissions), len(permissions))
        for perm in user_permissions:
            self.assertTrue(perm in permissions)

    def topic_to_dict(self, topic):
        return {
            'description': topic.description,
            'title': topic.title,
            'slug': topic.slug,
            'ontology_as_json': topic.ontology_as_json,
            'ontology_as_owl': topic.ontology_as_owl,
            'ontology_as_mod': topic.ontology_as_mod,
            'about': topic.about,
            'background': topic.background,
            'public': topic.public,
            'featured': topic.featured,
            'author': topic.author
        }


class TopicApiTestCase(ApiTestCase):

    def setUp(self):
        super(TopicApiTestCase, self).setUp()

    def tearDown(self):
        super(TopicApiTestCase, self).tearDown()

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
        resp = self.api_client.post('/api/detective/common/v1/user/signup/', format='json')
        self.assertHttpBadRequest(resp)

    def test_user_signup_existing_user(self):
        user_dict = dict(username=self.super_username, password=self.super_password, email=self.super_email)
        resp = self.signup_user(user_dict)
        self.assertHttpForbidden(resp)

    def test_user_activate_succeed(self):
        user_dict = dict(username='myuser', password='mypassword', email='myuser@mywebsite.com')
        self.assertHttpCreated(self.signup_user(user_dict))
        innactive_user = User.objects.get(email=user_dict.get('email'))
        activation_profile = RegistrationProfile.objects.get(user=innactive_user)
        activation_key = activation_profile.activation_key
        resp_activate = self.api_client.get('/api/detective/common/v1/user/activate/?token=%s' % activation_key)
        self.assertHttpOK(resp_activate)
        user = User.objects.get(email=user_dict.get('email'))
        self.assertTrue(user.is_active)

    def test_user_activate_fake_token(self):
        resp = self.api_client.get('/api/detective/common/v1/user/activate/?token=FAKE')
        self.assertHttpForbidden(resp)

    def test_user_activate_no_token(self):
        resp = self.api_client.get('/api/detective/common/v1/user/activate/')
        self.assertHttpBadRequest(resp)

    def test_user_activate_empty_token(self):
        resp = self.api_client.get('/api/detective/common/v1/user/activate/?token')
        self.assertHttpBadRequest(resp)

    def test_user_contrib_login_succeed(self):
        auth = dict(username=self.contrib_username, password=self.contrib_password)
        resp = self.api_client.post('/api/detective/common/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        data = json.loads(resp.content)
        self.assertTrue(data["success"])
        self.check_permissions(permissions=data.get("permissions"), user=self.contrib_user)

    def test_user_login_succeed(self):
        auth = dict(username=self.super_username, password=self.super_password)
        resp = self.api_client.post('/api/detective/common/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["success"], True)

    def test_user_login_failed(self):
        auth = dict(username=self.super_username, password=u"awrongpassword")
        resp = self.api_client.post('/api/detective/common/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["success"], False)

    def test_user_logout_succeed(self):
        # First login
        auth = dict(username=self.super_username, password=self.super_password)
        self.api_client.post('/api/detective/common/v1/user/login/', format='json', data=auth)
        # Then logout
        resp = self.api_client.get('/api/detective/common/v1/user/logout/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["success"], True)

    def test_user_logout_failed(self):
        resp = self.api_client.get('/api/detective/common/v1/user/logout/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["success"], False)

    def test_user_permissions_is_logged(self):
        auth = dict(username=self.contrib_username, password=self.contrib_password)
        self.api_client.post('/api/detective/common/v1/user/login/', format='json', data=auth)
        resp = self.api_client.get('/api/detective/common/v1/user/permissions/', format='json')
        self.assertValidJSON(resp.content)
        data = json.loads(resp.content)
        self.check_permissions(permissions=data.get("permissions"), user=self.contrib_user)

    def test_user_permissions_isnt_logged(self):
        resp = self.api_client.get('/api/detective/common/v1/user/permissions/', format='json')
        self.assertHttpUnauthorized(resp)


    def test_user_status_isnt_logged(self):
        resp = self.api_client.get('/api/detective/common/v1/user/status/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["is_logged"], False)

    def test_user_status_is_logged(self):
        # Log in
        auth = dict(username=self.super_username, password=self.super_password)
        resp = self.api_client.post('/api/detective/common/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])

        resp = self.api_client.get('/api/detective/common/v1/user/status/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["is_logged"], True)

    def test_contrib_user_status_is_logged(self):
        # Log in
        auth = dict(username=self.contrib_username, password=self.contrib_password, remember_me=True)
        resp = self.api_client.post('/api/detective/common/v1/user/login/', format='json', data=auth)
        self.assertValidJSON(resp.content)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])

        resp = self.api_client.get('/api/detective/common/v1/user/status/', format='json')
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual(data["is_logged"], True)


    def test_reset_password_success(self):
        email = dict(email=self.super_email)
        resp = self.api_client.post('/api/detective/common/v1/user/reset_password/', format='json', data=email)
        self.assertValidJSON(resp.content)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertTrue(data['success'])

    def test_reset_password_wrong_email(self):
        email = dict(email="wrong_email@detective.io")
        resp = self.api_client.post('/api/detective/common/v1/user/reset_password/', format='json', data=email)
        self.assertEqual(resp.status_code in [302, 404], True)

    def test_reset_password_no_data(self):
        resp = self.api_client.post('/api/detective/common/v1/user/reset_password/', format='json')
        self.assertHttpBadRequest(resp)

    def test_reset_password_empty_email(self):
        resp = self.api_client.post('/api/detective/common/v1/user/reset_password/', format='json', data=dict(email=''))
        self.assertHttpBadRequest(resp)

    def test_reset_password_confirm_succes(self):
        """
        Test to successfuly reset a password with a new one.
        Expected:
            HTTP 200 - OK
        """
        token = signing.dumps(self.super_user.pk, salt=self.salt)
        password = "testtest"
        auth = dict(password=password, token=token)
        resp = self.api_client.post(
                '/api/detective/common/v1/user/reset_password_confirm/',
                format='json',
                data=auth
            )
        self.assertValidJSON(resp.content)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        # we query users to get the latest user object (updated with password)
        user = User.objects.get(email=self.super_user.email)
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
        resp = self.api_client.post('/api/detective/common/v1/user/reset_password_confirm/', format='json')
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
        resp = self.api_client.post('/api/detective/common/v1/user/reset_password_confirm/', format='json', data=auth)
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
                '/api/detective/common/v1/user/reset_password_confirm/',
                format='json',
                data=auth
            )
        self.assertHttpForbidden(resp)

    def test_get_list_json(self):
        resp = self.api_client.get('/api/detective/energy/v1/energyproject/?limit=20', format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)
        # Number of element on the first page
        count = min(20, EnergyProject.objects.count())
        self.assertEqual( len(self.deserialize(resp)['objects']), count)

    def test_post_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.post('/api/detective/energy/v1/energyproject/', format='json', data=self.post_data_simple))

    def test_post_list_staff(self):
        # Check how many are there first.
        count = EnergyProject.objects.count()
        resp = self.api_client.post('/api/detective/energy/v1/energyproject/',
                format='json',
                data=self.post_data_simple,
                authentication=self.get_super_credentials()
        )
        self.assertHttpCreated( resp )
        # Verify a new one has been added.
        self.assertEqual(EnergyProject.objects.count(), count+1)

    def test_post_list_contributor(self):
        # Check how many are there first.
        count = EnergyProject.objects.count()
        self.assertHttpCreated(
            self.api_client.post('/api/detective/energy/v1/energyproject/',
                format='json',
                data=self.post_data_simple,
                authentication=self.get_contrib_credentials()
            )
        )
        # Verify a new one has been added.
        self.assertEqual(EnergyProject.objects.count(), count+1)

    def test_post_list_lambda(self):
        self.assertHttpUnauthorized(
            self.api_client.post('/api/detective/energy/v1/energyproject/',
                format='json',
                data=self.post_data_simple,
                authentication=self.get_lambda_credentials()
            )
        )

    def test_post_list_related(self):
        # Check how many are there first.
        count = EnergyProject.objects.count()
        # Record API response to extract data
        resp  = self.api_client.post('/api/detective/energy/v1/energyproject/',
            format='json',
            data=self.post_data_related,
            authentication=self.get_super_credentials()
        )
        # Vertify the request status
        self.assertHttpCreated(resp)
        # Verify a new one has been added.
        self.assertEqual(EnergyProject.objects.count(), count+1)
        # Are the data readable?
        self.assertValidJSON(resp.content)
        # Parse data to verify relationship
        data = json.loads(resp.content)
        # Since only the name is send during creation,
        # we have to patch the new object now
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : data["id"],
            'model_name' : 'energyproject',
            'patch_data' : self.post_data_related
        }
        resp = self.patch_individual(**args)
        # Are the data readable?
        self.assertValidJSON(resp.content)
        # Parse data to verify relationship
        data = json.loads(resp.content)
        self.assertEqual(len(data["owner"]), len(self.post_data_related["owner"]))
        self.assertEqual(len(data["activity_in_country"]), len(self.post_data_related["activity_in_country"]))

    def test_mine(self):
        resp = self.api_client.get('/api/detective/energy/v1/organization/mine/', format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual( len(data["objects"]), 2)

    def test_mine_empty(self):
        resp = self.api_client.get('/api/detective/energy/v1/organization/mine/', format='json')
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        self.assertEqual( len(data["objects"]), 0)

    def test_search_organization(self):
        resp = self.api_client.get('/api/detective/energy/v1/organization/search/?q=Journalism', format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # At least 2 results
        self.assertGreater( len(data.items()), 1 )

    def test_search_organization_wrong_page(self):
        resp = self.api_client.get('/api/detective/energy/v1/organization/search/?q=Roméra&page=10000', format='json', authentication=self.get_super_credentials())
        self.assertEqual(resp.status_code in [302, 404], True)

    def test_cypher_detail(self):
        resp = self.api_client.get('/api/detective/common/v1/cypher/111/', format='json', authentication=self.get_super_credentials())
        self.assertTrue(resp.status_code in [302, 404])

    def test_cypher_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/detective/common/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json'))

    def test_cypher_unauthorized(self):
        # Ensure the user isn't authorized to process cypher request
        self.super_user.is_staff = True
        self.super_user.is_superuser = False
        self.super_user.save()

        self.assertHttpUnauthorized(self.api_client.get('/api/detective/common/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json', authentication=self.get_super_credentials()))

    def test_cypher_authorized(self):
        # Ensure the user IS authorized to process cypher request
        self.super_user.is_superuser = True
        self.super_user.save()

        self.assertValidJSONResponse(self.api_client.get('/api/detective/common/v1/cypher/?q=START%20n=node%28*%29RETURN%20n;', format='json', authentication=self.get_super_credentials()))

    def test_summary_list(self):
        resp = self.api_client.get('/api/detective/common/v1/summary/', format='json')
        self.assertEqual(resp.status_code in [302, 404], True)

    def test_summary_mine_success(self):
        resp = self.api_client.get('/api/detective/energy/v1/summary/mine/', authentication=self.get_super_credentials(), format='json')
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        objects = data['objects']
        self.assertIsNotNone(find(lambda x: x['label'] == self.jpp.name, objects))
        self.assertIsNotNone(find(lambda x: x['label'] == self.jg.name,  objects))

    def test_summary_mine_unauthenticated(self):
        resp = self.api_client.get('/api/detective/energy/v1/summary/mine/', format='json')
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        objects = data['objects']
        self.assertEqual(len(objects), 0)

    def test_countries_summary(self):
        resp = self.api_client.get('/api/detective/energy/v1/summary/countries/', format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # Only France is present
        self.assertGreater(len(data), 0)
        # We added 1 relation to France
        self.assertEqual("count" in data["FRA"], True)

    def test_forms_summary(self):
        resp = self.api_client.get('/api/detective/energy/v1/summary/forms/', format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # As many descriptors as models
        self.assertEqual( 11, len(data.items()) )

    def test_types_summary(self):
        resp = self.api_client.get('/api/detective/energy/v1/summary/types/', format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)

    def test_search_summary(self):
        resp = self.api_client.get('/api/detective/energy/v1/summary/search/?q=Journalism', format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # At least 2 results
        self.assertGreater( len(data.items()), 1 )

    def test_search_summary_wrong_offset(self):
        resp = self.api_client.get('/api/detective/energy/v1/summary/search/?q=Journalism&offset=-1', format='json', authentication=self.get_super_credentials())
        self.assertEqual(resp.status_code in [302, 404], True)

    def test_summary_human_search(self):
        query = "Person activity in Journalism"
        resp = self.api_client.get('/api/detective/energy/v1/summary/human/?q=%s' % query, format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)
        data = json.loads(resp.content)
        self.assertGreater(len(data['objects']), 1)

    def test_rdf_search(self):
        # RDF object for persons that have activity in J++, we need to urlencode
        # the JSON string to avoid '+' loss
        rdf_str = urllib.quote(json.dumps(self.rdf_jpp))
        url = '/api/detective/energy/v1/summary/rdf_search/?limit=20&offset=0&q=%s' % rdf_str
        resp = self.api_client.get(url, format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)
        data = json.loads(resp.content)
        objects = data['objects']
        self.assertIsNotNone(find(lambda x: x['name'] == self.pr.name, objects))
        self.assertIsNotNone(find(lambda x: x['name'] == self.pb.name, objects))

    def test_patch_individual_date_staff(self):
        """
        Test a patch request on an invidividual's date attribute.
        Request: /api/detective/energy/v1/organization/
        Expected: HTTP 200 (OK)
        """
        # date are subject to special process with patch method.
        new_date  = datetime(2011, 4, 1, 0, 0, 0, 0)
        data = {
            'founded': new_date.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data
        }
        resp = self.patch_individual(**args)
        self.assertHttpOK(resp)
        self.assertValidJSONResponse(resp)
        updated_jpp = Organization.objects.get(name=self.jpp.name)
        self.assertEqual(timezone.make_naive(updated_jpp.founded), timezone.make_naive(new_date))

    def test_patch_individual_date_staff_with_null(self):
        """
        Test a patch request on an invidividual's date attribute.
        Request: /api/detective/energy/v1/organization/
        Expected: HTTP 200 (OK)
        """
        # date are subject to special process with patch method.
        data = {
            'founded': None,
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data
        }
        resp = self.patch_individual(**args)
        self.assertHttpOK(resp)
        self.assertValidJSONResponse(resp)
        updated_jpp = Organization.objects.get(name=self.jpp.name)
        self.assertTrue(updated_jpp.founded in [None, ''])

    def test_patch_individual_website_staff(self):
        jpp_url  = 'http://jplusplus.org/'
        data = {
            'website_url': jpp_url,
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data
        }
        resp = self.patch_individual(**args)
        self.assertHttpOK(resp)
        self.assertValidJSONResponse(resp)
        updated_jpp = Organization.objects.get(name=self.jpp.name)
        self.assertEqual(updated_jpp.website_url, jpp_url)

    def test_patch_individual_website_staff_with_null(self):
        jpp_url  = 'http://jplusplus.org/'
        data = {
            'website_url': None,
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data
        }
        resp = self.patch_individual(**args)
        self.assertHttpOK(resp)
        self.assertValidJSONResponse(resp)
        updated_jpp = Organization.objects.get(name=self.jpp.name)
        self.assertTrue(updated_jpp.website_url in ['', None])

    def test_patch_individual_website_unauthenticated(self):
        jpp_url  = 'http://jplusplus.org/'
        data = {
            'website_url': jpp_url,
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data,
            'skip_auth'  : True,
        }
        resp = self.patch_individual(**args)
        self.assertHttpUnauthorized(resp)

    def test_patch_individual_website_contributor(self):
        jpp_url  = 'http://www.jplusplus.org/'
        data = {
            'website_url': jpp_url,
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data,
            'auth'       : self.get_contrib_credentials(),
        }
        resp = self.patch_individual(**args)
        self.assertHttpOK(resp)
        self.assertValidJSONResponse(resp)
        updated_jpp = Organization.objects.filter(name=self.jpp.name)[0]
        self.assertEqual(updated_jpp.website_url, jpp_url)

    def test_patch_individual_website_lambda(self):
        jpp_url  = 'http://bam.jplusplus.org/'
        data = {
            'website_url': jpp_url,
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data,
            'auth'       : self.get_lambda_credentials(),
        }
        resp = self.patch_individual(**args)
        self.assertHttpUnauthorized(resp)


    def test_patch_individual_not_found(self):
        jpp_url  = 'http://jplusplus.org/'
        data = {
            'website_url': jpp_url,
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : 1337,
            'model_name' : 'organization',
            'patch_data' : data,
        }
        resp = self.patch_individual(**args)
        self.assertTrue(resp.status_code in [302, 404])

    def test_patch_with_composite_relations(self):
        """

        Test if I can link one entity to many entities without overwritting previous relations
        ref : https://github.com/jplusplus/detective.io/issues/452
        Depends of fixtures/tests_pillen.json

        """
        def get_relationship_reference(pilule_id, mol_id):
            resp = self.api_client.get('/api/detective/test-pillen/v1/pill/%d/relationships/molecules_contained/%d/' % (pilule_id, mol_id), follow=True, format='json')
            self.assertValidJSONResponse(resp)
            resp = json.loads(resp.content)
            return resp

        def patch_pilule_and_mols(pilule_id, mol_ids=[]):
            patch_args = dict(
                scope      = 'detective/test-pillen',
                model_name = 'pill',
                model_id   = pilule_id,
                patch_data = {"molecules_contained" : [{"id":mol_id} for mol_id in mol_ids]})
            resp = self.patch_individual(**patch_args)
            self.assertValidJSONResponse(resp)

        def add_properties(pilule_id, molecule_id, property):
            relation_id   = get_relationship_reference(pilule_id, molecule_id)["_relationship"]
            relation_args = {
                "_endnodes"                 : [pilule_id, molecule_id],
                "_relationship"             : relation_id,
                "quantity_(in_milligrams)." : property
            }
            PillMoleculesContainedMoleculeProperties.objects.create(**relation_args)
            relation = get_relationship_reference(pilule_id, molecule_id)
            self.assertIn("quantity_(in_milligrams).", relation.keys()        , relation)
            self.assertEqual(relation["quantity_(in_milligrams)."], property  , relation)

        topic    = Topic.objects.get(slug='test-pillen')
        models   = topic.get_models_module()
        # get models
        PillMoleculesContainedMoleculeProperties = models.PillMoleculesContainedMoleculeProperties
        Molecule                                 = models.Molecule
        Pill                                     = models.Pill
        # create entities
        pilulea       = Pill    .objects.create(name='pilule A')
        mola          = Molecule.objects.create(name="molecule A")
        molb          = Molecule.objects.create(name="molecule B")
        molc          = Molecule.objects.create(name="molecule C")
        mold_wo_infos = Molecule.objects.create(name="molecule D")
        # start to patch
        patch_pilule_and_mols(pilulea.id, [mola.id])
        add_properties(pilulea.id, mola.id, "10")
        # test to remove a relation
        patch_pilule_and_mols(pilulea.id, [])
        # check deletion
        relation = get_relationship_reference(pilulea.id, mola.id)
        self.assertNotIn("quantity_(in_milligrams).", relation.keys() , relation)
        self.assertIsNone(relation["_relationship"] , relation)
        # continue to add more relations
        def patch_mol_b_c_d():
            patch_pilule_and_mols(pilulea.id, [molb.id])
            patch_pilule_and_mols(pilulea.id, [molb.id, molc.id, mold_wo_infos.id])
            add_properties(pilulea.id, molb.id, "20")
            add_properties(pilulea.id, molc.id, "30")
        patch_mol_b_c_d()
        #remove all again
        patch_pilule_and_mols(pilulea.id, [])
        # and create again
        patch_mol_b_c_d()
        #check final states
        relation_pama = get_relationship_reference(pilulea.id, mola.id)
        relation_pamb = get_relationship_reference(pilulea.id, molb.id)
        relation_pamc = get_relationship_reference(pilulea.id, molc.id)
        relation_pamd = get_relationship_reference(pilulea.id, mold_wo_infos.id)
        # pila-mola
        self.assertNotIn("quantity_(in_milligrams).", relation_pama.keys() , relation_pama)
        self.assertIsNone(relation["_relationship"]                        , relation_pama)
        # pila-molb
        self.assertIn("quantity_(in_milligrams).", relation_pamb.keys()    , relation_pamb)
        self.assertEqual(relation_pamb["quantity_(in_milligrams)."], "20"  , relation_pamb)
        self.assertTrue(int(relation_pamb["_relationship"]) > 0            , relation_pamb)
        self.assertTrue(relation_pamb["_endnodes"], [pilulea.id, molb.id])
        # pila-molc
        self.assertIn("quantity_(in_milligrams).", relation_pamc.keys()    , relation_pamc)
        self.assertEqual(relation_pamc["quantity_(in_milligrams)."], "30"  , relation_pamc)
        self.assertTrue(int(relation_pamc["_relationship"]) > 0            , relation_pamc)
        self.assertTrue(relation_pamc["_endnodes"], [pilulea.id, molc.id])
        # pila-mold
        self.assertNotIn("quantity_(in_milligrams).", relation_pamd.keys() , relation_pamd)
        self.assertTrue(int(relation_pamd["_relationship"]) > 0            , relation_pamd)
        self.assertTrue(relation_pamd["_endnodes"], [pilulea.id, mold_wo_infos.id])
        # check if orphans exist. It shouldn't !
        def check_if_orphans_exist():
            orphans_count = 0
            for Model in topic.get_models():
                fields = utils.get_model_fields(Model)
                for field in fields:
                    if field["rel_type"] and field["direction"] == "out" and "through" in field["rules"]:
                        ids= []
                        for entity in Model.objects.all():
                            ids.extend([_.id for _ in entity.node.relationships.all()])
                        Properties = field["rules"]["through"]
                        for info in Properties.objects.all():
                            if info._relationship not in ids:
                                orphans_count += 1
            self.assertEqual(orphans_count, 0)
        # remove one molecule
        molb.delete()
        check_if_orphans_exist()
        pilulea.delete()
        check_if_orphans_exist()

    def test_patch_relations(self):
        """

        Test if I can link one entity to many entities without overwritting previous relations
        Depends of fixtures/tests_double_entities.json

        """
        def get_relationship_reference(event_id, victim_id):
            resp = self.api_client.get('/api/detective/test-double-entities/v1/event/%d/relationships/harmed/%d/' % (event_id, victim_id), follow=True, format='json')
            self.assertValidJSONResponse(resp)
            resp = json.loads(resp.content)
            return resp

        def patch_event_and_victim(event_id, victim_ids=[]):
            patch_args = dict(
                scope      = 'detective/test-double-entities',
                model_name = 'event',
                model_id   = event_id,
                patch_data = {"harmed" : [{"id":vic_id} for vic_id in victim_ids]})
            resp = self.patch_individual(**patch_args)
            self.assertValidJSONResponse(resp)

        topic                     = Topic.objects.get(slug='test-double-entities')
        # get models
        models                    = topic.get_models_module()
        Country                   = models.Country
        Event                     = models.Event
        Victim                    = models.Victim
        VictimDeadEventProperties = models.VictimDeadEventProperties
        # create entities
        event_a  = Event.objects.create(name='event A')
        victim_a = Victim.objects.create(name="victim A")
        victim_b = Victim.objects.create(name="victim B")
        # start to patch
        patch_event_and_victim(event_a.id, [victim_a.id])
        # check
        relation_a = get_relationship_reference(event_a.id, victim_a.id)
        self.assertTrue(int(relation_a["_relationship"]) > 0 , relation_a)
        self.assertTrue(relation_a["_endnodes"]              , [event_a.id, victim_a.id])
        patch_event_and_victim(event_a.id, [victim_a.id, victim_b.id])
        # check again
        relation_a = get_relationship_reference(event_a.id, victim_a.id)
        self.assertTrue(int(relation_a["_relationship"]) > 0 , relation_a)
        self.assertTrue(relation_a["_endnodes"]              , [event_a.id, victim_a.id])
        relation_b = get_relationship_reference(event_a.id, victim_b.id)
        self.assertTrue(int(relation_b["_relationship"]) > 0 , relation_b)
        self.assertTrue(relation_b["_endnodes"]              , [event_a.id, victim_b.id])

    def test_export_csv(self):
        from django_rq import get_worker
        export_resp1 = self.api_client.get('/api/detective/energy/v1/summary/export/', format='json')
        self.assertValidJSONResponse(export_resp1)
        export_resp1 = json.loads(export_resp1.content)
        self.assertEqual(export_resp1["status"], "enqueued", export_resp1)
        export_resp2 = self.api_client.get('/api/detective/energy/v1/summary/export/', format='json')
        export_resp2 = json.loads(export_resp2.content)
        # we have the same token
        self.assertEqual(export_resp1["token"], export_resp2["token"], export_resp2)
        job_resp     = self.api_client.get("/api/detective/common/v1/jobs/%s/" % (export_resp2["token"]))
        self.assertValidJSONResponse(job_resp)
        job_resp     = json.loads(job_resp.content)
        # processes all jobs then stop
        get_worker("default", "high").work(burst=True)
        job_resp     = self.api_client.get("/api/detective/common/v1/jobs/%s/?timestamp=1" % (export_resp2["token"]))
        job_resp     = json.loads(job_resp.content)
        self.assertEqual(job_resp["status"], "finished", job_resp)
        result1      = json.loads(job_resp["result"])
        self.assertIsNotNone(result1["file_name"], job_resp)
        self.assertNotEqual(result1["file_name"], "")
        # ask again to check if it's the same file (thanks to the cache)
        export_resp1 = self.api_client.get('/api/detective/energy/v1/summary/export/', format='json')
        export_resp1 = json.loads(export_resp1.content)
        get_worker("default", "high").work(burst=True)
        job_resp     = self.api_client.get("/api/detective/common/v1/jobs/%s/?timestamp=1" % (export_resp1["token"]))
        job_resp     = json.loads(job_resp.content)
        result2      = json.loads(job_resp["result"])
        self.assertEqual(result1["file_name"], result2["file_name"])
        # update an item and check if the file name change
        data = {
            'website_url': 'http://jpioupiou.org',
        }
        args = {
            'scope'      : 'detective/energy',
            'model_id'   : self.jpp.id,
            'model_name' : 'organization',
            'patch_data' : data
        }
        self.patch_individual(**args)
        export_resp3 = self.api_client.get('/api/detective/energy/v1/summary/export/', format='json')
        export_resp3 = json.loads(export_resp3.content)
        self.assertNotEqual(export_resp1["token"], export_resp3["token"])
        get_worker("default", "high").work(burst=True)
        job_resp     = self.api_client.get("/api/detective/common/v1/jobs/%s/?timestamp=2" % (export_resp3["token"]))
        job_resp     = json.loads(job_resp.content)
        result3      = json.loads(job_resp["result"])
        self.assertIsNotNone(result3["file_name"], job_resp)
        self.assertNotEqual(result3["file_name"], "")
        self.assertNotEqual(result1["file_name"], result3["file_name"])

    def test_topic_endpoint_exists(self):
        resp = self.api_client.get('/api/detective/common/v1/topic/?slug=christmas', follow=True, format='json')
        # Parse data to check the number of result
        data = json.loads(resp.content)
        # 1 result
        self.assertEqual( len( data["objects"] ), 1 )

    def test_topic_api_exists(self):
        resp = self.api_client.get('/api/{0}/christmas/v1/'.format(self.super_username), format='json')
        self.assertValidJSONResponse(resp)

    def test_topic_has_person(self):
        resp = self.api_client.get('/api/{0}/christmas/v1/'.format(self.super_username), format='json')
        self.assertValidJSONResponse(resp)

    def test_topic_multiple_api(self):
        # API 1
        resp = self.api_client.get('/api/{0}/christmas/v1/'.format(self.super_username), format='json')
        self.assertValidJSONResponse(resp)
        # API 2
        resp = self.api_client.get('/api/{0}/thanksgiving/v1/'.format(self.super_username), format='json')
        self.assertValidJSONResponse(resp)

    def test_topic_has_summary_syntax_from_ontology(self):
        resp = self.api_client.get('/api/{0}/christmas/v1/summary/syntax/'.format(self.super_username), format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)

    def test_topic_has_summary_syntax_from_file(self):
        resp = self.api_client.get('/api/detective/energy/v1/summary/syntax/', format='json', authentication=self.get_super_credentials())
        self.assertValidJSONResponse(resp)


    def test_my_topics_success_after_topic_delete(self):
        topic = Topic.objects.get(slug='test-topic')
        topic.delete()

        resp = self.api_client.get(
            '/api/detective/common/v1/user/{pk}/groups/'.format(pk=self.contrib_user.pk),
            format='json'
        )
        resp
        self.assertHttpOK(resp)

    def test_featured_success_after_topic_delete(self):
        topic = Topic.objects.get(slug='test-topic')
        topic.delete()

        resp = self.api_client.get(
            '/api/detective/common/v1/topic/?featured=1',
            format='json'
        )
        self.assertHttpOK(resp)

    def test_topic_update(self):
        topic = Topic.objects.get(slug='test-topic')
        topic.author = self.contrib_user
        topic.save()
        data  = self.topic_to_dict(topic)
        data['about'] = 'Changed'
        resp  = self.api_client.put(
            '/api/detective/common/v1/topic/{pk}/'.format(pk=topic.pk),
            data=data,
            format='json',
            authentication=self.get_contrib_credentials()
        )
        self.assertHttpOK(resp)
        updated_topic = Topic.objects.get(slug='test-topic')
        models_list = updated_topic.get_models()
        self.assertTrue(len(models_list) > 0)

    def test_topic_patch_empty_background(self):
        # Use Case: we want to patch a topic with an empty background to remove
        # it.
        # Excepted: updated topic should not have any background
        topic = Topic.objects.get(slug='test-topic')
        data = { 'background': None }
        resp  = self.api_client.patch(
            '/api/detective/common/v1/topic/{pk}/'.format(pk=topic.pk),
            data=data,
            format='json',
            authentication=self.get_contrib_credentials()
        )
        updated_topic = Topic.objects.get(slug='test-topic')
        # Accessing url attribute on topic.background will cause an error if no
        # file is related to this background, which is what we want
        self.assertRaises(ValueError, lambda t: t.background.url, updated_topic)

    def test_topic_update_empty_background(self):
        # Use Case: we want to patch a topic with an empty background to remove
        # it.
        # Excepted: updated topic should not have any background
        topic = Topic.objects.get(slug='test-topic')
        data  = self.topic_to_dict(topic)
        data['background'] =  None
        resp  = self.api_client.put(
            '/api/detective/common/v1/topic/{pk}/'.format(pk=topic.pk),
            data=data,
            format='json',
            authentication=self.get_contrib_credentials()
        )
        updated_topic = Topic.objects.get(slug='test-topic')
        # Accessing url attribute on topic.background will cause an error if no
        # file is related to this background, which is what we want
        self.assertRaises(ValueError, lambda t: t.background.url, updated_topic)

    def test_topic_patch_no_image_given(self):
        topic = Topic.objects.get(slug='test-topic')
        data  = { 'title': u'new title' }

        resp  = self.api_client.patch(
            '/api/detective/common/v1/topic/{pk}/'.format(pk=topic.pk),
            data=data,
            format='json',
            authentication=self.get_contrib_credentials()
        )
        self.assertTrue(resp.status_code in [200, 202])
        updated_topic = Topic.objects.get(slug='test-topic')
        self.assertEqual(updated_topic.title, data['title'])
        self.assertIsNotNone(updated_topic.background)

class TopicSkeletonApiTestCase(ApiTestCase):
    def setUp(self):
        super(TopicSkeletonApiTestCase, self).setUp()

    def tearDown(self):
        super(TopicSkeletonApiTestCase, self).tearDown()

    def create_topic(self, skeleton=None, credentials=None, data={}):
        if credentials is None:
            credentials = self.get_contrib_credentials()
        if skeleton is None:
            skeleton = TopicSkeleton.objects.get(title='Body Count')
        data['topic_skeleton'] = skeleton.pk
        return self.api_client.post(
            '/api/detective/common/v1/topic/',
            data=data,
            format='json',
            authentication=credentials
        )

    def test_topic_skeleton_list_unauthorized(self):
        client = self.api_client
        client.client.logout()
        # skeletons must be accessible only for logged users
        resp = client.get('/api/detective/common/v1/topicskeleton/',
            format='json'
        )
        self.assertHttpUnauthorized(resp)

    def test_topic_skeleton_list_lambda(self):
        resp = self.api_client.get('/api/detective/common/v1/topicskeleton/',
            format='json',
            authentication=self.get_lambda_credentials()
        )
        self.assertValidJSONResponse(resp)

    def test_topic_create_with_skeleton(self):
        skeleton = TopicSkeleton.objects.get(title='Body Count')
        resp = self.create_topic(skeleton=skeleton,
                                 data={'title': u'Skeletonist'})
        self.assertHttpCreated(resp)
        created_topic = json.loads(resp.content)
        self.assertEqual(created_topic['background'], skeleton.picture.url)
        self.assertEqual(created_topic['skeleton_title'], skeleton.title)
        self.assertIsNotNone(created_topic['ontology_as_json'])
        self.assertTrue(skeleton.picture_credits in created_topic['about'])

    def test_topic_create_with_skeleton_not_in_plan(self):
        skeleton = TopicSkeleton.objects.get(title='Family Affairs')
        resp = self.create_topic(skeleton=skeleton,
                                 credentials=self.get_lambda_credentials(),
                                 data={'title': u'Skeletonist'})
        self.assertHttpUnauthorized(resp)

    def test_topic_create_with_skeleton_with_background_url(self):
        # special test for caption issue: https://github.com/jplusplus/detective.io/issues/542
        skeleton = TopicSkeleton.objects.get(title='Body Count')
        topic_data = {
            'title': u'Skeletonist',
            'background_url': "http://i.imgur.com/4pObZpW.jpg"
        }
        resp = self.create_topic(skeleton=skeleton,
                                 data=topic_data)
        self.assertHttpCreated(resp)
        created_topic = json.loads(resp.content)
        self.assertIsNotNone(created_topic['background'])
        self.assertTrue(created_topic.get('about') in ['', None])

    def test_topic_create_with_skeleton_already_existing_title(self):
        data = {'title': u'Existing title'}
        resp = self.create_topic(data=data)
        self.assertHttpCreated(resp)
        resp = self.create_topic(data=data)
        self.assertHttpBadRequest(resp)
        errors = json.loads(resp.content)['topic']
        self.assertIsNotNone(errors[u'title'])

    def test_topic_create_with_skeleton_unavailble_image(self):
        data = {'title': u'Unavailable image test', 'background_url': "http://random.stuff.co.uk"}
        resp = self.create_topic(data=data)
        self.assertHttpBadRequest(resp)
        errors = json.loads(resp.content)['topic']
        self.assertIsNotNone(errors[u'background_url']['unavailable'])

    def test_create_then_patch_topic(self):
        skeleton = TopicSkeleton.objects.get(title='Body Count')
        resp = self.create_topic(skeleton=skeleton,
                                 data={'title': u'Skeletonist'})

        self.assertHttpCreated(resp)
        created_topic = json.loads(resp.content)
        self.assertEqual(created_topic['background'], skeleton.picture.url)
        self.assertIsNotNone(created_topic['ontology_as_json'])

        data  = { 'title': u'new title' }

        resp  = self.api_client.patch(
            '/api/detective/common/v1/topic/{pk}/'.format(pk=created_topic['id']),
            data=data,
            format='json',
            authentication=self.get_contrib_credentials()
        )
        self.assertTrue(resp.status_code in [200, 202])
        updated_topic = Topic.objects.get(slug=created_topic['slug'])
        self.assertEqual(updated_topic.title, data['title'])
        self.assertIsNotNone(updated_topic.background)

    def test_create_unauthorized(self):
        user = self.create_user(username='overrated', plan=PLANS_CHOICES[1][0])
        credentials = self.login(username=user.username, password=user.username)

        # should pass
        for i in range(0, 5):
            resp = self.create_topic(
                credentials=credentials,
                data={ 'title': 'Title %s' % i }
            )
            self.assertHttpCreated(resp)

        # should fail because of the plan selection
        resp = self.create_topic(credentials=credentials, data={'title': 'Title 5'})
        self.assertHttpUnauthorized(resp)


    def test_upload_over_1mb_image(self):
        background_url = "http://upload.wikimedia.org/wikipedia/commons/2/22/Turkish_Van_Cat.jpg"
        topic_data = {
            'title': 'oversized',
            'background_url': background_url
        }
        resp = self.create_topic(data=topic_data)
        self.assertHttpBadRequest(resp)
        errors = json.loads(resp.content)['topic']
        self.assertIsNotNone(errors[u'background_url']['oversized_file'])

class UserApiTestCase(ApiTestCase):
    def setUp(self):
        # call to super setUp is required.
        super(UserApiTestCase, self).setUp()

    def tearDown(self):
        # call to super tearDown is required.
        super(UserApiTestCase, self).tearDown()

    def test_user_signup_allowed_caracaters(self):
        special_chars = "._-"
        user_data = {
            'username':"UserName" + special_chars,
            'email':"myemail@test.me",
            'password':"r4nd0mpASSWORd_"
        }
        resp = self.signup_user(user_data)
        self.assertHttpCreated(resp)


    def test_user_signup_unallowed_caracaters_space(self):
        special_chars = " *&^/+@"
        user_data = {
            'username':"username" + special_chars,
            'email':"myemail@test.me",
            'password':"r4nd0mpASSWORd_"
        }
        resp = self.signup_user(user_data)
        self.assertHttpBadRequest(resp)
