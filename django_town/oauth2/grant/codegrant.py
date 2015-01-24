#-*- coding: utf-8 -*-

from .grant import Grant
from ..endpoint import AuthorizationEndpoint, TokenEndpoint


class CodeGrant(Grant):
    """
       The authorization code grant type is used to obtain both access
   tokens and refresh tokens and is optimized for confidential clients.
   Since this is a redirection-based flow, the client must be capable of
   interacting with the resource owner's user-agent (typically a web
   browser) and capable of receiving incoming requests (via redirection)
   from the authorization server.

     +----------+
     | Resource |
     |   Owner  |
     |          |
     +----------+
          ^
          |
         (B)
     +----|-----+          Client Identifier      +---------------+
     |         -+----(A)-- & Redirection URI ---->|               |
     |  User-   |                                 | Authorization |
     |  Agent  -+----(B)-- User authenticates --->|     Server    |
     |          |                                 |               |
     |         -+----(C)-- Authorization Code ---<|               |
     +-|----|---+                                 +---------------+
       |    |                                         ^      v
      (A)  (C)                                        |      |
       |    |                                         |      |
       ^    v                                         |      |
     +---------+                                      |      |
     |         |>---(D)-- Authorization Code ---------'      |
     |  Client |          & Redirection URI                  |
     |         |                                             |
     |         |<---(E)----- Access Token -------------------'
     +---------+       (w/ Optional Refresh Token)

   Note: The lines illustrating steps (A), (B), and (C) are broken into
   two parts as they pass through the user-agent.

    """
    
    def authorization(self):
        self._authorization_endpoint = AuthorizationEndpoint(self._server, self._request, self._client)
        redirect_uri = self._authorization_endpoint.authorization()
        return redirect_uri
        
    def get_credential(self, expires_in):
        self._token_endpoint = TokenEndpoint(self._server, self._request, self._client)
        return self._token_endpoint.get_credential(expires_in)