#-*- coding: utf-8 -*-

import functools
from ..errors import InvalidRequestError

STATE_SESSION_KEY = "STATE_SESSION_KEY"


class Endpoint(object):
    """
    base form of Endpoint.
    """
    use_dynamic_redirect_uri = True

    def __init__(self, server, request, client):
        self._server = server
        self._request = request
        self._client = client