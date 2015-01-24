# -*- coding: utf-8 -*-

import hashlib
import time
import base64
import hmac
from django.utils.six import iteritems
from django_town.utils import json
from django_town.utils.with3 import quote_plus, urlencode, urlparse, urlopen, Request, HTTPError

from django_town.facebook.multipartform import MultiPartForm
from django_town.facebook.exceptions import FBPermissionException, FBTokenExpiredException, \
    FBTokenInvalidException


class Client(object):
    def __init__(self, app_id=None, app_secret=None, access_token=None, code=None,
                 token_invalidate_callback=None, token_permission_required_callback=None,
                 token_expired_callback=None, api_version="v1.0"):
        self.app_id = app_id
        self.user_id = None
        self.app_secret = app_secret
        self.access_token = access_token
        self.code = code
        self.signed_request = {}
        self.token_invalidate_callback = token_invalidate_callback
        self.token_permission_required_callback = token_permission_required_callback
        self.token_expired_callback = token_expired_callback
        self.api_version = api_version

    def _token_expired(self):
        if self.token_expired_callback:
            self.token_expired_callback()
        else:
            raise FBTokenExpiredException("FBTokenExpiredException")

    def _token_invalid(self):
        if self.token_invalidate_callback:
            self.token_invalidate_callback()
        else:
            raise FBTokenInvalidException("FBTokenInvalidException")

    def _permission_error(self):
        if self.token_permission_required_callback:
            self.token_permission_required_callback()
        else:
            raise FBPermissionException("FBPermissionException")

    def _error_handle(self, e):

        if e.code == 400:
            err = e.read()
            err = json.loads(err)
            if err['error'].get('error_subcode') == 463:
                self._token_expired()
            else:
                self._token_invalid()

        elif e.code == 403:
            err = e.read()
            err = json.loads(err)
            self._permission_error()

    def get_login_url(self, request, redirect_uri, permissions):
        request.session['facebook_state'] = hashlib.sha224(str(time.time())).hexdigest()
        url = "https://www.facebook.com/" + ("v2.0/" if self.api_version == "v2.0" else "") + "dialog/oauth?client_id=%s&redirect_uri=%s&state=%s&scope=%s" % \
              (self.app_id, quote_plus(redirect_uri), request.session['facebook_state'], ",".join(permissions))
        return url


    def get_access_token_from_short_token(self, short):
        url = "https://graph.facebook.com/oauth/access_token?%s" % \
              (urlencode({'client_id': self.app_id, 'grant_type': 'fb_exchange_token',
                                 'client_secret': self.app_secret, 'fb_exchange_token': short}))
        parsed = urlparse.parse_qs(urlopen(url).read())
        access_token = parsed['access_token']
        if type(access_token) is list or type(access_token) is tuple:
            access_token = access_token[0]

        self.access_token = access_token
        return access_token

    def get_access_token_and_expire_timestamp(self, request, redirect_uri):
        if not request.session.has_key('facebook_state'):
            return None, None
        elif request.session['facebook_state'] != request.GET.get('state'):
            return None, None

        url = "https://graph.facebook.com/oauth/access_token?%s" % (urlencode({
            'client_id': self.app_id, 'redirect_uri': redirect_uri, 'client_secret': self.app_secret,
            'code': request.GET.get('code')}))
        parsed = urlparse.parse_qs(urlopen(url).read())
        access_token = parsed['access_token']
        expires = parsed['expires']
        if type(access_token) is list or type(access_token) is tuple:
            access_token = access_token[0]
            expires = expires[0]
        expires = int(expires) + int(time.time())
        self.access_token = access_token
        return access_token, expires

    def get_access_token(self, redirect_uri, code):
        url = "oauth/access_token?%s" % (urlencode({
            'client_id': self.app_id, 'redirect_uri': redirect_uri, 'client_secret': self.app_secret, 'code': code}))
        parsed = urlparse.parse_qs(urlopen(url).read())
        access_token = parsed['access_token']
        if type(access_token) is list or type(access_token) is tuple:
            access_token = access_token[0]

        self.access_token = access_token
        return access_token

    def get_page_access_token(self, uid, access_token=None):
        if access_token is None:
            access_token = self.access_token
        url = "%s?fields=access_token&%s" % (uid, urlencode({'access_token': access_token}))
        return self.get_object(url)['access_token']

    def set_access_token(self, access_token):
        self.access_token = access_token

    def check_permissions(self, permissions, required_permissions="", token=None):
        if token is None:
            token = self.access_token
        ret = self.get_object('me/permissions', access_token=token)['data'][0]

        permissions = permissions.split(',')

        allowed = []
        disallowed = []
        is_success = True
        for permission in permissions:
            permission = permission.strip()
            if ret.has_key(permission) is False:
                if permission.strip() in required_permissions:
                    is_success = False
                disallowed.append(permission)
            else:
                allowed.append(permission)
        return is_success, (allowed, disallowed)

    def get_object(self, path, **kwargs):
        if not 'access_token' in kwargs and self.access_token:
            kwargs['access_token'] = self.access_token
        url = "https://graph.facebook.com/" + self.api_version + "/%s?%s" % (str(path), urlencode(kwargs))
        try:
            ret = urlopen(url).read()
            return json.loads(ret)
        except HTTPError as e:
            self._error_handle(e)

    def post_object(self, path, data=None, file_data=None):
        if not 'access_token' in data and self.access_token:
            data['access_token'] = self.access_token
        url = "https://graph.facebook.com/" + self.api_version + "/%s" % str(path)
        if not data:
            data = {}
        try:
            if file_data:
                form = MultiPartForm()
                for key, val in iteritems(data):
                    form.add_field(key, val)
                for key, val in file_data.iteritmes():
                    form.add_file(key, val['name'], val['source'], mimetype=val.get('mimetype'))
                request = Request(url)
                body = str(form)
                request.add_header('Content-type', form.get_content_type())
                request.add_header('Content-length', len(body))
                request.data =body
                ret = urlopen(request).read()
            else:
                ret = urlopen(url, urlencode(data)).read()
            return json.loads(ret)
        except HTTPError as e:
            self._error_handle(e)
            return {}

    def load_signed_request(self, signed_request):
        """Load the user state from a signed_request value"""
        try:
            sig, payload = signed_request.split(u'.', 1)
            sig = self.base64_url_decode(sig)
            data = json.loads(self.base64_url_decode(payload))

            expected_sig = hmac.new(
                self.app_secret, msg=payload, digestmod=hashlib.sha256).digest()

            # allow the signed_request to function for upto 1 day
            if sig == expected_sig and \
                            data[u'issued_at'] > (time.time() - 86400):
                self.signed_request = data
                self.user_id = data.get(u'user_id')
                self.access_token = data.get(u'oauth_token')
        except ValueError:
            pass  # ignore if can't split on dot

    @staticmethod
    def base64_url_decode(data):
        data = data.encode(u'ascii')
        data += '=' * (4 - (len(data) % 4))
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def base64_url_encode(data):
        return base64.urlsafe_b64encode(data).rstrip('=')

    def login_or_get_login_url(self, request, permissions):
        #if request.is_secure():
        if request.is_secure:
            redirect_uri = "https://" + request.get_host() + request.path_info
        else:
            redirect_uri = "http://" + request.get_host() + request.path_info
        if request.GET.get('code'):
            access_token, expire_timestamp = self.get_access_token_and_expire_timestamp(request, redirect_uri)
            self.access_token = access_token
            return True, access_token
        else:
            url = self.get_login_url(request, redirect_uri, permissions)
            return False, url