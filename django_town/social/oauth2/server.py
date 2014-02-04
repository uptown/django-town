import urllib
import urllib2

from django_town.oauth2.server import OAuth2Server, UnsupportedResponseTypeError
from django_town.oauth2 import oauth2_request_class, oauth2_server, OAUTH2_SETTINGS
from django_town.social.oauth2.grants import FacebookAccessTokenGrant
from django_town.facebook import get_object, FBTokenInvalidException, FBPermissionException, \
    FBTokenExpiredException
from django_town.social.models import UserFacebook, UserGoogle
from django_town.utils import json


def facebook_grant(request):
    django_request = oauth2_request_class()(request)
    grant = FacebookAccessTokenGrant(oauth2_server, django_request)
    return grant.get_credential(OAUTH2_SETTINGS.ACCESS_TOKEN_EXPIRATION)


class Server(OAuth2Server):

    @staticmethod
    def user_from_facebook_access_token(access_token):
        try:
            facebook_data = get_object("me", fields="id", access_token=access_token)
        except FBTokenInvalidException:
            return None
        except FBPermissionException:
            return None
        except FBTokenExpiredException:
            return None
        try:
            user_facebook = UserFacebook.objects.get(facebook_id=facebook_data['id'])
            user_facebook.access_token = access_token
            user_facebook.save()
            return user_facebook.user
        except UserFacebook.DoesNotExist:
            return None

    @staticmethod
    def user_from_google_access_token(access_token):
        try:
            ret = urllib2.urlopen("https://www.googleapis.com/plus/v1/people/me?" +
                                  urllib.urlencode({'access_token': access_token})).read()
        except urllib2.HTTPError:
            return None

        user_data = json.loads(ret)
        try:
            user_google = UserGoogle.objects.get(google_id=user_data['id'])
            user_google.save()
            return user_google.user
        except UserGoogle.DoesNotExist:
            return None

    def get_credential_with_grant_type(self, grant_type, request):
        if grant_type == "facebook":
            return facebook_grant(request)
        raise UnsupportedResponseTypeError()
