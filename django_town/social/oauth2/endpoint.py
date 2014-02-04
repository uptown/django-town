#-*- coding: utf-8 -*-
from django_town.oauth2.endpoint.endpoint import Endpoint
from django_town.oauth2.errors import InvalidRequestError


class SocialEndpoint(Endpoint):
    def __init__(self, server, request, client):
                
        if request.method != "POST":
            raise InvalidRequestError()
        super(SocialEndpoint, self).__init__(server, request, client)


    def get_credential_facebook(self, expires_in):
        if self._request.grant_type != "facebook":
            raise InvalidRequestError()

        client_secret = self._request.client_secret

        if not client_secret or self._client.client_secret != client_secret:
            raise InvalidRequestError()

        try:
            user = self._server.user_from_facebook_access_token(self._request.facebook_access_token)
        except AttributeError:
            raise InvalidRequestError()

        access_token = self._server.generate_access_token(self._client, user, self._request.scope,
                                                          expires_in, is_refreshable=True)
        return access_token
