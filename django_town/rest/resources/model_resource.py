from django.utils.functional import cached_property
from django.db import IntegrityError, transaction, models
from django.db.models.loading import get_model

from django_town.rest.serializers import default_model_serializer
from django_town.rest.exceptions import RestNotFound, RestBadRequest, RestAlreadyExists
from django_town.rest.resources.base import DataBasedResource, ResourceInstance
from django_town.core.fields import JSONField
from django.utils.six import iteritems, string_types


class ModelResourceInstance(ResourceInstance):
    """
    Django-ORM based resource instance. instance._instance will return ORM-object with self.pk.
    """

    def __init__(self, pk, manager, instance=None):
        self.model = manager._meta.model
        if instance:
            self.__dict__['_instance'] = instance
        super(ModelResourceInstance, self).__init__(pk, manager)

    def get_instance(self):
        return self._instance

    @cached_property
    def _instance(self):
        try:
            return self.model.objects.get(pk=self._pk)
        except self.model.DoesNotExist:
            raise RestNotFound(self._manager)

    def update(self, data=None, files=None, acceptable_fields=None, required_fields=None):
        kwargs = {}
        if not files:
            files = {}
        for each_field in self._meta.model._meta.fields:
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
        # if data:
        #     kwargs.update(data)
        # if files:
        #     kwargs.update(files)

        all_keys = set(kwargs.keys())

        if not acceptable_fields:
            acceptable_fields = self._manager._meta.create_acceptable
        if not required_fields:
            required_fields = self._manager._meta.create_required

        if required_fields and not set(required_fields).issubset(all_keys):
            raise RestBadRequest()
        if acceptable_fields and not set(acceptable_fields).issuperset(all_keys):
            raise RestBadRequest()

        try:
            obj = self._instance
            for key, val in iteritems(kwargs):
                setattr(obj, key, val)
            obj.save()
        except ValueError:
            raise RestBadRequest()
        self._manager.invalidate_cache(pk=self._pk)
        return self

    def delete(self):
        self._instance.delete()
        del self.__dict__["_instance"]
        self._manager.invalidate_cache(pk=self._pk)
        return


class ModelResource(DataBasedResource):
    """
    Django-orm based resource.
    Default resource instance is "ModelResourceInstance".
    Default serializer is model_serializer.
    You must consider that pre_create, create, and post_create are in transaction.
    """
    using = None
    class Meta:
        resource_instance_cls = ModelResourceInstance
        model = None
        pk_regex = "\d+"

    def __init__(self, model=None, name=None, **kwargs):
        if not 'serializer' in kwargs or not kwargs['serializer']:
            kwargs['serializer'] = default_model_serializer

        if not model:
            model = self._meta.model
        if isinstance(model, string_types):
            model = get_model(model)
        if not self._meta.date_format_fields:
            self._meta.date_format_fields = []
            for each_field in model._meta.fields:
                if isinstance(each_field, models.DateTimeField) or isinstance(each_field, models.DateField):
                    self._meta.date_format_fields.append(each_field.name)

        super(ModelResource, self).__init__(name=model.__name__.lower() if not name else name, model=model, **kwargs)

    def create_from_db(self, data=None, files=None, or_get=False):
        kwargs = {}
        if not files:
            files = {}
        for each_field in self._meta.model._meta.fields:
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
            if or_get:
                _instance, created = self._meta.model.objects.get_or_create(**kwargs)
            else:
                _instance = self._meta.model.objects.create(**kwargs)
                created = False
        except ValueError:
            raise RestBadRequest()
        except IntegrityError as e:
            err_no = e.args[0]
            if err_no == 1048:
                raise RestBadRequest()
            elif err_no == 1452:
                raise RestNotFound()
            else:
                raise RestAlreadyExists()
        return _instance, created

    def _create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
               request_kwargs=None, or_get=False):
        with transaction.atomic(using=self.using):
            return super(ModelResource, self)._create(data, files, acceptable, required, exclude, request,
                                                      request_kwargs, or_get=or_get)

    def __call__(self, pk, instance=None):
        return self._meta.resource_instance_cls(pk, self, instance=instance)

    def pk_collection(self, **kwargs):
        return self._meta.model.objects.all().order_by('pk').values_list('pk', flat=True)

    def count(self, **kwargs):
        return self._meta.model.objects.filter(**kwargs).count()