# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userclientsecretkey',
            name='user_id',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
