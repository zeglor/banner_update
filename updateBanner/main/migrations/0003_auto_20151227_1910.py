# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-27 19:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20151221_2259'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='banner_id',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='banner',
            name='campaign_id',
            field=models.BigIntegerField(db_index=True, default=0),
        ),
    ]
