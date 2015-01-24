# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0005_auto_20150105_0740'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addresscomponent',
            name='ser_no',
        ),
    ]
