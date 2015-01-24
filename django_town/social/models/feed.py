from django.db import models
from django.utils import timezone

from django.utils.http import int_to_base36, base36_to_int
from django_town.utils import generate_random_from_vschar_set, encrypt_cbc, decrypt_cbc
from django_town.rest.exceptions import RestUnauthorized
from django_town.social.models.user import User
from django_town.social.define import PAGE_ROLE
from django_town.core.settings import SOCIAL_SETTINGS
from django_town.social.permissions import BasePermission
from django_town.core.fields import ImageThumbsField


class FeedManager(models.Manager):

    @classmethod
    def generate_feed_token(cls, feed_pk, user_pk):
        user_secret_key, created_unused = FeedSecretKey.objects.get_or_create(feed_id=feed_pk)

        secret_key = user_secret_key.secret_key.encode('utf-8')
        checksum = generate_random_from_vschar_set(length=10)

        return encrypt_cbc(int_to_base36(int(feed_pk)) + "." + int_to_base36(int(user_pk)) + '.'
                           + '.' + checksum,
                           SOCIAL_SETTINGS.FEED_TOKEN_SECRET_KEY) + '.' + encrypt_cbc(checksum, secret_key)


    @classmethod
    def is_feed_available(cls, feed_pk, feed_token):
        if not feed_token:
            return False
        part = feed_token.split('.')
        if len(part) != 2:
            return False

        info, check = part
        part = decrypt_cbc(info, SOCIAL_SETTINGS.FEED_TOKEN_SECRET_KEY).split('.')

        if len(part) != 4:
            return False

        feed_token_pk, user_pk, checksum = base36_to_int(part[0]), base36_to_int(part[1]), part[3]
        #TODO cache...
        secret_key = FeedSecretKey.objects.get_or_create(feed_id=feed_pk)[0].secret_key.encode('utf-8')
        if checksum != decrypt_cbc(check, secret_key):
            return False

        return int(feed_pk) == int(feed_token_pk)


class Feed(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    description = models.TextField(default="")
    category = models.SmallIntegerField(default=0)
    photo = ImageThumbsField(upload_to='image/feed/', default=None, null=True, blank=True, sizes=((300,300),))
    site_url = models.URLField(default='')
    created = models.DateTimeField(default=timezone.now)
    locale = models.CharField(max_length=6, default='ko-KR')

    objects = FeedManager()

    class Meta:
        app_label = 'social'


def _feed_rand_key():
    return generate_random_from_vschar_set(10)


class FeedSecretKey(models.Model):

    feed = models.ForeignKey(Feed, unique=True)
    secret_key = models.CharField(max_length=10, default=_feed_rand_key)

    class Meta:
        app_label = 'social'

class FeedTokenAuthenticated(BasePermission):
    """
    The request contains a valid feed token if it is for post or read-only.
    """
    def check_permission(self, request, *args, **kwargs):
        if request.method == 'GET':
            return
        if request.method == 'POST' and 'token' in request.POST and 'pk' in kwargs:
            token = request.POST['token']
            feed_id = kwargs['pk']
            if Feed.objects.is_feed_available(feed_id, token):
                return
        raise RestUnauthorized()


class FeedOwner(models.Model):
    user = models.ForeignKey(User)
    feed = models.ForeignKey(Feed)
    role = models.SmallIntegerField(default=0, choices=PAGE_ROLE)

    class Meta:
        app_label = 'social'


class FeedFollow(models.Model):
    user = models.ForeignKey(User)
    feed = models.ForeignKey(Feed)
    use_notification = models.BooleanField(default=False, db_index=True)
    count = models.SmallIntegerField(default=1)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'social'
        unique_together = ('user', 'feed')
