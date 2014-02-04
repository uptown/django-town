from django_town.rest.resources import Resource
from django_town.social.models.geo import AddressComponent, ADDRESS_COMPONENT_TYPES
from django.utils.http import int_to_base36, base36_to_int


class RegionResource(Resource):
    cache_key_format = "_ut_region:%(pk)s"

    def create(self, data=None, files=None):
        if not data['from_command']:
            raise Exception()
        data, files = self.validate_create(data=data, files=files)
        country = data['country']
        locality = data['locality']
        sub_localities = data['sub_localities']
        _country, unused = AddressComponent.objects.get_or_create(name=country['ko'], ascii_name=country['en'], type=0)
        try:
            _locality = AddressComponent.objects.get(name=locality['ko'], parent=_country, type=1)
            created = False
        except AddressComponent.DoesNotExist:
            code = int_to_base36(_country.ser_no) + '-' + int_to_base36(_country.children_count)
            _locality, created = AddressComponent.objects.get_or_create(name=locality['ko'], ascii_name=locality['en'],
                                                                        parent=_country, type=1,
                                                                        ser_no=_country.children_count,
                                                                        code=code)

        if created:
            _country.children_count += 1
            _country.save()
        parent = _locality
        _sub_localities = []
        current_code = parent.code
        for each in sub_localities:
            try:
                _sub_locality = AddressComponent.objects.get(name=each['ko'], parent=parent, type=2)
                created = False
            except AddressComponent.DoesNotExist:
                new_code = current_code + '-' + int_to_base36(parent.children_count)
                _sub_locality, created = AddressComponent.objects.get_or_create(name=each['ko'], ascii_name=each['en'],
                                                                                parent=parent, type=2,
                                                                                ser_no=parent.children_count,
                                                                                code=new_code)
            if created:
                parent.children_count += 1
                parent.save()
            _sub_localities.append(_sub_locality)
            parent = _sub_locality
            current_code = parent.code
        # pk = int_to_base36(_country.pk) + '-' + int_to_base36(_locality.ser_no) + '-' + \
        #      "-".join([int_to_base36(x.ser_no) for x in _sub_localities])
        return self.resource_instance_cls(parent.code, self)

    def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
        keys = resource_instance._pk.split('-')
        components = []
        queryset = AddressComponent.objects

        for index in range(len(keys)):
            queryset = queryset.select_related('parent')
        component = queryset.get(code=resource_instance._pk)
        _components = []
        while component.parent:
            _components.insert(0, component)
            component = component.parent
        _components.insert(0, component)
        for component in _components:
            components.append({'name': component.name, 'ascii': component.ascii_name, 'region_code': component.code,
                               'type': ADDRESS_COMPONENT_TYPES[component.type][1]})
        ret = {'components': components, 'formatted_name': ' '.join([x['name'] for x in components])}
        ret.update(resource_instance.all_virtual_items(exclude=exclude))
        return ret