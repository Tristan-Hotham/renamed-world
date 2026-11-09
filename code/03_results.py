"""Step 3: results.json (every number quoted anywhere), the derived data files and the page data.
Output: data/results.json, data/renamings.csv (every event with its flags and wave), data/places.json (page),
data/decades.csv, data/countries.csv, data/overrides_applied.csv
"""
import numpy as np, pandas as pd
from common import *
from rules import *

ev = pd.read_pickle(f"{WORK}/events.pkl")
st = pd.read_pickle(f"{WORK}/statements.pkl")
it = pd.read_pickle(f"{WORK}/items.pkl")
hist = pd.read_pickle(f"{WORK}/histories.pkl")
c1, c2 = jload(f"{WORK}/counts1.json"), jload(f"{WORK}/counts2.json")
ev["group"] = ev.group.fillna("other")
CORE_G = ev.group.isin(CORE)
core = ev[CORE_G]
R = {}
ren = core[core.renaming].copy()
ren["decade"] = ren.year // 10 * 10
R["n"] = {"rows": c1["n_rows"], "items": c1["n_items"], "statements": c1["n_statements"], "transitions": c1["n_transitions"],
          "events": int(len(ev)), "events_core": int(len(core)), "renamings": int(len(ren)), "places_renamed": int(ren.q.nunique()),
          "countries": int(ren.iso.nunique()),
          "spelling": int(((core.wave == "spelling") & (core.excluded == "")).sum()),
          "status": int(((core.wave == "status") & (core.excluded == "")).sum()),
          "qualifier": int(((core.wave == "qualifier") & (core.excluded == "")).sum()),
          "galician": int(core.excluded.str.startswith("Galician").sum()),
          "dup_same": int(core.excluded.str.startswith("the same change").sum()),
          "dup_two": int(core.excluded.str.startswith("a second Wikidata").sum()),
          "overridden": c2["n_overridden_events"], "since1800": int((ren.year >= 1800).sum())}
R["n"]["dup_x"] = R["n"]["dup_same"] + R["n"]["dup_two"]
R["n"]["minor"] = R["n"]["spelling"] + R["n"]["status"] + R["n"]["qualifier"]
R["n"]["removed_errors"] = R["n"]["galician"] + R["n"]["dup_same"] + R["n"]["dup_two"] + R["n"]["overridden"]
R["n"]["corrected_pc"] = round(100 * R["n"]["removed_errors"] / R["n"]["events_core"], 1)
R["n"]["minor_pc"] = round(100 * R["n"]["minor"] / R["n"]["events_core"], 1)
R["n"]["renaming_pc"] = round(100 * R["n"]["renamings"] / R["n"]["events_core"], 1)
# items whose official name ends with no successor: an end date that is not a renaming
stc = st[st.q.isin(set(it.index[it.group.isin(CORE)]))] if "group" in it else st
ended = set(stc[stc.ey.notna()].q)
with_ev = set(core.q)
R["n"]["ended_no_successor"] = int(len(ended - with_ev))
# the other kinds of thing
oth = ev[~CORE_G & ev.renaming]
R["other_kinds"] = {g: int((oth.group == g).sum()) for g in ["street", "station", "institution", "nature", "other"]}
R["other_kinds"]["total"] = int(len(oth))
# waves
R["waves"] = {}
for w in WAVES:
    s = ren[ren.wave == w]
    dec = s.groupby("decade").size()
    R["waves"][w] = {"name": WAVE_NAME[w], "n": int(len(s)), "pc": round(100 * len(s) / len(ren), 1),
                     "countries": int(s.iso.nunique()),
                     "top": [[k, int(v)] for k, v in s.groupby("iso").size().sort_values(ascending=False).head(5).items()],
                     "peak_decade": int(dec.idxmax()) if len(dec) else None, "peak_decade_n": int(dec.max()) if len(dec) else 0}
