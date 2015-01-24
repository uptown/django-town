from django_town.rest import RestFormInvalid
from django_town.rest.resources import MongoResource
from django_town.social.documents import Place, Address, AdministrativeArea
from django_town.social.resources.region import RegionResource
from django_town.utils.with3 import urlopen
import json


class PlaceResource(MongoResource):
    def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
        ret = super(PlaceResource, self).instance_to_python(resource_instance, fields=fields, exclude=exclude, **kwargs)
        if 'address' in ret:
            address_dict = ret['address']
            # ret['address'] = {'components': address_dict['region']['components'],
            # 'formatted_name': address_dict['region']['formatted_name'] + ' '
            # + " ".join([x for x in address_dict['remains']])}
            ret['address'] = address_dict['region']['formatted_name'] + ' ' + \
                             " ".join([x for x in address_dict['remains']])
        return ret


    class Meta:
        document = Place
        cache_key_format = "_ut_place:%(pk)s"
        create_required = ['name']


class AdministrativeAreaResource(MongoResource):


    @staticmethod
    def get_google_reverse_code(lat, lng):
        GOOGLE_REVERSE_GEOCODE = "http://maps.googleapis.com/maps/api/geocode/json?latlng=%s&sensor=false&language=ko"
        GOOGLE_REVERSE_GEOCODE_EN = "http://maps.googleapis.com/maps/api/geocode/json?latlng=%s&sensor=false&language=en"
        geocode_query = GOOGLE_REVERSE_GEOCODE % (str(lat) + ',' + str(lng))
        geocode_query_en = GOOGLE_REVERSE_GEOCODE_EN % (str(lat) + ',' + str(lng))
        # print geocode_query
        ret = urlopen(geocode_query).read()
        geocode_data = {}


        for geocode_data_ko in json.loads(ret.decode('utf8'))['results']:
            new_lat, new_lng = geocode_data_ko['geometry']['location']['lat'], geocode_data_ko['geometry']['location']['lng']
            cur_key = str(new_lat) + ',' + str(new_lng)

            current_geocode_data = geocode_data.get(cur_key, {'components': [],
                                                              'lat': new_lat, 'lng': new_lng})

            # current_geocode_data['locality']['original'] = original_address_component[0]
            # for sub in original_address_component[1:-1]:
            # current_geocode_data['sub_localities'].append({'original': sub})
            current_geocode_data['formatted_address'] = geocode_data_ko['formatted_address']
            geocode_data_ko['address_components'].reverse()
            sub_locality_idx = 0
            for each_data in geocode_data_ko['address_components']:
                com_types = each_data['types']
                if 'post_box' in com_types or 'floor' in com_types or 'room' in com_types or 'street_number' in com_types:
                    continue
                elif 'postal_code' in com_types:
                    current_geocode_data['postal_code'] = each_data['long_name']
                else:
                    try:
                        current_geocode_data['components'][sub_locality_idx]
                    except IndexError:
                        current_geocode_data['components'].append({})

                    current_geocode_data['components'][sub_locality_idx]['ko'] = each_data['long_name']
                    current_geocode_data['components'][sub_locality_idx]['types'] = each_data['types']
                    current_geocode_data['components'][sub_locality_idx]['depth'] = sub_locality_idx
                    sub_locality_idx += 1
            current_geocode_data['bounds'] = geocode_data_ko['geometry'].get('bounds')
            current_geocode_data['level'] = sub_locality_idx - 1
            geocode_data[cur_key] = current_geocode_data


        ret = urlopen(geocode_query_en).read()
        for geocode_data_en in json.loads(ret.decode('utf8'))['results']:
            new_lat, new_lng = geocode_data_en['geometry']['location']['lat'], geocode_data_en['geometry']['location']['lng']
            cur_key = str(new_lat) + ',' + str(new_lng)


            current_geocode_data = geocode_data.get(cur_key, {'components': [], 'lat': new_lat, 'lng': new_lng})

            current_geocode_data['formatted_address_ascii'] = geocode_data_en['formatted_address']
            geocode_data_en['address_components'].reverse()
            sub_locality_idx = 0
            for each_data in geocode_data_en['address_components']:
                com_types = each_data['types']
                if 'post_box' in com_types or 'floor' in com_types or 'room' in com_types or 'street_number' in com_types:
                    continue
                elif 'postal_code' in com_types:
                    current_geocode_data['postal_code'] = each_data['long_name']
                else:
                    try:
                        current_geocode_data['components'][sub_locality_idx]
                    except IndexError:
                        current_geocode_data['components'].append({})

                    current_geocode_data['components'][sub_locality_idx]['ascii'] = each_data['long_name']
                    current_geocode_data['components'][sub_locality_idx]['types'] = each_data['types']
                    current_geocode_data['components'][sub_locality_idx]['depth'] = sub_locality_idx
                    sub_locality_idx += 1
            current_geocode_data['from_command'] = True
            current_geocode_data['bounds'] = geocode_data_en['geometry'].get('bounds')
            current_geocode_data['level'] = sub_locality_idx - 1
            geocode_data[cur_key] = current_geocode_data
        # print(geocode_data)
        for each in geocode_data:
            current_geocode_data = geocode_data[each]
            region = RegionResource().create(data=current_geocode_data)
            address = Address(region=region, postal_code=current_geocode_data.get('postal_code', None))
            yield address, current_geocode_data['formatted_address'], current_geocode_data['lat'], current_geocode_data['lng'], current_geocode_data['level'], current_geocode_data['bounds']

    def pre_create(self, data, files, acceptable, required, exclude, request, request_kwargs, or_get):

        data['type'] = 'locality'
        data['verified'] = True
        return data, None

    class Meta:
        document = AdministrativeArea
        cache_key_format = "_ut_ad_area:%(pk)s"
        create_required = ['location']



