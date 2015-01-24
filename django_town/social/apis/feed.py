from django_town.rest import RestDocumentApiView, RestQuerySetCollectionApiView, RestApiView
from django_town.social.models.feed import FeedTokenAuthenticated
from django_town.social.resources.feed import FeedResource, FeedFollowResource, FeedTokenResource, feed_public_resource
from django_town.social.resources.post import PostResource
from django_town.social.resources.user import user_public_resource
from django_town.social.oauth2.permissions import OAuth2AuthenticatedOrReadOnly


class FeedApiView(RestDocumentApiView):
    resource = FeedResource(name='feed')
    crud_method_names = ['read', 'delete']


class FeedTokenApiView(RestApiView):

    def read(self, request,  *args, **kwargs):
        return {'feed_token': FeedTokenResource.get(kwargs['pk'], request)}

    @classmethod
    def path(cls):
        return "feed/{}/token"


class FeedsApiView(RestQuerySetCollectionApiView):
    resource = FeedResource(name='feed')
    crud_method_names = ['read', 'create']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.model.objects.all().order_by('-created')


class FeedPostsApiView(RestQuerySetCollectionApiView):
    resource = PostResource(name='post', filter=['-feed'])
    crud_method_names = ['read', 'create']
    permission_classes = [FeedTokenAuthenticated]

    def query_set(self, **kwargs):
        return self.resource._meta.document.objects.filter(feed=int(kwargs['pk'])).order_by('-created')

    def pre_create(self, data, request, **kwargs):
        data['feed'] = feed_public_resource(kwargs['pk'])
        return data

    @classmethod
    def path(cls):
        return "feed/{}/posts"


class FeedFollowersApiView(RestQuerySetCollectionApiView):
    resource = FeedFollowResource(filter=["-feed"])
    crud_method_names = ['read', 'create', 'delete']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.model.objects.filter(feed=kwargs['pk']). \
            order_by('-created')

    def create(self, request, **kwargs):
        ret = self.resource.create(data={'user_id': request.oauth2_user.pk,
                                         'feed_id': kwargs['pk']}).to_dict()
        feed_public_resource.invalidate_cache(pk=kwargs['pk'])
        return ret

    @classmethod
    def path(cls):
        return "feed/{}/followers"