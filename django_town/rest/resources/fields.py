from django_town.rest.resources.exceptions import ValidationError
from django_town.rest.resources.base import resource_by_name, resource_cache_manager
from django.utils import six
from django_town.cache.utlis import SimpleCache


class VirtualField(object):
    """
    VirtualField will allow a resource has a virtual field.

    Usage.

    .. code-block:: python

        class SomeResource(Resource):
            test_field = VirtualField()

            def _test_field(self, instance):
                return "test"

        SomeResource()(pk).test_field # will return "test"
    """

    def __init__(self, name=None, getter=None, setter=None, default=None):

        self._default = default
        self._getter = getter
        self._setter = setter
        self.name = name
        self.resource = None
        self.verbose_name = None

    def set_attributes_from_name(self, name):
        if not self.name:
            self.name = name
        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')

    def get_attname(self):
        return self.name

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        self.resource = cls

    def __get__(self, instance, owner):
        return self._getter(instance)

    def __set__(self, instance, value):
        self._setter(instance, value)

    def validate(self, value):
        pass


class VirtualRequestField(VirtualField):
    pass


class ModelCountField(VirtualField):
    def __init__(self, resource=None, cache_key_format=None, where=None, **kwargs):
        if isinstance(resource, six.string_types):
            resource = resource_by_name(resource)
        self.from_resource = resource
        self.cache_key_format = cache_key_format
        self.where = where
        super(ModelCountField, self).__init__(**kwargs)


    def contribute_to_class(self, cls, name):
        resource_cache_manager.register(self.from_resource, self.resource, self.where)
        super(ModelCountField, self).contribute_to_class(cls, name)


class RequestVirtualField(object):
    def __init__(self, name=None, getter=None, setter=None, default=None):

        self._default = default
        self._getter = getter
        self._setter = setter
        self.name = name
        self.resource = None
        self.verbose_name = None

    def set_attributes_from_name(self, name):
        if not self.name:
            self.name = name
        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')

    def get_attname(self):
        return self.name

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        self.resource = cls

    def __get__(self, instance, owner):
        return self._getter(instance)

    def __set__(self, instance, value):
        self._setter(instance, value)

    def validate(self, value):
        pass


class VirtualCharField(VirtualField):
    def __init__(self, name=None, getter=None, setter=None, default=None, max_length=255):
        self.max_length = max_length
        super(VirtualCharField, self).__init__(name=name, getter=getter, setter=setter, default=default)

    def validate(self, value):
        try:
            if len(str(value)) > self.max_length:
                raise ValidationError(self.name, "too_long")
        except ValueError:
            raise ValidationError(self.name, "wrong_type")


class VirtualResourceField(VirtualField):
    def __init__(self, resource_cls, key_path, name=None, getter=None, setter=None, default=None):
        self.resource_cls = resource_cls
        self.key_path = key_path
        super(VirtualResourceField, self).__init__(name=name, getter=getter, setter=setter, default=default)
