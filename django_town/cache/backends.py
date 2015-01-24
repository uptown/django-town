from __future__ import absolute_import
from django.core.cache.backends.memcached import BaseMemcachedCache
from django_town.utils import json


class json_wrapper(object):

    def __init__(self, p_file, protocol=None):
        self.p_file = p_file
        self.protocol = protocol

    def dump(self, val):
        json.dump(val, self.p_file)
        # print self.p_file

    def load(self):
        # print self.p_file
        return json.load(self.p_file)



class JsonMemcachedCache(BaseMemcachedCache):
    "An implementation of a cache binding using python-memcached"
    def __init__(self, server, params):
        import memcache
        super(JsonMemcachedCache, self).__init__(server, params,
                                             library=memcache,
                                             value_not_found_exception=ValueError)

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers, pickler=json_wrapper, unpickler=json_wrapper)
        return self._client
