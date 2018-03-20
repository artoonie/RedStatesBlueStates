# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from colour import Color

from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from .models import Party, City, Senator, ContactList
from .forms import ChooseForm
from .getPopulations import getCityStatePopulations
import initialization

# This seems to be the most that Facebook will allow, though it varies over time
NUM_CITIES_PER_QUERY = 50

def index(request):
    def colorToD3(color):
        return "rgb(%d,%d,%d)" % (color.red*255, color.green*255, color.blue*255)
    def substituteDesc(moc, desc):
        if "{{number}}" not in desc:
            desc += "\n\n%s's phone number is {{number}}" % moc.lastName

        if moc.phoneNumber:
            text = moc.phoneNumber
        else:
            text ="(unknown number)"

        desc = desc.replace("{{name}}", moc.firstName + " " + moc.lastName)
        return desc.replace("{{number}}", text)
    template = loader.get_template('halcyonic/index.html')

    if 'list' in request.GET:
        clId = str(request.GET['list'])
        contactList = get_object_or_404(ContactList, slug=clId)
    else:
        try:
            contactList = ContactList.objects.get(slug='75ba0d523963492093a3badbd1306b49')
        except ContactList.DoesNotExist:
            contactList = ContactList.objects.get(title="Republican")

    stateColor = colorToD3(Color(rgb=(125/255.0,   0/255.0,  16/255.0)))
    senatorToURLsPopsAndDesc = {}
    for senator in contactList.senators.all():
        senatorToURLsPopsAndDesc[senator] = _stateToFbCode(senator.state)
        senatorToURLsPopsAndDesc[senator]['callScript'] = substituteDesc(senator, contactList.description)

    context = {
        "stateColor": stateColor,
        "senatorToURLsPopsAndDesc": senatorToURLsPopsAndDesc
    }
    return HttpResponse(template.render(context, request))

def combineContactList(request):
    template = loader.get_template('viewsenators/combine.html')
    context = {'contactLists': ContactList.objects.all()}
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
            return HttpResponseRedirect(reverse('index')+'?list=' + cl.slug)
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

def _stateToFbCode(state):
    """ :return: the URL and the percentage of the population of the
        desired states which will be found via that URL """
    # While there are many better URL constructions that ideally start with
    # your friends, rather than start with all FB users in each city then
    # intersect that with your friends list, this is the only way I could get it
    # to work.
    # In particular, facebook seems to limit the number of unions to six,
    # whereas the number of intersections can be ten times that.
    setOfCities = City.objects.filter(state=state).order_by('-population')[:NUM_CITIES_PER_QUERY]
    url = "https://www.facebook.com/search/"
    for city in setOfCities:
        url += city.facebookId + "/residents/present/"
    url += "union/me/friends/intersect/"

    # % of population in this search
    cityPop = setOfCities.aggregate(Sum('population'))['population__sum']
    if cityPop is None: cityPop = 0 # TODO hack if a state has no cities
    statePop = state.population
    percentPopIncludedInURL = float(cityPop) / float(statePop)
    percentPopIncludedInURL = int(100*percentPopIncludedInURL+0.5)

    return {'url': url,
            'percentPopIncludedInURL': percentPopIncludedInURL}

def _makeContactList(title, description, senatorList, public):
    cl = ContactList.objects.create(
            title = title,
            description = description,
            public = public)
    cl.senators = senatorList
    cl.save()
    return cl

@user_passes_test(lambda u: u.is_superuser)
def populateSenators(request):
    def _createInitialLists():
        assert ContactList.objects.count() == 0
        assert Senator.objects.count() == 100
        for party in Party.objects.all():
            title = party.name
            description = "Call {{name}} at {{number}}"
            senators = Senator.objects.filter(party=party)
            _makeContactList(title, description, senators, public=True)

    initialization.populateAllData()
    _createInitialLists()

    senators = Senator.objects.all()
    def s2t(s): return "%s: %s, %s" % (s.state.abbrev, s.firstName, s.lastName)
    senText = '<br>'.join(sorted([s2t(s) for s in senators]))

    return debugWriteAnything("The list of senators: <br>" + senText)

@user_passes_test(lambda u: u.is_superuser)
def updateCitiesAndStatesWithLatestData(request):
    # This can take more than 30 seconds, so we need a streaming response
    # for Heroku to not shut it down
    # This is only run once by the admin, so the decreased performance
    # shouldn't matter.
    def runner():
        cityPopulations, statePopulations = getCityStatePopulations()
        for x in initialization.updateCitiesWithCurrentData(cityPopulations):
            yield x
        yield initialization.addPopulationToStates(statePopulations)
    return StreamingHttpResponse(runner())
