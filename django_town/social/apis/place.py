from django_town.rest import RestDocumentApiView, RestQuerySetCollectionApiView
from django_town.social.resources.place import PlaceResource
from django_town.social.define.place_categories import PLACE_CATEGORIES


class PlaceApiView(RestDocumentApiView):
    resource = PlaceResource(name='place')
    crud_method_names = ['read']


class PlacesApiView(RestQuerySetCollectionApiView):
    resource = PlaceResource(name='place')
    crud_method_names = ['read', 'create']
    max_limit = 10
    extra_parameters = ['center', 'type']

    def query_set(self, parameters=None, **kwargs):
        center = parameters.get('center')
        types = parameters.get('type')
        object_filter = {}
        if center:
            point = center.split(',')
            object_filter['location__near'] = [float(point[1]), float(point[0])]
            object_filter['location__max_distance'] = 1000
        if types:
            types = types.split(',')
            object_filter['type__in'] = [k for k, v in PLACE_CATEGORIES if v in types]
        return self.resource._meta.document.objects(**object_filter)
