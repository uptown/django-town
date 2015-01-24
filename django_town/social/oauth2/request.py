from django_town.oauth2.request import OAuth2Request


class Request(OAuth2Request):
    @property
    def facebook_access_token(self):
        return self._body.get('facebook_access_token')

    @property
    def google_access_token(self):
        return self._body.get('google_access_token')