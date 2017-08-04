import unittest
from app import db, app
from config import app_configs
import json


class AuthUserTest(unittest.TestCase):
    URL = "http://localhost:5000/auth/"

    def setUp(self):
        app.config.from_object(app_configs['testing'])
        self.client = app.test_client()
        self.user_data = {
            'username': 'tester',
            'email': 'test@example.com',
            'password': 'test_password'
        }
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def post(self, data, endpoint, expected_error=None):
        response = self.client.post(self.URL + endpoint, data=json.dumps(data), content_type="application/json")

        if expected_error:
            self.assertEqual(response.status_code, expected_error, msg="expected error should be equal to status code")

        return response

    def test_registration(self):
        """ test login works"""
        result = self.post(self.user_data, 'register/')
        self.assertEqual(result.status_code, 201)

    def test_duplicate_registration(self):
        """ test that a user can't be registered twice"""
        response = self.post(self.user_data, 'register/')

        self.assertEqual(response.status_code, 201)

        next_response = self.post(self.user_data, 'register/')
        next_response = json.loads(next_response.data)
        self.assertEqual(next_response['message'], "User already exists")

    def test_login(self):
        """Test registered user can login."""
        response = self.post(self.user_data, 'register/')
        self.assertEqual(response.status_code, 201)

        login_user = self.post(self.user_data, 'login/')

        # get the results in json format
        result = json.loads(login_user.data)
        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")
        # Assert that the status code is equal to 200
        self.assertEqual(login_user.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_login_non_registered_user(self):
        """Test non registered users cannot login."""
        unregistered = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        # send a POST request to /auth/login with the data above
        response = self.post(unregistered, 'login/', 401)
        # get the result in json
        result = json.loads(response.data)

        # assert that this response must contain an error message
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again")
