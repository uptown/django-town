#-*- coding: utf-8 -*-


from .endpoint import Endpoint
from ..errors import InvalidRequestError, UnauthorizedClientError
from django_town.utils import add_params_to_url
from django_town.utils import generate_random_from_vschar_set
from django_town.core.settings import OAUTH2_SETTINGS


class AuthorizationEndpoint(Endpoint):
    use_dynamic_redirect_uri = True
    def __init__(self, server, request, client):
                
        if request.method != "POST":
            raise InvalidRequestError()
        if request.redirect_uri and not self.use_dynamic_redirect_uri:
            raise InvalidRequestError()

        super(AuthorizationEndpoint, self).__init__(server, request, client)

    def authorization(self):
        if self._request.response_type != "code":
            raise InvalidRequestError()
        state = self._request.state
        if not state:
            state = generate_random_from_vschar_set(length=30)
        self._state = state
        #self._request.save_session(AUTHORIZATION_STATE_KEY , state)
        self._server.check_available_scope(self._client, self._request.scope)
        code = self._server.generate_code(self._client, self._request.scope, self._request.user)
        return add_params_to_url(self.redirect_uri, {'code': code, 'state': self._state})

    def implicit(self, expires_in):
        if self._request.response_type != "token":
            raise InvalidRequestError()

        redirect_uri = self._request.redirect_uri
        state = self._request.state
        scope = self._request.scope
        if not state:
            state = generate_random_from_vschar_set(length=30)

        access_token = self._server.generate_access_token(self._client, self._request.user, scope, expires_in,
                                                          is_refreshable=False)
        return add_params_to_url(redirect_uri,
                                 {'access_token': access_token.access_token, 'state': state, 'scope': ' '.join(scope),
                                  'expires_in': expires_in, 'token_type': 'Bearer'})


    @property
    def redirect_uri(self):
        if self._request.redirect_uri:
            return self._request.redirect_uri
        default_redirect_uri = self._client.default_redirect_uri
        if default_redirect_uri:
            return default_redirect_uri
        else:
            return OAUTH2_SETTINGS.default_redirect_uri
        # raise UnauthorizedClientError()
