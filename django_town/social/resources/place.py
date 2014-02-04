from django_town.rest.resources import MongoResource
from django_town.social.documents import Place


class PlaceResource(MongoResource):
    document = Place
    cache_key_format = "_ut_place:%(pk)s"
    create_required = ['name']

    def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
        ret = super(PlaceResource, self).instance_to_python(resource_instance, fields=fields, exclude=exclude, **kwargs)
        if 'address' in ret:
            address_dict = ret['address']
            # ret['address'] = {'components': address_dict['region']['components'],
            #                   'formatted_name': address_dict['region']['formatted_name'] + ' '
            #                                     + " ".join([x for x in address_dict['remains']])}
            ret['address'] = address_dict['region']['formatted_name'] + ' ' + \
                             " ".join([x for x in address_dict['remains']])
        return ret