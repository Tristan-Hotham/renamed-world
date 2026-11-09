"""Step 2: flag and classify each renaming event, apply the overrides read by eye, and build each place's name history.

Flags (a change that is not a new name is shown separately, never counted as a renaming; 'joined' is counted, as a merger):
  spelling   the same name respelled or transliterated (accents, hyphens, a letter or two, the same consonants)
  status     the same name with a different status word (village to town, county to city, Bezirksamt to Landkreis)
  qualifier  the same name with a qualifier added or dropped (Conflans to Conflans-sur-Anille, Poiana de Sus to Poiana)
  joined     a second name joined on (Mirabel to Mirabel-et-Blacons): counted, in mergers
For the rest, the wave, by the rules in rules.py, in this order:
  undoing communist names > communist name given > war and new borders > renamed under communist rule >
  mergers (programme years) > administrative reform > decolonisation > nation-building > admin area (merger) > other.
Then code/overrides.csv (wave or exclusion for single events, with a reason) is applied.
Output: WORK/events.pkl, WORK/histories.pkl
"""
import unicodedata, difflib
import numpy as np, pandas as pd
from common import *
from rules import *

ev = pd.read_pickle(f"{WORK}/events_raw.pkl")
st = pd.read_pickle(f"{WORK}/statements.pkl")
it = pd.read_pickle(f"{WORK}/items.pkl")


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
ev["group"] = ev.q.map(it.group)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower().replace("ヶ", "ケ").replace("ヵ", "カ"))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[\W_]+", "", s)


