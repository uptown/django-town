from django_town.rest.resources import ModelResource
from django_town.oauth2.models import Client, Service


class ClientResource(ModelResource):
    model = Client
    cache_key_format = "_ut_cli:%(pk)s"


class ServiceResource(ModelResource):
    model = Service
    cache_key_format = "_ut_svc:%(pk)s"