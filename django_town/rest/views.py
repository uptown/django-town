# -*- coding: utf-8 -*-
import urllib
import sys
import logging
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import classonlymethod
from django_town.http import http_json_response
from django_town.cache import defaultCacheManager
from django_town.rest.permissions import AllowAny
from django_town.rest.exceptions import RestError, RestRuntimeError, RestMethodNotAllowed, RestBadRequest
from django_town.rest.resources import Resource
from django_town.core.settings import REST_SETTINGS
from django_town.utils import pluralize

_CRUD_MAPPING = {
    'post': 'create',
    'get': 'read',
    'patch': 'update',
    'delete': 'delete'
}

logger = logging.getLogger('django.request')


def _prepare_request(request, *args, **kwargs):
    """
    Populates request.PUT and request.FILES from
    request.raw_post_data. PUT and POST requests differ
    only in REQUEST_METHOD, not in the way data is encoded.
    Therefore we can use Django's POST data retrieval method
    for PUT.
    """
    if request.method == "DELETE":
        request.method = 'POST'
        request._load_post_and_files()
        request.method = 'DELETE'
        request.DELETE = request.REQUEST

    elif request.method == 'PUT':
        request.method = 'POST'
        request._load_post_and_files()
        request.method = 'PUT'
        request.PUT = request.REQUEST


class RestApiView(View):
    """default Api View for rest design"""
    permission_classes = [AllowAny]
    crud_method_names = None

    @classonlymethod
    def as_view(cls, **kwargs):
        for key in kwargs:
            if key in cls.crud_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))

        return super(RestApiView, cls).as_view(**kwargs)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """
        the first entering point for http call,
        check method is allowed
        and cached ApiError and managed by lazy cache manager
        """
        # import datetime
        # start = datetime.datetime.now()
        _prepare_request(request, *args, **kwargs)
        self.request = request
        self.args = args
        self.kwargs = kwargs
        defaultCacheManager.start_session()
        success_status = 200

        suppress_http_code = request.REQUEST.get('suppress_http_code', False)
        try:
            self.check_permissions(request, *args, **kwargs)
            method = request.method.lower()
            if method == "head" or method == "options":
                method = "get"
            crud_method = _CRUD_MAPPING[method]
            if (self.crud_method_names and crud_method in self.crud_method_names) or \
                    (self.crud_method_names is None and method in self.http_method_names):
                handler = getattr(self, crud_method, None)
            else:
                handler = None
            if crud_method == "create":
                success_status = 201
            if not handler:
                raise RestMethodNotAllowed()
            response = handler(request, *args, **kwargs)
        except RestError, e:
            response = e.to_response(suppress_http_code=suppress_http_code)
        except:
            import traceback
            traceback.print_exc()
            logger.error('Internal Server Error: %s', request.path,
                         exc_info=sys.exc_info(), extra={'status_code': 500, 'request': request}
                         )
            response = RestRuntimeError().to_response(suppress_http_code=suppress_http_code)

        if isinstance(response, dict):
            if suppress_http_code:
                response['_http_status_code'] = success_status
                response = http_json_response(response)
            else:
                response = http_json_response(response, status=success_status)
        defaultCacheManager.end_session()
        # response["Access-Control-Allow-Origin"] = "*"
        # response["Access-Control-Allow-Methods"] = "GET"
        # response["Access-Control-Max-Age"] = "1000"
        # response["Access-Control-Allow-Headers"] = "*"
        # end = datetime.datetime.now()
        # print end - start
        return response

    def check_permissions(self, request, *args, **kwargs):
        """
        check permission for request
        """
        for permission in self.permission_classes:
            permission().check_permission(request, *args, **kwargs)

    @classonlymethod
    def as_rest_view(cls, **kwargs):
        """
        for future usage ...
        :param kwargs:
        :return:
        """
        as_view = cls.as_view(**kwargs)

        return as_view

    @classmethod
    def path(cls):
        return ""


