#-*- coding: utf-8 -*-
from django.contrib import auth
from django.utils.http import int_to_base36, base36_to_int
from django.utils.functional import SimpleLazyObject
from django_town.core.settings import OAUTH2_SETTINGS
from django_town.utils import class_from_path, generate_random_from_vschar_set, CurrentTimestamp, \
    encrypt_cbc, decrypt_cbc
from django_town.oauth2.errors import OAuth2Error, InvalidScopeError, InvalidRequestError, \
    UnsupportedResponseTypeError, InvalidAccessToken, AccessTokenExpired, InvalidRefreshToken
from django_town.oauth2.models import UserClientSecretKey, Client
from django.contrib.auth import get_user_model
from django_town.oauth2.user import OAuth2User
from django_town.oauth2.credential import OAuth2Credential
from django.db.models.signals import post_syncdb
from django_town.oauth2.models import Scope


def scope_update(sender, **kwargs):
    SCOPE_LOOKUP = {}
    R_SCOPE_LOOKUP = {}
    for each in OAUTH2_SETTINGS.SCOPE:
        scope, created = Scope.objects.get_or_create(name=each)
        SCOPE_LOOKUP[each] = scope.id - 1
        R_SCOPE_LOOKUP[scope.id - 1] = each

post_syncdb.connect(scope_update, sender=Scope)


