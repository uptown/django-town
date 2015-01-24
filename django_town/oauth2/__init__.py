#-*- coding: utf-8 -*-
from django_town.core.settings import OAUTH2_SETTINGS
from django_town.oauth2.request import oauth2_request_class, FakeRequest
from django_town.oauth2.grant import CodeGrant, ImplicitGrant, PasswordCredentialsGrant, SessionGrant, RefreshTokenGrant
from django_town.oauth2.errors import OAuth2Error, UnsupportedResponseTypeError, InvalidRequestError
from django_town.oauth2.server import oauth2_server


def authorization(request):
    """
    authorization process with django request.
    Request must be secure and default available response type is "code" and "token".
    """
    django_request = oauth2_request_class()(request)
    try:
        # if not request.is_secure():
        #     raise InvalidRequestError()
        if django_request.response_type == "code":
            return authorization_code_grant_step1(request)
        elif django_request.response_type == "token":
            return implicit_grant(request)
        raise UnsupportedResponseTypeError()
    except OAuth2Error as e:
        import traceback
        traceback.print_exc()
        if django_request.redirect_uri:
            return e.to_uri(django_request.redirect_uri)
        return e.to_uri(OAUTH2_SETTINGS.default_redirect_uri)


def get_credential(request):
    """
    token process with django resource.
    Request must be secure and default available grant type is password, authorization_code, client_credentials,
    and refresh_token.
    """
    django_request = oauth2_request_class()(request)
    if django_request.grant_type == "password":
        return password_grant(request)
    elif django_request.grant_type == "authorization_code":
        return authorization_code_grant_step2(request)
    elif django_request.grant_type == "client_credentials":
        return implicit_grant(request)
    elif django_request.grant_type == "session":
        return session_grant(django_request.client_id, request.user.id, django_request.scope)
    elif django_request.grant_type == "refresh_token":
        return refresh_token_grant(request)
    else:
        return oauth2_server.get_credential_with_grant_type(django_request.grant_type, request)
    # raise UnsupportedResponseTypeError()
    

def get_credential_from_user(request):
    return password_grant(request)


def authorization_code_grant_step1(request):
    """
    Code grant step1 short-cut. This will return url with code.
    """
    django_request = oauth2_request_class()(request)
    grant = CodeGrant(oauth2_server, django_request)
    return grant.authorization()


def authorization_code_grant_step2(request):
    """
    Code grant step2 short-cut. This will return access credential.
    """
    django_request = oauth2_request_class()(request)
    grant = CodeGrant(oauth2_server, django_request)
    credential = grant.get_credential(OAUTH2_SETTINGS.ACCESS_TOKEN_EXPIRATION)
    return credential


def password_grant(request):
    """
    Password grant short-cut.
    """
    django_request = oauth2_request_class()(request)
    grant = PasswordCredentialsGrant(oauth2_server, django_request)
    return grant.get_credential(OAUTH2_SETTINGS.ACCESS_TOKEN_EXPIRATION)


def refresh_token_grant(request):
    """
    Refresh token grant short-cut.
    """
    django_request = oauth2_request_class()(request)
    grant = RefreshTokenGrant(oauth2_server, django_request)
    return grant.get_credential(OAUTH2_SETTINGS.ACCESS_TOKEN_EXPIRATION)


def session_grant(client_id, user, scope):
    """
    Fake grant process for some usages. It will return access credential.
    """
    if user is None:
        raise UnsupportedResponseTypeError()
    django_request = FakeRequest({'client_id': client_id,
                                  'user': user,
                                  'scope': scope,
                                  'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                                  'grant_type': 'session'
                                  })
    grant = SessionGrant(oauth2_server, django_request)
    return grant.get_credential(OAUTH2_SETTINGS.ACCESS_TOKEN_EXPIRATION)
    

def implicit_grant(request):
    """
    Implicit token grant short-cut.
    """
    return ImplicitGrant(oauth2_server, oauth2_request_class()(request)).get_redirection_uri(3600)


def access_token_response(response):
    response['Content-Type'] = 'application/json;charset=UTF-8'
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-cache'
    return response

try:
    if not OAUTH2_SETTINGS.ACCESS_TOKEN_SECRET_KEY:
        raise ImportError
except KeyError:
    raise ImportError

