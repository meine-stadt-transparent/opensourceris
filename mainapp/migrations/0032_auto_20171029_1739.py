# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-29 16:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0031_auto_20171029_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agendaitem',
            name='title',
            field=models.TextField(),
        ),
    ]