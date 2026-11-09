"""Step 1: from the raw Wikidata rows to name histories and renaming events.

A renaming event is read from the official name (P1448) statements of one item: in one language, a name whose end date
falls within a year of the start date of a different name. Transitions in several languages in the same year or the next
are one event. Names that end with no successor (a municipality merged away, a station closed) are not events.
Output: WORK/items.pkl, WORK/events_raw.pkl (one row per event, with its transitions), WORK/statements.pkl, WORK/transitions.pkl
"""
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import Point
from common import *
from rules import *

df = pd.read_csv(RAW, sep="\t", dtype=str, quoting=3)
df.columns = [c.lstrip("?") for c in df.columns]
n_rows = len(df)
df["q"] = df["item"].str.extract(r"(Q\d+)")[0]
df["t"] = df["type"].str.extract(r"(Q\d+)")[0]
df["c"] = df["country"].str.extract(r"(Q\d+)")[0]
df["label"] = df["itemLabel"].str.extract(r'^"(.*)"@')[0]
m = df["name"].str.extract(r'^"(.*)"@([\w-]+)$')
df["nm"], df["lang"] = m[0].str.replace(r'\\"', '"', regex=True), m[1]
xy = df["coord"].str.extract(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)").astype(float)
df["lon"], df["lat"] = xy[0], xy[1]

# ---------------- items
it = df.groupby("q").agg(label=("label", "first"), lon=("lon", "first"), lat=("lat", "first"),
                         types=("t", lambda s: sorted(set(s.dropna()))), wdc=("c", lambda s: sorted(set(s.dropna()))))


def group_of(types, label):
    gs = {TYPE_GROUP[t] for t in types if t in TYPE_GROUP}
    for g in GROUP_ORDER:
        if g in gs:
            return g
    lab = label.lower() if isinstance(label, str) else ""
    for g, rx in LABEL_WORDS:
        if re.search(rx, lab):
            return g
    return "other"


it["group"] = [group_of(t, l) for t, l in zip(it.types, it.label)]
# present-day country and continent from Natural Earth (nearest country within 30 km for points on the coast)
ne = gpd.read_file(f"{GEO}/ne_10m_admin_0_countries.geojson")[["ISO_A2_EH", "ADMIN", "CONTINENT", "SUBREGION", "geometry"]]
ne.loc[ne.ADMIN == "France", "ISO_A2_EH"] = "FR"; ne.loc[ne.ADMIN == "Norway", "ISO_A2_EH"] = "NO"
ne.loc[ne.ADMIN == "Kosovo", "ISO_A2_EH"] = "XK"
pts = gpd.GeoDataFrame(it[["lon", "lat"]], geometry=gpd.points_from_xy(it.lon, it.lat), crs=4326)
j = gpd.sjoin(pts, ne, how="left", predicate="within")
j = j[~j.index.duplicated()]
miss = j.ADMIN.isna()
if miss.any():
    pm = pts[miss].copy(); pm["geometry"] = gpd.points_from_xy(pm.lon, pm.lat.clip(-84, 84))
    pm = pm[pm.lon.notna() & pm.lat.notna()]
    p3 = pm.set_crs(4326, allow_override=True).to_crs(3857)
    n3 = ne.copy(); n3["geometry"] = n3.geometry.intersection(gpd.GeoSeries.from_wkt(["POLYGON((-180 -84,180 -84,180 84,-180 84,-180 -84))"], crs=4326).iloc[0]); n3 = n3[~n3.geometry.is_empty].to_crs(3857)
    jn = gpd.sjoin_nearest(p3, n3, how="left", max_distance=30000)
    jn = jn[~jn.index.duplicated()]
    for c in ("ISO_A2_EH", "ADMIN", "CONTINENT", "SUBREGION"):
        j.loc[jn.index, c] = jn[c]
it["iso"], it["country"], it["continent"], it["subregion"] = j.ISO_A2_EH, j.ADMIN, j.CONTINENT, j.SUBREGION
it["iso"] = it["iso"].fillna("")
# the former East Germany (for communist-era rules)
a1 = gpd.read_file(f"{GEO}/ne_10m_admin_1_states_provinces.geojson")
east = a1[(a1.iso_a2 == "DE") & a1.name.isin(["Brandenburg", "Berlin", "Mecklenburg-Vorpommern", "Sachsen", "Sachsen-Anhalt", "Thüringen"])]
de = it.iso == "DE"
inside = gpd.sjoin(pts[de], east[["geometry"]], how="left", predicate="within")
inside = inside[~inside.index.duplicated()]
it["de_east"] = False
it.loc[inside.index[inside.index_right.notna()], "de_east"] = True
# Spanish regions with their own languages (for the language-policy rule)
reg = a1[(a1.iso_a2 == "ES") & a1.region.isin(["Galicia", "Cataluña", "País Vasco", "Foral de Navarra", "Asturias", "Valenciana", "Islas Baleares"])]
es = it.iso == "ES"
ins = gpd.sjoin(pts[es], reg[["geometry"]], how="left", predicate="within"); ins = ins[~ins.index.duplicated()]
it["es_reg"] = False
it.loc[ins.index[ins.index_right.notna()], "es_reg"] = True

