# Convert codes.pickle to a .py file containing all the codes.
# Usage: pass in the output .py filename.

import pickle
import sys

outFilename = sys.argv[1]
print "Writing to", outFilename

# For debugging:
def _makeContactList(cityCodes):
    url = "https://www.facebook.com/search/me/friends/"
    for city in cityCodes:
        key = city
        url += key + "/residents/present/"
    url += "intersect"
    return url

queriesData = pickle.load(open("codes.pickle", "rb"))
cityCodes = []
output =  "# Columns: City, State, FB Code\n"
output += "mapping = [\n"
for query in queriesData:
    if queriesData[query]:
        cityAndState = query[len("facebook things to do in "):]
        city = cityAndState[:-4]
        state = cityAndState[-2:]
        code = queriesData[query]
        output += "(\"%s\", \"%s\", \"%s\"),\n" % (city, state, code)
        #cityCodes.append(queriesData[query])
output += "]"

with open(outFilename, 'wb') as f:
    f.write(output)
