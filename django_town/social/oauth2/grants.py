# -*- coding: utf-8 -*-
from django_town.oauth2.grant.grant import Grant
from django_town.social.oauth2.endpoint import SocialEndpoint


class FacebookAccessTokenGrant(Grant):
    def get_credential(self, expires_in):
        self._token_endpoint = SocialEndpoint(self._server, self._request, self._client)
        return self._token_endpoint.get_credential_facebook(expires_in)


class GoogleAccessTokenGrant(Grant):
    def get_credential(self, expires_in):
        self._token_endpoint = SocialEndpoint(self._server, self._request, self._client)
        return self._token_endpoint.get_credential_google(expires_in)
