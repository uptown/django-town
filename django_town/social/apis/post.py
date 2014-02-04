from django_town.rest import RestDocumentApiView, RestCollectionApiView
from django_town.social.resources.post import PostResource


class PostApiView(RestDocumentApiView):

    resource = PostResource(name='post')
    crud_method_names = ['read']


class PostsApiView(RestCollectionApiView):

    resource = PostResource(name='post')
    crud_method_names = ['read', 'create']
