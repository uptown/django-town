
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django_town.social.oauth2.server import oauth2_server

class TastersBackend(ModelBackend):
    
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
                return super(TastersBackend, self).authenticate(username=username, password=password)
        else:
            return super(TastersBackend, self).authenticate(username=username, password=password)
    
    def facebook_authenticate(self, access_token):
        return oauth2_server.user_from_facebook_access_token(access_token)

    def google_authenticate(self, access_token):
        return oauth2_server.user_from_google_access_token(access_token)

    def twitter_authenticate(self, twitter_id, oauth_token, oauth_token_secret):
        return None
    
    def access_token_authenticate(self, access_token):
        return None
    
    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except  get_user_model().DoesNotExist:
            return None
    