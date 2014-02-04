# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Python client library for the Facebook Platform.

This client library is designed to support the Graph API and the official
Facebook JavaScript SDK, which is the canonical way to implement
Facebook authentication. Read more about the Graph API at
http://developers.facebook.com/docs/api. You can download the Facebook
JavaScript SDK at http://github.com/facebook/connect-js/.

If your application is using Google AppEngine's webapp framework, your
usage of this module might look like this:

    user = facebook.get_user_from_cookie(self.request.cookies, key, secret)
    if user:
        graph = facebook.GraphAPI(user["access_token"])
        profile = graph.get_object("me")
        friends = graph.get_connections("me", "friends")

"""

import urllib
import urlparse
import urllib2
import hashlib
import time
import base64
import hmac

from django_town.facebook.multipartform import MultiPartForm
from django_town.utils import json
from django_town.facebook.exceptions import FBPermissionException, FBTokenExpiredException, \
    FBTokenInvalidException


class Client(object):

    def __init__(self,  app_id=None, app_secret=None, access_token=None, code=None,
                 token_invalidate_callback=None, token_permission_required_callback=None,
                 token_expired_callback=None):
        self.app_id = app_id
        self.user_id = None
        self.app_secret = app_secret
        self.access_token = access_token
        self.code = code
        self.signed_request = {}
        self.token_invalidate_callback = token_invalidate_callback
        self.token_permission_required_callback = token_permission_required_callback
        self.token_expired_callback = token_expired_callback

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

    def get_login_url(self, request,redirect_uri, permissions ):
        request.session['facebook_state'] = hashlib.sha224(str(time.time())).hexdigest()
        url = "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&state=%s&scope=%s" % \
              (self.app_id, urllib.quote_plus(redirect_uri), request.session['facebook_state'],permissions)
        return url


    def get_access_token_from_short_token(self, short):
        url = "https://graph.facebook.com/oauth/access_token?%s" % \
              (urllib.urlencode({'client_id': self.app_id, 'grant_type': 'fb_exchange_token',
                                 'client_secret': self.app_secret, 'fb_exchange_token': short}))
        parsed = urlparse.parse_qs(urllib2.urlopen(url).read())
        access_token = parsed['access_token']
        if type(access_token) is list or type(access_token) is tuple:
            access_token = access_token[0]

        self.access_token = access_token
        return access_token

    def get_access_token_and_expire_timestamp(self, request,redirect_uri):
        if not request.session.has_key('facebook_state'):
            return None, None
        elif request.session['facebook_state'] != request.GET.get('state'):
            return None, None

        url = "https://graph.facebook.com/oauth/access_token?%s" % (urllib.urlencode({
        'client_id': self.app_id, 'redirect_uri': redirect_uri, 'client_secret': self.app_secret,
        'code': request.GET.get('code')}))
        parsed = urlparse.parse_qs(urllib2.urlopen(url).read())
        access_token = parsed['access_token']
        expires = parsed['expires']
        if type(access_token) is list or type(access_token) is tuple:
            access_token = access_token[0]
            expires = expires[0]
        expires = int(expires) + int(time.time())
        self.access_token = access_token
        return access_token, expires

    def get_access_token(self, redirect_uri, code):
        url = "oauth/access_token?%s" % (urllib.urlencode({
       'client_id': self.app_id, 'redirect_uri': redirect_uri, 'client_secret': self.app_secret, 'code': code}))
        parsed = urlparse.parse_qs(urllib2.urlopen(url).read())
        access_token = parsed['access_token']
        if type(access_token) is list or type(access_token) is tuple:
            access_token = access_token[0]

        self.access_token = access_token
        return access_token

    def get_page_access_token(self, uid, access_token=None):
        if access_token is None:
            access_token = self.access_token
        url = "%s?fields=access_token&%s" % (uid,urllib.urlencode({'access_token': access_token}))
        return self.get_object(url)['access_token']

    def set_access_token(self, access_token):
        self.access_token = access_token

    def check_permissions(self, permissions, required_permissions = "", token = None ):
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
        url = "https://graph.facebook.com/%s?%s" % (str(path), urllib.urlencode(kwargs))
        try:
            ret = urllib2.urlopen(url).read()
            return json.loads(ret)
        except urllib2.HTTPError, e:
            self._error_handle(e)

    def post_object(self, path, data=None, file_data=None):
        url = "https://graph.facebook.com/%s" % str(path)
        if not data:
            data = {}
        try:
            if file_data:
                form = MultiPartForm()
                for key, val in data.iteritems():
                    form.add_field(key, val)
                for key, val in file_data.iteritmes():
                    form.add_file(key, val['name'], val['source'], mimetype=val.get('mimetype'))
                request = urllib2.Request(url)
                body = str(form)
                request.add_header('Content-type', form.get_content_type())
                request.add_header('Content-length', len(body))
                request.add_data(body)
                ret = urllib2.urlopen(request).read()
            else:
                ret = urllib2.urlopen(url, data).read()
            return json.loads(ret)
        except urllib2.HTTPError, e:
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
            pass # ignore if can't split on dot

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
            access_token, expire_timestamp = self.get_access_token_and_expire_timestamp(request,redirect_uri)
            self.access_token = access_token
            return True, access_token
        else:
            url = self.get_login_url(request, redirect_uri, permissions)
            return False, url