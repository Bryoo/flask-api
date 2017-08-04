import unittest
from app import db, app
from config import app_configs
import json


class BucketListTest(unittest.TestCase):
    """This class represents the bucketlist test case"""
    URL = "http://localhost:5000/api/v1/"

    def setUp(self):
        app.config.from_object(app_configs['testing'])
        self.client = app.test_client()
        db.create_all()

        self.data = {
            "name": "Go to nairobi",
            "items":
                [
                    {
                        "done": False,
                        "name": "eat some chips"
                    },
                    {
                        "done": True,
                        "name": "try out sushi"
                    }
                ]
        }

        self.items_data ={
            "done": False,
            "name": "Enjoy the atmosphere"
        }

    def post(self, data, endpoint, access_token, expected_error=None):
        response = self.client.post(self.URL + endpoint, data=json.dumps(data),
                                    headers={'Authorization': "Bearer " + access_token,
                                             'content-type': "application/json"})

        if expected_error:
            self.assertEqual(response.status_code, expected_error, msg="expected error should be equal to status code")

        return response

    def get(self, endpoint, access_token, expected_error=None):
        response = self.client.get(self.URL + endpoint,
                                   headers=dict(Authorization="Bearer " + access_token,
                                                content_type="application/json"))
        if expected_error:
            self.assertEqual(response.status_code, expected_error, msg="expected error should be equal to status code")

        return response

    def put(self, data, endpoint, access_token, expected_error=None):
        response = self.client.put(self.URL + endpoint, data=json.dumps(data),
                                   headers={'Authorization': "Bearer " + access_token,
                                            'content-type': "application/json"})
        if expected_error:
            self.assertEqual(response.status_code, expected_error, msg="expected error should be equal to status code")

        return response

    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'username': 'tester',
            'email': email,
            'password': password
        }
        return self.client.post('http://localhost:5000/auth/register/',
                                data=json.dumps(user_data),
                                content_type="application/json")

    def login_user(self, email="user@test.com", password="test1234"):
        user_data = {
            'email': email,
            'password': password
        }
        return self.client.post('http://localhost:5000/auth/login',
                                data=json.dumps(user_data),
                                content_type="application/json")

    def authenticate_user(self):
        self.register_user()
        response = self.login_user()
        result = json.loads(response.data)
        access_token = result['access_token']
        return access_token

    def tearDown(self):
        db.drop_all()

    def test_post_works(self):
        self.register_user()
        response = self.login_user()
        # get the access token
        result = json.loads(response.data)
        access_token = result['access_token']

        resp = self.post(
            self.data,
            'bucketlist/',
            access_token
            )

        # response = self.post(self.data, 'bucketlist/')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('Go to nairobi', str(resp.data))

    def test_invalid_token(self):
        self.register_user()
        response = self.login_user()
        # get the access token
        result = json.loads(response.data)
        access_token = result['access_token'] + "extra chars"

        resp = self.post(
            self.data,
            'bucketlist/',
            access_token
        )
        result = json.loads(resp.data)
        self.assertEqual(result['message'], "Invalid token. Please register or login")

    def test_post_error_on_duplicate(self):
        access_token = self.authenticate_user()

        response = self.post(self.data, 'bucketlist/', access_token)
        self.assertEqual(response.status_code, 201)

        response2 = self.post(self.data, 'bucketlist/', access_token, 422)
        result = json.loads(response2.data)
        self.assertEqual(result['result'], "Bucketlist already exists")

    def test_get_all_bucketlists(self):
        """test that api properly retrieves all bucketlists"""
        access_token = self.authenticate_user()

        # post data first so that there's something to get
        self.post(self.data, 'bucketlist/', access_token)

        response = self.get('bucketlist/', access_token)
        result = json.loads(response.data)

        # confirm whats returned is what was posted
        self.assertEqual(result[0]['name'], self.data['name'])
        self.assertIn('eat some chips', str(result))

        # test get function with value greater than the limit
        response = self.get('bucketlist?limit=4', access_token)
        result = json.loads(response.data)
        self.assertEqual(result['message'], "posts per page shouldn't be more than 3")

        # test the get function with query and search string
        response = self.get('bucketlist?q=nairobi', access_token)
        self.assertEqual(response.status_code, 200)

    def test_post_without_token(self):
        response = self.client.post('http://localhost:5000/api/v1/bucketlist',
                                    data=json.dumps(self.data),
                                    content_type="application/json")
        result = json.loads(response.data)
        self.assertEqual(result['message'], "No authorization header present")

    def test_get_single_bucketlist(self):
        access_token = self.authenticate_user()

        response = self.post(self.data, 'bucketlist/', access_token)
        result = json.loads(response.data)

        response = self.get('bucketlist/{}'.format(result['id']), access_token)
        result = json.loads(response.data)

        self.assertEqual(self.data['name'], result['name'])

        # test getting an id that doesn't exist
        non_existent = -1
        response = self.get('bucketlist/{}'.format(non_existent), access_token)
        self.assertEqual(response.status_code, 404)

    def test_update_bucketlist(self):
        """test whether update bucket list PUT works"""
        access_token = self.authenticate_user()

        response = self.post(self.data, 'bucketlist/', access_token)
        result = json.loads(response.data)
        data = {
                   "name": "Move to mombasa instead"
               }
        resp = self.put(
            data,
            'bucketlist/{}'.format(result['id']),
            access_token
            )

        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.data)
        self.assertEqual(result['name'], "Move to mombasa instead")

        # test duplicate update of names
        resp = self.put(
            data,
            'bucketlist/{}'.format(result['id']),
            access_token
        )
        result = json.loads(resp.data)
        self.assertEqual(result['message'], "bucket name already exists")

    def test_delete_bucketlist(self):
        """test whether delete bucket list DELETE method works"""
        access_token = self.authenticate_user()

        response = self.post(self.data, 'bucketlist/', access_token)
        result = json.loads(response.data)

        del_result = self.client.delete(self.URL + 'bucketlist/{}'.format(result['id']),
                                        headers={'Authorization': "Bearer " + access_token,
                                        'content-type': "application/json"})
        self.assertEqual(del_result.status_code, 200)
        del_data = json.loads(del_result.data)
        self.assertTrue(del_data['result'])

    def test_add_items(self):
        """Test adding items to bucketlist"""
        access_token = self.authenticate_user()
        response = self.post(self.data, 'bucketlist/', access_token)
        result = json.loads(response.data)

        # test addition of items
        response = self.post(self.items_data, 'bucketlist/{}/items'.format(result['id']), access_token)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Enjoy the atmosphere", str(response.data))

        # test addition of duplicate item
        duplicate_response = self.post(self.items_data, 'bucketlist/{}/items'.format(result['id']), access_token)
        result = json.loads(duplicate_response.data)
        self.assertEqual(result['message'], "Duplicate item found")

    def test_update_items(self):
        """test updating of items in bucketlist"""
        access_token = self.authenticate_user()
        response = self.post(self.data, 'bucketlist/', access_token)
        result = json.loads(response.data)

        new_data = {
            "done": False,
            "name": "Altered item here"
        }
        response = self.put(new_data, 'bucketlist/{}/items/{}'.format(result['id'], result['items'][0]['item_id']),
                            access_token)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Altered item here", str(response.data))

    def test_delete_items(self):
        """test delete item"""
        access_token = self.authenticate_user()
        response = self.post(self.data, 'bucketlist/', access_token)
        result = json.loads(response.data)

        response = self.client.delete(self.URL + "bucketlist/{}/items/{}".format(result['id'],
                                                                                 result['items'][0]['item_id']
                                                                                 ),
                                      headers=dict(Authorization="Bearer " + access_token,
                                                   content_type="application/json"))
        self.assertEqual(response.status_code, 200)
        final_result = json.loads(response.data)
        self.assertTrue(final_result['result'])


