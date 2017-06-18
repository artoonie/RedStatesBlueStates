# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

Democrat = "D"
Republican = "R"
def _partyToText(whichParty):
    if whichParty == Democrat:
        return "Blue"
    elif whichParty == Republican:
        return "Red"
    else:
        assert False

def index(request):
    template = loader.get_template('viewsenators/index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def createContactList(request):
    whichParty = Republican

    template = loader.get_template('viewsenators/index.html')
    mocFn = os.path.join(settings.STATIC_ROOT, 'moc.json')

    with open(mocFn, 'rb') as dataFile:
        data = json.load(dataFile)
    assert data['status'] == 'OK'

    results = data['results']
    assert len(results) == 1 # could have multiple congresses?
    result = results[0]

    assert result['congress'] == '115'
    assert result['chamber'] == 'Senate'
    assert result['offset'] == '0'

    membersInParty = set()
    for member in result['members']:
        if member['party'] == whichParty:
            membersInParty.add(member['state'])

    partyText = _partyToText(whichParty)

    # TODO generate senators list once
    # TODO pass in data from the senators list
    context = {
        "text": partyText
    }
    return HttpResponse(template.render(context, request))
