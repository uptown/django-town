from django_town.utils import json
import datetime
from django.utils.functional import cached_property
from mongoengine import ListField, SortedListField, EmbeddedDocumentField, PointField, EmbeddedDocument, \
    NotUniqueError, ValidationError, DateTimeField
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from bson import ObjectId
from bson.errors import InvalidId

from django_town.mongoengine_extension.fields import DynamicResourceField, ResourceReferenceField
from django_town.rest.serializers import default_mongo_serializer
from django_town.rest.exceptions import RestNotFound, RestBadRequest, RestFormInvalid, RestDuplicate
from django_town.rest.resources.base import DataBasedResource, ResourceInstance
from django_town.utils.rand import generate_random_from_vschar_set


class MongoResourceInstance(ResourceInstance):
    """
    Mongoengine-based resource instance. instance._instance will return mongoengine object with self.pk.
    """

    def __init__(self, pk, manager, instance=None):
        self.document = manager._meta.document
        if instance:
            self.__dict__['_instance'] = instance
        super(MongoResourceInstance, self).__init__(pk, manager)

    @cached_property
    def _instance(self):
        try:
            return self.document.objects.get(pk=self._pk)
        except self.document.DoesNotExist:
            raise RestNotFound(self._manager)

    def update(self, data=None, files=None, acceptable_fields=None, required_fields=None):
        kwargs = {}
        if data:
            kwargs.update(data)
        if files:
            kwargs.update(files)

        all_keys = set(kwargs.keys())

        if not acceptable_fields:
            acceptable_fields = self._manager._meta.create_acceptable_fields
        if not required_fields:
            required_fields = self._manager._meta.create_required_fields

        if required_fields and not set(required_fields).issubset(all_keys):
            raise RestBadRequest()
        if acceptable_fields and not set(acceptable_fields).issuperset(all_keys):
            raise RestBadRequest()

        try:
            obj = self._instance
            obj.update(**kwargs)
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


class MongoResource(DataBasedResource):
    """
    Mongoengine based resource.
    Default resource instance is "MongoResourceInstance".
    Default serializer is mongo_serializer.
    You can install Mongoegine in "http://mongoengine.org/".
    """

    class Meta:
        resource_instance_cls = MongoResourceInstance
        document = None
        pk_regex = "[a-zA-Z0-9\-_]+"
        serializer = default_mongo_serializer

    @staticmethod
    def pk_to_object_id(pk):
        try:
            return ObjectId(urlsafe_base64_decode(pk))
        except TypeError:
            raise RestNotFound()

    @staticmethod
    def object_id_to_pk(obj_id):
        return urlsafe_base64_encode(obj_id.binary)

    def __init__(self, document=None, name=None, **kwargs):

        from django_town.mongoengine_extension import ResourceField, DynamicResourceField, ResourceIntField

        if not document:
            document = self._meta.document
        _db_field_map = document._db_field_map
        kwargs['_resource_fields'] = set()

        if not self._meta.date_format_fields:
            self._meta.date_format_fields = []

        for each_field in document._fields.items():
            field_name = _db_field_map.get(each_field[0])
            current_field = each_field[1]
            if isinstance(current_field, (ResourceField, DynamicResourceField, ResourceIntField, ResourceReferenceField)):
                kwargs['_resource_fields'].add((field_name, each_field[0]))

            if isinstance(each_field, DateTimeField):
                self._meta.date_format_fields.append(each_field.name)
            # if isinstance(field_name, TopLevelDocumentMetaclass):
            #     self._db_field_map[each_field[0]] = each_field[0]
            # print each_field
        if not name:
            name = document.__name__.lower()
        super(MongoResource, self).__init__(name=name, document=document, **kwargs)

    def create_from_db(self, data=None, files=None, or_get=False):

        kwargs = {}
        # ref_kwargs = {}
        _db_field_map = self._meta.document._db_field_map
        for each_field in self._meta.document._fields.items():
            field_name = _db_field_map.get(each_field[0])
            if not field_name:
                continue
            data_source = None
            if data and field_name in data:
                data_source = data
            elif files and field_name in files:
                data_source = files
            if data_source:
                from django_town.mongoengine_extension.fields.extra import LocalStorageFileField

                current_field = each_field[1]
                if isinstance(current_field, (SortedListField, ListField)) and hasattr(data_source, 'getlist'):
                    kwargs[field_name] = data_source.getlist(field_name)
                elif isinstance(current_field, EmbeddedDocumentField) and \
                        not isinstance(data_source.get(field_name), EmbeddedDocument):
                    kwargs[field_name] = json.loads(data_source.get(field_name))
                elif isinstance(current_field, PointField):
                    latlng = data_source.get(field_name)
                    if latlng:
                        latlng = data_source.get(field_name).split(',')
                        kwargs[field_name] = [float(latlng[1]), float(latlng[0])]
                # elif isinstance(current_field, LocalStorageFileField):
                #     file_fields[field_name] = data_source.get(field_name)
                elif isinstance(current_field, DynamicResourceField):
                    kwargs[field_name] = data_source.get(field_name)
                    kwargs[field_name + "_type"] = kwargs[field_name]._manager._meta.name
                elif isinstance(current_field, DateTimeField):
                    kwargs[field_name] = datetime.datetime.fromtimestamp(float(data_source.get(field_name)))
                # elif isinstance(current_field, ReferenceField):
                #     ref_kwargs[field_name] = data_source.get(field_name)
                else:
                    kwargs[field_name] = data_source.get(field_name)
        # print self.document._fields,  self.document._db_field_map
        # print kwargs
        try:
            if or_get:
                _instance, created = self._meta.document.objects.get_or_create(**kwargs)
            else:
                created = False
                _instance = self._meta.document(**kwargs).save()
            # for k, v in file_fields.iteritems():
            #     if v:
            #         getattr(_instance, k).save(generate_random_from_vschar_set(length=30), v)
        except ValueError:
            import traceback
            traceback.print_exc()
            raise RestBadRequest()
        except NotUniqueError:
            raise RestDuplicate()
        except ValidationError as e:
            import traceback
            traceback.print_exc()
            raise RestFormInvalid(e.errors.keys()[0])
        return _instance, created

    def __call__(self, pk, instance=None):
        if isinstance(pk, ObjectId):
            return self._meta.resource_instance_cls(pk, self, instance=instance)
        try:
            return self._meta.resource_instance_cls(self.pk_to_object_id(pk), self, instance=instance)
        except InvalidId:
            raise RestBadRequest()

    def serialize(self, resource_instance, options=None, request=None):
        ret = super(MongoResource, self).serialize(resource_instance, options=options, request=request)
        for each_resource_fields, field_in_python in self._meta._resource_fields:
            if each_resource_fields in ret:
                value = getattr(self._meta.document, field_in_python).to_python(ret[each_resource_fields])
                if isinstance(value, ResourceInstance):
                    ret[each_resource_fields] = value.to_dict()
                else:
                    pass
                    # else:
                    # default = getattr(self.document, field_in_python).default
                    #     if callable(default):
                    #         default = default()
                    #     if isinstance(default, ResourceInstance):
                    #         ret[each_resource_fields] = default.to_dict()
                    #     else:
                    #         ret[each_resource_fields] = default
        return ret

    def pk_collection(self, **kwargs):
        return self._meta.document.objects.order_by('pk').values_list('pk')

    def count(self, **kwargs):
        return self._meta.document(**kwargs).count()