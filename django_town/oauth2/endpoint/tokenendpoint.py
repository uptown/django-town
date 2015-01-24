#-*- coding: utf-8 -*-


from .endpoint import Endpoint
from ..errors import InvalidRequestError, InvalidClientError


class TokenEndpoint(Endpoint):
    def __init__(self, server, request, client):
                
        if request.method != "POST":
            raise InvalidRequestError()
        super(TokenEndpoint, self).__init__(server, request, client)
    
    def get_credential(self, expires_in):
        #TODO check redirect uri
        if self._request.grant_type != "authorization_code":
            raise InvalidRequestError()
        
        code = self._request.code
        client_secret = self._request.client_secret
        redirect_uri = self._request.redirect_uri
        user = self._request.user
        
        if not client_secret or (self._client.client_secret != client_secret):
            raise InvalidRequestError()
        
        scope = self._server.check_code_and_decrypt_scope(code, self._client, user)
        return self._server.generate_access_token(self._client, user, scope, expires_in, is_refreshable=True)
    
    def get_credential_refresh(self, expires_in):
        if self._request.grant_type != "refresh_token":
            raise InvalidRequestError()
        client_secret = self._request.client_secret

        if not client_secret or (self._client.client_secret != client_secret):
            raise InvalidRequestError()
        access_token = self._server.refresh_access_token(self._request.refresh_token,
                                                         self._request.access_token, expires_in)
        return access_token

    
    def get_credential_password(self, expires_in):
        if self._request.grant_type != "password":
            raise InvalidRequestError()
        try:
            user = self._server.user_from_username_and_password(self._request.username, self._request.password)
        except AttributeError:
            raise InvalidRequestError()
        client_secret = self._request.client_secret
        
        if not client_secret or (self._client.client_secret != client_secret):
            raise InvalidRequestError()
        
        access_token = self._server.generate_access_token(self._client, user, self._request.scope, expires_in, is_refreshable=True)
        return access_token
    
    def get_client_access_token(self, expires_in):
        if self._request.grant_type != "client_credentials":
            raise InvalidRequestError()


        client_secret = self._request.client_secret
        
        if not client_secret or (self._client.client_secret != client_secret):
            raise InvalidRequestError()
        
        access_token = self._server.generate_client_access_token(self._client, self._request.scope, expires_in)
        return access_token
    
    
    def get_credential_session(self, expires_in):
        if self._request.grant_type != "session":
            raise InvalidRequestError()

        access_token = self._server.generate_access_token(self._client, self._request.user, self._request.scope, expires_in,
                                                          is_refreshable=True)
        return access_token
