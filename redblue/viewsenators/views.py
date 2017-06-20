# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from colour import Color
import json
import os
import requests

from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from .models import State, Senator, ContactList
from .forms import ChooseForm

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
    def colorToD3(color):
        return "rgb(%d,%d,%d)" % (color.red*255, color.green*255, color.blue*255)
    template = loader.get_template('viewsenators/index.html')
    contactLists = [ContactList.objects.get(id=14),
                    ContactList.objects.get(id=15),
                    ContactList.objects.get(id=16)]

    statesInList = {}
    allStates = set()
    for cl in contactLists:
        statesInList[cl] = set([s.state for s in cl.senators.all()])
        allStates.update(statesInList[cl])

    stateToBitmask = {}
    setOfColorIdxs = set()
    for state in allStates:
        colorBitmask = int(0)
        for i, cl in enumerate(contactLists):
            if state in statesInList[cl]:
                colorBitmask |= 1 << i
        stateToBitmask[state] = colorBitmask
        setOfColorIdxs.add(colorBitmask)

    # Single-association colors
    bitmaskToColor = {}
    for i, cl in enumerate(contactLists):
        idx = 1 << i

        if 'Republican' in cl.title:
            bitmaskToColor[idx] = Color(rgb=(125/255.0,   0/255.0,  16/255.0))
        elif 'Democrat' in cl.title:
            bitmaskToColor[idx] = Color(rgb=( 13/255.0,   0/255.0,  76/255.0))
        elif 'Independent' in cl.title:
            bitmaskToColor[idx] = Color(rgb=(128/255.0, 128/255.0,   0/255.0))
        else:
            bitmaskToColor[idx] = Color(rgb=(213/255.0, 222/255.0, 217/255.0))

    # Double-association colors
    for i0 in range(len(contactLists)):
        for i1 in range(len(contactLists)):
            idx0 = 1 << i0
            idx1 = 1 << i1
            idx = idx0 | idx1
            if idx not in setOfColorIdxs: continue

            # Interpolate
            bitmaskToColor[idx] = \
                list(bitmaskToColor[idx0].range_to(bitmaskToColor[idx1], 3))[1]

    # Remove unused (single-associaten kept around);
    # Add used (more-than-two associations not added)
    for i in range(2**len(contactLists)):
        if i in setOfColorIdxs and i not in bitmaskToColor:
            bitmaskToColor[i] = Color()
        elif i not in setOfColorIdxs and i in bitmaskToColor:
            del bitmaskToColor[i]

    # Legend
    legendText = {}
    for colorBitmask in setOfColorIdxs:
        labels = []
        for i in range(len(contactLists)):
            if colorBitmask & 1 << i:
                labels.append(contactLists[i].title)

        legendText[colorBitmask] = "/".join(labels)

    assert len(legendText) == len(bitmaskToColor)
    for c in bitmaskToColor:
        bitmaskToColor[c] = colorToD3(bitmaskToColor[c])

    context = {
        "bitmaskToColor": json.dumps(bitmaskToColor),
        "stateToBitmasks": stateToBitmask,
        "legendText": json.dumps(legendText)
    }
    return HttpResponse(template.render(context, request))

def createContactList(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ChooseForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            data = form.cleaned_data
            title = data['title']
            description = data['description']
            senators = data['senators']
            cl = ContactList.objects.create(
                    title = title,
                    description = description)
            cl.senators = senators
            cl.save()

            text = '<br><br><br>'.join(
                [c.title + "<br>" + c.description + "<br>" +
                ', '.join(s.lastName for s in c.senators.all()) \
                for c in ContactList.objects.all()])
            return debugWriteAnything(text)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChooseForm()

    so = Senator.objects

    ids = {}
    for party in Senator.PARTY_CHOICES:
        idList = ["input[value=\""+str(s.id)+"\"]"
            for s in so.filter(party=party[0])]
        idsSet = set(idList)
        idsStr = ', '.join(idsSet)
        ids[party[1]] = idsStr

    template = loader.get_template('viewsenators/choose.html')
    context = {'form': form,
               'ids': ids}
    return HttpResponse(template.render(context, request))

def debugWriteAnything(text):
    response = HttpResponse()
    response.write(text)
    return response

def populateSenators(request):
    """ Populate the list of senators using the ProPublica API """
    def _populateSenatorsWith(data):
        """ Populate the list of senators with a propublica dictionary """
        numSenators = len(Senator.objects.all())
        if numSenators != 0:
            assert numSenators == 100
            return

        assert data['status'] == 'OK'
        results = data['results']
        assert len(results) == 1 # could have multiple congresses?
        result = results[0]

        assert result['congress'] == '115'
        assert result['chamber'] == 'Senate'
        assert result['offset'] == 0

        for member in result['members']:
            if member['in_office'] == 'false': continue
            assert member['in_office'] == 'true'

            state = State.objects.get(abbrev=member['state'])
            Senator.objects.create(firstName= member['first_name'],
                                   lastName = member['last_name'],
                                   party = member['party'],
                                   state = state)

    def _populateStates():
        """ Populate the list of states and their facebook codes """
        # For now, never overwrite
        numStates = len(State.objects.all())
        if len(State.objects.all()) != 0:
            assert numStates == 50
            return

        fp = os.path.join(settings.STATIC_ROOT, 'stateToFbCode.txt')
        with open(fp, 'rb') as dataFile:
            for line in dataFile:
                if line.startswith('#'): continue
                splitLine = line.split(',')

                abbrev = splitLine[0].strip()
                name = splitLine[1].strip()
                facebookId = splitLine[2].strip()

                State.objects.create(name=name,
                                     abbrev=abbrev,
                                     facebookId=facebookId)
    assert len(State.objects.all()) != 0
    url = 'https://api.propublica.org/congress/v1/115/senate/members.json'
    apiKey = os.environ['PROPUBLICA_API_KEY']
    headers = {'X-API-Key': apiKey}
    dataFile = requests.get(url, headers=headers)

    _populateStates()
    _populateSenatorsWith(dataFile.json())

    response = HttpResponse()
    senators = Senator.objects.all()
    def s2t(s): return "%s: %s, %s" % (s.state.abbrev, s.firstName, s.lastName)
    senText = '<br>'.join(sorted([s2t(s) for s in senators]))
    response.write("The list of senators: <br>" + senText)
    return response
