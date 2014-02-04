from django.conf.urls import patterns, url

_rest_api_managers = {}


class RestApiManager(object):

    def __init__(self, api_version):
        self.api_version = api_version
        self._url_patterns = []
        self.api_list = []
        self.base_url = ""

    def register_rest_api_view(self, rest_api_view_cls, default_args=None, name=None):
        if rest_api_view_cls in self.api_list:
            return
        if hasattr(rest_api_view_cls, 'resource'):
            regex = '^' + rest_api_view_cls.path().replace('{}', '(?P<pk>' +
                                                                 rest_api_view_cls.resource.pk_regex + ')') + '$'
        else:
            regex = '^' + rest_api_view_cls.path().replace('{}', '(?P<pk>\d+)') + '$'

        self.api_list.append(rest_api_view_cls)
        self._url_patterns.append(url(regex, rest_api_view_cls.as_rest_view(),
                                      kwargs=default_args, name=name))

    def set_base_url(self, base_url):
        self.base_url = base_url

    @property
    def patterns(self):
        return patterns('', *(self._url_patterns))

def rest_api_manager(version):
    if version in _rest_api_managers:
        return _rest_api_managers[version]
    _rest_api_managers[version] = RestApiManager(version)
    return _rest_api_managers[version]