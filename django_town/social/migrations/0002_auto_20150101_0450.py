# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremailverify',
            name='token',
            field=models.CharField(db_index=True, max_length=64, default='GRQJKweSC42CXO2Yb1bRw5cCERYPRZFY5tTTGWfjcPH6M4xRjEQuSvIFgNt2sxG5'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userpasswordreset',
            name='token',
            field=models.CharField(db_index=True, max_length=64, default='0yhdYUpnD89l5oAVsPdQt9ApeqZ49yzTuPmQadA9MabQnsxE8mcI50xxE9JcXnNx'),
            preserve_default=True,
        ),
    ]
