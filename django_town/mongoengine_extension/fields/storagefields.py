import datetime

import os
from mongoengine.base import BaseField
from mongoengine.python_support import str_types
from django.core.files.storage import default_storage
from django.utils.encoding import force_str, force_text


class DjangoStorageFileWrapper(object):
    def __init__(self, field, instance, name=''):
        self.field = field
        self.instance = instance
        self.name = name

    def save(self, name, content, save=True):
        name = self.field.generate_filename(self.instance, name)
        _file = self.instance._data.get(self.field.name)
        if _file:
            try:
                _file.delete()
            except IOError:
                pass
        self.name = self.field.storage.save(name, content)
        self.instance._data[self.field.name] = self.name
        self.instance._mark_as_changed(self.field.name)

        if save:
            self.instance.save()

    def delete(self):
        if self.name:
            self.field.storage.delete(self.name)


    @property
    def url(self):
        return self.field.storage.url(self.name)

    def __str__(self):
        return self.name


class DjangoStorageField(BaseField):
    file_wrapper_cls = DjangoStorageFileWrapper

    def __init__(self, upload_to='', storage=None, **kwargs):
        if callable(upload_to):
            self.generate_filename = upload_to
        else:
            self.upload_to = upload_to
        self.storage = storage or default_storage
        super(DjangoStorageField, self).__init__(**kwargs)

    def get_directory_name(self):
        return os.path.normpath(force_text(datetime.datetime.now().strftime(force_str(self.upload_to))))

    def get_filename(self, filename):
        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))

    def generate_filename(self, instance, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename))

    def __get__(self, instance, owner):
        val = instance._data.get(self.name)
        if isinstance(val, str_types):
            wrapper = self.file_wrapper_cls(self, instance, name=val)
            instance._data[self.name] = wrapper
            return wrapper
        elif isinstance(val, self.file_wrapper_cls):
            return val
        return self.file_wrapper_cls(self, instance)

    def __set__(self, instance, value):
        if isinstance(value, self.file_wrapper_cls):
            instance._data[self.name] = value
            instance._mark_as_changed(self.name)
            pass
        elif isinstance(value, str_types):
            instance._data[self.name] = self.file_wrapper_cls(self, instance, name=value)
            instance._mark_as_changed(self.name)
        else:
            raise TypeError
