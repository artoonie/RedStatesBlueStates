# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-20 05:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=1024)),
                ('fbUrl', models.CharField(max_length=4096)),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Senator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=128)),
                ('lastName', models.CharField(max_length=128)),
                ('party', models.CharField(choices=[('R', 'Republican'), ('D', 'Democrat'), ('I', 'Independent')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('abbrev', models.CharField(max_length=2)),
                ('facebookId', models.CharField(max_length=15)),
            ],
        ),
        migrations.AddField(
            model_name='senator',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewsenators.State'),
        ),
        migrations.AddField(
            model_name='contactlist',
            name='senators',
            field=models.ManyToManyField(to='viewsenators.Senator'),
        ),
    ]