R["political_pc"] = round(sum(R["waves"][w]["pc"] for w in ("colonial", "communist", "reversal", "war", "nation")), 1)
# decades from 1800
d = ren[ren.year >= 1800].groupby(["decade", "wave"]).size().unstack(fill_value=0).reindex(columns=WAVES, fill_value=0)
d = d.reindex(range(1800, 2030, 10), fill_value=0)
d.to_csv(f"{DATA}/decades.csv")
R["decades"] = [{"decade": int(k), "total": int(v.sum()), **{w: int(v[w]) for w in WAVES}} for k, v in d.iterrows()]
top = d.sum(axis=1).sort_values(ascending=False)
R["peak_decades"] = [{"decade": int(k), "n": int(v), "main_wave": d.loc[k].idxmax(), "main_n": int(d.loc[k].max())} for k, v in top.head(5).items()]
yr = ren.groupby(["year", "iso"]).size().sort_values(ascending=False)
R["peak_years"] = [{"year": int(y), "iso": i, "country": ren[ren.iso == i].country.iloc[0], "n": int(v)} for (y, i), v in yr.head(8).items()]
# countries
cn = ren.groupby("iso").agg(n=("q", "size"), places=("q", "nunique"), country=("country", "first"))
cw = ren.groupby(["iso", "wave"]).size().unstack(fill_value=0)
cn = cn.join(cw).sort_values("n", ascending=False)
cn.to_csv(f"{DATA}/countries.csv")
R["countries"] = [{"iso": k, "country": r.country, "n": int(r.n), "places": int(r.places), "main_wave": cw.loc[k].idxmax(),
                   "pc_of_all": round(100 * r.n / len(ren), 1)} for k, r in cn.head(15).iterrows()]
R["top5_pc"] = round(100 * cn.n.head(5).sum() / len(ren), 1)
R["former_ussr"] = {"n": int(ren.iso.isin(USSR).sum()), "pc": round(100 * ren.iso.isin(USSR).mean(), 1)}
R["continents"] = {k: int(v) for k, v in ren.groupby("continent").size().sort_values(ascending=False).items()}


def chain(q):
    g = ren[ren.q == q].sort_values("year")
    return [{"year": int(r.year), "old": r.old, "new": r.new, "wave": r.wave} for r in g.itertuples()]


# most renamed
n_by = ren.groupby("q").size().sort_values(ascending=False, kind="stable")
R["most_renamed"] = [{"q": q, "label": ren[ren.q == q].label.iloc[0], "iso": ren[ren.q == q].iso.iloc[0], "n": int(v), "chain": chain(q)}
                     for q, v in n_by.head(25).items()]
R["n_renamed_3plus"] = int((n_by >= 3).sum()); R["n_renamed_2plus"] = int((n_by >= 2).sum())
# renamed back
b = ren[ren.back]
R["back"] = {"events": int(len(b)), "places": int(b.q.nunique()), "by_wave": {w: int((b.wave == w).sum()) for w in WAVES}}
# named examples (labels are Wikidata English labels)
EX = {"volgograd": ("Volgograd", "RU"), "st_petersburg": ("Saint Petersburg", "RU"), "nizhny": ("Nizhny Novgorod", "RU"),
      "yekaterinburg": ("Yekaterinburg", "RU"), "samara": ("Samara", "RU"), "tver": ("Tver", "RU"), "astana": ("Astana", "KZ"),
      "luhansk": ("Luhansk", "UA"), "vladikavkaz": ("Vladikavkaz", "RU"), "dnipro": ("Dnipro", "UA"), "donetsk": ("Donetsk", "UA"),
      "kropyvnytskyi": ("Kropyvnytskyi", "UA"), "mariupol": ("Mariupol", "UA"), "chemnitz": ("Chemnitz", "DE"), "katowice": ("Katowice", "PL"),
      "brasov": ("Brașov", "RO"), "varna": ("Varna", "BG"), "podgorica": ("Podgorica", "ME"), "bishkek": ("Bishkek", "KG"),
      "dushanbe": ("Dushanbe", "TJ"), "gyumri": ("Gyumri", "AM"), "almaty": ("Almaty", "KZ"), "kinshasa": ("Kinshasa", "CD"),
      "harare": ("Harare", "ZW"), "maputo": ("Maputo", "MZ"), "mumbai": ("Mumbai", "IN"), "chennai": ("Chennai", "IN"),
      "oslo": ("Oslo", "NO"), "tallinn": ("Tallinn", "EE"), "gdansk": ("Gdańsk", "PL"), "wroclaw": ("Wrocław", "PL"),
      "kaliningrad": ("Kaliningrad", "RU"), "lyon": ("Lyon", "FR"), "bordeaux": ("Bordeaux", "FR"), "rybinsk": ("Rybinsk", "RU"),
      "hcmc": ("Ho Chi Minh City", "VN"), "la_roche": ("La Roche-sur-Yon", "FR"), "taipei": ("Taipei", "TW"), "kirov": ("Kirov", "RU"),
      "lubumbashi": ("Lubumbashi", "CD"), "khujand": ("Khujand", "TJ"), "ulyanovsk": ("Ulyanovsk", "RU"), "karakol": ("Karakol", "KG")}
