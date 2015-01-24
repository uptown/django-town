from django.db import transaction
from django_town.utils import json, urlencode, urlopen, HTTPError
import datetime

from django_town.core.settings import SOCIAL_SETTINGS
from django_town.oauth2.server import OAuth2Server, UnsupportedResponseTypeError
from django_town.oauth2 import oauth2_request_class, oauth2_server, OAUTH2_SETTINGS
from django_town.social.oauth2.grants import FacebookAccessTokenGrant, GoogleAccessTokenGrant
from django_town.facebook import get_object, FBTokenInvalidException, FBPermissionException, \
    FBTokenExpiredException
from django_town.social.models import UserFacebook, UserGoogle
from django_town.social.documents import AccessToken


def facebook_grant(request):
    django_request = oauth2_request_class()(request)
    grant = FacebookAccessTokenGrant(oauth2_server, django_request)
    return grant.get_credential(OAUTH2_SETTINGS.ACCESS_TOKEN_EXPIRATION)


def google_grant(request):
    django_request = oauth2_request_class()(request)
    grant = GoogleAccessTokenGrant(oauth2_server, django_request)
    return grant.get_credential(OAUTH2_SETTINGS.ACCESS_TOKEN_EXPIRATION)


class Server(OAuth2Server):
    @staticmethod
    def user_from_facebook_access_token(access_token):
        try:
            __unused = get_object("debug_token", fields="id", input_token=access_token, access_token=SOCIAL_SETTINGS.FACEBOOK_APP_TOKEN)
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
            pass
        from django_town.social.resources.user import UserResource
        with transaction.atomic():
            user_resource = UserResource().create(data={'facebook_access_token': access_token})

            user_facebook = UserFacebook(facebook_id=facebook_data['id'], user=user_resource.get_instance())
            user_facebook.access_token = access_token
            user_facebook.save()
            return user_resource.get_instance()


    @staticmethod
    def user_from_google_access_token(access_token):
        try:
            ret = urlopen("https://www.googleapis.com/plus/v1/people/me?" +
                                  urlencode({'access_token': access_token})).read()
        except HTTPError:
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
        elif grant_type == "google":
            return google_grant(request)
        raise UnsupportedResponseTypeError()


    @classmethod
    def store_credential(cls, credential, client_pk, user_pk, scope, expire, is_refreshable):
        # AccessToken(user_id=user_pk, client_id=client_pk, access_token=credential.access_token,
        #             refresh_token=credential.refresh_token, expire=datetime.datetime.fromtimestamp(expire),
        # scope=scope).save()
        pass