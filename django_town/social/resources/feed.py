from django_town.rest.resources import ModelResource, VirtualField, Resource, VirtualRequestField
from django_town.cache.utlis import SimpleCache
from django_town.social.models import Feed, FeedFollow, FeedOwner
from django_town.rest.exceptions import RestNotFound, RestForbidden
from django_town.social.resources.user import UserResource


def load_feed_follow_cache(**_kwargs):
    return {each[0]: 1 if each[1] else 0
            for each in FeedFollow.objects.filter(feed=_kwargs['pk']).values_list('pk', 'use_notification')}

feed_follows_cache = SimpleCache("_ut_feed_follows:%(pk)s", 60 * 60 * 24 * 15, load_feed_follow_cache)


class FeedResource(ModelResource):
    follower_count = VirtualField()
    following = VirtualRequestField()
    notification = VirtualRequestField()

    def post_create(self, resource_instance, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        data['owner'] = UserResource()(request.oauth2_user.pk)
        FeedOwner.objects.create(user_id=request.oauth2_user.pk, feed_id=resource_instance.pk)

    def invalidate_cache(self, pk):
        feed_follows_cache.delete(pk=pk)
        return super(FeedResource, self).invalidate_cache(pk)

    def field__follower_count(self, instance):
        return FeedFollow.objects.filter(feed_id=instance.pk).count()

    def field__following(self, instance, request):
        return request.oauth2_user.pk in feed_follows_cache.get(pk=instance.pk).keys()

    def field__notification(self, instance, request):
        data = feed_follows_cache.get(pk=instance.pk)
        if request.oauth2_user.pk in data:
            return data[request.oauth2_user.pk] == 1
        return False

    def post_delete(self, resource_instance):
        from django_town.social.documents.post import Post
        Post.objects.filter(feed=resource_instance).delete()
        pass

    class Meta:
        model = Feed
        cache_key_format = "_ut_feed:%(pk)s"
        cache_ignored_virtual_only = ['following', 'notification']
        fields = ['id', 'name', 'description', 'photo', 'site_url', 'category', 'following', 'notification', 'follower_count']


class FeedTokenResource(Resource):

    @classmethod
    def get(cls, feed_id, request):
        if feed_id and request.oauth2_user.pk:
            feed_owners = FeedOwner.objects.filter(feed_id=feed_id, user_id=request.oauth2_user.pk)
            for owner in feed_owners:
                if owner.user_id == request.oauth2_user.pk:
                    ret = Feed.objects.generate_feed_token(feed_id, request.oauth2_user.pk)
                    if ret:
                        return ret
        raise RestForbidden()


class FeedFollowResource(ModelResource):
    def create(self, **kwargs):
        FeedResource().invalidate_cache(pk=kwargs['data']['feed_id'])
        return super(FeedFollowResource, self).create(**kwargs)

    def delete(self, resource_instance):
        FeedResource().invalidate_cache(pk=resource_instance.feed.pk)
        return super(FeedFollowResource, self).delete(resource_instance)

    class Meta:
        model = FeedFollow
        fields = ['created', 'user.id', 'user.name', 'feed.id', 'feed.name']
        create_acceptable = ['user_id', 'feed_id', 'use_notification']


feed_public_resource = FeedResource()