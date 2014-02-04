from django.utils.functional import cached_property
from django_town.rest.serializers import default_model_serializer
from django_town.rest.exceptions import RestNotFound, RestBadRequest
from django_town.rest.resources.base import DataBasedResource, ResourceInstance
from django_town.core.fields import JSONField


class ModelResourceInstance(ResourceInstance):

    def __init__(self, pk, manager, instance=None):
        self.model = manager.model
        if instance:
            self.__dict__['_instance'] = instance
        super(ModelResourceInstance, self).__init__(pk, manager)

    @cached_property
    def _instance(self):
        try:
            return self.model.objects.get(pk=self._pk)
        except self.model.DoesNotExist:
            raise RestNotFound(self._manager)

    def update(self, data=None, files=None, acceptable_fields=None, required_fields=None):
        kwargs = {}
        if data:
            kwargs.update(data)
        if files:
            kwargs.update(files)

        all_keys = set(kwargs.keys())

        if not acceptable_fields:
            acceptable_fields = self._manager.create_acceptable_fields
        if not required_fields:
            required_fields = self._manager.create_required_fields

        if required_fields and not set(required_fields).issubset(all_keys):
            raise RestBadRequest()
        if acceptable_fields and not set(acceptable_fields).issuperset(all_keys):
            raise RestBadRequest()

        try:
            obj = self._instance
            obj.save(**kwargs)
        except ValueError:
            raise RestBadRequest()
        self._manager.invalidate_cache(self._pk)
        return self

    def delete(self):
        self._instance.delete()
        del self.__dict__["_instance"]
        self._manager.invalidate_cache(self._pk)
        return


class ModelResource(DataBasedResource):

    resource_instance_cls = ModelResourceInstance
    model = None
    pk_regex = "\d+"

    def __init__(self, model=None, name=None, **kwargs):
        if model:
            self.model = model
        if not self.model:
            raise Exception()
        if not 'serializer' in kwargs or not kwargs['serializer']:
            kwargs['serializer'] = default_model_serializer

        super(ModelResource, self).__init__(name=self.model.__name__.lower() if not name else name, **kwargs)

    def create_from_db(self, data=None, files=None):
        kwargs = {}
        if not files:
            files = {}
        for each_field in self.model._meta.fields:
            attname = each_field.attname
            name = each_field.name
            field_name = None
            data_source = None
            if attname in data:
                data_source = data
                field_name = attname
            elif attname in files:
                data_source = files
                field_name = attname
            elif name in data:
                data_source = data
                field_name = name
            elif name in files:
                data_source = files
                field_name = name
            if not field_name:
                continue
            if data_source:
                current_field = each_field
                if isinstance(current_field, JSONField) and hasattr(data_source, 'getlist'):
                    kwargs[field_name] = data_source.getlist(field_name)
                else:
                    kwargs[field_name] = data_source.get(field_name)
        try:
            _instance = self.model.objects.create(**kwargs)
        except ValueError:
            raise RestBadRequest()
        return _instance

    def __call__(self, pk, instance=None):
        return self.resource_instance_cls(pk, self, instance=instance)

    def pk_collection(self, **kwargs):
        return self.model.objects.all().order_by('pk').values_list('pk', flat=True)