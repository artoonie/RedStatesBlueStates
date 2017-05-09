== Summary ==
Generate a Facebook URL to search for friends in "Red States" or "Blue States."

Specifically, this searches for any friend in a state with at least one Senator in a given party.

Use this to have a discussion with your friends about topics you care about, and ask them to voice their opinion to their members of congress.


== Work-in-progress ==
I'm waiting for the Pro-Publica API Key to be able to download the full list of Senators

== Credit ==
[ProPublica](https://propublica.github.io/congress-api-docs/#lists-of-members) provides a fantastic aggregation of data on MoCs.
[Reddit user taniapdx](https://propublica.github.io/congress-api-docs/#lists-of-members) has created the only mapping of states-to-facebook-codes that I could find on the web, and I assume it was manually and painstakenly collected.

== Why only senators? ==
I originally tried to use the Facebook Graph Search API to get the representatives and senators for all your friends, but Facebook privacy settings prevent apps from accessing information about your friends.
Generating a search URL for every district seems impossible, since congressional districts don't line up with searchable cities (and also because the search URL would contain every city in the US).
The original project using the Facebook API is available here: https://github.com/artoonie/django-redblue
If you have suggestions on getting this to work for reps as well, please let me know.
