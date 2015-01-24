# -*- coding: utf-8 -*-
import sys
import logging
from django.core.exceptions import MiddlewareNotUsed
from django.core.handlers.wsgi import WSGIRequest

from django.conf import settings
from django.utils.module_loading import import_string
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import classonlymethod
from django.utils.six import iteritems
from django.utils.cache import patch_cache_control

from django_town.http import http_json_response
from django_town.cache.manager import defaultCacheManager
from django_town.cache.utlis import SimpleCache
from django_town.rest.permissions import AllowAny
from django_town.rest.exceptions import RestError, RestRuntimeError, RestMethodNotAllowed, RestBadRequest, \
    RestFormInvalid, RestFormRequired
from django_town.rest.resources import Resource
from django_town.core.settings import REST_SETTINGS
from django_town.utils import pluralize, quote_plus


_CRUD_MAPPING = {
    'post': 'create',
    'get': 'read',
    'patch': 'update',
    'put': 'update',
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
    """
    Default api view for rest design
    use CRUD words to define view function

    ========  ==============
    original  rest api view
    ========  ==============
    post      create
    get       read
    patch     update
    delete    delete
    ========  ==============
    """
    permission_classes = [AllowAny]
    cache_max_age = None
    crud_method_names = ['create', 'read', 'update', 'delete']

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """
        the first entering point for http call,
        check method is allowed
        and cached ApiError and managed by cache manager
        """
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
        except RestError as e:
            import traceback
            traceback.print_exc()
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
        response["Access-Control-Allow-Origin"] = "*"
        if self.cache_max_age:
            patch_cache_control(response, max_age=self.cache_max_age)
        defaultCacheManager.end_session()
        return response

    def check_permissions(self, request, *args, **kwargs):
        """
        check permission for request
        """
        for permission in self.permission_classes:
            permission().check_permission(request, *args, **kwargs)

    @classonlymethod
    def as_rest_view(cls, **kwargs):
        for key in kwargs:
            if key in cls.crud_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
        as_view = cls.as_view(**kwargs)

        return as_view

    @classmethod
    def path(cls):
        """
        url path for rest manager registration.
        """
        return ""


class RestListApiView(RestApiView):
    """
    List style api view.

    .. code-block:: python

        class SomeListView(RestListApiView):
            def collection(self, start, limit, parameters=None, request=None, **kwargs):
                return list of dictionary, start index, next index or None

    Print style

    .. code-block:: javascript

        {
            'data': [
                data0,
                data1,
                ...
            ],
            'paging': {
                'cursors': {
                    'prev': prev_url,
                    'next': next_url,
                }
            }
        }
    """
    base_url = REST_SETTINGS.SITE_URL
    default_path_format = ""
    reverse = False
    max_limit = 20
    crud_method_names = ['read', 'create']
    collection_path = ""
    parameters = ['filter', 'q', 'fields', 'date_format', 'access_token']
    extra_parameters = []

    def list_url(self, current_path, start, limit=20, parameters=None, **kwargs):
        """
        return url for arguments.
        """
        if not parameters:
            parameters = {}
        return self.base_url + current_path + "?start=" + str(start) + '&limit=' + str(limit) + "&" + \
               "&".join(
                   [key + '=' + quote_plus(val.encode('utf-8')) for key, val in iteritems(parameters) if val])


    def default_key(self, request, key):
        return request.GET.get(key)

    def read(self, request, **kwargs):
        current_path = request.path

        try:
            start = int(request.GET.get('start', -1 if self.reverse else 0))
        except ValueError:
            raise RestFormInvalid('start')
        try:
            limit = int(request.GET.get('limit', self.max_limit))
        except ValueError:
            raise RestFormInvalid('limit')
        if limit <= 0:
            raise RestFormInvalid('limit')
        if limit > self.max_limit:
            limit = self.max_limit
        parameters = {each: self.default_key(request, each) for each in self.parameters + self.extra_parameters}

        suppress_http_code = request.GET.get('suppress_http_code')
        if suppress_http_code:
            parameters['suppress_http_code'] = suppress_http_code

        fields = parameters.get('fields')
        if fields:
            fields = fields.split(',')
        date_format = parameters.get('date_format')
        if date_format:
            options = {'date_format': date_format}
        else:
            options = None
        ret = {}
        data, start, next_index = self.collection(start, limit, parameters=parameters, fields=fields,
                                                  options=options, request=request, **kwargs)

        ret['data'] = data

        if start < 0:
            raise RestBadRequest()
        paging = {}
        if start == 0 and next_index:
            paging['cursors'] = {'next': next_index}
            paging['next'] = self.list_url(current_path, next_index, limit=limit, parameters=parameters, **kwargs)
        elif next_index:
            paging['next'] = self.list_url(current_path, next_index, limit=limit, parameters=parameters, **kwargs)
            prev = start - limit
            if prev > 0:
                paging['cursors'] = {'next': next_index, 'prev': prev}
                paging['prev'] = self.list_url(current_path, prev, limit=limit, parameters=parameters, **kwargs)
            else:
                paging['cursors'] = {'next': next_index, 'prev': 0}
                paging['prev'] = self.list_url(current_path, 0, limit=start, parameters=parameters, **kwargs)
        elif start != 0:
            prev = start - limit
            if prev > 0:
                paging['cursors'] = {'prev': prev}
                paging['prev'] = self.list_url(current_path, prev, limit=limit, parameters=parameters, **kwargs)
            else:
                paging['cursors'] = {'prev': 0}
                paging['prev'] = self.list_url(current_path, 0, limit=start, parameters=parameters, **kwargs)

        ret['paging'] = paging
        return ret

    def collection(self, start, limit, parameters=None, request=None, **kwargs):
        """
        :param:
            start (int): start index

            limit (int): limit count

            parameters (dict): parameters from request.GET

            request (django request): django request Object

        :key param:
            same as django view's kargs.

        :returns: list of dictionary, start index, next index or None.
            If next index is none, next url will remove from json return.
        """
        return [], 0, 0

    def get_first_url(self, **kwargs):
        """
        return url with start index 0
        """
        return self.list_url(self.default_path_format % kwargs, 0)

    def get_url(self, parameters=None, request=None, **kwargs):
        data, start, next_index = self.collection(0, 1, parameters=parameters, request=request, **kwargs)
        if len(data) > 0:
            return self.get_first_url(**kwargs)
        return None

    def get_preview(self, preview_count=5, limit=20, parameters=None, request=None, **kwargs):
        data, start, next_index = self.collection(0, preview_count, parameters=parameters, request=request, **kwargs)
        if next_index:
            next_url = self.list_url(self.default_path_format % kwargs, 0, limit=limit, parameters=parameters, **kwargs)
            cursors = {'current': start, 'next': next_index}
        else:
            next_url = None
            cursors = {}
        ret = {'data': data, 'paging': {'cursors': cursors}}
        if next_url:
            ret['paging']['next'] = next_url
        return ret


class RestResourceApiMixin(object):
    resource = Resource()

    def __init__(self, **kwargs):
        if not isinstance(self.resource, Resource):
            raise RestRuntimeError()
        super(RestResourceApiMixin, self).__init__()


class RestCreateResourceApiMixin(RestResourceApiMixin):
    list_fields_for_create = []

    def pre_create(self, data, request, **kwargs):
        return data

    def create(self, request, **kwargs):
        data = {}
        for each_key in request.POST.keys():
            if each_key in self.list_fields_for_create:
                data[each_key] = request.POST.getlist(each_key)
            else:
                data[each_key] = request.POST[each_key]
        data = self.pre_create(data, request, **kwargs)
        ret = self.resource.create(data=data, files=request.FILES, request=request,
                                    request_kwargs=kwargs).to_dict(request=request)
        self.post_create(ret, request, **kwargs)
        return ret


    def post_create(self, data, request, **kwargs):
        return data


class RestDocumentApiView(RestApiView, RestResourceApiMixin):
    """
    Single object api view with django-town resource

    .. code-block:: python

        class SomeResourceView(RestDocumentApiView):
            resource = SomeResource()

    """

    def read(self, request, pk):
        fields = request.GET.get('fields')
        if fields:
            fields = fields.split(',')
        date_format = request.GET.get('date_format')
        if date_format:
            options = {'date_format': date_format}
        else:
            options = None
        return self.resource(pk).to_dict(fields=fields, options=options, request=request)

    def update(self, request, pk):
        kwargs = {}
        kwargs.update(request.PUT)
        kwargs.update(request.FILES)
        self.resource(pk).update(**kwargs)
        return {}

    def delete(self, request, pk):
        self.resource(pk).delete()
        return {}

    @classmethod
    def path(cls):
        return cls.resource._meta.name + "/{}"
        # return cls.resource._meta.name + "/{}"


class RestSpecifiedDocumentApiView(RestApiView, RestResourceApiMixin):
    """
    Single object api view with django-town resource specified by uri or sessions

    .. code-block:: python

        class SomeResourceView(RestSpecifiedDocumentApiView):
            resource = SomeResource()

            def get_pk(self, request)
                return some_pk

    """

    def get_pk(self, request):
        raise RestError()

    def read(self, request):
        pk = self.get_pk(request)
        fields = request.GET.get('fields')
        if fields:
            fields = fields.split(',')
        date_format = request.GET.get('date_format')
        if date_format:
            options = {'date_format': date_format}
        else:
            options = None
        return self.resource(pk).to_dict(fields=fields, options=options, request=request)

    def update(self, request):
        pk = self.get_pk(request)
        # kwargs = {}
        # kwargs.update(request.PUT)
        # kwargs.update(request.FILES)
        self.resource(pk).update(data=request.PUT, files=request.FILES)
        return {}

    def delete(self, request):
        pk = self.get_pk(request)
        self.resource(pk).delete()
        return {}

    @classmethod
    def path(cls):
        return pluralize(cls.resource._meta.name) + "/0"



class RestCollectionApiView(RestListApiView, RestCreateResourceApiMixin):
    """
    List api view with resource.

    .. code-block:: python

        class SomeResourceCollectionView(RestCollectionApiView):
            resource = SomeResource()

    """
    collection_cache_key_format = None
    collection_cache_duration = 14 * 24 * 3600

    def collection_step1(self, start, limit, request=None, parameters=None, **kwargs):
        return list(self.resource.pk_collection(request=request, parameters=parameters, **kwargs)[start:start + limit + 1])

    def collection_step2(self, list_with_extra, start, limit, parameters=None, fields=None, options=None, request=None, **kwargs):
        return [self.resource(pk).to_dict(fields=fields, options=options, request=request)
                        for pk in list_with_extra[:limit]]

    def collection_cache_key(self, start, limit, parameters=None, fields=None, options=None, request=None, **kwargs):
        return {}

    def collection(self, start, limit, parameters=None, fields=None, options=None, request=None, **kwargs):
        if self.collection_cache_key_format and start == 0:
            def load_cache(**kwargs):
                list_with_extra = self.collection_step1(start, limit, request, parameters, **kwargs)
                current_list = self.collection_step2(list_with_extra, start, limit, parameters, fields, options, request, **kwargs)
                return [len(list_with_extra), current_list]
            count, current_list = SimpleCache(self.collection_cache_key_format, self.collection_cache_duration, load_cache).get(
                **self.collection_cache_key(start, limit, parameters, fields, options, request, **kwargs)
            )
            return current_list, 0, limit if (count == limit + 1) else None
        else:
            list_with_extra = self.collection_step1(start, limit, request, parameters, **kwargs)
            current_list = self.collection_step2(list_with_extra, start, limit, parameters, fields, options, request, **kwargs)
            return current_list, start, start + limit if (len(list_with_extra) == limit + 1) else None

    @classmethod
    def path(cls):
        return pluralize(cls.resource._meta.name)

    @classmethod
    def invalidate_collection_cache(cls, **kwargs):
        SimpleCache(cls.collection_cache_key_format, cls.collection_cache_duration, None).delete(**kwargs)


class RestPrimaryKeyCollectionApiView(RestCollectionApiView):
    def pk_collection(self, **kwargs):
        return self.resource.pk_collection()

    def collection_step1(self, start, limit, request=None, parameters=None, **kwargs):
        return list(self.pk_collection(**kwargs)[start:start + limit + 1])


class RestQuerySetCollectionApiView(RestCollectionApiView):
    """
    List api view with resource.

    .. code-block:: python

        class SomeResourceCollectionView(RestQuerySetCollectionApiView):
            resource = SomeResource()

            def query_set(self, parameters=None, **kwargs):
                return self.resource.document.filter(some_filter)

    """
    resource_pk_name = "pk"

    def query_set(self, parameters=None, **kwargs):
        return self.resource._meta.document.objects()

    def collection_step1(self, start, limit, request=None, parameters=None, **kwargs):
        return list(self.query_set(parameters=parameters, request=request,
                                              **kwargs)[start:start + limit + 1])

    def collection_step2(self, list_with_extra, start, limit, parameters=None, fields=None, options=None, request=None, **kwargs):
        return [self.resource(getattr(each, self.resource_pk_name)).to_dict(fields=fields, options=options,
                                                                                      request=request)
                        for each in list_with_extra[:limit]]


class FakeWSGIRequest(WSGIRequest):
    def __init__(self, original_request, url):
        try:
            path, query = url.split('?', 1)
        except ValueError:
            path = url
            query = ""
        environ = original_request.environ.copy()
        environ["PATH_INFO"] = path
        environ["REQUEST_URI"] = path
        if query:
            environ["QUERY_STRING"] = query
            environ["REQUEST_URI"] += "?" + query
        environ["REQUEST_METHOD"] = "GET"
        super(FakeWSGIRequest, self).__init__(environ)


class RestBatchApiView(RestApiView):

    def generate_batch_view_url_args_and_kwargs(self, request, **kwargs):
        return []

    def read(self, request, *args, **kwargs):
        ret = {}
        batches = self.generate_batch_view_url_args_and_kwargs(request, **kwargs)

        request_middleware = []

        for middleware_path in settings.MIDDLEWARE_CLASSES:
            mw_class = import_string(middleware_path)
            try:
                mw_instance = mw_class()
            except MiddlewareNotUsed:
                continue

            if hasattr(mw_instance, 'process_request'):
                request_middleware.append(mw_instance.process_request)

        for view, url, _args, _kwargs in batches:
            fake_request = FakeWSGIRequest(request, url)
            for middleware_method in request_middleware:
                middleware_method(fake_request)
            try:
                if not _args:
                    _args = []
                if not _kwargs:
                    _kwargs = {}
                view_obj = view()
                view_obj.request = fake_request
                view_obj.args = _args
                view_obj.kwargs = _kwargs
                ret[url] = {"body": view_obj.read(fake_request, *_args, **_kwargs), "status_code": 200}
            except RestError as e:
                ret[url] = {"body": e.to_dict(), "status_code": e.status}
        return ret


class RestSafeReadMixin(object):

    read_safe_parameters = []

    def read(self, request, **kwargs):
        data = {}
        for each in self.read_safe_parameters:
            if isinstance(each, tuple):
                if each.endswith('[]'):
                    each = each[:-2]
                    data[each] = request.GET.getlist(each)
                else:
                    data[each] = request.GET.get(each)
                if not data[each]:
                    raise RestFormRequired(each)
            elif isinstance(each, tuple):
                if len(each) == 2:
                    each, type_cast = each
                    min_val, max_val = None, None
                elif len(each) == 4:
                    each, type_cast, min_val, max_val = each
                else:
                    raise RestRuntimeError()
                try:
                    if each.endswith('[]'):
                        each = each[:-2]
                        data[each] = [type_cast(val) for val in request.GET.getlist(each)]
                    else:
                        data[each] = type_cast(request.GET.get(each))
                    if not data[each]:
                        raise RestFormRequired(each)
                    if min_val:
                        if min_val > data[each] or max_val < data[each]:
                            raise RestFormInvalid(each)
                except TypeError:
                    raise RestFormInvalid(each)
            else:
                if each.endswith('[]'):
                    each = each[:-2]
                    data[each] = request.GET.getlist(each)
                else:
                    data[each] = request.GET.get(each)
                if not data[each]:
                    raise RestFormRequired(each)
        return self.read_safe(request, data, **kwargs)

    def read_safe(self, request, data, **kwargs):
        return {}
