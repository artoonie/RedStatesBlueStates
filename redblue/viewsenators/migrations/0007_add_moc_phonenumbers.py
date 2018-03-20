# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-03-13 01:08
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewsenators', '0006_make_fb_id_longer'),
    ]

    operations = [
        migrations.AddField(
            model_name='congressmember',
            name='phoneNumber',
            field=models.CharField(max_length=12, null=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Must be in format 555-555-5555', regex='^\\d{3}-\\d{3}-\\d{4}$')]),
        ),
        migrations.AddField(
            model_name='senator',
            name='phoneNumber',
            field=models.CharField(max_length=12, null=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Must be in format 555-555-5555', regex='^\\d{3}-\\d{3}-\\d{4}$')]),
        ),
    ]
