from mongoengine import IntField, StringField, DictField, ReferenceField
from django_town.utils import json
from django.utils.six import string_types
from django.db.models.loading import get_model


class OptionField(IntField):
    def __init__(self, option=None, **kwargs):
        self.option = option
        super(OptionField, self).__init__(**kwargs)

    def to_mongo(self, value):
        lookup = {v: k for k, v in self.option}
        return lookup[value]

    def to_python(self, value):
        lookup = {k: v for k, v in self.option}
        try:
            return lookup[value]
        except KeyError:
            return value

    def to_dict(self, value, serializer=None):
        return self.to_python(value)

    def validate(self, value):
        lookup = [v for k, v in self.option]
        if value in lookup:
            return
        self.error('%s is not in [%s]' % value, ', '.join([str(each) for each in lookup]))


class ResourceField(StringField):
    def __init__(self, resource, fields=None, **kwargs):
        self.resource = resource
        self.fields = fields
        super(ResourceField, self).__init__(**kwargs)

    def to_mongo(self, value):
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return value._pk
        return value

    def to_python(self, value):
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return value
        return self.resource(value)

    def validate(self, value):
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return
        self.error('%s could not be converted to resource' % value)


class ResourceIntField(IntField):
    def __init__(self, resource, fields=None, **kwargs):
        self.resource = resource
        self.fields = fields
        super(ResourceIntField, self).__init__(**kwargs)


    def to_mongo(self, value):
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return int(value._pk)
        return int(value)

    def to_python(self, value):
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return value
        return self.resource(value)

    def validate(self, value):
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return
            # self.error('%s could not be converted to resource' % value)



class ModelField(IntField):
    def __init__(self, model, fields=None, **kwargs):
        if isinstance(model, string_types):
            model = get_model(model)
        self.model = model
        self.fields = fields
        super(ModelField, self).__init__(**kwargs)


    def to_mongo(self, value):
        if isinstance(value, self.model):
            return int(value.pk)
        return int(value)

    def to_python(self, value):
        if isinstance(value, self.model):
            return value
        return self.model.objects.get(pk=value)

    def validate(self, value):
        if isinstance(value, self.model):
            return
            # self.error('%s could not be converted to resource' % value)


class DynamicResourceField(DictField):
    def __init__(self, available_resources, fields=None, **kwargs):
        self.available_resources = available_resources
        self.fields = fields
        super(DynamicResourceField, self).__init__(**kwargs)

    def to_mongo(self, value):
        for resource in self.available_resources:
            if hasattr(value, '_manager') and isinstance(value._manager, resource.__class__):
                return {'_resource_name': resource._meta.name, '_pk': value._pk}
        return value

    def __get__(self, instance, owner):
        """Descriptor for retrieving a value from a field in a document.
        """
        if instance is None:
            # Document class being used rather than a document object
            return self

        # Get value from document instance if available
        return self.to_python(instance._data.get(self.name))

    def to_python(self, value):
        if isinstance(value, string_types):
            try:
                value = json.loads(value)
            except ValueError:
                return None
        resource_name = value['_resource_name'] if isinstance(value, dict) and '_resource_name' in value else None
        for resource in self.available_resources:
            if isinstance(value, resource._meta.resource_instance_cls):
                return value
            if resource_name and resource_name == resource._meta.name:
                _pk = value.get('_pk')
                ret = resource(_pk)
                # getattr(ret, '_instance')
                return ret
        return None

    def validate(self, value):
        for resource in self.available_resources:
            if isinstance(value, resource._meta.resource_instance_cls):
                getattr(resource._meta.resource_instance_cls, '_instance')
                return
            if isinstance(value, dict) and value == {}:
                return
        self.error('%s could not be converted to resource' % value)


class ResourceReferenceField(ReferenceField):
    def __init__(self, document_type, fields=None, exclude=None, cache_key_format=None, **kwargs):
        from django_town.rest.resources import MongoResource
        self.resource = MongoResource(document_type, fields=fields, exclude=exclude, cache_key_format=cache_key_format)
        self.fields = fields
        super(ResourceReferenceField, self).__init__(document_type, **kwargs)

    def to_mongo(self, value):
        # print 'to_mongo', value
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return value._pk
        return value

    def to_python(self, value):
        # print 'to_python', value
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return value
        return self.resource(value)

    def validate(self, value):
        if isinstance(value, self.resource._meta.resource_instance_cls):
            return
        self.error('%s could not be converted to resource' % value)