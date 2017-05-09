# Summary
Generate a Facebook URL to search for friends in "Red States" or "Blue States."

Specifically, this searches for any friend in a state with at least one Senator in a given party.

Use this to have a discussion with your friends about topics you care about, and ask them to voice their opinion to their members of congress.


# Generated URLs
You don't need to run this code to see a list of your Red Friends or Blue Friends, you just need to click the links below:
Here are a list of your [Red Friends](https://www.facebook.com/search/109146809103536/residents/present/112083625475436/residents/present/109714185714936/residents/present/104039182964473/residents/present/105486989486087/residents/present/108325505857259/residents/present/108301835856691/residents/present/108337852519784/residents/present/112822538733611/residents/present/104083326294266/residents/present/104131666289619/residents/present/109306932420886/residents/present/108545005836236/residents/present/112825018731802/residents/present/105528489480786/residents/present/109176885767113/residents/present/106153826081984/residents/present/108083605879747/residents/present/104037882965264/residents/present/111689148842696/residents/present/103994709636969/residents/present/111957282154793/residents/present/104004246303834/residents/present/108296539194138/residents/present/108037302558105/residents/present/108603925831326/residents/present/105818976117390/residents/present/104024609634842/residents/present/104164412953145/residents/present/103118929728297/residents/present/105493439483468/residents/present/109983559020167/residents/present/113067432040067/residents/present/108635949160808/residents/present/109438335740656/residents/present/112283278784694/residents/present/union/me/friends/intersect).
Red Friends are from states: AK, AL, AR, AZ, CO, FL, GA, IA, ID, IN, KS, KY, LA, ME, MO, MS, MT, NC, ND, NE, NV, OH, OK, PA, SC, SD, TN, TX, UT, WI, WV, WY
 
Here are a list of your [Blue Friends](https://www.facebook.com/search/110453875642908/residents/present/105643859470062/residents/present/109146809103536/residents/present/112083625475436/residents/present/113667228643818/residents/present/109714185714936/residents/present/105486989486087/residents/present/108325505857259/residents/present/108301835856691/residents/present/104131666289619/residents/present/109306932420886/residents/present/112825018731802/residents/present/105528489480786/residents/present/108295552526163/residents/present/109176885767113/residents/present/109564639069465/residents/present/106153826081984/residents/present/108131585873862/residents/present/107907135897622/residents/present/112386318775352/residents/present/111957282154793/residents/present/112750485405808/residents/present/108178019209812/residents/present/112439102104396/residents/present/104024609634842/residents/present/103118929728297/residents/present/112577505420980/residents/present/109706309047793/residents/present/109983559020167/residents/present/109564342404151/residents/present/union/me/friends/intersect)
Blue Friends are from states: CA, CO, CT, DE, FL, HI, IL, IN, MA, MD, MI, MN, MO, MT, ND, NH, NJ, NM, NV, NY, OH, OR, PA, RI, VA, VT, WA, WI, WV

# Credit
[ProPublica](https://propublica.github.io/congress-api-docs/#lists-of-members) provides a fantastic aggregation of data on MoCs.
[Reddit user taniapdx](https://propublica.github.io/congress-api-docs/#lists-of-members) has created the only mapping of states-to-facebook-codes that I could find on the web, and I assume it was manually and painstakenly collected.

# Why only senators?
I originally tried to use the Facebook Graph Search API to get the representatives and senators for all your friends, but Facebook privacy settings prevent apps from accessing information about your friends.
Generating a search URL for every district seems impossible, since congressional districts don't line up with searchable cities (and also because the search URL would contain every city in the US).
The original project using the Facebook API is available here: https://github.com/artoonie/django-redblue
If you have suggestions on getting this to work for reps as well, please let me know.
