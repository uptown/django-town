from django_town.rest.resources import ModelResource, VirtualField, VirtualRequestField
from django_town.cache.utlis import SimpleCache
from django_town.social.models import Page, PageOwner, PageLike, PageFeed


def load_page_like_cache(**_kwargs):
    return PageLike.objects.filter(page=_kwargs['pk']).values_list('pk', flat=True)

page_like_cache = SimpleCache("_ut_page_likes:%(pk)s", 60 * 60 * 24 * 15, load_page_like_cache)


def load_page_feeds_cache(**_kwargs):
    return PageFeed.objects.filter(page=_kwargs['pk']).values_list('feed', flat=True)

page_feeds_cache = SimpleCache("_ut_page_feeds:%(pk)s", 60 * 60 * 24 * 15, load_page_feeds_cache)


class PageResource(ModelResource):
    like_count = VirtualField()
    liked = VirtualRequestField()

    def post_create(self, resource_instance, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        # data['owner'] = UserResource()(request.oauth2_user.pk)
        PageOwner(user_id=request.oauth2_user.pk, page_id=resource_instance.pk).save()

    def invalidate_cache(self, **kwargs):
        page_like_cache.delete(**kwargs)
        return super(PageResource, self).invalidate_cache(**kwargs)

    def field__like_count(self, instance):
        return PageLike.objects.filter(page_id=instance.pk).count()

    def field__liked(self, instance, request):
        return request.oauth2_user.pk in page_like_cache.get(pk=instance.pk)

    class Meta:
        model = Page
        cache_key_format = "_ut_page:%(pk)s"
        cache_ignored_virtual_only = ['liked']
        fields = ['id', 'name', 'about', 'category', 'liked', 'like_count', 'photo']


class PageLikeResource(ModelResource):
    def create(self, **kwargs):
        PageResource().invalidate_cache(pk=kwargs['data']['page_id'])
        return super(PageLikeResource, self).create(**kwargs)

    def delete(self, resource_instance):
        PageResource().invalidate_cache(pk=resource_instance.post.pk)
        return super(PageLikeResource, self).delete(resource_instance)

    def post_create(self, resource_instance, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        PageResource().invalidate_cache(pk=data['page_id'])

    class Meta:
        model = PageLike
        fields = ['created', 'user.id', 'user.name', 'page.id', 'page.name', 'page.photo']
        create_acceptable = ['user_id', 'page_id', ]


class PageFeedResource(ModelResource):

    def delete(self, resource_instance):
        PageResource().invalidate_cache(pk=resource_instance.post.pk)
        return super(PageFeedResource, self).delete(resource_instance)

    def post_create(self, resource_instance, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        PageResource().invalidate_cache(pk=data['page_id'])

    class Meta:
        model = PageFeed
        fields = ['created', 'feed.id', 'feed.name', 'feed.photo', 'page.id', 'page.name']
        create_acceptable = ['feed_id', 'page_id', ]