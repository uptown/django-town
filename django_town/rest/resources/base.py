import datetime
from django.utils import six
from django.utils.functional import cached_property
from django_town.cache.utlis import SimpleCache
from django_town.rest.serializers import BaseSerializer
from django_town.rest.manager import rest_manager
from django_town.utils.common import recursive_dict_filter
from django_town.rest.exceptions import RestBadRequest, RestFormRequired


_resource_lookup = {}


def resource_by_name(name):
    return _resource_lookup[name]


class ResourceCacheManager(object):

    def __init__(self):
        self.lookup = {}

    def register(self, trigger_resource, resource, mapping_role):
        if isinstance(resource, six.string_types):
            resource = resource_by_name(resource)
        if isinstance(trigger_resource, six.string_types):
            trigger_resource = resource_by_name(trigger_resource)
        self.lookup[trigger_resource.__name__] = [resource, mapping_role]

    def check_and_execute(self, resource_instance, action):
        if resource_instance._manager.__name__ in self.lookup:
            target, role = self.lookup[resource_instance._manager.__name__]
            kwargs = {}
            for key, val in six.iteritems(role):
                kwargs[val] = getattr(resource_instance, key)
            target().invalidate_cache(**kwargs)


resource_cache_manager = ResourceCacheManager()


from django_town.rest.resources.fields import VirtualField, VirtualRequestField, ModelCountField


REST_RESERVED_FIELDS = ['suppress_http_code']


class _Meta(object):
    pass


class ResourceMeta(type):
    """
    Resource meta class.
    """

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def __new__(cls, name, bases, attrs):
        super_new = super(ResourceMeta, cls).__new__


        # if name == 'NewBase' and attrs == {}:
        # return super_new(cls, name, bases, attrs)
        #
        # # Also ensure initialization is only performed for subclasses of Model
        # # (excluding Model class itself).
        # parents = [b for b in bases if isinstance(b, ResourceBase) and
        #         not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))]
        # if not parents:
        #     return super_new(cls, name, bases, attrs)

        new_cls = super_new(cls, name, bases, attrs)
        # print getattr(new_cls, '_virtual_fields', [])
        all_virtual_fields = {}

        for key, attr in six.iteritems(attrs):
            if isinstance(attr, VirtualField):
                attr.contribute_to_class(new_cls, key)
                all_virtual_fields[key] = type(attr)

        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_cls, 'Meta', None)
        else:
            meta = attr_meta
        base_meta = getattr(new_cls, '_meta', None)
        new_meta = _Meta()
        if base_meta:
            for key, val in vars(base_meta).items():
                if not key.startswith('__'):
                    setattr(new_meta, key, val)

        for key, val in vars(meta).items():
            if not key.startswith('__'):
                setattr(new_meta, key, val)
        new_cls.add_to_class('_meta', new_meta)

        setattr(new_cls, '_virtual_fields', all_virtual_fields)
        _resource_lookup[new_cls.__name__] = new_cls
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

    def to_dict(self, fields=None, exclude=None, options=None, request=None):
        ret = self._manager.serialize(self, options=options, request=request)
        if fields or exclude:
            ret = recursive_dict_filter(ret, fields, exclude)
        return ret

    @cached_property
    def _instance(self):
        return {}

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        if hasattr(self._instance, item):
            return getattr(self._instance, item)
        if item in self.__dict__['_manager']._virtual_fields:
            return getattr(self._manager, "field__" + item)(self)
        raise AttributeError()

    def all_virtual_items(self, fields=None, exclude=None, request=None):
        ret = {}
        if fields:
            for field in self._manager._virtual_fields:
                if field in fields:
                    if self._manager._virtual_fields[field] == VirtualRequestField:
                        if request:
                            ret[field] = getattr(self._manager, "field__" + field)(self, request=request)
                    else:
                        ret[field] = getattr(self._manager, "field__" + field)(self)
        elif exclude:
            for field in self._manager._virtual_fields:
                if field not in exclude:
                    if self._manager._virtual_fields[field] == VirtualRequestField:
                        if request:
                            ret[field] = getattr(self._manager, "field__" + field)(self, request=request)
                    else:
                        ret[field] = getattr(self._manager, "field__" + field)(self)
        else:
            for field in self._manager._virtual_fields:
                if request and self._manager._virtual_fields[field] == VirtualRequestField:
                    ret[field] = getattr(self._manager, "field__" + field)(self, request=request)
                else:
                    ret[field] = getattr(self._manager, "field__" + field)(self)
        return ret

    def __copy__(self):
        return self.__class__(self._pk, self._manager)

    def __deepcopy__(self, memo):
        return self.__class__(self._pk, self._manager)


