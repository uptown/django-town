from django_town.utils import CurrentTimestamp
from django_town.oauth2.server import oauth2_server
from django.utils.functional import SimpleLazyObject
from django_town.cache.utlis import SimpleCache


__all__ = ['OAuth2Middleware']


class AuthorizationInfo(object):

    def __init__(self):
        self.secret_key = None
        self.client_pk = None
        self.user_pk = None
        self.scope = None
        self.expire = None


def get_access_token(request):
    if not hasattr(request, '_cached_access_token'):
        access_token = request.REQUEST.get('access_token')
        if not access_token:
            try:
                auth_info = request.META.get('HTTP_AUTHORIZATION').split(' ')
                if auth_info[0] == 'Bearer':
                    access_token = auth_info[1]
                else:
                    access_token = None
            except KeyError:
                access_token = None
            except AttributeError:
                access_token = None
        request._cached_access_token = access_token
        return access_token
    return request._cached_access_token



def load_access_info_cache(**_kwargs):
    ret = {}
    client_pk, user_pk, scope, is_refreshable, expire, user_secret_key = \
        oauth2_server.reverse_access_token(_kwargs['access_token'])
    ret['_ut_oauth2_client_pk'] = client_pk
    ret['_ut_oauth2_user_pk'] = user_pk
    ret['_ut_oauth2_scope'] = scope
    ret['_ut_oauth2_secret_key'] = user_secret_key
    ret['_ut_oauth2_expire'] = expire
    ret['_ut_oauth2_access_token'] = _kwargs['access_token'].encode('utf8')
    return ret


access_info_cache = SimpleCache("_ut_ai:%(access_token)s", 60 * 60, load_access_info_cache)



def get_oauth2_authorization_info(request):
    if not hasattr(request, '_cached_oauth2_authorization_info'):
        access_token = request.access_token
        access_info = {}
        if access_token:
            #TODO: session -> cache, api doesn't allow session ...
            try:
                is_access_token_valid = False
                access_info = access_info_cache.get(access_token=access_token)
                if access_info.get('_ut_oauth2_access_token'):
                    if access_info['_ut_oauth2_access_token'] != access_token.encode('utf8'):
                        is_access_token_valid = False
                    else:
                        uask = oauth2_server.get_user_secret_key(access_info['_ut_oauth2_user_pk'],
                                                                 access_info['_ut_oauth2_client_pk'])
                        if access_info['_ut_oauth2_secret_key'] != uask:
                            is_access_token_valid = False
                        elif access_info['_ut_oauth2_expire'] - CurrentTimestamp()() <= 0:
                            is_access_token_valid = False
                        else:
                            is_access_token_valid = True
                if not is_access_token_valid:
                    client_pk, user_pk, scope, is_refreshable, expire, user_secret_key = \
                        oauth2_server.reverse_access_token(access_token)
                    access_info['_ut_oauth2_client_pk'] = client_pk
                    access_info['_ut_oauth2_user_pk'] = user_pk
                    access_info['_ut_oauth2_scope'] = scope
                    access_info['_ut_oauth2_secret_key'] = user_secret_key
                    access_info['_ut_oauth2_expire'] = expire
                    access_info['_ut_oauth2_access_token'] = access_token.encode('utf8')
            except:
                import traceback
                traceback.print_exc()
                access_info['_ut_oauth2_client_pk'] = None
                access_info['_ut_oauth2_scope'] = None
                access_info['_ut_oauth2_secret_key'] = None
                access_info['_ut_oauth2_expire'] = None
                access_info['_ut_oauth2_access_token'] = None
                access_info['_ut_oauth2_user_pk'] = None
        else:
            access_info['_ut_oauth2_client_pk'] = None
            access_info['_ut_oauth2_scope'] = None
            access_info['_ut_oauth2_secret_key'] = None
            access_info['_ut_oauth2_expire'] = None
            access_info['_ut_oauth2_access_token'] = None
            access_info['_ut_oauth2_user_pk'] = None
        request._cached_oauth2_authorization_info = AuthorizationInfo()
        request._cached_oauth2_authorization_info.secret_key = access_info.get('_ut_oauth2_secret_key')
        request._cached_oauth2_authorization_info.client_pk = access_info.get('_ut_oauth2_client_pk')
        request._cached_oauth2_authorization_info.user_pk = access_info.get('_ut_oauth2_user_pk')
        request._cached_oauth2_authorization_info.scope = access_info.get('_ut_oauth2_scope')
        request._cached_oauth2_authorization_info.expire = access_info.get('_ut_oauth2_expire')
        return request._cached_oauth2_authorization_info
    return request._cached_oauth2_authorization_info


class OAuth2Middleware(object):

    def process_request(self, request):
        request.access_token = SimpleLazyObject(lambda: get_access_token(request))
        request.oauth2_authorization_info = SimpleLazyObject(lambda: get_oauth2_authorization_info(request))
        request.oauth2_user = SimpleLazyObject(lambda: oauth2_server.user(request.oauth2_authorization_info.user_pk))

