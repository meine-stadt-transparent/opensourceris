# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-27 13:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0029_auto_20171022_0942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useralert',
            name='alert_json',
        ),
        migrations.AddField(
            model_name='useralert',
            name='search_string',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]