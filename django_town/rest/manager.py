from django.conf.urls import patterns, url
from django_town.core.settings import REST_SETTINGS

_rest_api_managers = {}


class RestManager(object):

    def __init__(self):
        self.resource_cls_lookup = {}
        self.default_resources_lookup = {}

    def register_resource_cls(self, resource_cls, resource_name):
        self.resource_cls_lookup[resource_name] = resource_cls

    def get_resource_cls_from_name(self, resource_name):
        return self.resource_cls_lookup[resource_name]

    def get_default_resource(self, resource_name):
        ret = self.default_resources_lookup.get(resource_name)
        if ret:
            return ret
        resource_cls = self.get_resource_cls_from_name(resource_name)
        self.default_resources_lookup[resource_name] = resource_cls()
        return self.default_resources_lookup[resource_name]

    def register_default_resource(self, resource_name, resource):
        self.default_resources_lookup[resource_name] = resource

    def setup(self):
        global _rest_service_inited
        if _rest_service_inited:
            return
        from django.conf import settings
        from django_town.rest.manager import rest_manager
        from importlib import import_module
        import inspect
        from django.utils.module_loading import module_has_submodule
        #
        # self.models = all_models
        resource_module = import_module('django_town.social.resources.feed')
        for each in settings.INSTALLED_APPS:
            try:
                models_module_name = '%s.%s' % (each, 'resources')
                resource_module = import_module(models_module_name)
                print(models_module_name)
                for name, obj in inspect.getmembers(resource_module):
                    if isinstance(obj, Resource):
                        print(obj)
            except ImportError:
                import traceback
                traceback.print_exc()
                pass
        _rest_service_inited = True

class RestApiManager(object):
    """
    Rest api url manager
    """
    def __init__(self, api_version, name=None, description=None):
        self.api_version = api_version
        self.name = name
        self.description = description
        self._url_patterns = []
        self.api_list = []
        self.base_url = REST_SETTINGS.SITE_URL + "/" + api_version + "/"
        self.info = {}

    def register_rest_api_view(self, rest_api_view_cls, default_args=None, name=None):
        """
        register rest api view. view's path property will use for url path.
        """
        if rest_api_view_cls in self.api_list:
            return
        if hasattr(rest_api_view_cls, 'resource'):
            regex = '^' + rest_api_view_cls.path().replace('{}', '(?P<pk>' +
                                                           rest_api_view_cls.resource._meta.pk_regex + ')') + '$'
        else:
            regex = '^' + rest_api_view_cls.path().replace('{}', '(?P<pk>\d+)') + '$'
        if not name:
            name = rest_api_view_cls.__name__

        self.api_list.append(rest_api_view_cls)
        view_func = rest_api_view_cls.as_rest_view()

        self._url_patterns.append(url(regex, rest_api_view_cls.as_rest_view(),
                                      kwargs=default_args, name=name))

    def set_base_url(self, base_url):
        self.base_url = base_url

    @property
    def patterns(self):
        """
        return api manager's url patterns.
        """
        return patterns('', *(self._url_patterns))


def rest_api_manager(version, name=None, description=None):
    """
    return rest api manager for version if already exists or create rest api manager for version and return.
    """
    if version in _rest_api_managers:
        return _rest_api_managers[version]
    _rest_api_managers[version] = RestApiManager(version, name, description)
    return _rest_api_managers[version]


rest_manager = RestManager()