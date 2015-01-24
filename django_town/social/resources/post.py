from django_town.utils import json
from django_town.rest.resources import MongoResource, VirtualField, VirtualRequestField, resource_cache_manager
from django_town.social.documents import Post, Comment, PostLike
from django_town.cache.utlis import SimpleCache
from django_town.social.resources.user import user_public_resource
from django_town.social.resources.link import link_public_resource
from django_town.rest.permissions import BasePermission, RestUnauthorized


class PostDeleteAuthorized(BasePermission):
    """
    If request is delete, check authorized user is matched with post's author.
    """
    def check_permission(self, request, *args, **kwargs):
        if request.method == "DELETE":
            if request.oauth2_user.pk == PostResource()(kwargs['pk'])._from.pk:
                return
            raise RestUnauthorized()


def load_cache(**_kwargs):
    ret = {'user': [], 'page': []}
    for each in PostLike.objects(post=_kwargs['pk']):
        ret[each._from._manager._meta.name].append(each._from.pk)
    return ret


post_like_cache = SimpleCache("_ut_post_likes:%(pk)s", 60 * 60 * 24 * 15, load_cache)


class PostResource(MongoResource):
    comment_count = VirtualField()
    like_count = VirtualField()
    liked = VirtualRequestField()

    def pre_create(self, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        if request.oauth2_user.pk:
            data['from'] = user_public_resource(request.oauth2_user.pk)
        data['client'] = request.oauth2_authorization_info.client_pk
        if 'link' in data:
            link_data = data['link']
            if link_data[0] == '{':
                link_data = json.loads(link_data)
            else:
                link_data = {'url': link_data}
            data['link'] = link_public_resource.create(link_data)
        return data, files

    def invalidate_cache(self, **kwargs):
        post_like_cache.delete(**kwargs)
        return super(PostResource, self).invalidate_cache(**kwargs)

    def field__comment_count(self, instance):
        return Comment.objects(post_id=instance.pk).count()

    def field__like_count(self, instance):
        return PostLike.objects(post_id=instance.pk).count()

    def field__liked(self, instance, request):
        return request.oauth2_user.pk in post_like_cache.get(pk=instance.pk).get('user', [])

    class Meta:
        document = Post
        cache_key_format = "_ut_post:%(pk)s"
        create_acceptable = ['content', 'feed', 'created', 'link']
        exclude = ['is_hidden']
        cache_ignored_virtual_only = ['liked']
        filter = ['-client']


class CommentResource(MongoResource):
    def pre_create(self, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        data['from'] = user_public_resource(request.oauth2_user.pk)
        data['client'] = request.oauth2_authorization_info.client_pk
        return data, files

    def post_create(self, resource_instance, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        PostResource().invalidate_cache(pk=self.object_id_to_pk(data['post'].pk))

    class Meta:
        document = Comment
        cache_key_format = "_ut_cmt:%(pk)s"
        exclude = ['client']
        create_acceptable = ['post', 'content']


class PostLikeResource(MongoResource):

    def delete(self, resource_instance):
        PostResource().invalidate_cache(pk=resource_instance.post.pk)
        return super(PostLikeResource, self).delete(resource_instance)

    class Meta:
        document = PostLike
        exclude = ['post']
        create_acceptable = ['from', 'post', ]

    def pre_create(self, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        data['from'] = user_public_resource(request.oauth2_user.pk)
        data['post'] = self.pk_to_object_id(request_kwargs['pk'])
        return data, files

    def post_create(self, resource_instance, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        PostResource().invalidate_cache(pk=request_kwargs['pk'])


resource_cache_manager.register("PostLikeResource", "PostResource", {"post_id": "pk"})
