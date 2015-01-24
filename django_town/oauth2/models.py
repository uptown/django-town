#-*- coding: utf-8 -*-

from django_town.core.settings import OAUTH2_SETTINGS

try:
    if not OAUTH2_SETTINGS.ACCESS_TOKEN_SECRET_KEY:
        raise ImportError
except KeyError:
    # import traceback
    # traceback.print_exc()
    raise ImportError

from django.db import models
from django.conf import settings
from django.contrib import admin
from django_town.cache.model import CachingModel
from django_town.core.fields import JSONField
from django_town.utils import generate_random_from_vschar_set


class Service(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name


# class ServiceSecretKey(CachingModel):
#     cache_key_format = "_ut_o2ss:%(service__pk)d"
#
#     service = models.ForeignKey(Service, unique=True)
#     secret_key = models.CharField(max_length=OAUTH2_SETTINGS.SERVICE_SECRET_KEY_LENGTH,
#                                   default=lambda: generate_random_from_vschar_set(
#                                       OAUTH2_SETTINGS.SERVICE_SECRET_KEY_LENGTH))

def _generate_random_from_vschar_set_for_client_id():
    return generate_random_from_vschar_set(OAUTH2_SETTINGS.CLIENT_ID_LENGTH)


def _generate_random_from_vschar_set_for_client_secret():
    return generate_random_from_vschar_set(OAUTH2_SETTINGS.CLIENT_ID_LENGTH)


class Client(CachingModel):

    IOS_CLIENT = 1

    CLIENT_TYPE = (
        (0, "Web"),
        (1, "iOS"),
        (2, "Android"),
        (3, "Win"),
    )

    cache_key_format = "_ut_o2c:%(client_id)s"

    name = models.CharField(max_length=200)
    service = models.ForeignKey(Service)
    client_id = models.CharField(max_length=OAUTH2_SETTINGS.CLIENT_ID_LENGTH, unique=True,
                                 default=_generate_random_from_vschar_set_for_client_id)
    client_secret = models.CharField(max_length=OAUTH2_SETTINGS.CLIENT_SECRET_LENGTH,
                                 default=_generate_random_from_vschar_set_for_client_secret)
    redirect_uris = JSONField(blank=True)
    default_redirect_uri = models.URLField()
    available_scope = JSONField(blank=True)
    client_type = models.IntegerField(default=IOS_CLIENT, choices=CLIENT_TYPE)
    client_min_version = models.CharField(max_length=20, default="")
    client_cur_version = models.CharField(max_length=20, default="")
    client_store_id = models.CharField(max_length=30, default="")



    def __unicode__(self):
        return self.name

def _generate_random_from_vschar_set_for_secret_key():
    return generate_random_from_vschar_set(OAUTH2_SETTINGS.USER_SECRET_KEY_LENGTH)

class UserClientSecretKey(CachingModel):

    cache_key_format = "_ut_o2u:%(user_id)d:%(client__pk)d"

    user_id = models.IntegerField()
    client = models.ForeignKey(Client)
    secret_key = models.CharField(max_length=OAUTH2_SETTINGS.USER_SECRET_KEY_LENGTH,
                                  default=_generate_random_from_vschar_set_for_secret_key)

    unique_together = (("user_id", "client"),)

class Scope(models.Model):
    name = models.CharField(max_length=30, unique=True)


class ClientAdmin(admin.ModelAdmin):
    readonly_fields = ['client_id', 'client_secret']

admin.site.register(Client, admin.ModelAdmin)
admin.site.register(Service, admin.ModelAdmin)
