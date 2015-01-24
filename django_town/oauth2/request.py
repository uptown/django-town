#-*- coding: utf-8 -*-
from django_town.utils import CaseLessDict
from .errors import AccessDeniedError
from django_town.utils import class_from_path
from django_town.core.settings import OAUTH2_SETTINGS
from django_town.oauth2.user import OAuth2User



def authorization_from_django_request(request):
    return request.META.get('HTTP_AUTHORIZATION')


def uri_from_django_request(request):
    return request.build_absolute_uri()


def http_method_from_django_request(request):
    return request.method


def get_dict_from_django_request(request):
    return request.GET


def post_dict_from_django_request(request):
    return request.POST


class OAuth2Request(object):

    def __init__(self, request):
        if request:
            self._uri = uri_from_django_request(request)
            self._method = http_method_from_django_request(request).upper()
            self._body = CaseLessDict((get_dict_from_django_request(request)
                                       if self._method == "GET" else post_dict_from_django_request(request)))
            self._request = request
            self._client = None
        
    def save_session(self, key, value):
        pass
    
    @property
    def method(self):
        return self._method
    
    @property
    def client_id(self):
        return self._body.get('client_id')
    
    @property
    def client_secret(self):
        return self._body.get('client_secret')
    
    @property
    def username(self):
        return self._body.get('username')
    
    @property
    def password(self):
        return self._body.get('password')
    
    @property
    def grant_type(self):
        return self._body.get('grant_type')
    
    @property
    def code(self):
        return self._body.get('code')
    
    @property
    def redirect_uri(self):
        return self._body.get('redirect_uri')
    
    @property
    def response_type(self):
        return self._body.get('response_type')
        
    @property
    def refresh_token(self):
        return self._body.get('refresh_token')

    @property
    def access_token(self):
        return self._body.get('access_token')

    @property
    def state(self):
        return self._body.get('state')
    
    @property
    def scope(self):
        scope = self._body.get('scope')
        if scope:
            return scope.split(' ')
        return []
    #
    #@property
    #def scope(self):
    #    return self._body.get('scope')

    @property
    def user(self):
        if self._request.user.is_authenticated():
            return OAuth2User(django_user=self._request.user)
        else:
            raise AccessDeniedError()
    

def oauth2_request_class():
    try:
        return class_from_path(OAUTH2_SETTINGS.REQUEST)
    except KeyError:
        return OAuth2Request


class FakeRequest(OAuth2Request):
    
    def __init__(self, body):
        self._body = body
        self._method = "POST"
        super(FakeRequest, self).__init__(None)
    
    
    @property
    def method(self):
        return self._method
    
    @property
    def client_id(self):
        return self._body.get('client_id')
    
    @property
    def client_secret(self):
        return self._body.get('client_secret')
    
    @property
    def username(self):
        return self._body.get('username')
    
    @property
    def password(self):
        return self._body.get('password')
    
    @property
    def grant_type(self):
        return self._body.get('grant_type')
    
    @property
    def code(self):
        return self._body.get('code')
    
    @property
    def redirect_uri(self):
        return self._body.get('redirect_uri')
    
    @property
    def response_type(self):
        return self._body.get('response_type')
        
    @property
    def state(self):
        return self._body.get('state')
    
    @property
    def user(self):
        return self._body.get('user')
