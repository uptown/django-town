#-*- coding: utf-8 -*-

from django_town.utils import add_params_to_url

class OAuth2Error(Exception):
    error = "temporarily_unavailable"
    status_code = 400

    def __init__(self, description=None, uri=None, state=None, status_code=None):
        self.description = description
        self.uri = uri
        self.state = state
        if status_code:
            self.status_code = status_code

    def to_dict(self):
        error = {'error': self.error}
        if self.description:
            error['error_description'] = self.description
        if self.uri:
            error['error_uri'] = self.uri
        if self.state:
            error['state'] = self.state
        return error
    
    def to_uri(self, redirect_uri):
        return add_params_to_url(redirect_uri, self.to_dict())


class InvalidRequestError(OAuth2Error):
    error = "invalid_request"
    status_code = 400


class InvalidAccessToken(OAuth2Error):
    error = "invalid_access_token"
    status_code = 401


class InvalidRefreshToken(OAuth2Error):
    error = "invalid_refresh_token"
    status_code = 401


class AccessTokenExpired(InvalidAccessToken):
    error = "access_token_expired"
    status_code = 401

    
class UnauthorizedClientError(OAuth2Error):
    error = "unauthorized_client"
    status_code = 401
    
    
class AccessDeniedError(OAuth2Error):
    error = "access_denied"
    status_code = 401


class UnsupportedResponseTypeError(OAuth2Error):
    error = "unsupported_response_type"
    status_code = 400


class InvalidScopeError(OAuth2Error):
    error = "invalid_scope"
    status_code = 400


class InvalidClientError(OAuth2Error):
    error = "invalid_client"
    status_code = 401

