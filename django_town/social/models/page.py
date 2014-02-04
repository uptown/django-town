from django.db import models
from django.utils import timezone
from django_town.social.models.user import User


class Page(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    about = models.TextField(default="")
    owner = models.ForeignKey(User, default=None, null=True)


    can_post = models.BooleanField(default=False)

    created = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'social'

