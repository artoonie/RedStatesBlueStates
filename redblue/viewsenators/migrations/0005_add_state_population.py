# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('viewsenators', '0004_add_cities'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='population',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

