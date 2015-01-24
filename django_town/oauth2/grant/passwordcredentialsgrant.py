#-*- coding: utf-8 -*-

from .grant import Grant
from ..endpoint import TokenEndpoint


class PasswordCredentialsGrant(Grant):
    """
   The resource owner password credentials grant type is suitable in
   cases where the resource owner has a trust relationship with the
   client, such as the device operating system or a highly privileged
   application.  The authorization server should take special care when
   enabling this grant type and only allow it when other flows are not
   viable.

   This grant type is suitable for clients capable of obtaining the
   resource owner's credentials (username and password, typically using
   an interactive form).  It is also used to migrate existing clients
   using direct authentication schemes such as HTTP Basic or Digest
   authentication to OAuth by converting the stored credentials to an
   access token.
     +----------+
     | Resource |
     |  Owner   |
     |          |
     +----------+
          v
          |    Resource Owner
         (A) Password Credentials
          |
          v
     +---------+                                  +---------------+
     |         |>--(B)---- Resource Owner ------->|               |
     |         |         Password Credentials     | Authorization |
     | Client  |                                  |     Server    |
     |         |<--(C)---- Access Token ---------<|               |
     |         |    (w/ Optional Refresh Token)   |               |
     +---------+                                  +---------------+

            Figure 5: Resource Owner Password Credentials Flow
    """
    
    def get_credential(self, expires_in):
        self._token_endpoint = TokenEndpoint(self._server, self._request, self._client)
        return self._token_endpoint.get_credential_password(expires_in)
        