class ResourceBase(object):
    """
    Resource class. You can set variable as the class variable or as the instance variable
    by initiation with args.
    Resource()(pk) will return resource instance object with some pk.

    .. code-block:: python

        class SomeResource(Resource):
            name = "Resource" # resource name
            cache_key_format = None # resource cache key format
            cache_duration = 60 * 60 * 15 # resource cache alive time

            create_acceptable = None # acceptable args for create
            create_required = None # required args for create
            create_exclude = None # exclude args for create

            update_acceptable = None
            update_required = None
            update_exclude = None

            fields = None # resource fields
            exclude = None # resource exclude fields

            #always reload
            cache_ignored = None # always reload fields
            cache_ignored_virtual_only = None # virtual fields only

            serializer = BaseSerializer() # serializer for this resource


    """
    # __metaclass__ = ResourceMeta

    _meta = _Meta()

    class Meta:
        resource_instance_cls = ResourceInstance

        name = None
        cache_key_format = None
        cache_duration = 60 * 60 * 15

        create_acceptable = None
        create_required = None
        create_exclude = None

        update_acceptable = None
        update_required = None
        update_exclude = None

        fields = None
        exclude = None
        date_format_fields = None

        # always reload
        cache_ignored = None
        cache_ignored_virtual_only = None
        cache_bind = None
        options = None
        serializer = BaseSerializer()
        pk_regex = ""

    def __init__(self, **kwargs):
        # if serializer:
        # self._runtime_meta.serializer = serializer
        old_meta = self._meta
        self._meta = _Meta()
        for key, val in vars(old_meta).items():
            setattr(self._meta, key, val)

        for key, val in kwargs.items():
            setattr(self._meta, key, val)

        if hasattr(self._meta, 'filter'):
            self._meta.filter_include = []
            self._meta.filter_exclude = []
            for each in self._meta.filter:
                # print each
                if each[0] == '-':
                    self._meta.filter_exclude.append(each[1:])
                else:
                    self._meta.filter_include.append(each)
        else:
            self._meta.filter_include = []
            self._meta.filter_exclude = []

        if self._meta.cache_ignored:
            removing = []
            for each in self._meta.cache_ignored:
                if each in self._virtual_fields:
                    removing.append(each)
                    self._meta.cache_ignored_virtual_only.append(each)
            for each in removing:
                self._meta.cache_ignored.remove(each)
        if not self._meta.name:
            self._meta.name = self.__class__.__name__
        rest_manager.register_resource_cls(self.__class__, self._meta.name)
            # print self._meta.__dict__

    def validate_create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
                        request_kwargs=None, or_get=False):
        """
        This method called before pre_create and creating a resource to validate inputs.
        """
        if not files:
            files = {}
        if not data:
            data = {}
        if not acceptable:
            acceptable = self._meta.create_acceptable
        all_keys = set(data.keys()) | set(files.keys())
        if acceptable and not set(acceptable).issuperset(all_keys):
            data = {k: v for k, v in six.iteritems(data.copy()) if k in acceptable}
            all_keys = data.keys()
        for each in REST_RESERVED_FIELDS:
            if each in all_keys:
                all_keys.remove(each)
        if not required:
            required = self._meta.create_required
        if not exclude:
            exclude = self._meta.create_exclude

        if required and not set(required).issubset(all_keys):
            raise RestFormRequired(required[0])
        if exclude and len(set(exclude).intersection(all_keys)) > 0:
            raise RestBadRequest()
        return data, files

    def create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
               request_kwargs=None):
        """
        Create method. validate_create will invoke before creating.
        """
        data, file = self.validate_create(data=data, files=files, acceptable=acceptable, required=required,
                                          exclude=exclude, request=request, request_kwargs=request_kwargs)
        return self._meta.resource_instance_cls(data['pk'], self)

    def get_or_create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
               request_kwargs=None):
        """
        Get or create method. validate_create will invoke before creating.
        """
        data, file = self.validate_create(data=data, files=files, acceptable=acceptable, required=required,
                                          exclude=exclude, request=request, request_kwargs=request_kwargs)
        return self._meta.resource_instance_cls(data['pk'], self)


    def delete(self, resource_instance):
        """
        Delete method.
        """
        pass

    def update(self, resource_instance, *args, **kwargs):
        """
        Update method.
        """
        resource_instance.update(*args, **kwargs)
        pass

    def serialize(self, resource_instance, options=None, request=None):
        """
        Serialize a resource instance. This method must return a json-convertible dictionary.
        This method use caches if available.
        """

        def load_cache(**_kwargs):
            return self.instance_to_python(resource_instance, exclude=self._meta.cache_ignored, options=options,
                                           request=request, **_kwargs)

        if self._meta.cache_key_format:
            cache = SimpleCache(self._meta.cache_key_format, self._meta.cache_duration, load_cache)
            ret = cache.get(pk=resource_instance._pk)
        else:
            ret = load_cache(pk=resource_instance._pk)
        if self._meta.cache_ignored:
            ret.update(self.instance_to_python(resource_instance,
                                               fields=self._meta.cache_ignored + self._meta.cache_ignored_virtual_only,
                                               request=request))
        elif self._meta.cache_ignored_virtual_only:
            ret.update(
                resource_instance.all_virtual_items(fields=self._meta.cache_ignored_virtual_only, request=request))
        if self._meta.filter_include or self._meta.filter_exclude:
            ret = recursive_dict_filter(ret, self._meta.filter_include, self._meta.filter_exclude)
        if options:
            if 'date_format' in options:
                is_timestamp_mode = options['date_format'] == 'F'
                if is_timestamp_mode:
                    for each in self._meta.date_format_fields:
                        if each in ret and ret[each]:
                            ret[each] = str(datetime.datetime.fromtimestamp(int(ret[each])))

        return ret

    def instance_to_python(self, resource_instance, fields=None, exclude=None, options=None, request=None, **kwargs):
        """
        Serialize a resource instance. This method must return a json-convertible dictionary.
        This method always ignore caches.
        """
        # print self._meta.filter_include, self._meta.name
        if not exclude:
            exclude = self._meta.exclude
        elif self._meta.exclude:
            exclude += self._meta.exclude
        if not fields:
            fields = self._meta.fields
        elif self._meta.fields:
            fields += self._meta.fields
        elif self._meta.options:
            options += self._meta.options
        ret = self._meta.serializer.serialize(resource_instance, fields=fields, exclude=exclude,
                                              options=options)
        ret.update(resource_instance.all_virtual_items(fields=fields, exclude=exclude, request=request))
        return ret

    def __call__(self, pk):
        return self._meta.resource_instance_cls(pk, self)

    def invalidate_cache(self, **kwargs):
        if self._meta.cache_bind:
            for each in self._meta.cache_bind:
                each.delete(**kwargs)
        SimpleCache(self._meta.cache_key_format, self._meta.cache_duration, None).delete(**kwargs)

    def update_cache(self, pk, key, value):
        cache = SimpleCache(self._meta.cache_key_format, self._meta.cache_duration,
                            lambda **kwargs: self(kwargs['pk']).to_dict())
        original = cache.get(pk=pk)
        if original:
            original[key] = value
            cache.set(original, pk=pk)

    def post_create(self, resource_instance, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        """
        This method will invoke after create instance.
        """
        pass

    def pre_create(self, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        """
        This method will invoke before create instance.
        """
        return data, files

    def pre_delete(self, resource_instance):
        pass

    def post_delete(self, resource_instance):
        pass

    def count(self, **kwargs):
        return 0


class Resource(six.with_metaclass(ResourceMeta, ResourceBase)):
    pass


class DataBasedResource(Resource):
    """
    Base class for database-based resources such as a django-ORM resource or a mongodb resource.
    """
    def create_from_db(self, data=None, files=None, or_get=False):
        """
        This method will implement in each database-based resource.
        """
        return None, False

    def _create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
               request_kwargs=None, or_get=False):
        data, files = self.pre_create(data=data, files=files, acceptable=acceptable, required=required,
                                      exclude=exclude, request=request, request_kwargs=request_kwargs, or_get=or_get)
        _instance, created = self.create_from_db(data=data, files=files)
        ret = self._meta.resource_instance_cls(_instance.pk, self, instance=_instance)
        self.post_create(resource_instance=ret, data=data, files=files, acceptable=acceptable, required=required,
                         exclude=exclude, request=request, request_kwargs=request_kwargs, or_get=(not created))
        return ret, created

    def create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
               request_kwargs=None):
        data, files = self.validate_create(data=data, files=files, acceptable=acceptable, required=required,
                                           exclude=exclude, request=request, or_get=False)
        ret, unused = self._create(data, files, acceptable, required, exclude, request, request_kwargs)
        return ret

    def get_or_create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
               request_kwargs=None):

        data, files = self.validate_create(data=data, files=files, acceptable=acceptable, required=required,
                                           exclude=exclude, request=request, or_get=True)
        ret, created = self._create(data, files, acceptable, required, exclude, request, request_kwargs, or_get=True)
        return ret, created

    def _delete(self, resource_instance):
        resource_instance.delete()
        self.invalidate_cache(pk=resource_instance.pk)

    def delete(self, resource_instance):
        self.pre_delete(resource_instance)
        self._delete(resource_instance)
        self.post_delete(resource_instance)
        return {}


def all_resources():
    pass