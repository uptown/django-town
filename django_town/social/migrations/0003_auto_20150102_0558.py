# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0002_auto_20150101_0450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremailverify',
            name='token',
            field=models.CharField(max_length=64, db_index=True, default='ack8lIqzSYKW5nGOZoqDYjgABNsaRtRkaMrNyauRG7lMA8BpAmz76rtLuLjZA7a8'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userpasswordreset',
            name='token',
            field=models.CharField(max_length=64, db_index=True, default='KY4oNnrSfmBr10MLzOfkamAswB5sjdFDhgHqR56f3j34kpQfV9Qu5i7KcqvNyHbl'),
            preserve_default=True,
        ),
    ]
