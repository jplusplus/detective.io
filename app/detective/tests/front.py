import unittest
from django.test import Client

class FrontTestCase(unittest.TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_home(self):
        # Issue a GET request.
        response = self.client.get('/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_partial_exists(self):
        # Issue a GET request.
        response = self.client.get('/partial/account.login.html')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        from django.contrib.auth.models import User
        from django.core.exceptions import ObjectDoesNotExist
        # Look for the test user
        self.username  = 'tester'
        self.password  = 'tester'
        try:
            self.user = User.objects.get(username=self.username)
        except ObjectDoesNotExist:
            # Create the new user
            self.user = User.objects.create_user(self.username, 'tester@detective.io', self.password)
            self.user.is_staff = True
            self.user.save()

        self.client.login(username=self.username, password=self.password)
        # Issue a GET request.
        response = self.client.get('/')
        # Check that the user is loged
        self.assertEqual( eval(response.cookies["user__is_logged"].value), True )
        # Check that the user is staff
        self.assertEqual( eval(response.cookies["user__is_staff"].value), self.user.is_staff )
        # Check that the username is correct
        self.assertEqual( response.cookies["user__username"].value, self.user.username )
        # Logout the user
        self.client.logout()
        # Issue a GET request.
        response = self.client.get('/')
        # Ensure the cookie is deleted
        self.assertEqual( hasattr(response.cookies, "user__is_logged"), False )

#EOF
