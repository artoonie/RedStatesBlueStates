# Convert codes.pickle to a .py file containing all the codes.
# Usage: pass in the output .py filename.

import codecs
import pickle
import sys

if len(sys.argv) != 2:
    print "You must pass in the output python filename as an argument."
    sys.exit(-1)
outFilename = sys.argv[1]

queriesData = pickle.load(open("codes.pickle", "rb"))
cityCodes = []
output =  "# Columns: City, State, FB Code\n"
output += "# -*- coding: utf-8 -*-\n"
output += "mapping = [\n"
for query in queriesData:
    if queriesData[query]:
        cityAndState = query[len("facebook things to do in "):]

        # Some city names are unicode (Espa\xf1ola, NM for example)
        city = cityAndState[:-4].decode('latin-1')
        state = cityAndState[-2:]
        code = queriesData[query]
        output += "(\"%s\", \"%s\", \"%s\"),\n" % (unicode(city), state, code)
output += "]"

with codecs.open(outFilename, 'wb', 'utf-8') as f:
    f.write(output)
