import os
import pickle
import progressbar
import re
import requests
import shutil
import sys
import time
import traceback

from googleSearcher import GoogleSearcher, TimeoutError

sys.path.append("../redblue/viewsenators")
from getCityPopulations import getCityPopulations
from stateToFbCode import mapping

PICKLE_FILENAME = "codes.pickle"

# Parse CSV for cities/states
def readAllCities():
    stateNameToAbbrev = {}
    for row in mapping:
        stateNameToAbbrev[row[1]] = row[0]

    populations = getCityPopulations()
    statesToCitiesList = {}
    for state in populations:
        if state not in stateNameToAbbrev: continue
        stateAbbrev = stateNameToAbbrev[state]
        statesToCitiesList[stateAbbrev] = []
        for city in populations[state]:
            statesToCitiesList[stateAbbrev].append(city)
    return statesToCitiesList

def countCities(statesToCitiesList):
    return sum(len(statesToCitiesList[state]) for state in statesToCitiesList)

def getRegex():
    return re.compile('https://www.facebook.com/places/Things-to-do-in-[^/]*/([0-9]{15}[0-9]*)')

def searchGoogleSimple(statesToCitiesList):
    i = 1
    count = countCities(statesToCitiesList)
    urlRegex = getRegex()

    for state in statesToCitiesList:
        for city in statesToCitiesList[state]:
            goog = requests.get("https://encrypted.google.com/search?q=facebook+%22things+to+do+in+{}%2C+{}".format(city, state))
            code = re.search(urlRegex, goog.text).group(1)
            print "%05d/%04d %s, %s: %s" % (i, count, city, state, code)
            time.sleep(1)
            i += 1

def searchGoogleSmart(statesToCitiesList):
    queries = []
    for state in statesToCitiesList:
        for city in statesToCitiesList[state]:
            query = "facebook things to do in {}, {}".format(city, state)
            queries.append(query)

    fp = PICKLE_FILENAME
    if os.path.exists(fp):
        count = 0
        while os.path.exists(fp + "_backup_" + str(count)):
            count += 1
        shutil.copy2(fp, fp + "_backup_" + str(count))

        results = pickle.load(open(fp, "rb"))
        print "Preloaded", len(results), "cities."
    else:
        results = {}

    try:
        runSearchesOn(statesToCitiesList, queries, results)
        #cleanSearches(results)
    finally:
        pickle.dump(results, open(fp, "wb"))

badList = ["165814966441934"]

def cleanSearches(results):
    queries = results.keys()
    for query in queries:
        if results[query] in badList:
            del results[query]

def runSearchesOn(statesToCitiesList, queries, results):
    googleSearcher = GoogleSearcher(getRegex())

    i = 0
    consecutiveErrorCount = 0
    count = countCities(statesToCitiesList)
    bar = progressbar.ProgressBar(redirect_stdout=True, max_value = count)

    for query in queries:
        try:
            tic = time.time()
            if query not in results or results[query] is None:
                results[query] = googleSearcher.searchGoogle(query)
            toc = time.time()

            elapsed = toc - tic
            consecutiveErrorCount = 0

            i += 1
            if float(elapsed) > 0.1: # hack - why does it keep restarting?
                clock = time.localtime()
                clockStr = '%02d:%02d:%02d' % (clock.tm_hour, clock.tm_min, clock.tm_sec)
                print "%05d/%04d @ %s (%2.2fs): %s (%s)" % (i, count, clockStr, elapsed, query, results[query])
            bar.update(i)
        except TimeoutError:
            print "ERROR! Timeout on query", query
            consecutiveErrorCount += 1
        except Exception as e:
            print "ERROR! Unknown error for", query, ":", e
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            consecutiveErrorCount += 1

        if consecutiveErrorCount > 10:
            print "Getting repeated errors! Going to try again from the beginning."
            del googleSearcher
            searchGoogleSmart(statesToCitiesList)
            return

    return True

if __name__ == "__main__":
    statesToCitiesList = readAllCities()
    searchGoogleSmart(statesToCitiesList)