def words(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return [w for w in re.split(r"[\W_]+", s) if w]


ADMIN_RX = re.compile(r"(?<![\w])(" + "|".join(sorted((re.escape(w) for w in ADMIN_WORDS), key=len, reverse=True)) + r")(?![\w])", re.I)
CJK_RX = re.compile("(" + "|".join(sorted(CJK_ADMIN, key=len, reverse=True)) + ")$")


ADJ_RX = re.compile(r"(ського|ська|ське|ський|ські|ская|ское|ский|ские|ской|ая|ое|ые|ий|ой|ый|ія|ья|ов|ев|ів|ка|ке|ко|ки)$")


def strip_status(s):
    s = str(s).lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = ADMIN_RX.sub(" ", s)
    s = s.strip()
    s = re.sub(r"^(大字|字)", "", s)
    for _ in range(2):
        s = CJK_RX.sub("", s).strip()
    s = re.sub(r"\b(of|de|du|des|la|le|les|d|di|del)\b", " ", s)
    return norm(s)


def stem(s):
    """status-stripped name with Slavonic adjective endings removed (Veresky sovet and Veresky volost are one name)"""
    w = [ADJ_RX.sub("", x) for x in words(strip_status_words(s))]
    return "".join(w)


def skeleton(s):
    return re.sub(r"[aeiouyjwh]", "", norm(s))


def one_edit(a, b):
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def kind(a, b):
    """'spelling', 'status', 'qualifier' or '' for a pair of names in one language"""
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return ""
    if na == nb:
        return "spelling"
    sa, sb = strip_status(a), strip_status(b)
    if sa and sa == sb:
        return "status"
    if (sa != na or sb != nb) and stem(a) and stem(a) == stem(b):
        return "status"
    ca, cb = (sa, sb) if (sa and sb) else (na, nb)        # compare the names without their status words
    r = difflib.SequenceMatcher(None, ca, cb).ratio()
    if r >= 0.8 and abs(len(ca) - len(cb)) <= 3:
        return "spelling"
    if len(na) >= 4 and len(skeleton(a)) >= 3 and skeleton(a) == skeleton(b):
        return "spelling"
    if min(len(ca), len(cb)) >= 4 and not re.search(r"[぀-鿿가-힯]", ca + cb) and one_edit(ca, cb):
        return "spelling"                       # one letter changed, added or dropped (Bira to Bâra)
    wa, wb = set(words(strip_status_words(a))), set(words(strip_status_words(b)))
    if wa and wb and (wa < wb or wb < wa):
        extra = (wb - wa) if wa < wb else (wa - wb)
        if wa < wb and extra & JOIN_WORDS:
            return "joined"                     # a second name joined on: Mirabel to Mirabel-et-Blacons
        return "qualifier"
    if sa and sb and min(len(sa), len(sb)) >= 2 and re.search(r"[぀-鿿]", sa + sb) and (sa in sb or sb in sa):
        return "qualifier"                      # CJK: one name contains the other (a district added to a village name)
    return ""


def strip_status_words(s):
    s = re.sub(r"\(.*?\)", " ", str(s).lower())
    return ADMIN_RX.sub(" ", s)


def event_kind(trs, local):
    use = [t for t in trs if t[0] in local] or trs
    ks = [kind(o, n) for _, o, n in use]
    for k in ("spelling", "status", "qualifier", "joined"):
        if ks.count(k) > len(ks) / 2:
            return k
    if ks and all(k for k in ks):
        return max(set(ks), key=ks.count)
    return ""


CYR = str.maketrans({"і": "и", "ї": "и", "є": "е", "ґ": "г", "ё": "е", "ь": "", "ъ": "", "'": "", "’": ""})
TOK = sorted(set(t.translate(CYR) for t in RED_TOKENS))


def red(s):
    s = str(s).lower().translate(CYR)
    return any(t in s for t in TOK)


def stalin(s):
    s = str(s).lower()
    return any(t in s for t in ("stalin", "сталин", "сталін", "molotov", "молотов", "kaganovich", "каганович", "каганович", "ստալին"))


def in_box(lon, lat, b):
    return b is None or (b[0] <= lon <= b[1] and b[2] <= lat <= b[3])


def farm(s):
    s = str(s).lower()
    return any(t in s for t in FARM_TOKENS)


def classify(e):
    y, c = e["year"], e["iso"]
    old = e["all_old"] + " | " + e["old_local"] + " | " + str(e["old"])
    new = e["all_new"] + " | " + e["new_local"] + " | " + str(e["new"])
    if e["kind"] == "joined":
        return "merger", "two names joined"
    if e["kind"] == "qualifier" and c in COMMUNIST and red(old) and not red(new) and y >= 1953:
        return "reversal", "communist word dropped"
    if e["kind"]:
        return e["kind"], ""
    if c == "FR":
        for a, b, w, why in FR_REVOLUTION:
            if a <= y <= b and (w == "communist" or (e["q"], norm(e["old"])) in REV_NAMES):
                return w, why
    ckey = "DE_EAST" if (c == "DE" and e["de_east"]) else c
    late = e["sov0"] if e["sov0"] == e["sov0"] else None      # first year of Soviet rule in a late-annexed region
    if ckey in COMMUNIST:
        y0, y1 = COMMUNIST[ckey]
        if late:
            y0 = max(y0, int(late))
        if farm(old) and not farm(new) and y < 1989:
            return "communist", "state-farm settlement named"
        if red(old) and not red(new) and y >= 1953:
            if y <= 1964 and stalin(old):
                return "reversal", "de-Stalinisation"
            if c == "UA" and y >= 2015:
                return "reversal", "Ukraine's decommunisation laws"
            if y >= 1985:
                return "reversal", "after communism"
            return "reversal", "communist name dropped"
        if red(new) and y0 <= y <= y1:
            return "communist", "communist name given"
    if c == "UA" and UA_DECOM[0] <= y <= UA_DECOM[1]:
        return "reversal", "Ukraine's decommunisation laws"
    for wc, a, b, bx in WAR:
        if c == wc and a <= y <= b and in_box(e["lon"], e["lat"], bx):
            return "war", "border moved after war"
    if ckey in COMMUNIST:
        y0, y1 = COMMUNIST_RULE[ckey]
        if late:
            y0 = max(y0, int(late))
        if y0 <= y <= y1:
            return "communist", "renamed under communist rule"
    for a, b in MERGER.get(c, []):
        if a <= y <= b and e["group"] in CORE:
            return "merger", "municipal merger programme"
    for a, b in MERGER_ADMIN.get(c, []):
        if a <= y <= b and e["group"] == "admin":
            return "merger", "administrative reform"
    if c in INDEPENDENCE:
        i0 = INDEPENDENCE[c]
        if i0 + DECOL_WINDOW[0] <= y <= i0 + DECOL_WINDOW[1]:
            return "colonial", f"independence {i0}"
    for nk in (c + "_POST", "ES_REG" if (c == "ES" and e["es_reg"]) else None, c):
        if nk and nk in NATION and NATION[nk][0] <= y <= NATION[nk][1]:
            return "nation", "nation-building and language"
    if c in INDEPENDENCE and y > INDEPENDENCE[c] + DECOL_WINDOW[1]:
        return "nation", "later renaming in a former colony"
    if e["group"] == "admin":
        return "merger", "administrative area renamed"
    return "other", ""


# regions that came under Soviet rule late (rules.SOVIET_FROM): before that year, renamings there were not made under communist rule
import geopandas as gpd
a1 = gpd.read_file(f"{GEO}/ne_10m_admin_1_states_provinces.geojson")[["iso_a2", "name", "geometry"]]
ev["sov0"] = np.nan
for c, where, y0 in SOVIET_FROM:
    m = ev.iso == c
    if isinstance(where, tuple):
        m &= ev.lon.between(where[0], where[1]) & ev.lat.between(where[2], where[3])
    else:
        poly = a1[(a1.iso_a2 == c) & a1.name.isin(where)]
        assert len(poly) == len(where), where
        sub = ev[m]
        pts = gpd.GeoDataFrame(sub[[]], geometry=gpd.points_from_xy(sub.lon, sub.lat), crs=4326)
        j = gpd.sjoin(pts, poly, how="inner", predicate="within")
        m = ev.index.isin(j.index.unique())
    ev.loc[m, "sov0"] = y0

# Crimea is counted with Ukraine
cr = (ev.lon.between(CRIMEA[0], CRIMEA[1])) & (ev.lat.between(CRIMEA[2], CRIMEA[3])) & ev.iso.isin(["RU", "UA"])
ev.loc[cr, "iso"] = "UA"; ev.loc[cr, "country"] = "Ukraine"
ev["kind"] = [event_kind(t, set(l) if l else set()) for t, l in zip(ev.tr, ev.local_langs)]
# names given in the French Revolution (so that their removal after 1800 counts as undoing them)
REV_NAMES = {(e.q, norm(n)) for e in ev[(ev.iso == "FR") & ev.year.between(1790, 1799)].itertuples() for _, o, n in e.tr}
w = ev.apply(classify, axis=1, result_type="expand")
ev["wave"], ev["why"] = w[0], w[1]
ev["auto_wave"] = ev["wave"]
ev["excluded"] = ""
# bulk batches that are not renamings: one source dated a whole gazetteer at once
batch = ev.groupby(["iso", "date", "lang"]).q.transform("size")
gal = (ev.iso == "ES") & ev.es_reg & (ev.year == 2026)
ev.loc[gal, "excluded"] = "Galician gazetteer revision dated 2026 (a bulk update of local names, mostly articles and spellings)"

# ---------------- overrides read by eye
ov = pd.read_csv(os.path.join(ROOT, "code", "overrides.csv"), comment="#", dtype=str).fillna("")
n_ov = 0
for r in ov.itertuples():
    m = (ev.q == r.qid) & ((ev.year == int(r.year)) if r.year else True)
    if not m.any():
        raise SystemExit(f"override matches nothing: {r}")
    if r.action == "exclude":
        ev.loc[m, "excluded"] = r.reason
    elif r.action == "wave":
        ev.loc[m, "wave"] = r.value; ev.loc[m, "why"] = r.reason
    elif r.action == "kind":
        ev.loc[m, "kind"] = r.value; ev.loc[m, "wave"] = r.value; ev.loc[m, "why"] = r.reason
    n_ov += int(m.sum())
# duplicates: the same change recorded twice on one item (keep the first), or on two items for the same place within 5 km
# (a Romanian commune and its main village, a city and its district; keep the settlement, then the lower number)
ev["_k"] = ev.old.map(norm) + ">" + ev.new.map(norm)
ev["_r"] = ev.new.map(norm) + ">" + ev.old.map(norm)
dup_in = pd.Series(False, index=ev.index)
for q, g in ev[ev.duplicated(["q", "_k"], keep=False)].groupby("q"):
    allq = ev[ev.q == q].sort_values("year")
    for k, gg in g.groupby("_k"):
        ys = sorted(gg.year)
        for a, b in zip(ys, ys[1:]):
            between = allq[(allq.year > a) & (allq.year < b) & (allq._r == k)]
            if not len(between):          # repeated with no change back in between: a second record of one change
                dup_in.loc[gg[gg.year == b].index] = True
dup_in &= (ev.excluded == "")
ev.loc[dup_in, "excluded"] = "the same change recorded again on this item"
ev["_qn"] = ev.q.str[1:].astype(int) + np.where(ev.group == "place", 0, 10 ** 10)   # prefer the settlement, then the lower number
cand = ev[(ev.excluded == "")].groupby(["_k", "year"])
dup_x = []
for k, g in cand:
    if len(g) < 2:
        continue
    g = g.sort_values("_qn")
    keep = g.iloc[0]
    for r in g.iloc[1:].itertuples():
        d = math.hypot((r.lon - keep.lon) * math.cos(math.radians(keep.lat)), r.lat - keep.lat) * 111.2
        if d <= 5:
            dup_x.append(r.Index)
ev.loc[dup_x, "excluded"] = "a second Wikidata item for the same place records the same change"
n_dup_in, n_dup_x = int(dup_in.sum()), len(dup_x)
ev["renaming"] = ~ev.wave.isin(["spelling", "status", "qualifier"]) & (ev.excluded == "")

# ---------------- renamed back: the new name was an earlier official name of the same item in that language
stl = st[st.q.isin(set(ev.q))].copy(); stl["n"] = stl.nm.map(norm)
first = {k: h for k, h in stl.groupby(["q", "lang"])}
back = []
for e in ev.itertuples():
    b = False
    for lang, o, n in e.tr:
        h = first.get((e.q, lang))
        if h is None: continue
        nn = norm(n)
        earlier = h[(h.n == nn) & h.ey.notna() & (h.ey <= e.year - 2)]
        if len(earlier):
            b = True; break
    back.append(b)
ev["back"] = back

# ---------------- name histories (display language and local language) for the page
hist = {}
lang_of = ev.groupby("q").lang.first().to_dict()
for (q, lang), h in first.items():
    if lang_of.get(q) != lang:
        continue
    h = h.sort_values(["sy", "ey"], na_position="first")
    hist[q] = [(r.nm, None if pd.isna(r.sy) else int(r.sy), None if pd.isna(r.ey) else int(r.ey)) for r in h.itertuples()]
ev.to_pickle(f"{WORK}/events.pkl"); pd.to_pickle(hist, f"{WORK}/histories.pkl")
jsave({"n_overrides_rows": int(len(ov)), "n_overridden_events": n_ov, "n_dup_same_item": n_dup_in, "n_dup_two_items": n_dup_x}, f"{WORK}/counts2.json")
core = ev[ev.group.isin(CORE)]
print(core.groupby("wave").size(), "\nrenamings (core)", int(core.renaming.sum()), "of", len(core), "; overrides", n_ov)
