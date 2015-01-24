# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_auto_20150102_0558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremailverify',
            name='token',
            field=models.CharField(default='UFUqJx2G2TcspGS0S1i9QOAtVEg9QyCwq5Jy0Wsv3LobbWLUkw0Ld3MuopdoOIGV', db_index=True, max_length=64),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userpasswordreset',
            name='token',
            field=models.CharField(default='fFigwtwTIEN2GoBAumesMDrbrGZiohQPgdHps3k2EnnMtPVUaijchVhRyNgr7nG1', db_index=True, max_length=64),
            preserve_default=True,
        ),
    ]
