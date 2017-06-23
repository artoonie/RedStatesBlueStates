# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools

from django.db import models
from django.utils.text import slugify
import uuid

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
    fbUrl = models.CharField(max_length=4096)
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
                    print "SLUG", self.slug
                    break

                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
            else:
                assert self.slug is not None
        super(ContactList, self).save(*args, **kwargs)
