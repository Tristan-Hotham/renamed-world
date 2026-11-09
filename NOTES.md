# renamed-world: working notes

Brief: /home/claude/work/new9/BRIEFS.md (study 5) + shared rules in /home/claude/work/new8/BRIEFS.md and /home/claude/newdata/BRIEF.md.
Format refs: studies/church-orientation, sunless-valleys (shared ../ink-map/ engine, so the repo stays small).
Intermediates: /home/claude/scratch/renamed-world/work (not in repo; delete at end).

## Pipeline
- 01_events.py (~9 min): raw TSV -> statements (deduplicated), items (group by P31 class map in rules.py, else label words;
  present-day country from Natural Earth 10m, nearest within 30 km for coastal points), transitions per language (an end
  date within a year of another name's start date), events (transitions within a year merged).
- 02_classify.py (~2 min): flags spelling / status / qualifier / joined; waves by rules.py; Galician 2026 batch excluded;
  duplicates (same change twice on one item with no change back between; same change on two items within 5 km, keep the
  settlement then the lower QID); overrides.csv; renamed-back flag; name histories.
- 03_results.py: results.json, data/renamings.csv, renamings_other_kinds.csv, places.json (page), decades.csv, countries.csv.

## Data facts (checked)
- 118,507 rows, 32,309 items, 79,554 distinct name statements, 36,052 transitions, 33,454 events; 17,025 on places
  (settlements and administrative areas); the rest streets, stations, institutions, natural features.
- Wikidata class labels and country labels are NOT in the extract (QIDs only). Classes grouped by hand from sample labels
  (rules.py TYPE_GROUP); countries from Natural Earth point-in-polygon. Crimea counted with Ukraine (NE draws it in Russia).
- Galicia (ES): 1,859 events dated 2026 (1,260 on 2026-04-11, 624 on 2026-01-01), all gl: a bulk revision of the Galician
  gazetteer (articles O/A and spellings). Excluded as not renamings.
- 4,967 place items have an official name with an end date but no successor name: mergers, dissolutions. Not events by design.
- Coverage is very uneven: Ukraine, Romania, Russia, France, Japan dominate. Africa has very few dated official names
  (Kinshasa, Lubumbashi, Harare, Maputo...). Ireland: no Kingstown/Queenstown records at all (0 place events); UK: civil
  parish and urban district renamings only. Say so plainly; do not invent.
- Japan: most events are village to town to city (status) changes; excluded as status.

## Review by eye (done)
- All colonial (22), war (106), reversal (~440) events listed and read; the most-renamed top 30; renamed-back list (first
  ~60); UK and Ireland list; famous examples (Volgograd, St Petersburg, Nizhny Novgorod, Astana, Luhansk, Vladikavkaz, Dnipro,
  Donetsk, Chemnitz, Katowice, Brasov, Varna, Podgorica, Bishkek, Dushanbe, Gyumri, Kinshasa, Harare, Maputo, Mumbai,
  Chennai, Oslo, Tallinn, Gdansk, Wroclaw, Kaliningrad, Lyon, Bordeaux, La Roche-sur-Yon, Rybinsk).
- Samples of 25 to 30 of each other class (communist, nation, other, merger, spelling, status, qualifier, joined) per round.
- Fixes made from the review (rules, not one-offs): status words incl. Indonesian kota besar/kotapraja, Russian
  okrug/volost/uyezd/otdel/guberniya, CJK suffixes and the 大字 prefix, Slavonic adjective endings; comparisons on names
  without status words (Ukrainian rural councils were wrongly 'spelling'); 'joined' only with an explicit and/et/und/och;
  Ukrainian spellings of communist names (Cyrillic i/yi/ye normalised; chervon, zhovten, pershe travnia, Volodarsky,
  Tsiurupa, Torez, Andropov, Shcherbakov, Brezhnev, Dnipropetrovsk); state-farm placeholder names (sovkhoz settlement No 4)
  are Soviet naming, not undoing; French Revolution names 1790s and their undoing to 1815 only if the old name was a
  revolutionary one (so Napoleon-era La Roche-sur-Yon is 'other'); fallback 'under communist rule' ends 1989 (USSR) so
  1990 to 1991 national renamings are nation-building; institution words checked before admin words in label grouping.
- One-off overrides (code/overrides.csv): Zabrze 1920 and 1922 (bracketed German forms).
- Duplicates removed: same change twice on one item (25), same change on a second item within 5 km (~145).

## Done
- 04 figures (map, decades, europe, chains, countries, funnel, header), 05 page (index.html + js/page.js), 06 paper (9 pp),
  07 blog (6 figures, ~900 words) + Zenodo, 08 README/LICENSE/post, reddit collage (2700x4500). QA 0 console errors at 1280/390.
- Results: 6,848 renamings of 5,79x places from 17,025 dated name changes (see data/results.json for exact).

## References to verify (cited from memory; reviewer please check)
- Vrandecic, D. and Krotzsch, M. (2014) Wikidata: a free collaborative knowledgebase. Communications of the ACM 57(10), 78-85.
- Bast, H. and Buchhold, B. (2017) QLever: a query engine for efficient SPARQL+text search. CIKM 2017, 647-656.
- Azaryahu, M. (1996) The power of commemorative street names. Environment and Planning D 14(3), 311-330.
- Rose-Redwood, R., Alderman, D. and Azaryahu, M. (2010) Geographies of toponymic inscription. Progress in Human Geography 34(4), 453-470.
- Light, D. (2004) Street names in Bucharest, 1990-1997. Journal of Historical Geography 30(1), 154-172.
- Historical facts stated without the data: Kingstown -> Dun Laoghaire and Queenstown -> Cobh both 1920 (page and blog); Lyon renamed
  Commune-Affranchie as punishment for its 1793 revolt; Ukraine's decommunisation laws of 2015; Puturoasa from Romanian for stench.

## Not done / caveats
- No new data fetched. Wikidata class and country labels unavailable (QIDs only): classes grouped by hand from sample labels.
- Wave rules are heuristic; 'other' (27%) is mostly France and Japan local renamings (Japan pre-war village renamings may be mergers).

## Independent review (2026)
- Re-ran 01 to 07 from the raw extract. The published numbers did not reproduce exactly from the code as it stood (6,847
  renamings, not 6,848: an earlier 01 run with older class groups); everything is now regenerated from the current code.
- Fixes to rules (rules.py, 02_classify.py):
  - Ukraine 2015 to 2017: every renaming counted as undoing under the decommunisation laws (83 of the 261 renamings of 2016
    had been put in nation-building or admin reform because the old name, e.g. Komintern, Frunzivka, Petrovske, Uritske,
    Lunacharske, was not on the vocabulary list).
  - Communist vocabulary extended (Frunze, Komintern, revolution, Uritsky, Lunacharsky, Menzhinsky, Luxemburg, Ukrainian
    Kuibyshev, Khalturin, Postyshev, Kosior, Chubar, pioneer, five-year plan, International, Ustinov).
  - SOVIET_FROM: in regions annexed late (western Ukraine and Belarus 1939, Chernivtsi, Budjak, Karelia 1940,
    Transcarpathia, Kaliningrad, southern Sakhalin 1945) earlier renamings are no longer "under communist rule" (Finnish
    Kakisalmi 1917, Czechoslovak and Hungarian names in Transcarpathia, Polish names, German East Prussian renamings of 1938).
  - Spelling: one letter changed in Latin or Cyrillic names of 4+ letters (Bira/Bara, Koz'ia/Kiz'ia); kana ヶ = ケ.
- Text fixes: "most / almost all of the 1960s is one year" (it is 48%); 2024 Ukrainian renamings are under the 2023 law
  and 91 of 219 removed Soviet names (not "names that honoured Russia" only); blog list of Astana's names omitted Ak-Mola;
  decolonisation (22) now described everywhere as an artefact (20 famous cases checked: 7 absent from the extract, 2 with no
  dated change, 4 in other waves, 7 decolonisation; results.json decol_check); paper Table 5 split around Table 4 fixed.
- References verified online (all five correct as cited). Kingstown and Queenstown renamings both 1920 (confirmed).
- Not fixed (noted in the paper's limitations): renamings under German or Romanian occupation 1941 to 1944 in the USSR still
  count with Soviet rule; Hungarian Magyarisation (1890s to 1910s) and the 1919 Hungarian Soviet Republic are "other".
