# Summary
A Django Application which gives you a list of your friends in "Red States" or "Blue States."
You can also use it to generate your own lists - for example, friends who live in states whose senators could swing certain votes.

Your friends' senators don't represent you, but you can ask your friends to contact their senators.

View it live on [Heroku](https://www.redfriendsbluefriends.com).

# Generated URLs
When this project started, I used to search by state. Facebook has blocked that functionally, so instead, we now only find friends in the sixty most populous cities in each region.
This is not ideal. We'd like the following links to work again:
## [Your Red Friends](https://www.facebook.com/search/109146809103536/residents/present/112083625475436/residents/present/109714185714936/residents/present/104039182964473/residents/present/108337852519784/residents/present/112822538733611/residents/present/104083326294266/residents/present/104131666289619/residents/present/109306932420886/residents/present/108545005836236/residents/present/105528489480786/residents/present/109176885767113/residents/present/106153826081984/residents/present/108083605879747/residents/present/104037882965264/residents/present/111689148842696/residents/present/103994709636969/residents/present/111957282154793/residents/present/104004246303834/residents/present/108296539194138/residents/present/108037302558105/residents/present/108603925831326/residents/present/105818976117390/residents/present/104024609634842/residents/present/104164412953145/residents/present/103118929728297/residents/present/105493439483468/residents/present/109983559020167/residents/present/113067432040067/residents/present/108635949160808/residents/present/109438335740656/residents/present/112283278784694/residents/present/union/me/friends/intersect)
## [Your Blue Friends](https://www.facebook.com/search/110453875642908/residents/present/105643859470062/residents/present/109146809103536/residents/present/112083625475436/residents/present/113667228643818/residents/present/109714185714936/residents/present/105486989486087/residents/present/108325505857259/residents/present/108301835856691/residents/present/104131666289619/residents/present/109306932420886/residents/present/112825018731802/residents/present/105528489480786/residents/present/108295552526163/residents/present/109176885767113/residents/present/109564639069465/residents/present/106153826081984/residents/present/108131585873862/residents/present/107907135897622/residents/present/112386318775352/residents/present/111957282154793/residents/present/112750485405808/residents/present/108178019209812/residents/present/112439102104396/residents/present/104024609634842/residents/present/103118929728297/residents/present/112577505420980/residents/present/109706309047793/residents/present/109983559020167/residents/present/109564342404151/residents/present/union/me/friends/intersect)

If you know anyone at Facebook who can re-enable searching by state, please ask them or put me in contact with them!

# Credit
- [ProPublica](https://propublica.github.io/congress-api-docs/#lists-of-members) provides a fantastic aggregation of data on MoCs.

- [Reddit user taniapdx](https://propublica.github.io/congress-api-docs/#lists-of-members) has created the only mapping of states-to-facebook-codes that I could find on the web, and I assume it was manually and painstakenly collected.

- This project was inspired by [Indivisible Berkeley](http://www.indivisibleberkeley.org). \#resist

# Technical Details
## Running the code
You need the following environment variables:
- PROPUBLICA_API_KEY: [obtain it here](https://www.propublica.org/datastore/api/propublica-congress-api)
- DEBUG: set to "True" to enable, "False" to disable

After installing requirements and heroku CLI, you should be able to run `heroku local` to run it.


## Why not use the Facebook API?
I originally tried to use the Facebook Graph Search API to get the representatives and senators for all your friends, but Facebook privacy settings prevent apps from accessing information about your friends.
Generating a search URL for every district seems impossible, since congressional districts don't line up with searchable cities (and also because the search URL would contain every city in the US).

The original project using the Facebook API is available here: https://github.com/artoonie/django-redblue
