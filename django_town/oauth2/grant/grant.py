#-*- coding: utf-8 -*-

from django_town.oauth2.client import oauth2_client_class


class Grant(object):

    def __init__(self, server, request, client=None):
        
        self._server = server
        self._request = request
        if not client:
            self._client = oauth2_client_class()(request.client_id)
        else:
            self._client = client
            
        self._scope = request.scope
