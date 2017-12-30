# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

import viewsenators.initialization as initter

def populateParties(apps, schema_editor):
    PartyInProgress = apps.get_model('viewsenators', 'Party')
    db_alias = schema_editor.connection.alias
    allPartyObjects = PartyInProgress.objects.using(db_alias)
    initter.populateParties(PartyInProgress, allPartyObjects)

def unpopulateParties(apps, schema_editor):
    PartyInProgress = apps.get_model('viewsenators', 'Party')
    db_alias = schema_editor.connection.alias
    PartyInProgress.objects.using(db_alias).all().delete()

# Convert and unconvert a party from a string to an object
def convertParty(apps, schema_editor):
    SenatorInProgress = apps.get_model('viewsenators', 'Senator')
    PartyInProgress = apps.get_model('viewsenators', 'Party')
    db_alias = schema_editor.connection.alias
    for senator in SenatorInProgress.objects.using(db_alias).all():
        senator.party = PartyInProgress.objects.using(db_alias).get(abbrev=senator.party_old)
        senator.save()

def unconvertParty(apps, schema_editor):
    SenatorInProgress = apps.get_model('viewsenators', 'Senator')
    db_alias = schema_editor.connection.alias
    for senator in SenatorInProgress.objects.using(db_alias).all():
        senator.party_old = senator.party.abbrev
        senator.save()

class Migration(migrations.Migration):

    dependencies = [
        ('viewsenators', '0003_contactlist_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('facebookId', models.CharField(max_length=16)),
                ('population', models.PositiveIntegerField()),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewsenators.State')),
            ],
        ),
        migrations.CreateModel(
            name='Congressmember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=128)),
                ('lastName', models.CharField(max_length=128)),
                ('cities', models.ManyToManyField(to='viewsenators.City')),
            ],
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbrev', models.CharField(max_length=1)),
                ('name', models.CharField(max_length=16)),
                ('adjective', models.CharField(max_length=16)),
            ],
        ),
        migrations.AddField(
            model_name='congressmember',
            name='party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewsenators.Party'),
        ),

        # move "party" to "party_old", create a new field, run code to convert,
        # then delete "party_old"
        migrations.RunPython(populateParties, reverse_code=unpopulateParties),
        migrations.RenameField(
            model_name='senator',
            old_name='party',
            new_name='party_old',
        ),
        migrations.AddField(
            model_name='senator',
            name='party',
            field=models.ForeignKey(null=True,on_delete=django.db.models.deletion.CASCADE, to='viewsenators.Party'),
        ),
        migrations.RunPython(convertParty, reverse_code=unconvertParty),
        migrations.AlterField( # make it not nullable anymore
            model_name='senator',
            name='party',
            field=models.ForeignKey(null=True,on_delete=django.db.models.deletion.CASCADE, to='viewsenators.Party'),
        ),
        migrations.AlterField( # make nullable so it can be reversed
            model_name='senator',
            name='party_old',
            preserve_default=True,
            field=models.CharField(max_length=1, default="R", null=True),
        ),
        migrations.RemoveField(
            model_name='senator',
            name='party_old',
        ),
    ]
