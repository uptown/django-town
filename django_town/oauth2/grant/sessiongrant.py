#-*- coding: utf-8 -*-

from .grant import Grant
from ..endpoint import TokenEndpoint

class SessionGrant(Grant):
    
    def get_credential(self, expires_in):
        self._token_endpoint = TokenEndpoint(self._server, self._request, self._client)
        return self._token_endpoint.get_credential_session(expires_in)
