from django.utils.functional import cached_property
from django_town.rest.serializers import default_mongo_serializer
from django_town.rest.exceptions import RestNotFound, RestBadRequest
from django_town.rest.resources.base import DataBasedResource, ResourceInstance
from mongoengine import ListField, SortedListField, EmbeddedDocumentField, PointField, EmbeddedDocument
from django.utils.http import urlsafe_base64_decode
from bson import ObjectId
from bson.errors import InvalidId
from django_town.utils import json
from django_town.mongoengine_extension import ResourceField, DynamicResourceField, ResourceIntField


class MongoResourceInstance(ResourceInstance):

    def __init__(self, pk, manager, instance=None):
        self.document = manager.document
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
            acceptable_fields = self._manager.create_acceptable_fields
        if not required_fields:
            required_fields = self._manager.create_required_fields

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
        self._manager.invalidate_cache(self._pk)
        return self

    def delete(self):
        self._instance.delete()
        del self.__dict__["_instance"]
        self._manager.invalidate_cache(self._pk)
        return


class MongoResource(DataBasedResource):

    resource_instance_cls = MongoResourceInstance
    document = None
    pk_regex = "[a-zA-Z0-9\-_]+"

    def __init__(self, document=None, name=None, resource_instance_cls=None, fields=None, exclude=None, options=None,
                 cache_key_format=None, cache_duration=None, create_acceptable=None, create_required=None,
                 serializer=default_mongo_serializer):
        if document:
            self.document = document
        if not self.document:
            raise Exception()
        if not self.cache_exclude:
            self.cache_exclude = []
        map = self.document._db_field_map
        for each_field in self.document._fields.items():
            field_name = map.get(each_field[0])
            current_field = each_field[1]
            if isinstance(current_field, (ResourceField, DynamicResourceField, ResourceIntField)):
                self.cache_exclude.append(field_name)
        super(MongoResource, self).__init__(name=self.document.__name__.lower() if not name else name,
                                            cache_key_format=cache_key_format
                                            ,cache_duration=cache_duration, resource_instance_cls=resource_instance_cls,
                                            create_acceptable=create_acceptable,
                                            create_required=create_required, fields=fields,
                                            exclude=exclude, options=options, serializer=serializer)

    def create_from_db(self, data=None, files=None):

        kwargs = {}
        map = self.document._db_field_map
        for each_field in self.document._fields.items():
            field_name = map.get(each_field[0])
            if not field_name:
                continue
            data_source = None
            if data and field_name in data:
                data_source = data
            elif files and field_name in files:
                data_source = files
            if data_source:
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
                else:
                    kwargs[field_name] = data_source.get(field_name)
        # print self.document._fields,  self.document._db_field_map
        try:
            _instance = self.document(**kwargs).save()
        except ValueError:
            raise RestBadRequest()
        return _instance

    def __call__(self, pk, instance=None):
        if isinstance(pk, ObjectId):
            return self.resource_instance_cls(pk, self, instance=instance)
        try:
            return self.resource_instance_cls(ObjectId(urlsafe_base64_decode(pk)), self, instance=instance)
        except InvalidId:
            raise RestBadRequest()

    def pk_collection(self, **kwargs):
        return self.document.objects.all().order_by('pk').values_list('pk')