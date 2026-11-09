"""Step 8: README.md, LICENSE and reddit/post.md from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
n, W = R["n"], R["waves"]
waves = "; ".join(f"{W[w]['name'].lower()} {W[w]['n']:,} ({W[w]['pc']:.1f}%)" for w in R["wave_order"])
top = ", ".join(f"{c['country']} {c['n']:,}" for c in R["countries"][:8])
readme = f"""# The renamed world

Official renamings of places in Wikidata, by decade and by wave. Every Wikidata item with coordinates whose official name (P1448) carries a start or end date ({n['items']:,} items, {n['statements']:,} names) is read into name histories; the {n['events_core']:,} dated changes of name on settlements and administrative areas are sorted into spelling, status and qualifier changes (set aside) and {n['renamings']:,} true renamings, each assigned to a wave by written rules.

Interactive page: https://maps.tristanhotham.com/renamed-world/
Paper: {{https://doi.org/10.5281/zenodo.24075301}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/renamed-world/}}
Code and data: https://github.com/Tristan-Hotham/renamed-world

## Headline results

- {n['events_core']:,} dated changes of official name on places; {n['minor_pc']:.1f}% keep the name ({n['spelling']:,} spellings, {n['status']:,} status changes, {n['qualifier']:,} qualifiers); {n['galician']:,} Galician names dated 2026 (one gazetteer revision) and {n['dup_x']:,} duplicated records removed. {n['renamings']:,} renamings of {n['places_renamed']:,} places in {n['countries']} countries remain.
- Waves: {waves}.
- Busiest decade: the {R['peak_decades'][0]['decade']}s ({R['peak_decades'][0]['n']:,}); busiest year: Romania 1964 ({R['romania']['y1964']} villages). Ukraine: {R['ukraine']['y2016']} renamings in 2016 (decommunisation) and {R['ukraine']['y2024']} in 2024.
- {R['n_renamed_2plus']:,} places renamed twice or more, {R['n_renamed_3plus']} three times or more; {R['back']['places']} returned to an earlier name. Astana: {R['most_renamed'][0]['n']} renamings.
- Coverage is very uneven: {R['former_ussr']['pc']:.1f}% of renamings are in the former Soviet Union; most renamings: {top}. Africa {R['africa']['renamings']}, the UK {R['uk']['renamings']}, Ireland none.
- The decolonisation wave ({W['colonial']['n']}) is an artefact of the record, not a finding: of {R['decol_check']['n']} well-known renamings away from colonial names in Africa and Asia, {R['decol_check']['absent']} are not in the extract at all, {R['decol_check']['no_event']} have no dated change, {R['decol_check']['other_wave']} fall in other waves (Bombay to Mumbai and Madras to Chennai came more than 25 years after independence) and {R['decol_check']['colonial']} are counted as decolonisation.
- {n['ended_no_successor']:,} places have an official name that ends with no successor (mostly merged municipalities); these are not counted as renamings.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive page: The Inked World base map (shared engine from ../ink-map/), every renaming coloured by wave, decade slider, search by old or new name, popups with the name history. |
| `header.png` | Social card, 1200 x 630. |
| `data/renamings.csv` | Every dated change of name on places ({n['events_core']:,} rows): QID, label, position, country, kind, year and date, old and new name (display and local language), languages, whether it is a renaming, wave and reason, minor flag, exclusion reason, renamed back. |
| `data/renamings_other_kinds.csv` | Renamings of streets, stations, institutions and natural features ({R['other_kinds']['total']:,}), not analysed. |
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
- Checked by eye: all decolonisation, war and undoing events, places renamed three times or more, every place named in the text, samples of the rest. {n['corrected_pc']:.1f}% of name changes on places removed as errors, duplicates or the Galician batch.
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

Hotham, T. (2026) The renamed world: official renamings of places in Wikidata, by decade and by wave. Zenodo. {{10.5281/zenodo.24075301}}

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """Code (code/, js/, reddit/collage.py): MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text, figures and the paper: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
Derived data (data/): CC0 1.0, like its source, Wikidata.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""**Title:** [OC] The renamed world: {n['renamings']:,} official renamings of places in Wikidata, by decade and by why. The busiest year was Romania in 1964, when {R['romania']['y1964']} villages got new names

**Body:**

I read every official name in Wikidata that has a start or end date and rebuilt the name history of each place.

- Of {n['events_core']:,} dated name changes on towns, villages and regions, {n['minor_pc']:.0f}% keep the name (new spelling, village to town, a qualifier like -sur-Mer). {n['renamings']:,} are true renamings.
- Biggest wave: revolution and communism ({W['communist']['n']:,}), then nation-building and language ({W['nation']['n']:,}). {W['reversal']['n']} undid communist or revolutionary names (Leningrad back to St Petersburg, Karl-Marx-Stadt back to Chemnitz).
- Busiest decade: the {R['peak_decades'][0]['decade']}s. Ukraine: {R['ukraine']['y2016']} renamings in 2016 and {R['ukraine']['y2024']} in 2024.
- {R['back']['places']} places went back to an earlier name. Vladikavkaz was Ordzhonikidze twice; Luhansk was Voroshilovgrad twice.
- Big caveat: this maps Wikidata's record. {R['former_ussr']['pc']:.0f}% of renamings are in the former USSR; Africa has only {R['africa']['renamings']}, the UK {R['uk']['renamings']}.

Interactive map (decade slider, tap any place for its name history): https://maps.tristanhotham.com/renamed-world/

**Source comment:**

Data: Wikidata official name (P1448) with start and end dates, via QLever (CC0); Natural Earth for present-day countries. Tools: Python (pandas, geopandas, matplotlib), MapLibre. Waves assigned by written rules (country, date, words in the names), checked by eye. Paper and code: https://github.com/Tristan-Hotham/renamed-world
"""
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
for t in (readme, post):
    for bad in ("—", "–", "DSIT", "DCMS"):
        assert bad not in t, bad
print("readme", len(readme.split()), "words")