class RestListApiView(RestApiView):

    base_url = REST_SETTINGS.SITE_URL
    default_path_format = ""
    reverse = False
    max_limit = 20
    crud_method_names = ['read', 'create']
    collection_path = ""

    def list_url(self, current_path, start, limit=20, filter_type=None, query_string=None, **kwargs):
        return self.base_url + current_path + "?start=" + str(start) + '&limit=' + str(limit) + \
               (("&filter=" + str(filter_type)) if filter_type else "") + ("&q=" +
                urllib.quote_plus(query_string.encode('utf-8')) if query_string else "")

    def read(self, request, **kwargs):
        current_path = request.path
        try:
            start = int(request.GET.get('start', -1 if self.reverse else 0))
            limit = int(request.GET.get('limit', self.max_limit))
        except ValueError:
            raise RestBadRequest()
        if limit <= 0:
            raise RestBadRequest()
        if limit > self.max_limit:
            limit = self.max_limit
        filter_type = request.GET.get('filter')
        query_string = request.GET.get('q')

        ret = {}
        data, start, next_index = self.collection(start, limit, filter_type=filter_type,
                                                  query_string=query_string, request=request, **kwargs)

        ret['data'] = data

        if start < 0:
            raise RestBadRequest()
        paging = {}
        if start == 0 and next_index:
            paging['next'] = self.list_url(current_path, next_index, limit=limit, filter_type=filter_type,
                                           query_string=query_string, **kwargs)
            paging['cursors'] = {'next': next_index, 'current': start}
        elif next_index:
            paging['next'] = self.list_url(current_path, next_index, limit=limit, filter_type=filter_type,
                                           query_string=query_string, **kwargs)
            prev = start - limit
            if prev > 0:
                paging['prev'] = self.list_url(current_path, prev, limit=limit, filter_type=filter_type,
                                               query_string=query_string, **kwargs)
                paging['cursors'] = {'next': next_index, 'current': start, 'prev': prev}
            else:
                paging['prev'] = self.list_url(current_path, 0, limit=start, filter_type=filter_type,
                                               query_string=query_string, **kwargs)
                paging['cursors'] = {'next': next_index, 'current': start, 'prev': 0}
        elif start != 0:
            prev = start - limit
            if prev > 0:
                paging['prev'] = self.list_url(current_path, prev, limit=limit, filter_type=filter_type,
                                               query_string=query_string, **kwargs)
                paging['cursors'] = {'current': start, 'prev': prev}
            else:
                paging['prev'] = self.list_url(current_path, 0, limit=start, filter_type=filter_type,
                                               query_string=query_string, **kwargs)
                paging['cursors'] = {'current': start, 'prev': 0}

        ret['paging'] = paging
        return ret

    def collection(self, start, limit, filter_type=None, query_string=None, request=None, **kwargs):
        return [], 0, 0

    def get_first_url(self, **kwargs):
        return self.list_url(self.default_path_format % kwargs, 0)

    def get_url(self, filter_type=None, query_string=None, request=None, **kwargs):
        data, start, next_index = self.collection(0, 1, filter_type=filter_type,
                                                  query_string=query_string, request=request, **kwargs)
        if len(data) > 0:
            return self.get_first_url(**kwargs)
        return None

    def get_preview(self, preview_count=5, limit=20, filter_type=None, query_string=None, request=None, **kwargs):
        data, start, next_index = self.collection(0, preview_count, filter_type=filter_type,
                                                      query_string=query_string, request=request, **kwargs)
        if next_index:
            next_url = self.list_url(self.default_path_format % kwargs, 0, limit=limit, filter_type=filter_type,
                                     query_string=query_string, **kwargs)
            cursors = {'current': start, 'next': next_index}
        else:
            next_url = None
            cursors = {'current': start}
        ret = {'data': data, 'paging': {'cursors': cursors}}
        if next_url:
            ret['paging']['next'] = next_url
            ret['paging']['start'] = start
        return ret


class RestResourceApiMixin(object):

    resource = None

    def __init__(self, **kwargs):
        if not isinstance(self.resource, Resource):
            raise RestRuntimeError()
        super(RestResourceApiMixin, self).__init__()


class RestDocumentApiView(RestApiView, RestResourceApiMixin):

    read_fields = None
    read_exclude = None
    update_fields = None
    update_exclude = None

    def read(self, request, pk):
        _fields = request.GET.get('fields')
        if _fields:
            fields = list(set(self.read_fields).intersection(set(_fields.split(','))))
        else:
            fields = self.read_fields
        return self.resource(pk).to_dict(fields=fields, exclude=self.read_exclude)

    def update(self, request, pk):
        kwargs = {}
        kwargs.update(request.PUT)
        kwargs.update(request.FILES)
        return self.resource(pk).update(**kwargs).to_dict(fields=self.update_fields, exclude=self.update_exclude)

    def delete(self, request, pk):
        self.resource(pk).delete()
        return {}

    @classmethod
    def path(cls):
        return cls.resource.name + "/{}"


class RestCollectionApiView(RestListApiView, RestResourceApiMixin):

    create_fields = None
    create_exclude = None

    read_fields = None
    read_exclude = None

    def create(self, request):
        return self.resource.create(data=request.POST, files=request.FILES).to_dict(fields=self.create_fields,
                                                                                    exclude=self.create_exclude)

    def collection(self, start, limit, **kwargs):
        list_with_extra = list(self.resource.pk_collection()[start:start+limit + 1])
        current_list = [self.resource(pk).to_dict(fields=self.read_fields, exclude=self.read_exclude)
                        for pk in list_with_extra[:limit]]
        return current_list, start, start + limit if (len(list_with_extra) == limit + 1) else None

    @classmethod
    def path(cls):
        return pluralize(cls.resource.name)


class RestModelCollectionApiView(RestCollectionApiView):

    def pk_collection(self, **kwargs):
        return self.resource.pk_collection()

    def collection(self, start, limit, **kwargs):
        list_with_extra = list(self.pk_collection(**kwargs)[start:start+limit + 1])
        current_list = [self.resource(pk).to_dict(fields=self.read_fields,
                                                  exclude=self.read_exclude) for pk in list_with_extra[:limit]]
        return current_list, start, start + limit if (len(list_with_extra) == limit + 1) else None

