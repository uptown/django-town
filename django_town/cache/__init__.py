# -*- coding: utf-8 -*-
from django.core.cache import cache
from django_town.utils import DictObject
import copy


class LazyCacheManager(object):
    """
    As a default cache manager, if start session, all caches are managed by locally until the end of session
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
        :param key:
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
        :param key:
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
                self.local_mem_cached[key] = copy.deepcopy(ret)
            return ret
        else:
            return cache.get(key)

    def set(self, key, value, duration):
        """
        if session started, remove reversed delete key but force set. otherwise, cache set
        :param key:
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


defaultCacheManager = LazyCacheManager()


class CacheBase(object):

    def __init__(self, key_format, duration, manager=None):
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

    def set(self,value, **kwargs):
        key = self.key_format % kwargs
        if value:
            self.manager.set(key, value, self.duration)
        else:
            self.manager.delete(key)

    def add(self, value, **kwargs):
        key = self.key_format % kwargs
        if not cache.get(key):
            self.manager.set(key, value, self.duration)

    def delete(self, **kwargs):
        key = self.key_format % kwargs
        self.manager.delete(key)

    def delete_many(self, kwargs_list):
        self.manager.delete_many([self.key_format % kwargs for kwargs in kwargs_list])


class StaticCache(CacheBase):
    """ StaticCache class,
    usage:
    class SomeCache(StaticCache):
        def get_from_db(self, key1, key2):
            do something
            return something
    """
    key_format = ""
    duration = 60*60*24*14

    def __init__(self, manager=None):
        super(StaticCache, self).__init__(self.key_format, self.duration, manager=manager)


class SimpleCache(CacheBase):


    def __init__(self, key_format, duration, load_callback, manager=None):
        self.load_callback = load_callback
        super(SimpleCache, self).__init__(key_format, duration, manager=manager)

    def load(self, **kwargs):
        return self.load_callback(**kwargs)


class ModelCache(StaticCache):

    cachedClass = None
    cachingCount = -1
    cachingValues = 'id', 'name'

    @staticmethod
    def decorator(obj):
        return obj

    @staticmethod
    def build_filter(*args):
        raise Exception()

    def get_from_db(self, *args):
        #base_class
        query_set = self.cachedClass.objects.filter(self.build_filter(*args))
        if self.cachingCount > 0:
            query_set = query_set[:self.cachingCount]
        values = query_set.values(self.cachingValues)
        return self.decorator(values)