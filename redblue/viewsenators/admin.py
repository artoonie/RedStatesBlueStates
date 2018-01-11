# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib import admin

from .models import ContactList, Senator, City, State

class ChooseFormSimple(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea())

@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    form = ChooseFormSimple

@admin.register(State)
class StateAdmin(admin.ModelAdmin): pass

@admin.register(Senator)
class SenatorAdmin(admin.ModelAdmin): pass

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'facebookId', 'population', 'get_state')

    def get_state(self, obj):
        return obj.state.name
    get_state.admin_order_field = 'state'
    get_state.short_description = 'State'
