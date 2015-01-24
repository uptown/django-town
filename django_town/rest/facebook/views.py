# -*- coding: utf-8 -*-
"""
According to RFC6793(http://tools.ietf.org/html/rfc6749#section-1.3), the flow of facebook authorization like that.
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

 The flow illustrated in Figure 3 includes the following steps:

   (A)  The client initiates the flow by directing the resource owner's
        user-agent to the authorization endpoint.  The client includes
        its client identifier, requested scope, local state, and a
        redirection URI to which the authorization server will send the
        user-agent back once access is granted (or denied).

   (B)  The authorization server authenticates the resource owner (via
        the user-agent) and establishes whether the resource owner
        grants or denies the client's access request.

   (C)  Assuming the resource owner grants access, the authorization
        server redirects the user-agent back to the client using the
        redirection URI provided earlier (in the request or during
        client registration).  The redirection URI includes an
        authorization code and any local state provided by the client
        earlier.

   (D)  The client requests an access token from the authorization
        server's token endpoint by including the authorization code
        received in the previous step.  When making the request, the
        client authenticates with the authorization server.  The client
        includes the redirection URI used to obtain the authorization
        code for verification.

   (E)  The authorization server authenticates the client, validates the
        authorization code, and ensures that the redirection URI
        received matches the URI used to redirect the client in
        step (C).  If valid, the authorization server responds back with
        an access token and, optionally, a refresh token.

This code covers client-side flow.
"""
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.views.decorators.cache import cache_page
from django.views.generic import View
from django_town.facebook import default_client
from django_town.core.settings import SOCIAL_SETTINGS
from django_town.social.resources.user import user_public_resource


class FacebookOAuth2View(View):

    #TODO: not finished
    def success(self, request, access_token, expire_timestamp, allowed, disallowed):
        # print access_token
        user = auth.authenticate(type="facebook", access_token=access_token)
        if user:
            auth.login(request, user)
            if 'sign_in_redirect_uri' in request.session and request.session['sign_in_redirect_uri']:
                sign_in_redirect_uri = request.session['sign_in_redirect_uri']
                del request.session['sign_in_redirect_uri']
                return HttpResponseRedirect(sign_in_redirect_uri)
            return HttpResponseRedirect('/')
        else:
            user_public_resource.create(data={'facebook_access_token': access_token})
            user = auth.authenticate(type="facebook", access_token=access_token)
            if user:
                auth.login(request, user)
                if 'sign_in_redirect_uri' in request.session and request.session['sign_in_redirect_uri']:
                    sign_in_redirect_uri = request.session['sign_in_redirect_uri']
                    del request.session['sign_in_redirect_uri']
                    return HttpResponseRedirect(sign_in_redirect_uri)
                return HttpResponseRedirect('/')
        return self.fail(request)

    def fail(self, request):
        return HttpResponse()

    def permission_required(self, request, allowed, disallowed):
        return HttpResponse()

    def get(self, request):
        if request.GET.get('r'):
            request.session['sign_in_redirect_uri'] = request.GET['r']
        if request.is_secure():
            redirect_uri = "https://" + request.get_host() + request.path_info
        else:
            redirect_uri = "http://" + request.get_host() + request.path_info
        if request.GET.get('code'):
            access_token, expire_timestamp = default_client.get_access_token_and_expire_timestamp(request, redirect_uri)
            # is_success, permissions = default_client.check_permissions(SOCIAL_SETTINGS.FACEBOOK_PERMISSIONS,
            #                                                            SOCIAL_SETTINGS.FACEBOOK_REQUIRED_PERMISSIONS)
            if access_token:
                return self.success(request, access_token, expire_timestamp, [], [])
            return self.permission_required(request,  [], [])
        else:
            url = default_client.get_login_url(request, redirect_uri, SOCIAL_SETTINGS.FACEBOOK_PERMISSIONS)
            return HttpResponseRedirect(url)


@cache_page(60 * 60 * 24 * 365)
def facebook_js_channel(request):
    return HttpResponse("""<script src="//connect.facebook.net/en_US/all.js"></script>""")