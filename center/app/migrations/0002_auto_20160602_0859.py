# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-02 08:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='start_service_time',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='speed',
            field=models.IntegerField(default='low', null=True),
        ),
    ]
