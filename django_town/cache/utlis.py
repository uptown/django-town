# -*- coding: utf-8 -*-
from django_town.utils import DictObject
from django_town.cache.manager import defaultCacheManager


class CacheBase(object):
    """Class for using cache with key_format and keys based on django cache system.

    """

    def __init__(self, key_format, duration, manager=None):
        """
        Args:
            key_format (str): format-string for cache key. ex) _simple_cache_%(key1)s
            duration (int): duration for cache's live time.

        KArgs:
            manager: if none, use default cache manager as this instance's cache manager. Otherwise use passed one.
        """
        self.key_format = key_format
        self.duration = duration
        if not manager:
            global defaultCacheManager
            self.manager = defaultCacheManager
        else:
            self.manager = manager

    def load(self, **kwargs):
        raise Exception()

    def get(self, **kwargs):
        if len(kwargs) == 0:
            key = self.key_format
        else:
            key = self.key_format % kwargs
        cached = self.manager.get(key)
        if cached:
            return cached

        cached = self.load(**kwargs)
        self.set(cached, **kwargs)

        return cached

    def get_object(self, **kwargs):
        result = self.get(**kwargs)
        if result:
            return DictObject(result)
        return None

    def set(self, value, **kwargs):
        key = self.key_format % kwargs
        if value:
            self.manager.set(key, value, self.duration)
        else:
            self.manager.delete(key)

    def add(self, value, **kwargs):
        key = self.key_format % kwargs
        if not self.manager.get(key):
            self.manager.set(key, value, self.duration)

    def delete(self, **kwargs):
        key = self.key_format % kwargs
        self.manager.delete(key)

    def delete_many(self, kwargs_list):
        self.manager.delete_many([self.key_format % kwargs for kwargs in kwargs_list])


class StaticCache(CacheBase):
    """
    StaticCache class is simple cache class inherited from CacheBase class.

    .. code-block:: python

        class SomeCache(StaticCache):
            key_format = "some_cache_%(key1)s_%(key2)s"
            duration = 2400 # sec
            def load(self, key1, key2):
                do something
                return something
    """
    key_format = ""
    duration = 60 * 60 * 24 * 14

    def __init__(self, manager=None):
        super(StaticCache, self).__init__(self.key_format, self.duration, manager=manager)


class SimpleCache(CacheBase):
    """
    Load cache with passed callback function.

    .. code-block:: python
        def callback(key):
            return something

        simple_cache = SimpleCache("simple_%(key)s", 2000, callback)
        simple_cache.get(key=1) # will return something

    """

    def __init__(self, key_format, duration, load_callback, manager=None):
        self.load_callback = load_callback
        super(SimpleCache, self).__init__(key_format, duration, manager=manager)

    def load(self, **kwargs):
        return self.load_callback(**kwargs)
