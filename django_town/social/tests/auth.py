from django_town.utils import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from django_town.oauth2.models import Service, Client
import urllib2


def create_client_and_service(service_name="test_service", client_name="test client"):
    service = Service.objects.create(name=service_name)
    client = Client.objects.create(name=client_name, service=service)
    return client


def join(self, email="test@test.com", password="testpassword"):
    return self.client.post(reverse("UsersApiView"), {'email': email, 'password': password})


def sign_in(self, email="test@test.com", password="testpassword"):
    return self.client.post(reverse("SessionsApiView"), {'email': email, 'password': password})


def sign_out(self, email="test@test.com", password="testpassword"):
    return self.client.delete(reverse("SessionsApiView"))


def get_access_token(self, grant_type="password", email="test@test.com", password="testpassword", client=None):
    if grant_type == 'password':
        if not client:
            client = create_client_and_service()
        response = self.client.post(reverse("OAuth2TokenView"), {'grant_type': 'password', 'client_id': client.client_id,
                                                        'client_secret': client.client_secret, 'username': email,
                                                        'password': password})
        return json.loads(response.content)['access_token']
    elif grant_type == 'authorization_code':
        #Warning can't test with Macro
        if not client:
            client = create_client_and_service()
        sign_in(self, email, password)
        urllib2.urlopen(reverse("OAuth2TokenView"),)
        response = self.client.post(reverse("OAuth2TokenView"), {'grant_type': 'password', 'client_id': client.client_id,
                                                        'client_secret': client.client_secret, 'username': email,
                                                        'password': password})
        return json.loads(response.content)['access_token']



class SocialOAuth2Tests(TestCase):

    def test_join(self):
        """
        test for join
        """
        email = "test@inval.id"
        password = "test1234"
        response = join(self, email, password)

        self.assertContains(response, email, status_code=201)
        self.assertNotContains(response, password, status_code=201)

        response = join(self, email, password)
        self.assertContains(response, "already_exists", status_code=409)

    def test_sign_in(self):
        """
        test for sign in
        """
        email = "test@inval.id"
        password = "test1234"
        join(self, email, password)
        response = sign_in(self, email, password)
        self.assertEqual(response.status_code, 201)


        email = "test@inval.id"
        password = "testt1234"
        response = sign_in(self, email, password)
        self.assertContains(response, "not_found", status_code=404)

        email = "test2inval.id"
        password = "test1234"
        response = sign_in(self, email, password)
        self.assertContains(response, "form_invalid", status_code=400)


        email = "test2@inval.id"
        password = "tes"
        response = sign_in(self, email, password)
        self.assertContains(response, "form_invalid", status_code=400)

    def test_sign_out(self):
        """
        test for sign out
        """
        email = "test@inval.id"
        password = "test1234"
        join(self, email, password)
        sign_in(self, email, password)
        response = sign_out(self, email, password)
        self.assertEqual(response.status_code, 200)