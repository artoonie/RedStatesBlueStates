import os
import requests
import cityToFbCode
import stateToFbCode
from .models import Party, City, State, Senator
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
        partyModel(name="Independent", abbrev="I", adjective="Independent")
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
        yield "Beginning downlod.<br>"

    if verboseYield:
        yield "Completed download. Processing.<br>"

    for i, line in enumerate(cityToFbCode.mapping):
        city = line[0]
        stateAbbrev = line[1]
        facebookId = line[2]

        if verboseYield and i % 100 == 0:
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
            population = 0
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

def populateAllData():
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
            assert isinstance(member['in_office'], bool) # was once a string
            if member['in_office'] == False: continue

            state = State.objects.get(abbrev=member['state'])
            party = Party.objects.get(abbrev=member['party'])
            Senator.objects.create(firstName= member['first_name'],
                                   lastName = member['last_name'],
                                   party = party,
                                   state = state)

    url = 'https://api.propublica.org/congress/v1/115/senate/members.json'
    apiKey = os.environ['PROPUBLICA_API_KEY']
    headers = {'X-API-Key': apiKey}

    cityPopulations, statePopulations = getCityStatePopulations()

    populateParties(Party, Party.objects)
    populateStates(statePopulations)
    populateCities(cityPopulations)
    senatorDataFile = requests.get(url, headers=headers)
    _populateSenatorsWith(senatorDataFile.json())
