from django_town.rest import RestDocumentApiView, RestQuerySetCollectionApiView
from django_town.social.resources.page import PageResource, PageLikeResource, PageFeedResource, page_feeds_cache
from django_town.social.resources.post import PostResource
from django_town.social.oauth2.permissions import OAuth2AuthenticatedOrReadOnly


class PageApiView(RestDocumentApiView):
    resource = PageResource(name='page')
    crud_method_names = ['read']


class PagesApiView(RestQuerySetCollectionApiView):
    resource = PageResource(name='page')
    crud_method_names = ['read', 'create']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.model.objects.all().order_by('-created')


class PagePostsApiView(RestQuerySetCollectionApiView):
    resource = PostResource(name='post')
    crud_method_names = ['read', 'create']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.document.objects(_to__in=page_feeds_cache.get(pk=kwargs['pk'])).\
            order_by('-created')

    @classmethod
    def path(cls):
        return "pages/{}/posts"


class PageLikesApiView(RestQuerySetCollectionApiView):
    resource = PageLikeResource(filter=["-page"])
    crud_method_names = ['read', 'create', 'delete']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.model.objects.filter(page=kwargs['pk']). \
            order_by('-created')

    def create(self, request, **kwargs):
        ret = self.resource.create(data={'user_id': request.oauth2_user.pk,
                                         'page_id': kwargs['pk']}).to_dict()
        PageResource().invalidate_cache(pk=kwargs['pk'])
        return ret

    @classmethod
    def path(cls):
        return "pages/{}/likes"


class PageFeedsApiView(RestQuerySetCollectionApiView):
    resource = PageFeedResource(filter=["-page"])
    crud_method_names = ['read', 'create', 'delete']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.model.objects.filter(page=kwargs['pk']). \
            order_by('feed')

    def pre_create(self, data, request, **kwargs):
        data['page_id'] = kwargs['pk']
        return data


    def create(self, request, **kwargs):
        ret = self.resource.create(data={'feed_id': request.oauth2_user.pk,
                                         'page_id': kwargs['pk']}).to_dict()
        PageResource().invalidate_cache(pk=kwargs['pk'])
        return ret

    @classmethod
    def path(cls):
        return "pages/{}/feeds"

