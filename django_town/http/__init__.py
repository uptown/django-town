# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django_town.utils import json


def http_json_response(response_dictionary, **kwargs):
    return HttpResponse(json.dumps(response_dictionary), content_type="application/json", **kwargs)