# ---------------- statements: one row per item, name, language, start, end
st = df.drop_duplicates(["q", "nm", "lang", "start", "end"])[["q", "nm", "lang", "start", "end"]].copy()
st["sy"] = st["start"].str.extract(r"^(-?\d+)-")[0].astype(float)
st["ey"] = st["end"].str.extract(r"^(-?\d+)-")[0].astype(float)
st["s10"] = st["start"].str.slice(0, 10).where(st.sy.notna())
st["e10"] = st["end"].str.slice(0, 10).where(st.ey.notna())
st["e_unknown"] = st["end"].fillna("").str.contains("genid")
st = st[st.nm.notna() & (st.nm.str.len() > 0)]


# ---------------- transitions within a language
trans = []
for (q, lang), h in st.groupby(["q", "lang"], sort=False):
    if len(h) < 2:
        continue
    ends = h[h.ey.notna()]; starts = h[h.sy.notna()]
    for a in ends.itertuples():
        best = None
        for b in starts.itertuples():
            if b.nm == a.nm or abs(b.sy - a.ey) > 1:
                continue
            if best is None or abs(b.sy - a.ey) < abs(best.sy - a.ey):
                best = b
        if best is not None:
            trans.append((q, lang, a.nm, best.nm, int(a.ey), int(best.sy), a.e10, best.s10))
tr = pd.DataFrame(trans, columns=["q", "lang", "old", "new", "ey", "sy", "e10", "s10"])
n_ended = st[st.ey.notna()].q.nunique()

# ---------------- events: transitions of one item within a year of each other
rows = []
for q, h in tr.sort_values(["q", "sy"]).groupby("q", sort=False):
    h = h.reset_index(drop=True)
    cl, cur, last = [], [], None
    for i, r in h.iterrows():
        if last is not None and r.sy - last > 1:
            cl.append(cur); cur = []
        cur.append(i); last = r.sy
    cl.append(cur)
    for c in cl:
        rows.append((q, h.loc[c]))
iso_of = it["iso"].to_dict()
EV = []
for q, h in rows:
    loc = LOCAL_LANG.get(iso_of.get(q, ""), None)
    langs = sorted(set(h.lang))
    local = [l for l in langs if loc is None or l in loc]
    pick = None
    for pref in DISPLAY_PREF:
        if pref in langs:
            pick = pref; break
    lo = local[0] if local else None
    if pick is None:
        pick = lo or h.lang.value_counts().index[0]
    d = h[h.lang == pick].iloc[0]
    l2 = h[h.lang == lo].iloc[0] if lo else d
    year = int(h.sy.mode().iloc[0]) if len(h.sy.mode()) == 1 else int(round(h.sy.median()))
    EV.append(dict(q=q, year=year, date=d.s10, old=d.old, new=d.new, lang=pick, old_local=l2.old, new_local=l2.new, lang_local=l2.lang,
                   n_lang=len(langs), langs=" ".join(langs), local_support=bool(local) or loc is None,
                   tr=[(r.lang, r.old, r.new) for r in h.itertuples()], local_langs=local,
                   all_old=" | ".join(sorted(set(h.old))), all_new=" | ".join(sorted(set(h.new)))))
ev = pd.DataFrame(EV)
ev = ev.merge(it[["label", "lon", "lat", "group", "iso", "country", "continent", "subregion", "de_east", "es_reg"]], left_on="q", right_index=True, how="left")


st.to_pickle(f"{WORK}/statements.pkl"); it.to_pickle(f"{WORK}/items.pkl"); ev.to_pickle(f"{WORK}/events_raw.pkl")
tr.to_pickle(f"{WORK}/transitions.pkl")
jsave({"n_rows": n_rows, "n_items": int(it.shape[0]), "n_statements": int(len(st)), "n_transitions": int(len(tr)),
       "n_items_with_end": int(n_ended)}, f"{WORK}/counts1.json")
print(len(it), "items;", len(st), "statements;", len(tr), "transitions;", len(ev), "events")
print(ev.group.value_counts())
