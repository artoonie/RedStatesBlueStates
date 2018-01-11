# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools

from django.db import models
from django.utils.text import slugify
import uuid

class Party(models.Model):
    abbrev = models.CharField(max_length=1)
    name = models.CharField(max_length=16)

    # e.g. a "Democratic" senator, or a "Republican" congressperson
    adjective = models.CharField(max_length=16)

class State(models.Model):
    name = models.CharField(max_length=16)
    abbrev = models.CharField(max_length=2)
    facebookId = models.CharField(max_length=15)
    population = models.PositiveIntegerField(default=0)

class City(models.Model):
    name = models.CharField(max_length=64) # largest city name is 57 chars
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    population = models.PositiveIntegerField()
    # cities can have 15 or 16 char IDs, though Scottville, MI has 17
    facebookId = models.CharField(max_length=17)

class Congressmember(models.Model):
    firstName = models.CharField(max_length=128)
    lastName = models.CharField(max_length=128)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    cities = models.ManyToManyField(City)

class Senator(models.Model):
    firstName = models.CharField(max_length=128)
    lastName = models.CharField(max_length=128)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

class ContactList(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    senators = models.ManyToManyField(Senator)
    uid = models.UUIDField(primary_key=False, default=uuid.uuid4,
                           editable=False, max_length=16)
    slug = models.SlugField(unique=True, editable=False)
    public = models.BooleanField(default=True,
        verbose_name="Make this list viewable to anyone, even without a link?")

    def save(self, *args, **kwargs):
        if not self.pk:
            # Creating, not editing
            # keyerror.com/blog/automatically-generating-unique-slugs-in-django
            max_length = ContactList._meta.get_field('slug').max_length
            self.slug = orig = slugify(self.title)[:max_length]

            for x in itertools.count(1):
                if not ContactList.objects.filter(slug=self.slug).exists():
                    break

                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
            else:
                assert self.slug is not None
        super(ContactList, self).save(*args, **kwargs)
