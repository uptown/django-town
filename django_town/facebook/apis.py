import urllib2

from django.utils.functional import SimpleLazyObject

from django_town.core.settings import SOCIAL_SETTINGS
from django_town.facebook.client import Client


default_client = SimpleLazyObject(lambda: Client(app_id=SOCIAL_SETTINGS.FACEBOOK_APP_ID,
                                                 app_secret=SOCIAL_SETTINGS.FACEBOOK_APP_SECRET))


def get_object(path, **kwargs):
    return default_client.get_object(path, **kwargs)


def fql(query, access_token=None):
    return get_object('fql', query=urllib2.quote(query), access_token=access_token)


def get_profile(access_token=None):
    return get_object('me', fields="picture,bio,email,id,name", access_token=access_token)


def get_feed(uid, **kwargs):
    return get_object(('%s/feed' % uid), **kwargs)


def get_music_listens(**kwargs):
    return get_object('me/music.listens', **kwargs)