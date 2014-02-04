import time
import collections
import urllib
import urlparse


class DictObject(object):

    def __init__(self, dict_object, case_sensitive=True):
        if case_sensitive:
            self._object = dict_object
        else:
            self._object = CaselessDict(dict_object)

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


#http://code.activestate.com/recipes/66315/
class CaselessDict(dict):

    def __init__(self, other = None, **kwargs):
        super(CaselessDict, self).__init__(**kwargs)
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

    def update(self, other):
        for k,v in other.items():
            dict.__setitem__(self, k.lower(), v)

    def fromkeys(self, iterable, value=None):
        d = CaselessDict()
        for k in iterable:
            dict.__setitem__(d, k.lower(), value)
        return d

    def pop(self, key, def_val=None):
        return dict.pop(self, key.lower(), def_val)


def recursive_dict_update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

def add_params_to_url(url, params):
    if not params: return url
    param_string = urllib.urlencode(params)
    scheme, host, path, cur_params, query, fragment = urlparse.urlparse(url)
    if query:
        query = query + '&' + param_string
    else:
        query = param_string
    return urlparse.urlunparse((scheme, host, path, cur_params, query, fragment))


def recursive_filter(a, fields):
    if type(a) is dict:
        return recursive_dict_filter(a, fields)
    elif type(a) is list:
        return recursive_list_filter(a, fields)


def recursive_dict_filter(d, fields):
    mapp = {}
    new_filter = []
    for field in fields:
        if '.' in field:
            ss = field.split('.', 1)
            if not ss[0] in mapp:
                mapp[ss[0]] = []
                new_filter.append(ss[0])
            mapp[ss[0]].append(ss[1])
        else:
            new_filter.append(field)
    ret = {k: v for k, v in d.iteritems() if k in new_filter}
    for k, v in mapp.iteritems():
        if k in d:
            ret[k] = recursive_filter(d[k], v)
    return ret


def recursive_list_filter(l, fields):
    new_l = []
    for d in l:
        new_l.append(recursive_filter(d, fields))
    return new_l