R["ex"] = {}
for k, (lab, iso) in EX.items():
    g = ren[(ren.label == lab) & (ren.iso == iso)]
    if not len(g):
        print("example missing", k); continue
    q = g.groupby("q").size().sort_values(ascending=False).index[0]
    R["ex"][k] = {"q": q, "label": lab, "iso": iso, "chain": chain(q)}
# Ukraine, Romania 1964, the French Revolution, decolonisation, the UK and Ireland
ua = ren[ren.iso == "UA"]
R["ukraine"] = {"n": int(len(ua)), "y2016": int((ua.year == 2016).sum()), "y2015_17": int(ua.year.between(2015, 2017).sum()),
                "y2023_25": int(ua.year.between(2023, 2025).sum()), "y2024": int((ua.year == 2024).sum()),
                "reversal_2015": int(((ua.wave == "reversal") & (ua.year >= 2015)).sum()),
                "nation_2022": int(((ua.wave == "nation") & (ua.year >= 2022)).sum())}
ro = ren[ren.iso == "RO"]
R["romania"] = {"n": int(len(ro)), "y1964": int((ro.year == 1964).sum()), "y1960s": int(ro.year.between(1960, 1969).sum())}
fr = ren[ren.iso == "FR"]
R["france"] = {"n": int(len(fr)), "revolution": int((fr.why == "French Revolution").sum()), "y1793": int(((fr.why == "French Revolution") & (fr.year == 1793)).sum()),
               "restored": int((fr.why == "after the French Revolution").sum())}
col = ren[ren.wave == "colonial"]
R["colonial"] = {"n": int(len(col)), "africa": int((col.continent == "Africa").sum()), "cd": int((col.iso == "CD").sum())}
gb = core[core.iso == "GB"]
R["uk"] = {"events": int(len(gb)), "renamings": int(gb.renaming.sum()), "merger": int((gb.renaming & (gb.wave == "merger")).sum())}
R["ireland"] = {"events": int((core.iso == "IE").sum()), "items_any": int((it.iso == "IE").sum())}
R["india"] = {"renamings": int((ren.iso == "IN").sum())}
R["africa"] = {"renamings": int((ren.continent == "Africa").sum()), "pc": round(100 * (ren.continent == "Africa").mean(), 1)}
R["japan"] = {"events": int((core.iso == "JP").sum()), "status": int(((core.iso == "JP") & (core.wave == "status")).sum()),
              "renamings": int((ren.iso == "JP").sum())}
R["soviet"] = {"communist_ussr": int(((ren.wave == "communist") & ren.iso.isin(USSR)).sum()),
               "reversal_ussr": int(((ren.wave == "reversal") & ren.iso.isin(USSR)).sum()),
               "token_given": int((ren.why == "communist name given").sum()), "destal": int((ren.why == "de-Stalinisation").sum()),
               "post": int((ren.why == "after communism").sum())}
# share of the busiest decade that is the busiest single year (Romania 1964)
R["peak_year_share_pc"] = round(100 * R["peak_years"][0]["n"] / R["peak_decades"][0]["n"])
R["ukraine"]["y2016_reversal"] = int(((ua.year == 2016) & (ua.wave == "reversal")).sum())
R["ukraine"]["y2024_reversal"] = int(((ua.year == 2024) & (ua.wave == "reversal")).sum())
# decolonisation: twenty well-known renamings away from colonial-era names in Africa and Asia, checked against the extract.
# Most are missing or dated too late for the rule, so the size of the decolonisation wave is an artefact of the record.
FAMOUS = [("Kinshasa", "CD"), ("Lubumbashi", "CD"), ("Kisangani", "CD"), ("Harare", "ZW"), ("Maputo", "MZ"), ("N'Djamena", "TD"),
          ("Banjul", "GM"), ("Bujumbura", "BI"), ("Antananarivo", "MG"), ("Annaba", "DZ"), ("Kabwe", "ZM"), ("Huambo", "AO"),
          ("Malabo", "GQ"), ("Jakarta", "ID"), ("Mumbai", "IN"), ("Chennai", "IN"), ("Kolkata", "IN"), ("Yangon", "MM"),
          ("Dhaka", "BD"), ("Ho Chi Minh City", "VN")]
