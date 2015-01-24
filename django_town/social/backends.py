from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

try:
    from django_town.social.oauth2.server import oauth2_server
except ImportError:
    from django_town.utils import json, urlopen, urlencode, HTTPError

    from django_town.facebook import get_object, FBTokenInvalidException, FBPermissionException, \
        FBTokenExpiredException
    from django_town.social.models import UserFacebook, UserGoogle

    oauth2_server = None


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


class SocialBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        auth_type = kwargs.get('type', None)
        if auth_type:
            if auth_type == "facebook":
                return self.facebook_authenticate(access_token=kwargs.get('access_token'))
            elif auth_type == "google":
                return self.google_authenticate(access_token=kwargs.get('access_token'))
            elif auth_type == "twitter":
                return self.twitter_authenticate(**kwargs)
            elif auth_type == "access_token":
                return self.access_token_authenticate(**kwargs)
            else:
                return super(SocialBackend, self).authenticate(username=username, password=password)
        else:
            return super(SocialBackend, self).authenticate(username=username, password=password)

    def facebook_authenticate(self, access_token):
        if oauth2_server:
            return oauth2_server.user_from_facebook_access_token(access_token)
        return user_from_facebook_access_token(access_token)

    def google_authenticate(self, access_token):
        if oauth2_server:
            return oauth2_server.user_from_google_access_token(access_token)
        return user_from_google_access_token(access_token)

    def twitter_authenticate(self, twitter_id, oauth_token, oauth_token_secret):
        return None

    def access_token_authenticate(self, access_token):
        return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except  get_user_model().DoesNotExist:
            return None
    