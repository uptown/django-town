# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_town.social.models.user
import django.utils.timezone
import django_town.core.fields
import datetime
import django_town.social.models.feed


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('email', django_town.core.fields._EmailField(max_length=75, unique=True)),
                ('name', models.CharField(max_length=60)),
                ('dob', models.DateField(null=True, blank=True)),
                ('photo', django_town.core.fields.ImageThumbsField(upload_to=django_town.social.models.user.User.upload_to, null=True, default=None, blank=True)),
                ('locale', models.CharField(default='en', max_length=4)),
                ('gender', models.CharField(default='U', max_length=1, db_index=True)),
                ('bio', models.TextField(default='', blank=True)),
                ('timezone_offset', models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)),
                ('email_tbd', models.CharField(default='', blank=True, max_length=75)),
                ('is_super', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AddressComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('code', models.CharField(default=0, max_length=40, unique=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('ser_no', models.SmallIntegerField(default=0, db_index=True)),
                ('ascii_name', models.CharField(max_length=200)),
                ('type', models.SmallIntegerField(choices=[(0, 'country'), (1, 'locality'), (2, 'sublocality')])),
                ('children_count', models.SmallIntegerField(default=0)),
                ('parent', models.ForeignKey(null=True, default=None, to='social.AddressComponent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplePushNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(default=0)),
                ('client_id', models.IntegerField(default=0)),
                ('device_token', models.CharField(max_length=256)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('state', models.IntegerField(choices=[('N', 'New'), ('P', 'Pending')], default=0, max_length=1, db_index=True)),
                ('message', models.CharField(max_length=100)),
                ('additional_info', models.CharField(max_length=500)),
                ('badge_count', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ('-id',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('system_type', models.SmallIntegerField(choices=[(0, 'iOS'), (1, 'Android')], default=0)),
                ('device_identifier', models.CharField(max_length=130)),
                ('device_version', models.CharField(default='', blank=True, max_length=10)),
                ('model', models.CharField(default='', blank=True, max_length=20)),
                ('system_version', models.CharField(default='', blank=True, max_length=20)),
                ('device_token', models.CharField(null=True, default=None, blank=True, max_length=255, unique=True)),
                ('client', models.ForeignKey(to='oauth2.Client')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60, db_index=True)),
                ('description', models.TextField(default='')),
                ('category', models.SmallIntegerField(default=0)),
                ('photo', django_town.core.fields.ImageThumbsField(upload_to='image/feed/', null=True, default=None, blank=True)),
                ('site_url', models.URLField(default='')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('locale', models.CharField(default='ko-KR', max_length=6)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedFollow',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('use_notification', models.BooleanField(default=False, db_index=True)),
                ('count', models.SmallIntegerField(default=1)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('feed', models.ForeignKey(to='social.Feed')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('role', models.SmallIntegerField(choices=[(0, 'Owner'), (1, 'Admin'), (2, 'Manager')], default=0)),
                ('feed', models.ForeignKey(to='social.Feed')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedSecretKey',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('secret_key', models.CharField(default=django_town.social.models.feed._feed_rand_key, max_length=10)),
                ('feed', models.ForeignKey(to='social.Feed', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60, db_index=True)),
                ('about', models.TextField(default='')),
                ('category', models.SmallIntegerField(default=0)),
                ('can_post', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('photo', django_town.core.fields.ImageThumbsField(upload_to='image/page/', null=True, default=None, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('feed', models.ForeignKey(to='social.Feed')),
                ('page', models.ForeignKey(to='social.Page')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageLike',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('page', models.ForeignKey(to='social.Page')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('role', models.SmallIntegerField(choices=[(0, 'Owner'), (1, 'Admin'), (2, 'Manager')], default=0)),
                ('page', models.ForeignKey(to='social.Page')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60, db_index=True)),
                ('about', models.TextField(default='')),
                ('category', models.SmallIntegerField(default=0)),
                ('url', models.URLField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserEmailVerify',
            fields=[
                ('user', models.ForeignKey(to='social.User', primary_key=True, serialize=False)),
                ('token', models.CharField(default='ouGglqEsuWjdgFP189Zepd8NxjRJEWZU4fYx2GEf8biLIOq8hdCSSnJXr7O4xeLZ', max_length=64, db_index=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserFacebook',
            fields=[
                ('user', models.ForeignKey(to='social.User', primary_key=True, serialize=False)),
                ('facebook_id', models.BigIntegerField(default=0, unique=True)),
                ('access_token', models.CharField(default='', max_length=400)),
                ('is_show', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserGoogle',
            fields=[
                ('user', models.ForeignKey(to='social.User', primary_key=True, serialize=False)),
                ('email', models.EmailField(default='', max_length=75, unique=True)),
                ('google_id', models.DecimalField(max_digits=22, decimal_places=0, default=0, db_index=True)),
                ('is_show', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserPasswordReset',
            fields=[
                ('user', models.ForeignKey(to='social.User', primary_key=True, serialize=False)),
                ('token', models.CharField(default='fVyrhIlBuzN32yrLsyjTlb5IC3lUCUMgHRlC5UBE8NT1e83u1JNbUTx6Pxfm8slG', max_length=64, db_index=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pageowner',
            name='user',
            field=models.ForeignKey(to='social.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pagelike',
            name='user',
            field=models.ForeignKey(to='social.User'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='pagelike',
            unique_together=set([('user', 'page')]),
        ),
        migrations.AddField(
            model_name='feedowner',
            name='user',
            field=models.ForeignKey(to='social.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feedfollow',
            name='user',
            field=models.ForeignKey(to='social.User'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='feedfollow',
            unique_together=set([('user', 'feed')]),
        ),
        migrations.AddField(
            model_name='device',
            name='user',
            field=models.ForeignKey(null=True, default=None, to='social.User', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set([('client', 'device_identifier')]),
        ),
        migrations.AlterUniqueTogether(
            name='addresscomponent',
            unique_together=set([('parent', 'name')]),
        ),
    ]