fam = []
for lab, iso in FAMOUS:
    inx = bool(((it.label == lab) & (it.iso == iso)).any())
    g = ren[(ren.label == lab) & (ren.iso == iso)]
    fam.append({"label": lab, "iso": iso, "in_extract": inx, "renamed": bool(len(g)), "wave": g.wave.iloc[0] if len(g) else None})
R["decol_check"] = {"n": len(fam), "absent": sum(not f["in_extract"] for f in fam), "no_event": sum(f["in_extract"] and not f["renamed"] for f in fam),
                    "colonial": sum(f["wave"] == "colonial" for f in fam), "other_wave": sum(bool(f["wave"]) and f["wave"] != "colonial" for f in fam),
                    "cases": fam}
R["wave_order"] = WAVES
R["wave_name"] = {w: WAVE_NAME[w] for w in WAVES + ["spelling", "status", "qualifier"]}
R["wave_col"] = WAVE_COL
R["year_min"] = int(ren.year.min()); R["year_max"] = int(ren.year.max())

# ---------------- data files
out = ev[CORE_G].copy()
out["minor"] = out.wave.where(out.wave.isin(["spelling", "status", "qualifier"]), "")
cols = ["q", "label", "lon", "lat", "iso", "country", "group", "year", "date", "old", "new", "lang", "old_local", "new_local", "lang_local",
        "langs", "renaming", "wave", "why", "minor", "excluded", "back"]
out[cols].sort_values(["iso", "q", "year"]).to_csv(f"{DATA}/renamings.csv", index=False)
oth_out = ev[~CORE_G & ev.renaming][["q", "label", "lon", "lat", "iso", "group", "year", "old", "new", "lang", "wave"]]
oth_out.to_csv(f"{DATA}/renamings_other_kinds.csv", index=False)
ov = pd.read_csv(os.path.join(ROOT, "code", "overrides.csv"), comment="#", dtype=str).fillna("")
ov.to_csv(f"{DATA}/overrides_applied.csv", index=False)
# ---------------- page data: one row per place, one per event
pl = ren.groupby("q").agg(lon=("lon", "first"), lat=("lat", "first"), iso=("iso", "first"), country=("country", "first"),
                          label=("label", "first")).reset_index()
pl["now"] = [ren[ren.q == q].sort_values("year").new.iloc[-1] for q in pl.q]
pl = pl.sort_values("q").reset_index(drop=True)
idx = {q: i for i, q in enumerate(pl.q)}
W = {w: i for i, w in enumerate(WAVES)}
evs = [[idx[r.q], int(r.year), W[r.wave], r.old, r.new, 1 if r.back else 0] for r in ren.sort_values(["year", "q"]).itertuples()]
places = []
for r in pl.itertuples():
    h = hist.get(r.q, [])[:14]
    places.append([r.q, r.label if isinstance(r.label, str) else r.now, round(r.lon, 4), round(r.lat, 4), r.iso, r.country,
                   [[n, a, b] for n, a, b in h]])
jsave({"waves": WAVES, "wave_name": [WAVE_NAME[w] for w in WAVES], "wave_col": [WAVE_COL[w] for w in WAVES], "places": places, "events": evs},
      f"{DATA}/places.json", nodash=False)
jsave(R, f"{DATA}/results.json", indent=1, nodash=False)
print(json.dumps(R["n"], indent=0)[:1500])
print({w: R["waves"][w]["n"] for w in WAVES}, R["peak_decades"][:3], R["peak_years"][:4])
print(os.path.getsize(f"{DATA}/places.json") // 1024, "KB places.json")
