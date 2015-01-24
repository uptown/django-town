# ...
# This code from
# https://github.com/MongoEngine/extras-mongoengine/blob/master/fields/fields.py
# ...
# ...
from datetime import timedelta
import datetime

from mongoengine.base import BaseField
from mongoengine.fields import StringField, EmailField
import os
from mongoengine.python_support import str_types
from django.db.models.fields.files import FieldFile
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.utils.encoding import force_str, force_text


class TimedeltaField(BaseField):
    """A timedelta field.

    Looks to the outside world like a datatime.timedelta, but stores
    in the database as an integer (or float) number of seconds.

    """

    def validate(self, value):
        if not isinstance(value, (timedelta, int, float)):
            self.error(u'cannot parse timedelta "%r"' % value)

    def to_mongo(self, value):
        return self.prepare_query_value(None, value)

    def to_python(self, value):
        return timedelta(seconds=value)

    def prepare_query_value(self, op, value):
        if value is None:
            return value
        if isinstance(value, timedelta):
            return self.total_seconds(value)
        if isinstance(value, (int, float)):
            return value

    @staticmethod
    def total_seconds(value):
        """Implements Python 2.7's datetime.timedelta.total_seconds()
        for backwards compatibility with Python 2.5 and 2.6.

        """
        try:
            return value.total_seconds()
        except AttributeError:
            return (value.days * 24 * 3600) + \
                   (value.seconds) + \
                   (value.microseconds / 1000000.0)


class LocalStorageFileField(BaseField):
    proxy_class = FieldFile

    def __init__(self,
                 size=None,
                 name=None,
                 upload_to='',
                 storage=None,
                 **kwargs):
        self.size = size
        self.storage = storage or default_storage
        self.upload_to = upload_to
        if callable(upload_to):
            self.generate_filename = upload_to
        super(LocalStorageFileField, self).__init__(**kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        file = instance._data.get(self.name)

        if isinstance(file, str_types) or file is None:
            attr = self.proxy_class(instance, self, file)
            instance._data[self.name] = attr

        return instance._data[self.name]

    def __set__(self, instance, value):
        key = self.name
        if isinstance(value, File) and not isinstance(value, self.proxy_class):
            file = instance._data.get(self.name)
            if file:
                try:
                    file.delete()
                except:
                    pass
            # Create a new proxy object as we don't already have one
            file_copy = self.proxy_class(instance, self, value.name)
            file_copy.file = value
            instance._data[key] = file_copy
        else:
            instance._data[key] = value

        instance._mark_as_changed(key)

    def get_directory_name(self):
        return os.path.normpath(force_text(datetime.datetime.now().strftime(force_str(self.upload_to))))

    def get_filename(self, filename):
        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))

    def generate_filename(self, instance, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename))

    def to_mongo(self, value):
        if isinstance(value, self.proxy_class):
            return value.name
        return value

    def to_dict(self, value, serializer=None):
        # print value, type(value), self.storage.url(value)
        if value:
            return self.storage.url(value)
        return self.to_mongo(value)


class LowerStringField(StringField):
    def __set__(self, instance, value):
        value = self.to_python(value)
        return super(LowerStringField, self).__set__(instance, value)

    def to_python(self, value):
        if value:
            value = value.lower()
        return value

    def prepare_query_value(self, op, value):
        value = value.lower() if value else value
        return super(LowerStringField, self).prepare_query_value(op, value)


class LowerEmailField(LowerStringField):
    def validate(self, value):
        if not EmailField.EMAIL_REGEX.match(value):
            self.error('Invalid Mail-address: %s' % value)
        super(LowerEmailField, self).validate(value)
