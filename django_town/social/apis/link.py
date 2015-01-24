from django_town.rest import RestDocumentApiView, RestQuerySetCollectionApiView
from django_town.social.resources.link import LinkResource
from django_town.social.oauth2.permissions import OAuth2AuthenticatedOrReadOnly


class LinkApiView(RestDocumentApiView):
    resource = LinkResource(name='link')
    crud_method_names = ['read']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]


class LinksApiView(RestQuerySetCollectionApiView):
    resource = LinkResource(name='link')
    crud_method_names = ['read', 'create']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]
    max_limit = 10

    def query_set(self, **kwargs):
        return self.resource._meta.document.objects.all().order_by('-created')


class LinksSearchApiView(RestQuerySetCollectionApiView):
    resource = LinkResource(name='link')
    crud_method_names = ['read']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]
    max_limit = 10

    def query_set(self, parameters=None, **kwargs):
        return self.resource._meta.document.objects.filter(keywords__istartswith=parameters.get('q')).order_by('-created')

    @classmethod
    def path(cls):
        return super(LinksSearchApiView, cls).path() + '/search'