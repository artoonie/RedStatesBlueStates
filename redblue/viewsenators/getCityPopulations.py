import csv
import os
import requests

def getCityPopulations(minPopulation = 2500):
    """
        :param minPopulation: Populations below this amount are ignored
        :return: A dictionary where dict[state][city] = population.
    """
    localFileForFastDebug = os.path.expanduser("~/Downloads/sub-est2016_all.csv")
    if os.path.exists(localFileForFastDebug):
        with file(localFileForFastDebug) as f:
            content = f.read()
    else:
        # This official URL gives an SSL error, so use a mirror instead
        # csvURL = "https://www2.census.gov/programs-surveys/popest/datasets/2010-2016/cities/totals/sub-est2016_all.csv"
        csvURL = "http://mcdc.missouri.edu/data/popests/archives/rawdata/SUB-EST2016_ALL.csv"

        response = requests.get(csvURL)
        content = response.content.decode('latin1').encode('utf-8')

    populationDataByState = {}
    cr = csv.reader(content.splitlines(), delimiter=',')
    firstRow = next(cr) # python2 is cr.next()

    assert firstRow[8] == "NAME"
    assert firstRow[9] == "STNAME"
    assert firstRow[18] == "POPESTIMATE2016"

    for row in cr:
        cityName = row[8]
        stateName = row[9]
        population = row[18]

        if population < minPopulation:
            continue

        if cityName.endswith(" city") or cityName.endswith(" town"):
            cityName = cityName[:-5]
        else:
            # only work on cities/towns, not counties etc
            continue

        if stateName not in populationDataByState:
            populationDataByState[stateName] = {}

        populationDataByState[stateName][cityName] = int(population)
    return populationDataByState

if __name__ == "__main__":
    getCityPopulations()
