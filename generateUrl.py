# Example URL: https://www.facebook.com/search/106153826081984/residents/present/108296539194138/residents/present/union/me/friends/intersect

import json

Democrat = "D"
Republican = "R"
def partyToText(whichParty):
    if whichParty == Democrat:
        return "Blue"
    elif whichParty == Republican:
        return "Red"
    else:
        assert False

def loadStateToParty(whichParty):
    """ Returns a list of states with at least one senator in the Party.
        Generated via the ProPublica API:
         """
    with open('moc.json', 'rb') as dataFile:
        data = json.load(dataFile)

    assert data['status'] == 'OK'
    results = data['results']
    assert len(results) == 1 # could have multiple congresses?
    result = results[0]

    assert result['congress'] == '115'
    assert result['chamber'] == 'Senate'
    assert result['offset'] == '0'

    membersInParty = set()
    for member in result['members']:
        if member['party'] == whichParty:
            membersInParty.add(member['state'])

    partyText = partyToText(whichParty)
    print partyText + " Friends are from states: " + ', '.join(sorted(membersInParty))
    return membersInParty

def loadStateToFbCode():
    # A singe line looks like:
    # AL  Alabama 104037882965264 1 Mar 2016
    stateToFbCode = {}
    with open('stateToFbCode.txt', 'rb') as dataFile:
        for line in dataFile:
            if line.startswith('#'): continue
            splitLine = line.split(',')
            stateCode = splitLine[0].strip()
            fbCode = splitLine[2].strip()
            stateToFbCode[stateCode] = fbCode
    return stateToFbCode

stateToFbCode = loadStateToFbCode()

for party in (Republican, Democrat):
    url = "https://www.facebook.com/search/"
    for state in loadStateToParty(party):
        key = stateToFbCode[state]
        url += key + "/residents/present/"
    url += "union/me/friends/intersect"
    print partyToText(party) + " Friends URL:"
    print url
    print
