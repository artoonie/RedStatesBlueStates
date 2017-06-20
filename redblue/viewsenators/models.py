# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class State(models.Model):
    name = models.CharField(max_length=16)
    abbrev = models.CharField(max_length=2)
    facebookId = models.CharField(max_length=15)

class Senator(models.Model):
    PARTY_CHOICES = (
        ('R', 'Republican'),
        ('D', 'Democrat'),
        ('I', 'Independent'),
    )
    firstName = models.CharField(max_length=128)
    lastName = models.CharField(max_length=128)
    party = models.CharField(max_length=1, choices=PARTY_CHOICES)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

class ContactList(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    senators = models.ManyToManyField(Senator)
