# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-21 21:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewsenators', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactlist',
            name='public',
            field=models.BooleanField(default=True, verbose_name='Make this list viewable to anyone, even without a link?'),
        ),
    ]
