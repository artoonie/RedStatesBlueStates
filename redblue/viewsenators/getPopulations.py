import csv
import os
import requests

def getCityStatePopulations(minPopulation = 2500):
    """
        :param minPopulation: Populations below this amount are ignored
        :return: A pair of dictionaries:
            1. City populations:  dict[state][city] = population.
            2. State populations:  dict[state] = population.
    """
    localFileForFastDebug = os.path.expanduser("~/Downloads/sub-est2016_all.csv")
    if os.path.exists(localFileForFastDebug):
        with file(localFileForFastDebug) as f:
            content = f.read()
    else:
        # This official URL gives an SSL error, so use a mirror instead
        # csvURL = "https://www2.census.gov/programs-surveys/popest/datasets/2010-2016/cities/totals/sub-est2016_all.csv"

        csvURL = "https://raw.githubusercontent.com/a113n/Matplotlib-2.0-by-examples/master/sub-est2016_all.csv"

        response = requests.get(csvURL)
        content = response.content.decode('latin1').encode('utf-8')

    statePopulations = {}
    cityPopulationDataByState = {}
    cr = csv.reader(content.splitlines(), delimiter=',')
    firstRow = cr.next()

    CITY_SUMLEV = "162"
    STATE_SUMLEV = "040"
    assert firstRow[0] == "SUMLEV"
    assert firstRow[8] == "NAME"
    assert firstRow[9] == "STNAME"
    assert firstRow[18] == "POPESTIMATE2016"

    for row in cr:
        sumlev = row[0]
        cityName = row[8]
        stateName = row[9]
        population = int(row[18])

        if population < minPopulation:
            continue

        if sumlev == CITY_SUMLEV:
            # Ignore municipalities, villages, borough, etc
            if cityName.endswith(" city") or cityName.endswith(" town"):
                cityName = cityName[:-5]
        elif sumlev == STATE_SUMLEV:
            assert cityName == stateName
            statePopulations[stateName] = population
        else:
            continue

        if stateName not in cityPopulationDataByState:
            cityPopulationDataByState[stateName] = {}

        cityPopulationDataByState[stateName][cityName] = int(population)

    return cityPopulationDataByState, statePopulations

if __name__ == "__main__":
    print getCityStatePopulations()
