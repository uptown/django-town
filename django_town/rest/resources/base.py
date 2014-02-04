from django_town.cache import SimpleCache
from django_town.rest.serializers import default_model_serializer, BaseSerializer
from django_town.utils.common import recursive_dict_filter
from django_town.rest.exceptions import RestBadRequest
from django_town.rest.resources.fields import VirtualField

REST_RESERVED_FIELDS = ['suppress_http_code']


class ResourceBase(type):
    """
    resource meta class
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ResourceBase, cls).__new__
        new_cls = super_new(cls, name, bases, attrs)
        # print cls, name, bases, attrs
        # print getattr(new_cls, '_virtual_fields', [])
        all_virtual_fields = []

        for key, attr in attrs.iteritems():
            if isinstance(attr, VirtualField):
                attr.contribute_to_class(new_cls, key)
                all_virtual_fields.append(key)
        setattr(new_cls, '_virtual_fields', all_virtual_fields)
        return new_cls


class ResourceInstance(object):

    def __init__(self, pk, manager):
        self._pk = pk
        self._manager = manager
        self._values = {}

    def update(self, **kwargs):
        return self._manager.update(self, **kwargs)

    def delete(self):
        return self._manager.delete(self)

    def to_dict(self, fields=None, exclude=None, serializer=None):
        ret = self._manager.serialize(self)
        if fields:
            ret = recursive_dict_filter(ret, fields)
        if exclude:
            for each in exclude:
                if each in ret:
                    del ret[each]
        return ret

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        if item in self.__dict__['_manager']._virtual_fields:
            return getattr(self._manager, "_" + item)(self)

    def all_virtual_items(self, fields=None, exclude=None):
        ret = {}
        if fields:
            for field in self._manager._virtual_fields:
                if field in fields:
                    ret[field] = getattr(self, field)
        elif exclude:
            for field in self._manager._virtual_fields:
                if field not in exclude:
                    ret[field] = getattr(self, field)
        else:
            for field in self._manager._virtual_fields:
                ret[field] = getattr(self, field)
        return ret


class Resource(object):

    __metaclass__ = ResourceBase
    resource_instance_cls = ResourceInstance

    name = "Resource"
    cache_key_format = None
    cache_duration = 60 * 60 * 15

    create_acceptable = None
    create_required = None
    create_exclude = None

    update_acceptable = None
    update_required = None
    update_exclude = None

    cache_exclude = []
    fields = None
    exclude = None
    options = None
    serializer = None

    def __init__(self, name=None, resource_instance_cls=None, fields=None, exclude=None, options=None,
                 cache_key_format=None, cache_duration=None, create_acceptable=None, create_required=None,
                 create_exclude=None, update_exclude=None,
                 update_acceptable=None, update_required=None, serializer=default_model_serializer):
        if name:
            self.name = name
        if cache_key_format:
            self.cache_key_format = cache_key_format
        if cache_duration:
            self.cache_duration = cache_duration
        if resource_instance_cls:
            self.resource_instance_cls = resource_instance_cls
        if create_acceptable:
            self.create_acceptable = create_acceptable
        if create_required:
            self.create_required = create_required
        if update_acceptable:
            self.update_acceptable = update_acceptable
        if update_required:
            self.update_required = update_required
        if create_exclude:
            self.create_exclude = create_exclude
        if update_exclude:
            self.update_exclude = update_exclude
        if fields:
            self.fields = fields
        if exclude:
            self.exclude = exclude
        if options:
            self.options = options
        if serializer:
            self.serializer = serializer
        else:
            self.serializer = BaseSerializer()

    def validate_create(self, data=None, files=None, acceptable=None, required=None, exclude=None):
        if not files:
            files = {}
        if not data:
            data = {}
        all_keys = set(data.keys()) | set(files.keys())
        for each in REST_RESERVED_FIELDS:
            if each in all_keys:
                all_keys.remove(each)
        if not acceptable:
            acceptable = self.create_acceptable
        if not required:
            required = self.create_required
        if not exclude:
            exclude = self.create_exclude

        if required and not set(required).issubset(all_keys):
            raise RestBadRequest()
        if acceptable and not set(acceptable).issuperset(all_keys):
            raise RestBadRequest()
        if exclude and len(set(exclude).intersection(all_keys)) > 0:
            raise RestBadRequest()
        return data, files

    def create(self, data=None, files=None):
        return self.resource_instance_cls(data['pk'], self)

    def delete(self, resource_instance):
        pass

    def update(self, resource_instance, *args, **kwargs):
        pass

    def serialize(self, resource_instance):
        def load_cache(**_kwargs):
            ret = self.instance_to_python(resource_instance, exclude=self.cache_exclude,
                                          **_kwargs)
            return ret

        if self.cache_key_format:
            cache = SimpleCache(self.cache_key_format, self.cache_duration, load_cache)
            ret = cache.get(pk=resource_instance._pk)
        else:
            ret = load_cache(pk=resource_instance._pk)
        if len(self.cache_exclude) > 0:
            ret.update(resource_instance.all_virtual_items(fields=self.cache_exclude))
            ret.update(self.instance_to_python(resource_instance, fields=self.cache_exclude))
        return ret

    def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
        if not exclude:
            exclude = self.exclude
        elif self.exclude:
            exclude += self.exclude
        if not fields:
            fields = self.fields
        elif self.fields:
            fields += self.fields
        ret = self.serializer.serialize(resource_instance._instance, fields=fields, exclude=exclude,
                                        options=self.options)
        ret.update(resource_instance.all_virtual_items(exclude=exclude))
        return ret

    def __call__(self, pk):
        return self.resource_instance_cls(pk, self)

    def invalidate_cache(self, pk):
        SimpleCache(self.cache_key_format, self.cache_duration, None).delete(pk=pk)



class DataBasedResource(Resource):

    def create_from_db(self, data=None, files=None):
        return None

    def create(self, data=None, files=None, acceptable=None, required=None, exclude=None):
        data, file = self.validate_create(data=data, files=files, acceptable=acceptable, required=required, exclude=exclude)
        _instance = self.create_from_db(data=data, files=files)
        return self.resource_instance_cls(_instance.pk, self, instance=_instance)