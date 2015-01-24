# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0004_auto_20150102_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressComponentType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='addresscomponent',
            name='children_count',
        ),
        migrations.RemoveField(
            model_name='addresscomponent',
            name='type',
        ),
        migrations.AddField(
            model_name='addresscomponent',
            name='depth',
            field=models.SmallIntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='addresscomponent',
            name='types',
            field=models.ManyToManyField(to='social.AddressComponentType'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='useremailverify',
            name='token',
            field=models.CharField(max_length=64, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userpasswordreset',
            name='token',
            field=models.CharField(max_length=64, db_index=True),
            preserve_default=True,
        ),
    ]
