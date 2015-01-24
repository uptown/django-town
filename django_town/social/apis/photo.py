from django_town.rest import RestDocumentApiView, RestQuerySetCollectionApiView
from django_town.social.resources.photo import PhotoResource
from django_town.social.oauth2.permissions import OAuth2AuthenticatedOrReadOnly


class PhotoApiView(RestDocumentApiView):
    resource = PhotoResource(name='photo')
    crud_method_names = ['read']


class PhotosApiView(RestQuerySetCollectionApiView):
    resource = PhotoResource(name='photo')
    crud_method_names = ['read', 'create']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.document.objects.all().order_by('-created')