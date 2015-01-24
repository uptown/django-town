from django_town.rest import RestDocumentApiView, RestQuerySetCollectionApiView
from django_town.social.resources.post import PostResource, CommentResource, PostLikeResource, PostDeleteAuthorized
from django_town.social.oauth2.permissions import OAuth2AuthenticatedOrReadOnly


class PostApiView(RestDocumentApiView):
    resource = PostResource(name='post')
    crud_method_names = ['read', 'delete']
    permission_classes = [OAuth2AuthenticatedOrReadOnly, PostDeleteAuthorized]

    def delete(self, request, pk):
        return super(PostApiView, self).delete(request, pk)


class PostsApiView(RestQuerySetCollectionApiView):
    resource = PostResource(name='post')
    crud_method_names = ['read', 'create']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]
    max_limit = 10

    def query_set(self, **kwargs):
        return self.resource._meta.document.objects.all().order_by('-created')


class PostCommentsApiView(RestQuerySetCollectionApiView):
    resource = CommentResource(name='comment')
    crud_method_names = ['read', 'create']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.document.objects(post=self.resource.pk_to_object_id(kwargs['pk'])). \
            order_by('-created')

    def create(self, request, **kwargs):
        request.POST['post'] = self.resource.pk_to_object_id(kwargs['pk'])
        ret = self.resource.create(data=request.POST, files=request.FILES, request=request).to_dict()
        return ret

    @classmethod
    def path(cls):
        return "post/{}/comments"


class PostLikesApiView(RestQuerySetCollectionApiView):
    resource = PostLikeResource()
    crud_method_names = ['read', 'create', 'delete']
    permission_classes = [OAuth2AuthenticatedOrReadOnly]

    def query_set(self, **kwargs):
        return self.resource._meta.document.objects(post=self.resource.pk_to_object_id(kwargs['pk'])). \
            order_by('-created')

    @classmethod
    def path(cls):
        return "post/{}/likes"