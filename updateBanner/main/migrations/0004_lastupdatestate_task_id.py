# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-28 22:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20151227_1910'),
    ]

    operations = [
        migrations.AddField(
            model_name='lastupdatestate',
            name='task_id',
            field=models.CharField(default='', max_length=200),
        ),
    ]