import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_town.core.fields import ImageThumbsField

from django_town.core.fields import _EmailField, RandomNameUploadTo


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        user = self.model(email=email)
        if password:
            user.set_password(password)
        user.is_verified = False
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email)
        user.set_password(password)
        user.is_super = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser):

    def upload_to(self, name):
        return RandomNameUploadTo('image/user/')(self, name)

    email = _EmailField(unique=True)
    name = models.CharField(max_length=60)
    dob = models.DateField(null=True, blank=True)
    photo = ImageThumbsField(upload_to=upload_to, default=None, null=True, blank=True, sizes=((300,300),))
    locale = models.CharField(max_length=4, default="en", blank=False)
    gender = models.CharField(max_length=1, default='U', db_index=True)
    bio = models.TextField(blank=True, default="")
    timezone_offset = models.DecimalField(null=True, blank=True, max_digits=3, decimal_places=1)
    email_tbd = models.CharField(max_length=75, blank=True, default="")
    is_super = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    date_joined = models.DateTimeField(_('last login'), default=timezone.now)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return self.is_super

    def has_module_perms(self, app_label):
        return self.is_super

    def get_short_name(self):
        return self.name

    def get_username(self):
        return self.email

    class Meta:
        app_label = 'social'


class UserFacebook(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    facebook_id = models.BigIntegerField(default=0, unique=True)
    access_token = models.CharField(max_length=400, default="")
    is_show = models.BooleanField(default=True)

    class Meta:
        app_label = 'social'


class UserGoogle(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    email = models.EmailField(default='', unique=True)
    google_id = models.DecimalField(default=0, max_digits=22, decimal_places=0, db_index=True)
    is_show = models.BooleanField(default=True)

    class Meta:
        app_label = 'social'


class UserEmailVerify(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    token = models.CharField(max_length=64, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, default=datetime.datetime.now)
    email = models.EmailField(max_length=254)

    class Meta:
        app_label = 'social'


class UserPasswordReset(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    token = models.CharField(max_length=64, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, default=datetime.datetime.now)

    class Meta:
        app_label = 'social'