class OAuth2Server(object):

    @classmethod
    def check_available_scope(cls, client, scope):
        for a_scope in scope:
            # print client.available_scope
            if a_scope.lower() not in client.available_scope:
                raise InvalidScopeError()
        return

    def __init__(self):
        pass


    @classmethod
    def str_to_scope(cls, scope_str):
        global R_SCOPE_LOOKUP
        s_int = base36_to_int(scope_str)
        arr = []
        while s_int != 0:
            remain = s_int % 2
            s_int /= 2
            arr.append(remain)
        scope = []
        for val in arr:
            if val:
                scope.append(R_SCOPE_LOOKUP[val])
        return scope

    @classmethod
    def scope_to_str(cls, scope):
        global SCOPE_LOOKUP
        ret = 0
        for a_scope in scope:
            try:
                ret += 1 << SCOPE_LOOKUP(a_scope)
            except ValueError:
                raise InvalidScopeError()
        return int_to_base36(ret)

    @classmethod
    def store_credential(cls, credential, client_pk, user_pk, scope, expire, is_refreshable):
        pass

    @classmethod
    def _generate_access_token(cls, client_pk, user_pk, scope, expires_in, is_refreshable):
        user_secret_key, created_unused = UserClientSecretKey.objects.get_or_create_safe(user_id=user_pk,
                                                                                         client=Client(pk=client_pk))

        secret_key = user_secret_key.secret_key.encode('utf-8')
        expire = CurrentTimestamp(expires_in)()
        checksum = generate_random_from_vschar_set(length=10)

        scope_str = cls.scope_to_str(scope)

        info = scope_str + "." + int_to_base36(int(is_refreshable))
        access_token = int_to_base36(expire) + "." + \
                       encrypt_cbc(int_to_base36(client_pk) + "." + int_to_base36(user_pk) + '.' + \
                       int_to_base36(expire) + '.' + info + '.' + checksum, OAUTH2_SETTINGS.ACCESS_TOKEN_SECRET_KEY) \
                       + '.' + encrypt_cbc(checksum, secret_key)
        if is_refreshable:
            refresh_token = encrypt_cbc(checksum + "." + generate_random_from_vschar_set(length=2),
                                        secret_key)
        else:
            refresh_token = None
        ret = OAuth2Credential(access_token=access_token, refresh_token=refresh_token, user_secret_key=secret_key,
                                expires_in=expires_in)
        cls.store_credential(ret, client_pk, user_pk, scope, expire, is_refreshable)
        return ret

    @classmethod
    def generate_access_token(cls, client, user, scope, expires_in, is_refreshable):
        if not user:
            raise InvalidRequestError()
        cls.check_available_scope(client, scope)
        return cls._generate_access_token(client.pk, user.pk, scope, expires_in, is_refreshable)

    @classmethod
    def check_code_and_decrypt_scope(cls, code, client, user):
        #TODO make fancy for error handling
        try:
            client_pk, scope_str, user_pk, timestamp, checksum_unused \
                = decrypt_cbc(code, OAUTH2_SETTINGS.CODE_SECRET_KEY).split('.')
            if timestamp >= CurrentTimestamp() and str(client.pk) == str(client_pk) and str(user.pk) == str(user_pk):
                return cls.str_to_scope(scope_str)
            raise InvalidRequestError()
        except OAuth2Error:
            raise
        except:
            raise InvalidRequestError()

    @classmethod
    def generate_code(cls, client, scope, user):
        checksum = generate_random_from_vschar_set(length=3)
        info = int_to_base36(client.pk) + "." + cls.scope_to_str(scope) + "." + int_to_base36(user.pk) + "." \
               + int_to_base36(CurrentTimestamp(OAUTH2_SETTINGS.CODE_EXPIRATION)()) + '.' + checksum
        return encrypt_cbc(info, OAUTH2_SETTINGS.CODE_SECRET_KEY)

    @classmethod
    def validate_access_token(cls, access_token, scope):
        raise OAuth2Error()
    
    def user_password_changed(self, user_id):
        raise OAuth2Error()

    @staticmethod
    def user_from_username_and_password(username, password):
        return OAuth2User(django_user=auth.authenticate(username=username, password=password))

    @staticmethod
    def user(user_pk):
        return OAuth2User(django_user=get_user_model()(pk=user_pk))
    
    def user_from_access_token_and_scope(self, access_token, scope):
        raise OAuth2Error()
        
    def generate_client_access_token(self,  client, scope, expires_in):
        raise OAuth2Error()
    
    def register_client(self, holder_id, client_name, description, redirect_uri):
        pass
    
    def check_user_authorized_client_for_scope(self, user_id, client_id, scope):
        raise OAuth2Error()

    @classmethod
    def reverse_access_token(cls, access_token):
        if not access_token:
            raise InvalidAccessToken()
        part = access_token.split('.')
        if len(part) != 3:
            raise InvalidAccessToken()

        expire, info, check = part
        expire_timestamp = int(base36_to_int(expire))
        if CurrentTimestamp()() > expire_timestamp:
            raise AccessTokenExpired()

        part = decrypt_cbc(info, OAUTH2_SETTINGS.ACCESS_TOKEN_SECRET_KEY).split('.')

        if len(part) != 6:
            raise InvalidAccessToken()

        client_pk, user_pk, expire2, scope, is_refreshable, checksum = base36_to_int(part[0]), base36_to_int(part[1]), \
                                                                       part[2], part[3], part[4], part[5]
        if expire2 != expire:
            raise InvalidAccessToken()

        user_secret_key = UserClientSecretKey.objects.get_cached(user_id=user_pk,
                                                                 client=Client(pk=client_pk)).secret_key.encode('utf-8')
        if checksum != decrypt_cbc(check, user_secret_key):
            raise InvalidAccessToken()

        return client_pk, user_pk, scope, is_refreshable, expire_timestamp, user_secret_key

    @classmethod
    def refresh_access_token(cls, refresh_token, old_access_token, expires_in):
        if not old_access_token:
            raise InvalidAccessToken()
        part = old_access_token.split('.')
        if len(part) != 3:
            raise InvalidAccessToken()

        expire, info, check = part
        part = decrypt_cbc(info, OAUTH2_SETTINGS.ACCESS_TOKEN_SECRET_KEY).split('.')
        client_pk, user_pk, expire2, scope, is_refreshable, checksum = base36_to_int(part[0]), base36_to_int(part[1]), \
                                                                       part[2], part[3], part[4], part[5]
        user_secret_key = UserClientSecretKey.objects.get_cached(user_id=user_pk,
                                                                 client=Client(pk=client_pk)).secret_key.encode('utf-8')
        if checksum != decrypt_cbc(check, user_secret_key):
            raise InvalidAccessToken()

        refresh_checksum, _unused = decrypt_cbc(refresh_token, user_secret_key).split('.')
        if checksum != refresh_checksum:
            raise InvalidRefreshToken()
        return cls._generate_access_token(client_pk, user_pk, cls.str_to_scope(scope), expires_in, is_refreshable)
        # def generate_access_token(cls, client, user, scope, expires_in, is_refreshable):

    def get_user_secret_key(self, user_pk, client_pk):
        return UserClientSecretKey.objects.get_cached(user_id=user_pk,
                                                      client=Client(pk=client_pk)).secret_key.encode('utf-8')

    def get_credential_with_grant_type(self, grant_type, request):
        raise UnsupportedResponseTypeError()


def lazy_load_oauth2_server():

    try:
        return class_from_path(OAUTH2_SETTINGS.SERVER)()
    except KeyError:
        return OAuth2Server()

oauth2_server = SimpleLazyObject(lazy_load_oauth2_server)