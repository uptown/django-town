from django_town.rest.resources.exceptions import ValidationError


class VirtualField(object):

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