**Title:** [OC] The renamed world: 6,842 official renamings of places in Wikidata, by decade and by why. The busiest year was Romania in 1964, when 596 villages got new names

**Body:**

I read every official name in Wikidata that has a start or end date and rebuilt the name history of each place.

- Of 17,025 dated name changes on towns, villages and regions, 48% keep the name (new spelling, village to town, a qualifier like -sur-Mer). 6,842 are true renamings.
- Biggest wave: revolution and communism (2,852), then nation-building and language (890). 529 undid communist or revolutionary names (Leningrad back to St Petersburg, Karl-Marx-Stadt back to Chemnitz).
- Busiest decade: the 1960s. Ukraine: 261 renamings in 2016 and 219 in 2024.
- 303 places went back to an earlier name. Vladikavkaz was Ordzhonikidze twice; Luhansk was Voroshilovgrad twice.
- Big caveat: this maps Wikidata's record. 47% of renamings are in the former USSR; Africa has only 35, the UK 23.

Interactive map (decade slider, tap any place for its name history): https://maps.tristanhotham.com/renamed-world/

**Source comment:**

Data: Wikidata official name (P1448) with start and end dates, via QLever (CC0); Natural Earth for present-day countries. Tools: Python (pandas, geopandas, matplotlib), MapLibre. Waves assigned by written rules (country, date, words in the names), checked by eye. Paper and code: https://github.com/Tristan-Hotham/renamed-world
