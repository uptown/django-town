from django_town.rest import RestDocumentApiView, RestCollectionApiView
from django_town.social.resources.place import PlaceResource


class PlaceApiView(RestDocumentApiView):

    resource = PlaceResource(name='place')
    crud_method_names = ['read']


class PlacesApiView(RestCollectionApiView):

    resource = PlaceResource(name='place')
    crud_method_names = ['read', 'create']

