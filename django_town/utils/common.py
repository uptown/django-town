import time
import collections
from django_town.utils.with3 import urlparse, urlencode
from django.utils.six import iteritems


class DictObject(object):
    def __init__(self, dict_object, case_sensitive=True):
        if case_sensitive:
            self._object = dict_object
        else:
            self._object = CaseLessDict(dict_object)

    def __getattr__(self, attr):
        if not hasattr(self._object, attr):
            ret = self._object[attr]
            if type(ret) is dict:
                self._object[attr] = DictObject(ret)
                return ret
            if type(ret) is list:
                self._object[attr] = DictObject(ret)
                return ret
            return ret
        else:
            return getattr(self._object, attr)

    def __getitem__(self, key):
        ret = self._object[key]
        if type(ret) is dict:
            self._object[key] = DictObject(ret)
            return ret
        if type(ret) is list:
            self._object[key] = DictObject(ret)
            return ret
        return ret


class CurrentTimestamp(object):
    def __init__(self, seconds=0):
        self.seconds = seconds

    def __call__(self):
        return int(time.time()) + self.seconds


def class_from_path(path):
    sub_path = path.split('.')[-1]
    module_name = ".".join(x for x in path.split('.')[:-1])
    mod = __import__(module_name, fromlist=[sub_path])
    return getattr(mod, sub_path)


# http://code.activestate.com/recipes/66315/
class CaseLessDict(dict):
    def __init__(self, other=None, **kwargs):
        super(CaseLessDict, self).__init__(**kwargs)
        if other:
            # Doesn't do keyword args
            if isinstance(other, dict):
                for k, v in other.items():
                    dict.__setitem__(self, k.lower(), v)
            else:
                for k, v in other:
                    dict.__setitem__(self, k.lower(), v)

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        dict.__setitem__(self, key.lower(), value)

    def __contains__(self, key):
        return dict.__contains__(self, key.lower())

    def has_key(self, key):
        return dict.has_key(self, key.lower())

    def get(self, key, def_val=None):
        return dict.get(self, key.lower(), def_val)

    def setdefault(self, key, def_val=None):
        return dict.setdefault(self, key.lower(), def_val)

    def update(self, E=None, **F):
        if E:
            for k, v in E.items():
                dict.__setitem__(self, k.lower(), v)

    @staticmethod
    def fromkeys(S, v=None):
        d = CaseLessDict()
        for k in S:
            dict.__setitem__(d, k.lower(), v)
        return d

    def pop(self, key, def_val=None):
        return dict.pop(self, key.lower(), def_val)


class ReadOnlyList(list):
    def __init__(self, safe_list, **kwargs):
        super(ReadOnlyList, self).__init__(**kwargs)
        self.__dict__['_safe_list'] = safe_list

    def append(self, p_object):
        raise TypeError

    def extend(self, iterable):
        raise TypeError

    def insert(self, index, p_object):
        raise TypeError

    def pop(self, index=None):
        raise TypeError

    def remove(self, value):
        raise TypeError

    def reverse(self):
        raise TypeError

    def sort(self, cmp=None, key=None, reverse=False):
        raise TypeError

    def __add__(self, y):
        raise TypeError

    def __delitem__(self, y):
        raise TypeError

    def __delslice__(self, i, j):
        raise TypeError

    def __setitem__(self, i, y):
        raise TypeError

    def __setslice__(self, i, j, y):
        raise TypeError


    def __getitem__(self, key):
        ret = self.__dict__['_safe_list'][key]
        if type(ret) is dict:
            self.__dict__['_safe_list'][key] = ReadOnlyDict(ret)
            return ret
        if type(ret) is list:
            self.__dict__['_safe_list'][key] = ReadOnlyList(ret)
            return ret
        return ret

    def __getslice__(self, i, j):
        raise TypeError


class ReadOnlyDict(dict):
    def __init__(self, safe_dict, **kwargs):
        super(ReadOnlyDict, self).__init__(**kwargs)
        self.__dict__['_safe_dict'] = safe_dict

    def __setitem__(self, key, item):
        raise TypeError

    def __delitem__(self, key):
        raise TypeError

    def clear(self):
        raise TypeError

    def pop(self, key, *args):
        raise TypeError

    def popitem(self):
        raise TypeError

    def __getitem__(self, key):
        ret = self.__dict__['_safe_dict'][key]
        if type(ret) is dict:
            self.__dict__['_safe_dict'][key] = ReadOnlyDict(ret)
            return ret
        if type(ret) is list:
            self.__dict__['_safe_dict'][key] = ReadOnlyList(ret)
            return ret
        return ret


def recursive_dict_update(d, u):
    for k, v in iteritems(u):
        if isinstance(v, collections.Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def add_params_to_url(url, params):
    if not params: return url
    param_string = urlencode(params)
    scheme, host, path, cur_params, query, fragment = urlparse.urlparse(url)
    if query:
        query = query + '&' + param_string
    else:
        query = param_string
    return urlparse.urlunparse((scheme, host, path, cur_params, query, fragment))


def recursive_filter(a, fields, exclude):
    if type(a) is dict:
        return recursive_dict_filter(a, fields, exclude)
    elif type(a) is list:
        return recursive_list_filter(a, fields, exclude)


def recursive_dict_filter(d, fields, exclude):
    mapp = {}
    new_fields = []
    new_exclude = []
    if fields:
        for field in fields:
            if '.' in field:
                ss = field.split('.', 1)
                if not ss[0] in mapp:
                    mapp[ss[0]] = []
                    new_fields.append(ss[0])
                mapp[ss[0]].append(ss[1])
            else:
                new_fields.append(field)
        ret = {k: v for k, v in iteritems(d) if k in new_fields}
        for k, v in iteritems(mapp):
            if k in d:
                ret[k] = recursive_filter(d[k], v, None)
    elif exclude:
        for each in exclude:
            if '.' in each:
                ss = each.split('.', 1)
                if not ss[0] in mapp:
                    mapp[ss[0]] = []
                mapp[ss[0]].append(ss[1])
            else:
                new_exclude.append(each)
        ret = {k: v for k, v in iteritems(d) if not k in new_exclude}
        for k, v in iteritems(mapp):
            if k in d:
                ret[k] = recursive_filter(d[k], None, v)
    else:
        ret = d
    return ret


def recursive_list_filter(l, fields, exclude):
    new_l = []
    for d in l:
        new_l.append(recursive_filter(d, fields, exclude))
    return new_l

