#-*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django_town.oauth2.errors import InvalidClientError
from django_town.utils import generate_random_from_vschar_set
from django_town.oauth2.models import Client
from django_town.utils import class_from_path
from django_town.core.settings import OAUTH2_SETTINGS


def generate_client_id(length=30):
    return generate_random_from_vschar_set(length)


def generate_client_secret(length=30):
    return generate_random_from_vschar_set(length)


class OAuth2Client(object):
    def __init__(self, client_id=None, client_pk=None):
        if client_id:
            try:
                self.django_client = Client.objects.get_cached(client_id=client_id)
            except ObjectDoesNotExist:
                raise InvalidClientError()
        else:
            try:
                self.django_client = Client.objects.get(pk=client_pk)
            except ObjectDoesNotExist:
                raise InvalidClientError()

    @property
    def pk(self):
        try:
            return self.django_client.pk
        except ObjectDoesNotExist:
            raise InvalidClientError()

    @property
    def client_id(self):
        try:
            return self.django_client.client_id
        except ObjectDoesNotExist:
            raise InvalidClientError()

    @property
    def service_id(self):
        try:
            return self.django_client.service_id
        except ObjectDoesNotExist:
            raise InvalidClientError()

    @property
    def client_secret(self):
        try:
            return self.django_client.client_secret
        except ObjectDoesNotExist:
            raise InvalidClientError()
    
    @property
    def default_redirect_uri(self):
        try:
            return self.django_client.default_redirect_uri
        except ObjectDoesNotExist:
            raise InvalidClientError()

    
    @property
    def available_scope(self):
        try:
            return self.django_client.available_scope
        except ObjectDoesNotExist:
            import traceback
            traceback.print_exc()
            raise InvalidClientError()


def oauth2_client_class():
    try:
        return class_from_path(OAUTH2_SETTINGS.CLIENT)
    except KeyError:
        return OAuth2Client