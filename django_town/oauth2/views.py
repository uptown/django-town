#-*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django_town.oauth2 import get_credential, authorization, OAuth2Error
from django_town.http import http_json_response
from django.shortcuts import render_to_response
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext


class TokenView(View):

    def post(self, request):
        try:
            return http_json_response(get_credential(request).to_dict())
        except OAuth2Error as e:
            return http_json_response(e.to_dict(), status=400)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TokenView, self).dispatch(*args, **kwargs)


class AuthorizeView(View):

    def post(self, request):
        return HttpResponseRedirect(authorization(request))

    def get(self, request):
        return render_to_response("oauth2/authorize.html", request.GET, RequestContext(request))

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthorizeView, self).dispatch(request, *args, **kwargs)

class DialogView(View):

    def get(self, request):
        return render_to_response()

class CheckPermissionView(View):

    def get(self, request):
        return HttpResponseRedirect(authorization(request))