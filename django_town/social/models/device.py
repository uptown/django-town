from django.db import models
from django_town.social.models.user import User
from django_town.social.resources.oauth2 import Client


class Device(models.Model):

    IOS_TYPE = 0
    ANDROID_TYPE = 1


    SYSTEM_TYPE = (
        (IOS_TYPE, 'iOS'),
        (ANDROID_TYPE, 'Android')
    )


    user = models.ForeignKey(User, default=None, blank=True, null=True)
    system_type = models.SmallIntegerField(default=0, choices=SYSTEM_TYPE)
    client = models.ForeignKey(Client, blank=False, null=False)
    device_identifier = models.CharField(max_length=130)
    device_version = models.CharField(max_length=10, blank=True, default="")
    model = models.CharField(max_length=20, blank=True, default="")
    system_version = models.CharField(max_length=20, blank=True, default="")
    device_token = models.CharField(max_length=255, blank=True, default=None, null=True, unique=True)

    class Meta:
        unique_together = (("client", "device_identifier"),)
        app_label = 'social'


class ApplePushNotification(models.Model):

    NEW = 0
    PENDING = 1
    DONE = 2
    ERROR = 3

    PUSH_STATE = (
        ('N', "New"),
        ('P', "Pending"),
    )

    # user = models.ForeignKey(User)
    # client = models.ForeignKey(Client)
    user_id = models.IntegerField(default=0)
    client_id = models.IntegerField(default=0)
    device_token = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now=True)
    state = models.IntegerField(max_length=1, choices=PUSH_STATE, db_index=True, default=NEW)
    message = models.CharField(max_length=100)
    additional_info = models.CharField(max_length=500)
    badge_count = models.IntegerField(default=1)
    # result_text = models.CharField(max_length=256)

    class Meta:
        ordering = ('-id',)
        app_label = 'social'
