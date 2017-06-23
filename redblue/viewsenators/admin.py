# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib import admin

from .models import ContactList

class ChooseFormSimple(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea())

@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    form = ChooseFormSimple
