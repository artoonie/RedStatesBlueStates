# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from colour import Color
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from .models import Party, City, Senator, ContactList
from .forms import ChooseForm, CombineForm
import initialization

NUM_CITIES_PER_QUERY = 70

def index(request):
    def colorToD3(color):
        return "rgb(%d,%d,%d)" % (color.red*255, color.green*255, color.blue*255)
    template = loader.get_template('halcyonic/index.html')

    if 'lists' in request.GET:
        clIds = str.split(str(request.GET['lists']), ',')
        clIds = [str(x) for x in clIds]
        contactLists = [get_object_or_404(ContactList, slug=x) for x in clIds]
    else:
        contactLists = []
        try:
            trumpcare = ContactList.objects.get(slug='75ba0d523963492093a3badbd1306b49')
            contactLists.append(trumpcare)
        except ContactList.DoesNotExist:
            for party in Party.objects.all():
                contactList = ContactList.objects.get(title=party.name)
                contactLists.append(contactList)
    if len(contactLists) > 8:
        return debugWriteAnything("You can combine up to 8 lists at most")
    elif len(contactLists) == 0:
        return debugWriteAnything("No lists found")

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
            bitmaskToColor[idx] = Color(pick_for=idx)

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
            bitmaskToColor[i] = Color(pick_for=i)
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

    urls = [_senatorListToFbCode(cl.senators.all()) for cl in contactLists]
    context = {
        "bitmaskToColor": json.dumps(bitmaskToColor),
        "stateToBitmasks": stateToBitmask,
        "legendText": json.dumps(legendText),
        "contactLists": zip(contactLists, urls),
        "twelveOverLenContactLists": int(12.0/len(contactLists))
    }
    return HttpResponse(template.render(context, request))

def combineContactList(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CombineForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            data = form.cleaned_data
            contactLists = data['contactLists']
            slugs = [ContactList.objects.get(id=c).slug for c in contactLists]
            slugStr = ','.join(slugs)
            return HttpResponseRedirect(reverse('index')+'?lists=' + slugStr)

    # if a GET (or any other method) we'll create a blank form
    form = CombineForm()

    template = loader.get_template('viewsenators/combine.html')
    context = {'form': form}
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
            public = data['public']
            cl = _makeContactList(title, description, senators, public)
            return HttpResponseRedirect(reverse('index')+'?lists=' + cl.slug)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChooseForm()

    so = Senator.objects

    ids = {}
    for party in Party.objects.all():
        idList = ["input[value=\""+str(s.id)+"\"]"
                  for s in so.filter(party=party)]
        idsSet = set(idList)
        idsStr = ', '.join(idsSet)
        ids[party.name] = idsStr

    template = loader.get_template('viewsenators/choose.html')
    context = {'form': form,
               'ids': ids}
    return HttpResponse(template.render(context, request))

def debugWriteAnything(text):
    response = HttpResponse()
    response.write(text)
    return response

def _senatorListToFbCode(senators):
    setOfStates = set([s.state for s in senators])
    setOfCities = City.objects.filter(state__in=setOfStates).order_by('-population')[:NUM_CITIES_PER_QUERY]
    url = "https://www.facebook.com/search/"
    for city in setOfCities:
        url += city.facebookId + "/residents/"
    url += "union/me/friends/intersect/"
    return url

def _makeContactList(title, description, senatorList, public):
    cl = ContactList.objects.create(
            title = title,
            description = description,
            public = public)
    cl.senators = senatorList
    cl.fbUrl = _senatorListToFbCode(cl.senators.all())
    cl.save()
    return cl

def populateSenators(request):
    def _createInitialLists():
        assert ContactList.objects.count() == 0
        assert Senator.objects.count() == 100
        for party in Party.objects.all():
            title = party.name
            desc = party.adjective
            description = "All " + desc + " senators"
            senators = Senator.objects.filter(party=party)
            _makeContactList(title, description, senators, public=True)

    initialization.initialize()
    _createInitialLists()

    senators = Senator.objects.all()
    def s2t(s): return "%s: %s, %s" % (s.state.abbrev, s.firstName, s.lastName)
    senText = '<br>'.join(sorted([s2t(s) for s in senators]))

    return debugWriteAnything("The list of senators: <br>" + senText)

def fixCities(request):
    initialization.fixCities()
    return debugWriteAnything("Cities fixed!")
