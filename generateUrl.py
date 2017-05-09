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
    """ Returns a list of states with at least one senator in the Party. """
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

def loadStateData():
    """ Returns a mapping from states abbreviations to their facebook
        code and the full state name. """
    stateData = {}
    with open('stateToFbCode.txt', 'rb') as dataFile:
        for line in dataFile:
            if line.startswith('#'): continue
            splitLine = line.split(',')
            stateCode = splitLine[0].strip()
            fullStateName = splitLine[1].strip()
            fbCode = splitLine[2].strip()
            stateData[stateCode] = {}
            stateData[stateCode]['fbcode'] = fbCode
            stateData[stateCode]['name'] = fullStateName
    return stateData

# Load data
stateData = loadStateData()
stateToParty = {} # key: party, val: result of loadStateToParty(party)
for party in (Republican, Democrat):
    stateToParty[party] = loadStateToParty(party)

# Print URLs
for party in stateToParty:
    url = "https://www.facebook.com/search/"
    stateToParty[party] = loadStateToParty(party)
    for state in stateToParty[party]:
        key = stateData[state]['fbcode']
        url += key + "/residents/present/"
    url += "union/me/friends/intersect"
    print partyToText(party) + " Friends URL:"
    print url
    print

# Print a CSV containing state,color for the D3 visualization
stateColors = {} # key: state full name, val: 0 for dem, 1 for rep, 2 for both
for state in stateData:
    currStateData = stateData[state]
    fullStateName = currStateData['name']
    isBlue = state in stateToParty[Democrat]
    isRed = state in stateToParty[Republican]
    if isBlue and isRed:
        stateColors[fullStateName] = 0
    elif isBlue:
        stateColors[fullStateName] = 1
    elif isRed:
        stateColors[fullStateName] = 2
    else:
        assert False
for state in sorted(stateColors.keys()):
    print state + "," + str(stateColors[state])
