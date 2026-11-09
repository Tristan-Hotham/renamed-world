# The renamed world

Official renamings of places in Wikidata, by decade and by wave. Every Wikidata item with coordinates whose official name (P1448) carries a start or end date (32,309 items, 79,554 names) is read into name histories; the 17,025 dated changes of name on settlements and administrative areas are sorted into spelling, status and qualifier changes (set aside) and 6,842 true renamings, each assigned to a wave by written rules.

Interactive page: https://maps.tristanhotham.com/renamed-world/
Paper: https://doi.org/10.5281/zenodo.24075301
Blog post: https://blog.tristanhotham.com/2026/10/31/renamed-world/
Code and data: https://github.com/Tristan-Hotham/renamed-world

## Headline results

- 17,025 dated changes of official name on places; 47.9% keep the name (1,237 spellings, 3,185 status changes, 3,730 qualifiers); 1,859 Galician names dated 2026 (one gazetteer revision) and 170 duplicated records removed. 6,842 renamings of 5,769 places in 78 countries remain.
- Waves: decolonisation 22 (0.3%); revolution and communism 2,852 (41.7%); undoing revolutionary and communist names 529 (7.7%); war and new borders 107 (1.6%); nation-building and language policy 890 (13.0%); mergers and administrative reform 548 (8.0%); other renamings 1,894 (27.7%).
- Busiest decade: the 1960s (1,242); busiest year: Romania 1964 (596 villages). Ukraine: 261 renamings in 2016 (decommunisation) and 219 in 2024.
- 860 places renamed twice or more, 158 three times or more; 303 returned to an earlier name. Astana: 6 renamings.
- Coverage is very uneven: 47.4% of renamings are in the former Soviet Union; most renamings: Ukraine 1,515, Romania 1,053, Russia 777, France 563, Japan 532, China 314, Armenia 290, Canada 221. Africa 35, the UK 23, Ireland none.
- The decolonisation wave (22) is an artefact of the record, not a finding: of 20 well-known renamings away from colonial names in Africa and Asia, 7 are not in the extract at all, 2 have no dated change, 4 fall in other waves (Bombay to Mumbai and Madras to Chennai came more than 25 years after independence) and 7 are counted as decolonisation.
- 4,946 places have an official name that ends with no successor (mostly merged municipalities); these are not counted as renamings.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive page: The Inked World base map (shared engine from ../ink-map/), every renaming coloured by wave, decade slider, search by old or new name, popups with the name history. |
| `header.png` | Social card, 1200 x 630. |
| `data/renamings.csv` | Every dated change of name on places (17,025 rows): QID, label, position, country, kind, year and date, old and new name (display and local language), languages, whether it is a renaming, wave and reason, minor flag, exclusion reason, renamed back. |
| `data/renamings_other_kinds.csv` | Renamings of streets, stations, institutions and natural features (13,573), not analysed. |
| `data/decades.csv`, `data/countries.csv` | Renamings by decade and by country, by wave. |
| `data/overrides_applied.csv` | Hand corrections. |
| `data/places.json` | Page data. |
| `data/results.json` | Every number quoted anywhere. |
| `code/` | Scripts in order, `rules.py` (every classification rule), templates, `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- A renaming: within one language, a name whose end date is within a year of another name's start date; transitions in several languages within a year are one event. Names ending with no successor are not events.
- Set aside: spelling (same after accents and punctuation, similarity at least 0.8, or the same consonants), status (same after removing status words such as town, city, district, rural council, Bezirksamt, and CJK suffixes), qualifier (one name's words a subset of the other's). Names joined with and, et, und count as mergers.
- Waves by rules in order: undoing communist or revolutionary names (and every Ukrainian renaming of 2015 to 2017, made under the decommunisation laws); communist names given; war and new borders; renamed under communist rule (from 1939, 1940 or 1945 only in the regions annexed then: western Ukraine and Belarus, Bessarabia, Transcarpathia, Kaliningrad, Karelia, southern Sakhalin); merger programmes and admin reform; decolonisation (independence minus 3 to plus 25 years); nation-building and language policy; other. See `code/rules.py`.
- Checked by eye: all decolonisation, war and undoing events, places renamed three times or more, every place named in the text, samples of the rest. 11.9% of name changes on places removed as errors, duplicates or the Galician batch.
- Caveats: counts describe Wikidata's record, not the world; dates as recorded; waves are rules, not a historian's reading of each case.

## How to rerun

Needs Python 3 with pandas, geopandas, shapely, pyproj, matplotlib, scipy and Pillow; xelatex (TeX Gyre Pagella, Inter, FreeSerif, Noto Serif CJK); node with Playwright for `code/qa.js`. Raw input path in `code/common.py`.

```
python3 code/01_events.py      # name statements, transitions, events (about 10 minutes)
python3 code/02_classify.py    # flags, waves, duplicates, overrides, histories
python3 code/03_results.py     # results.json and data files
python3 code/04_figures.py     # figures and header
python3 code/05_build_site.py  # index.html
python3 code/06_paper.py       # paper PDF (set DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py      # collage
python3 code/08_readme.py      # README, LICENSE, Reddit post
python3 code/07_release.py     # blog post, Zenodo files
```

## Sources and licences

- Wikidata (https://www.wikidata.org/), CC0, queried with QLever.
- Natural Earth (public domain): present-day countries.
- Base map on the page: The Inked World (https://maps.tristanhotham.com/ink-map/), OpenStreetMap vector tiles by OpenFreeMap (ODbL), AWS Terrain Tiles. Fonts: MedievalSharp, IM Fell (SIL OFL).
- Derived data CC0; text and figures CC BY 4.0; code MIT.

## Citation

Hotham, T. (2026) The renamed world: official renamings of places in Wikidata, by decade and by wave. Zenodo. 10.5281/zenodo.24075301

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
