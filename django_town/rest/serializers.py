# -*- coding: utf-8 -*-

import base64
import datetime
import time

import re
import bson
from bson import RE_TYPE, SON
from bson.binary import Binary
from bson.code import Code
from bson.dbref import DBRef
from bson.max_key import MaxKey
from bson.min_key import MinKey
from bson.objectid import ObjectId
from bson.timestamp import Timestamp
from bson.py3compat import PY3, binary_type, string_types
from django.utils.functional import SimpleLazyObject
from django.db.models import FileField, DateTimeField, DecimalField, DateField, SmallIntegerField
from django.db.models.fields.related import ManyToManyField, RelatedField
from django.utils.http import urlsafe_base64_encode
from django.utils.six import iteritems

from django_town.core.settings import REST_SETTINGS
from django_town.utils import class_from_path
from django_town.utils import recursive_dict_filter
# from django_town.mongoengine_extension import LocalStorageFileField


class BaseSerializer(object):
    @classmethod
    def serialize(cls, resource_instance, fields=None, exclude=None, options=None):
        return resource_instance._values.copy()


def datetime_to_iso(object):
    return object.strftime("%Y-%m-%dT%H:%M:%S")


def datetime_to_timestamp(object):
    return time.mktime(object.timetuple())  # int(object.utcnow().strftime("%s"))


class ModelSerializer(object):
    """
    Model Resource to dict serializer
    """

    @classmethod
    def _serialize(cls, instance, fields=None, exclude=None, options=None):
        # if options and 'date_format' in options and options['date_format'] == 'U':
        #     date_func = datetime_to_timestamp
        #     options = options.copy()
        #     del options['date_format']
        # else:
        #     date_func = datetime_to_timestamp
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
        if fields:
            fields = set(fields)
        if exclude:
            exclude = set(exclude)
        for f in opts.concrete_fields + opts.virtual_fields + opts.many_to_many:
            if fields and not f.name in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if isinstance(f, ManyToManyField):
                if instance.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = [cls._serialize(x, related_fields_fetch.get(f.name),
                                                   related_exclude_fetch.get(f.name), options) for x in
                                    f.value_from_object(instance)]
            elif isinstance(f, RelatedField):
                child = getattr(instance, f.name)
                if child:
                    data[f.name] = cls._serialize(child, related_fields_fetch.get(f.name),
                                                  related_exclude_fetch.get(f.name), options)
            elif isinstance(f, FileField):
                value = f.value_from_object(instance)
                try:
                    if value and hasattr(value, 'url'):
                        data[f.name] = value.url
                    else:
                        data[f.name] = None
                except ValueError:
                    data[f.name] = None
            elif isinstance(f, DecimalField):
                new_val = f.value_from_object(instance)
                data[f.name] = float(new_val) if new_val else None
                # print data[f.name]
            elif isinstance(f, DateTimeField) or isinstance(f, DateField):
                val = f.value_from_object(instance)
                if val:
                    data[f.name] = datetime_to_timestamp(val)
                else:
                    data[f.name] = None
            elif isinstance(f, SmallIntegerField) and getattr(f, '_choices'):
                v = f.value_from_object(instance)
                for key, val in f._choices:
                    if key == v:
                        data[f.name] = val
                        break
            else:
                data[f.name] = f.value_from_object(instance)
        return data

    @classmethod
    def serialize(cls, resource_instance, fields=None, exclude=None, options=None):
        return cls._serialize(resource_instance._instance, fields=fields, exclude=exclude, options=options)


def lazy_load_model_serializer():
    try:
        return class_from_path(REST_SETTINGS.SERIALIZER)()
    except KeyError:
        return ModelSerializer()


default_model_serializer = SimpleLazyObject(lazy_load_model_serializer)


class MongoSerializer(object):
    """
    Mongodb Resource to dict serializer
    """

    @classmethod
    def serialize(cls, resource_instance, fields=None, exclude=None, options=None):
        # instance = resource_instance
        # related_fields_fetch = {}
        # related_exclude_fetch = {}
        # if fields is not None:
        # for x in fields:
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
        if options and 'date_format' in options and options['date_format'] == 'U':
            date_func = datetime_to_timestamp
            options = options.copy()
            del options['date_format']
        else:
            date_func = datetime_to_timestamp
        ret = _json_convert(resource_instance._instance.to_dict(serializer=cls), date_func=date_func)
        if '_id' in ret:
            ret['id'] = ret['_id']
            del ret['_id']
        if fields or exclude:
            ret = recursive_dict_filter(ret, fields, exclude)
        return ret


def _json_convert(obj, date_func=None):
    if hasattr(obj, 'iteritems') or hasattr(obj, 'items'):  # PY3 support
        return SON(((k, _json_convert(v, date_func=date_func)) for k, v in iteritems(obj)))
    elif hasattr(obj, '__iter__') and not isinstance(obj, string_types):
        return list((_json_convert(v, date_func=date_func) for v in obj))
    try:
        return default(obj, date_func=date_func)
    except TypeError:
        return obj


def default(obj, date_func=None):
    if isinstance(obj, ObjectId):
        return urlsafe_base64_encode(obj.binary).decode('utf8')
    if isinstance(obj, DBRef):
        return _json_convert(obj.as_doc())
    if isinstance(obj, datetime.datetime):
        return date_func(obj)
    if isinstance(obj, RE_TYPE):
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
        return {"$regex": obj.pattern,
                "$options": flags}
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