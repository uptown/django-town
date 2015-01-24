# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_town.core.fields
import django_town.oauth2.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('client_id', models.CharField(max_length=30, default=django_town.oauth2.models._generate_random_from_vschar_set_for_client_id, unique=True)),
                ('client_secret', models.CharField(max_length=30, default=django_town.oauth2.models._generate_random_from_vschar_set_for_client_secret)),
                ('redirect_uris', django_town.core.fields.JSONField(blank=True, default='{}')),
                ('default_redirect_uri', models.URLField()),
                ('available_scope', django_town.core.fields.JSONField(blank=True, default='{}')),
                ('client_type', models.IntegerField(choices=[(0, 'Web'), (1, 'iOS'), (2, 'Android'), (3, 'Win')], default=1)),
                ('client_min_version', models.CharField(max_length=20, default='')),
                ('client_cur_version', models.CharField(max_length=20, default='')),
                ('client_store_id', models.CharField(max_length=30, default='')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserClientSecretKey',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('secret_key', models.CharField(max_length=5, default=django_town.oauth2.models._generate_random_from_vschar_set_for_secret_key)),
                ('client', models.ForeignKey(to='oauth2.Client')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='client',
            name='service',
            field=models.ForeignKey(to='oauth2.Service'),
            preserve_default=True,
        ),
    ]
