from django.utils.http import int_to_base36

from django_town.rest.resources import Resource
from django_town.social.models.geo import AddressComponent, AddressComponentType


class RegionResource(Resource):
    def create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
               request_kwargs=None):
        if not data['from_command']:
            raise Exception()
        data, files = self.validate_create(data=data, files=files)
        components = data['components']
        parent = None
        for each in components:
            types = []
            try:
                _sub_locality = AddressComponent.objects.get(name=each['ko'], parent=parent)
            except AddressComponent.DoesNotExist:

                _sub_locality, created = AddressComponent.objects.get_or_create(name=each['ko'],
                                                                                parent=parent,
                                                                                ascii_name=each['ascii'], depth=each['depth'])
            for each_type in each['types']:
                cur_type, created = AddressComponentType.objects.get_or_create(name=each_type)
                _sub_locality.types.add(cur_type)
            _sub_locality.save()
            parent = _sub_locality
        region_code = int_to_base36(parent.pk)
        parent = parent.parent
        while parent:
            region_code = int_to_base36(parent.pk) + ":" + region_code
            parent = parent.parent
        return self._meta.resource_instance_cls(region_code, self)

    def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
        keys = resource_instance._pk.split(':')
        components = []
        queryset = AddressComponent.objects

        for index in range(len(keys)):
            queryset = queryset.select_related('parent')
        component = queryset.get(pk=resource_instance._pk.split(":")[-1])
        _components = []
        while component.parent:
            _components.insert(0, component)
            component = component.parent
        _components.insert(0, component)
        for component in _components:
            components.append({'name': component.name, 'ascii': component.ascii_name, 'region_code': component.code,
                               'types': component.types})
        ret = {'components': components, 'formatted_name': ' '.join([x['name'] for x in components])}
        ret.update(resource_instance.all_virtual_items(exclude=exclude))
        return ret

    class Meta:
        cache_key_format = "_ut_region:%(pk)s"