# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class State(models.Model):
    name = models.CharField(max_length=16)

class Senator(models.Model):
    firstName = models.CharField(max_length=128)
    lastName = models.CharField(max_length=128)
    party = models.CharField(max_length=16)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

class ContactList(models.Model):
    senators = models.ManyToManyField(Senator)
