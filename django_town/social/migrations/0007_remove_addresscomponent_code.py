# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0006_remove_addresscomponent_ser_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addresscomponent',
            name='code',
        ),
    ]
