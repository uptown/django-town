import unittest
from django.test import Client


class UserTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        response = self.client.post('/api/alpha/users',data={'email': 'test@example.com', 'password': 'hehe'})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 201)
