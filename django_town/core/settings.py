from django.conf import settings
from django.utils.functional import SimpleLazyObject

from django_town.core.exceptions import SettingError
from django_town.utils import DictObject, recursive_dict_update


_DJANGO_TOWN_SETTINGS = {
    "oauth2": {
        "USER_SECRET_KEY_LENGTH": 5,
        "SERVICE_SECRET_KEY_LENGTH": 5,
        "CLIENT_ID_LENGTH": 30,
        "CLIENT_SECRET_LENGTH": 30,
        "ACCESS_TOKEN_EXPIRATION": 3600,
        "SCOPE_MAX_LENGTH": 30,
        "CODE_EXPIRATION": 600
    },
    "cache": {

    },
    "rest": {
        "site_url": "",
    },
    "core": {
        "CACHE_PREFIX": "_dt",
        "DEFAULT_CACHE_DURATION": 3600 * 24 * 14,
    },
    "microdata": {
        "DATABASES": ["default"],
        "SHARD_HELPING_DATABASE": "default",
        "SLAVE_DATABASES": {}
    },
    "mongodb": {
        "HOST": "localhost",
        "PORT": 27017,
        "USERNAME": None,
        "PASSWORD": None,
    },
    "social": {
        "master_oauth2_service_id": 1
    }
}

try:
    recursive_dict_update(_DJANGO_TOWN_SETTINGS, (getattr(settings, "DJANGO_TOWN_SETTINGS")))
except AttributeError:
    pass


def lazy_load_settings(key, necessary_fields=None):
    ret = DictObject(_DJANGO_TOWN_SETTINGS[key], case_sensitive=False)
    if necessary_fields:
        for necessary_field in necessary_fields:
            if not getattr(ret, necessary_field):
                raise SettingError("%s does not exist in %s setting" % (necessary_field, key))
    return ret


CORE_SETTINGS = SimpleLazyObject(lambda: lazy_load_settings('core'))
OAUTH2_SETTINGS = SimpleLazyObject(lambda: lazy_load_settings('oauth2', necessary_fields=['ACCESS_TOKEN_SECRET_KEY',
                                                                                          "REFRESH_TOKEN_SECRET_KEY",
                                                                                          'CODE_SECRET_KEY', 'SCOPE',
                                                                                          'BASE_URL']))
REST_SETTINGS = SimpleLazyObject(lambda: lazy_load_settings('rest'))
CACHE_SETTINGS = SimpleLazyObject(lambda: lazy_load_settings('cache'))
MICRODATA_SETTINGS = SimpleLazyObject(lambda: lazy_load_settings('microdata'))
SOCIAL_SETTINGS = SimpleLazyObject(lambda: lazy_load_settings('social'))
MONGODB_SETTINGS = SimpleLazyObject(lambda: lazy_load_settings('mongodb', necessary_fields=['DATABASES']))