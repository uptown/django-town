from django.db import models
from django.utils import timezone

from django_town.social.models.user import User
from django_town.social.models.feed import Feed
from django_town.social.define import PAGE_ROLE
from django_town.core.fields import ImageThumbsField


class Page(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    about = models.TextField(default="")
    category = models.SmallIntegerField(default=0)
    can_post = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    photo = ImageThumbsField(upload_to='image/page/', default=None, null=True, blank=True, sizes=((300,300),))

    class Meta:
        app_label = 'social'


class PageFeed(models.Model):
    page = models.ForeignKey(Page)
    feed = models.ForeignKey(Feed)

    class Meta:
        app_label = 'social'


class PageOwner(models.Model):
    user = models.ForeignKey(User)
    page = models.ForeignKey(Page)
    role = models.SmallIntegerField(default=0, choices=PAGE_ROLE)

    class Meta:
        app_label = 'social'


class PageLike(models.Model):
    user = models.ForeignKey(User)
    page = models.ForeignKey(Page)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'social'
        unique_together = ('user', 'page')