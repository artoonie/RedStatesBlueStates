# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .forms import ChooseForm
from django.contrib import admin

from .models import ContactList

@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    form = ChooseForm
