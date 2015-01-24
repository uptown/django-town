# -*- coding: utf-8 -*-
import copy

from django.core.cache import cache

from django_town.utils import DictObject


class CacheManager(object):
    """
    Default Cache Manager. Just encapsulate django cache system.
    """

    def start_session(self):
        pass

    def end_session(self):
        pass

    def delete(self, key):
        cache.delete(key)

    def get(self, key):
        return cache.get(key)

    def set(self, key, value, duration):
        cache.set(key, value, duration)

    def delete_many(self, keys):
        cache.delete_many(keys)


class LazyCacheManager(object):
    """
    If this manager is set as the default cache manager, all caches are managed by locally until the end of session.

    .. todo:: deepcopy process is too slow rather than read caches from the cache server.
    """

    def __init__(self):
        self.is_managed = [False]
        self.local_mem_cached = None
        self.reversed_delete_keys = None

    def start_session(self):
        """
        start lazy cache delete session
        """
        self.local_mem_cached = {}
        self.reversed_delete_keys = set()
        self.is_managed.append(True)

    def end_session(self):
        """
        end lazy cache delete session
        """
        del self.is_managed[-1]
        if not self.is_managed[-1]:
            for key in self.reversed_delete_keys:
                cache.delete(key)
            del self.local_mem_cached
            del self.reversed_delete_keys

    def delete(self, key):
        """
        if session started, just put the key into the set. otherwise, cache delete
        """
        if self.is_managed[-1]:
            if key in self.local_mem_cached:
                del self.local_mem_cached[key]
            self.reversed_delete_keys.add(key)
        else:
            # print "cached delete", key
            cache.delete(key)

    def get(self, key):
        """
        if session started, use local cache. otherwise, cache get
        """
        if self.is_managed[-1]:
            if key in self.reversed_delete_keys:
                self.reversed_delete_keys.remove(key)
                if key in self.local_mem_cached:
                    del self.local_mem_cached[key]
                cache.delete(key)
            ret = self.local_mem_cached.get(key)
            if not ret:
                # print "cached get", key
                ret = cache.get(key)
                self.local_mem_cached[key] = ret
            return copy.deepcopy(ret)
        else:
            return cache.get(key)

    def set(self, key, value, duration):
        """
        if session started, remove reversed delete key but force set. otherwise, cache set
        """
        if self.is_managed[-1]:
            if key in self.reversed_delete_keys:
                self.reversed_delete_keys.remove(key)
            self.local_mem_cached[key] = copy.deepcopy(value)
            # print "cached set", key
            cache.set(key, value, duration)

        else:
            cache.set(key, value, duration)

    def delete_many(self, keys):
        if self.is_managed[-1]:
            self.reversed_delete_keys.update(keys)
        else:
            cache.delete_many(keys)


defaultCacheManager = CacheManager()


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
