# -*- coding: utf-8 -*-

import base64
import datetime
import re
import bson
from bson import RE_TYPE, SON
from bson.binary import Binary
from bson.code import Code
from bson.dbref import DBRef
from bson.max_key import MaxKey
from bson.min_key import MinKey
from bson.objectid import ObjectId
from bson.regex import Regex
from bson.timestamp import Timestamp

from bson.py3compat import PY3, binary_type, string_types
from django.utils.functional import SimpleLazyObject
from django_town.core.settings import REST_SETTINGS
from django_town.utils import class_from_path
from django.db.models import FileField, DateTimeField, DecimalField
from django.db.models.fields.related import ManyToManyField, RelatedField
from django.utils.http import urlsafe_base64_encode
from django_town.utils import recursive_dict_filter

class BaseSerializer(object):

    @classmethod
    def serialize(cls, resource_instance, fields=None, exclude=None, options=None):
        return resource_instance._values.copy()


class ModelSerializer(object):

    @classmethod
    def serialize(cls, resource_instance, fields=None, exclude=None, options=None):
        instance = resource_instance
        related_fields_fetch = {}
        related_exclude_fetch = {}
        if fields is not None:
            for x in fields:
                if '.' in x:
                    _first, second = x.split('.', 1)
                    if not _first in related_fields_fetch:
                        related_fields_fetch[_first] = []
                    related_fields_fetch[_first].append(second)
                    fields.append(_first)

        if exclude is not None:
            for x in exclude:
                if '.' in x:
                    _first, second = x.split('.', 1)
                    if not _first in related_exclude_fetch:
                        related_exclude_fetch[_first] = []
                    related_exclude_fetch[_first].append(second)
                    exclude.append(_first)
        opts = instance._meta
        data = {}
        for f in opts.concrete_fields + opts.virtual_fields + opts.many_to_many:
            if not getattr(f, 'editable', False):
                continue
            if fields and not f.name in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if isinstance(f, ManyToManyField):
                if instance.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = [cls.serialize(x, related_fields_fetch.get(f.name),
                                                      related_exclude_fetch.get(f.name), options) for x in
                                    f.value_from_object(instance)]
            elif isinstance(f, RelatedField):
                child = getattr(instance, f.name)
                if child:
                    data[f.name] = cls.serialize(child, related_fields_fetch.get(f.name),
                                                 related_exclude_fetch.get(f.name), options)
            elif isinstance(f, FileField):
                value = f.value_from_object(instance)
                if hasattr(value, 'url'):
                    data[f.name] = value.url
                else:
                    data[f.name] = None
            elif isinstance(f, DecimalField):
                new_val = f.value_from_object(instance)
                data[f.name] = float(new_val) if new_val else None
                # print data[f.name]
            elif isinstance(f, DateTimeField):
                data[f.name] = f.value_from_object(instance).strftime("%Y-%m-%dT%H:%M:%S")
            else:
                data[f.name] = f.value_from_object(instance)
        return data


def lazy_load_model_serializer():
    try:
        return class_from_path(REST_SETTINGS.SERIALIZER)()
    except KeyError:
        return ModelSerializer()


default_model_serializer = SimpleLazyObject(lazy_load_model_serializer)


class MongoSerializer(object):

    @classmethod
    def serialize(cls, resource_instance, fields=None, exclude=None, options=None):
        # instance = resource_instance
        # related_fields_fetch = {}
        # related_exclude_fetch = {}
        # if fields is not None:
        #     for x in fields:
        #         if '.' in x:
        #             _first, second = x.split('.', 1)
        #             if not _first in related_fields_fetch:
        #                 related_fields_fetch[_first] = []
        #             related_fields_fetch[_first].append(second)
        #             fields.append(_first)
        #
        # if exclude is not None:
        #     for x in exclude:
        #         if '.' in x:
        #             _first, second = x.split('.', 1)
        #             if not _first in related_exclude_fetch:
        #                 related_exclude_fetch[_first] = []
        #             related_exclude_fetch[_first].append(second)
        #             exclude.append(_first)
        ret = _json_convert(resource_instance.to_dict(serializer=cls))
        if '_id' in ret:
            ret['id'] = ret['_id']
            del ret['_id']
        if fields:
            ret = recursive_dict_filter(ret, fields)
        return ret



def _json_convert(obj):
    """Recursive helper method that converts BSON types so they can be
    converted into json.
    """
    if hasattr(obj, 'iteritems') or hasattr(obj, 'items'):  # PY3 support
        return SON(((k, _json_convert(v)) for k, v in obj.iteritems()))
    elif hasattr(obj, '__iter__') and not isinstance(obj, string_types):
        return list((_json_convert(v) for v in obj))
    try:
        return default(obj)
    except TypeError:
        return obj

def default(obj):
    if isinstance(obj, ObjectId):
        return urlsafe_base64_encode(obj.binary)
    if isinstance(obj, DBRef):
        return _json_convert(obj.as_doc())
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(obj, (RE_TYPE, Regex)):
        flags = ""
        if obj.flags & re.IGNORECASE:
            flags += "i"
        if obj.flags & re.LOCALE:
            flags += "l"
        if obj.flags & re.MULTILINE:
            flags += "m"
        if obj.flags & re.DOTALL:
            flags += "s"
        if obj.flags & re.UNICODE:
            flags += "u"
        if obj.flags & re.VERBOSE:
            flags += "x"
        if isinstance(obj.pattern, unicode):
            pattern = obj.pattern
        else:
            pattern = obj.pattern.decode('utf-8')
        return SON([("$regex", pattern), ("$options", flags)])
    if isinstance(obj, MinKey):
        return {"$minKey": 1}
    if isinstance(obj, MaxKey):
        return {"$maxKey": 1}
    if isinstance(obj, Timestamp):
        return SON([("t", obj.time), ("i", obj.inc)])
    if isinstance(obj, Code):
        return SON([('$code', str(obj)), ('$scope', obj.scope)])
    if isinstance(obj, Binary):
        return SON([
            ('$binary', base64.b64encode(obj).decode()),
            ('$type', "%02x" % obj.subtype)])
    if PY3 and isinstance(obj, binary_type):
        return SON([
            ('$binary', base64.b64encode(obj).decode()),
            ('$type', "00")])
    if bson.has_uuid() and isinstance(obj, bson.uuid.UUID):
        return {"$uuid": obj.hex}
    raise TypeError("%r is not JSON serializable" % obj)


def lazy_load_mongo_serializer():
    try:
        return class_from_path(REST_SETTINGS.SERIALIZER)()
    except KeyError:
        return MongoSerializer()

default_mongo_serializer = SimpleLazyObject(lazy_load_mongo_serializer)