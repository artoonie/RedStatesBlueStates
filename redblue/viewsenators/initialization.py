import os
import requests
import viewsenators.cityToFbCode as cityToFbCode
import viewsenators.stateToFbCode as stateToFbCode
from .models import Party, City, State, Senator, Congressmember, ContactList
from .getPopulations import getCityStatePopulations

def populateParties(partyModel, partyObjects):
    """ Takes in partyObjects instead of using the Party.objects.all() so it
        can get the correct Model from an in-progress migration if needed. """
    numParties = len(partyObjects.all())
    if len(partyObjects.all()) != 0:
        assert numParties == 3
        return

    partyObjects.bulk_create([
        partyModel(name="Republican",  abbrev="R", adjective="Republican"),
        partyModel(name="Democrat",    abbrev="D", adjective="Democratic"),
        partyModel(name="Independent", abbrev="ID", adjective="Independent")
    ])

def populateStates(statePopulations):
    """ Populate the list of states and their facebook codes """
    # For now, never overwrite
    numStates = len(State.objects.all())
    if len(State.objects.all()) != 0:
        assert numStates == 50
        return

    for line in stateToFbCode.mapping:
        abbrev = line[0]
        name = line[1]
        facebookId = line[2]
        population = statePopulations[name]

        State.objects.create(name=name,
                             abbrev=abbrev,
                             facebookId=facebookId,
                             population=population)

def addPopulationToStates(statePopulations):
    """ For migration, most likely, though maybe to update when we get
        newer data? """
    for state in statePopulations:
        if state == "District of Columbia": continue
        stateObj = State.objects.get(name=state)
        stateObj.population = statePopulations[state]
        stateObj.save()

def populateCities(cityPopulations, fixMode=False, verboseYield = False):
    """ Populate the list of cities and their facebook codes.
        :param fixMode: Will create any new cities not in the database,
            and update any facebook codes and populations of existing cities.
            Will not delete cities,
        :param verboseYield: To overcome heroku timeouts, will yield
            progress strings.

    """
    # For now, never overwrite
    numCities = len(City.objects.all())
    if not fixMode and len(City.objects.all()) != 0:
        # sanity check to make sure it didn't crash on a previous run
        assert numCities > 18000
        return

    if verboseYield:
        yield "Beginning download.<br>"

    if verboseYield:
        yield "Completed download. Processing.<br>"

    for i, line in enumerate(cityToFbCode.mapping):
        city = line[0]
        stateAbbrev = line[1]
        facebookId = line[2]

        if verboseYield and (i+1) % 100 == 0:
            yield "%d/%d<br>" % (i+1, len(cityToFbCode.mapping))

        try:
            state = State.objects.get(abbrev=stateAbbrev)
        except State.DoesNotExist:
            # Puerto Rico & other territories
            if verboseYield:
                yield "Skipping non-state: " + stateAbbrev + "<br>"
            continue

        stateName = state.name
        assert stateName in cityPopulations
        if city not in cityPopulations[stateName]:
            try:
                cityObj = City.objects.get(name=city, state=state)
                cityObj.delete()
            except City.DoesNotExist:
                pass
            continue # city likely below minPopulation threshold
        else:
            population = cityPopulations[stateName][city]

        if fixMode:
            try:
                cityObj = City.objects.get(name=city, state=state)
                if cityObj.facebookId != facebookId or cityObj.population != population:
                    cityObj.facebookId = facebookId
                    cityObj.population = population
                    cityObj.save()
                continue
            except City.DoesNotExist:
                # Continue to create
                pass

        City.objects.create(name=city,
                            state=state,
                            facebookId=facebookId,
                            population=population)

def updateCitiesWithCurrentData(cityPopulations):
    for x in populateCities(cityPopulations, fixMode=True, verboseYield=True):
        yield x

def clearDataForNewCongress():
    Party.objects.all().delete()
    State.objects.all().delete()
    Senator.objects.all().delete()
    Congressmember.objects.all().delete()

    # Note: contactlists have links to senators which are now defunct
    ContactList.objects.all().delete()

def populateAllData():
    def _populateMOCWith(data, mocType):
        """ Populate members of congress with a propublica dictionary.
            mocType should be either Senator or Congressmember
            """
        assert(mocType == Senator or mocType == Congressmember)

        assert data['status'] == 'OK'
        results = data['results']
        assert len(results) == 1 # could have multiple congresses?
        result = results[0]

        assert result['congress'] == '116'
        assert result['chamber'] == 'Senate' if mocType == 'Senator' else 'House'
        assert result['offset'] == 0

        for member in result['members']:
            assert isinstance(member['in_office'], bool) # was once a string
            if member['in_office'] == False: continue

            state = State.objects.get(abbrev=member['state'])
            party = Party.objects.get(abbrev=member['party'])
            try:
                senator = mocType.objects.get(firstName= member['first_name'],
                                              lastName = member['last_name'])
                senator.phoneNumber = member['phone']
                senator.save()
            except mocType.DoesNotExist:
                mocType.objects.create(firstName= member['first_name'],
                                       lastName = member['last_name'],
                                       phoneNumber = member['phone'],
                                       party = party,
                                       state = state)

    url = 'https://api.propublica.org/congress/v1/116/senate/members.json'
    apiKey = os.environ['PROPUBLICA_API_KEY']
    headers = {'X-API-Key': apiKey}

    cityPopulations, statePopulations = getCityStatePopulations()

    populateParties(Party, Party.objects)
    populateStates(statePopulations)
    populateCities(cityPopulations)
    senatorDataFile = requests.get(url, headers=headers)
    _populateMOCWith(senatorDataFile.json(), Senator)
