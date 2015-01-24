#-*- coding: utf-8 -*-


class OAuth2Credential(object):

    def __init__(self, access_token=None, refresh_token=None, user_secret_key=None, expires_in=None):
        self._inited = False
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_secret_key = user_secret_key
        self.expires_in = expires_in

    def to_dict(self):
        ret = {'access_token': self.access_token, 'token_type': "Bearer", 'expires_in': self.expires_in}
        if self.refresh_token:
            ret['refresh_token'] = self.refresh_token
        return ret