import os
import requests
from .models import Party, City, State, Senator
from .getCityPopulations import getCityPopulations

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

def populateStates():
    """ Populate the list of states and their facebook codes """
    # For now, never overwrite
    numStates = len(State.objects.all())
    if len(State.objects.all()) != 0:
        assert numStates == 50
        return

    from .stateToFbCode import mapping
    for line in mapping:
        abbrev = line[0]
        name = line[1]
        facebookId = line[2]

        State.objects.create(name=name,
                             abbrev=abbrev,
                             facebookId=facebookId)

def populateCities(fixMode=False, progressBar = False):
    """ Populate the list of cities and their facebook codes.
        fixMode: Will create any new cities not in the database,
            and update any facebook codes and populations of existing cities.
            Will not delete cities, """
    # For now, never overwrite
    numCities = len(City.objects.all())
    if not fixMode and len(City.objects.all()) != 0:
        # sanity check to make sure it didn't crash on a previous run
        assert numCities > 18000
        return

    if progressBar:
        yield "Beginning downlod.<br>"

    populationDataByState = getCityPopulations()

    if progressBar:
        yield "Completed download. Processing.<br>"

    from .cityToFbCode import mapping
    for i, line in enumerate(mapping):
        city = line[0]
        stateAbbrev = line[1]
        facebookId = line[2]

        try:
            state = State.objects.get(abbrev=stateAbbrev)
        except State.DoesNotExist:
            # Puerto Rico & other territories
            continue

        stateName = state.name
        assert stateName in populationDataByState
        if city not in populationDataByState[stateName]:
            population = 0
        else:
            population = populationDataByState[stateName][city]

        if progressBar and i % 1000 == 0:
            # A bit of a hack to overcome the heroku timeout
            yield "%d/%d<br>" % (i, len(mapping))

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

def updateCitiesWithCurrentData():
    for x in populateCities(fixMode = True, progressBar = True):
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

    populateParties(Party, Party.objects)
    populateStates()
    populateCities()
    senatorDataFile = requests.get(url, headers=headers)
    _populateSenatorsWith(senatorDataFile.json())
