"""Step 4: figures for the page (img/*.jpg), the blog (release/blog/b_*.png), the paper (release/paper/f_*.png), and header.png."""
import numpy as np, pandas as pd
from PIL import Image
import matplotlib.patheffects as pe
from figstyle import *
from rules import WAVES, WAVE_NAME, WAVE_COL

R = jload(f"{DATA}/results.json")
E = pd.read_csv(f"{DATA}/renamings.csv")
REN = E[E.renaming].copy()
BLOG, PAPERD = f"{ROOT}/release/blog", f"{ROOT}/release/paper"
for d in (BLOG, PAPERD):
    os.makedirs(d, exist_ok=True)
HALO = [pe.withStroke(linewidth=3, foreground=PAPER)]
SHORT = {"colonial": "Decolonisation", "communist": "Revolution and communism", "reversal": "Undoing revolutionary and communist names",
         "war": "War and new borders", "nation": "Nation-building and language", "merger": "Mergers and admin reform", "other": "Other renamings"}


def out(fig, name, page=True, blog=True, paper=True, dpi=200):
    fig.savefig(f"{WORK}/{name}.png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    im = Image.open(f"{WORK}/{name}.png").convert("RGB")
    if page:
        w = min(1600, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=84, optimize=True)
    if blog:
        w = 1800; im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    if paper:
        w = min(2000, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{PAPERD}/f_{name}.png", optimize=True)
    os.remove(f"{WORK}/{name}.png")


def dots(ax, f, df, s=5, alpha=0.85, z=6):
    order = ["other", "merger", "nation", "war", "colonial", "communist", "reversal"]
    for w in order:
        d = df[df.wave == w]
        if not len(d): continue
        x, y = f(d.lon.values, d.lat.values)
        ax.scatter(x, y, s=s, c=WAVE_COL[w], edgecolors=INKC, linewidths=0.15, alpha=alpha, zorder=z)


def legend(ax, x, y, fs=11, dy=0.045, title="Why the name changed", counts=True, transform=None):
    tr = transform or ax.transAxes
    ax.text(x, y, title, fontproperties=FELLSC, fontsize=fs + 1.5, color=RED, transform=tr, va="center")
    for i, w in enumerate(WAVES):
        yy = y - (i + 1) * dy
        ax.scatter([x + 0.008], [yy], s=fs * 6, c=WAVE_COL[w], edgecolors=INKC, linewidths=0.4, transform=tr, zorder=10, clip_on=False)
        lab = SHORT[w] + (f"  {R['waves'][w]['n']:,}" if counts else "")
        ax.text(x + 0.025, yy, lab, fontproperties=FELL, fontsize=fs, color=INKC, transform=tr, va="center", path_effects=HALO)


def hlegend(fig, x, y, fs=11.5, counts=True, cols=3, dx=0.31, dy=0.032, title="Why the name changed"):
    fig.text(x, y, title, fontproperties=FELLSC, fontsize=fs + 1.5, color=RED, va="center")
    for i, w in enumerate(WAVES):
        cx, cy = x + (i % cols) * dx, y - (1 + i // cols) * dy
        fig.patches.append(plt.Circle((cx + 0.006, cy), 0.0055, fc=WAVE_COL[w], ec=INKC, lw=0.4, transform=fig.transFigure))
        fig.text(cx + 0.016, cy, SHORT[w] + (f"  {R['waves'][w]['n']:,}" if counts else ""), fontproperties=FELL, fontsize=fs, color=INKC, va="center")


# ---------- 1. the world map
WORLD = "+proj=eqearth +lon_0=0 +datum=WGS84 +units=m +no_defs"
fig = plt.figure(figsize=(14, 8.6)); parchment(fig)
ax = fig.add_axes([0.0, 0.175, 1, 0.71])
ext, f = ink_base(ax, WORLD, (-179.9, 179.9, -56, 78), ripple_m=(120e3, 300e3), coast_lw=0.5, min_area=2e9)
dots(ax, f, REN, s=4.5)
xa, _ = f(-180, 0); xb, _ = f(180, 0); _, ya = f(0, -56); _, yb = f(0, 80)
ax.set_xlim(xa, xb); ax.set_ylim(ya, yb)
fig.text(0.04, 0.955, f"The renamed world: {R['n']['renamings']:,} official renamings of towns, villages and regions", fontproperties=FELL, fontsize=23, color=INKC, va="center")
fig.text(0.04, 0.918, f"Every place in Wikidata whose official name has dated start and end, after setting aside {R['n']['minor']:,} changes of spelling, status or qualifier",
         fontproperties=FELL, fontsize=12.5, color=MUT, va="center")
hlegend(fig, 0.04, 0.125)
fig.text(0.04, 0.012, "Data: Wikidata (CC0), official name (P1448) with start and end dates; present-day countries from Natural Earth. Coverage is uneven: Africa, the Americas and the UK have few dated names.",
         fontproperties=FELL, fontsize=10, color=MUT)
out(fig, "map")

# ---------- 2. renamings by decade
D = pd.DataFrame(R["decades"]).set_index("decade")
D = D.loc[1800:]
fig = plt.figure(figsize=(13, 7.2)); parchment(fig)
ax = fig.add_axes([0.07, 0.11, 0.62, 0.72])
bottom = np.zeros(len(D))
for w in WAVES:
    ax.bar(D.index + 5, D[w].values, width=8.6, bottom=bottom, color=WAVE_COL[w], edgecolor=INKC, linewidth=0.35, label=SHORT[w])
    bottom += D[w].values
ax.set_xlim(1795, 2032)
ax.set_xticks(range(1800, 2030, 20)); ax.set_xticklabels([f"{y}s" for y in range(1800, 2030, 20)], fontproperties=FELL, fontsize=11)
for t in ax.get_yticklabels(): t.set_fontproperties(FELL); t.set_fontsize(11)
ax.set_ylabel("Renamings in the decade", fontproperties=FELL, fontsize=12)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.grid(axis="y", color="#E2D3AE", lw=0.6); ax.set_axisbelow(True)
py = {p["year"]: p for p in R["peak_years"]}
notes = [(1960, f"Romania, 1964:\n{R['romania']['y1964']:,} villages renamed", (1972, 1150)),
         (1940, "Soviet renamings,\nwar and new borders", (1888, 880)),
         (2010, f"Ukraine: {R['ukraine']['y2016']} in 2016,\n{R['ukraine']['y2024']} in 2024", (1990, 760)),
         (1990, "After the\nSoviet Union", (1974, 600))]
for dec, t, (tx, ty) in notes:
    yv = D.loc[dec].drop("total").sum()
    ax.annotate(t, (dec + 5, yv), xytext=(tx, ty), fontproperties=FELL, fontsize=11, color=INKC,
                ha="left", va="bottom", arrowprops=dict(arrowstyle="-", color=INKC, lw=0.6, shrinkB=2), path_effects=HALO)
fig.text(0.07, 0.94, "Renamings by decade, and why", fontproperties=FELL, fontsize=23, color=INKC, va="center")
fig.text(0.07, 0.895, f"{R['n']['since1800']:,} official renamings of places since 1800, coloured by the wave they belong to", fontproperties=FELL, fontsize=12.5, color=MUT, va="center")
legend(ax, 1.04, 0.92, fs=11.5, dy=0.075, counts=True)
out(fig, "decades")

# ---------- 3. Europe and the former Soviet Union
EUR = "+proj=laea +lat_0=52 +lon_0=35 +datum=WGS84 +units=m +no_defs"
fig = plt.figure(figsize=(13, 9.6)); parchment(fig)
ax = fig.add_axes([0.0, 0.135, 1, 0.755])
ext, f = ink_base(ax, EUR, (-8, 82, 33, 66), ripple_m=(25e3, 60e3), coast_lw=0.5, min_area=2e8)
dots(ax, f, REN, s=6)
x0, y0 = f(-11, 31); x1, y1 = f(85, 69)
ax.set_xlim(-2.9e6, 3.2e6); ax.set_ylim(-2.3e6, 2.0e6)
fig.text(0.04, 0.955, "From the Atlantic to the Tien Shan", fontproperties=FELL, fontsize=23, color=INKC, va="center")
fig.text(0.04, 0.918, f"{R['former_ussr']['n']:,} of the renamings ({R['former_ussr']['pc']:.0f}%) are in the former Soviet Union; with Romania and France they make most of the map",
         fontproperties=FELL, fontsize=12.5, color=MUT, va="center")
hlegend(fig, 0.04, 0.112, counts=False)
out(fig, "europe")

# ---------- 4. name histories of twelve places
TR = {"Санкт-Петербург": "St Petersburg", "Петроград": "Petrograd", "Ленинград": "Leningrad", "Нижний Новгород": "Nizhny Novgorod",
      "Горький": "Gorky", "Владикавказ": "Vladikavkaz", "Орджоникидзе": "Ordzhonikidze", "Дзауджикау": "Dzaudzhikau",
      "Луганский завод": "Luhansk Works", "Луганск": "Luhansk", "Луганськ": "Luhansk", "Ворошиловград": "Voroshilovgrad",
      "Рыбная слобода": "Rybnaya Sloboda", "Усть-Шексна": "Ust-Sheksna", "Рыбинск": "Rybinsk", "Щербаков": "Shcherbakov", "Андропов": "Andropov",
      "Ак-Мола": "Ak-Mola", "Акмолінськ": "Akmolinsk", "Акмолинск": "Akmolinsk", "Целиноград": "Tselinograd", "Акмола": "Akmola", "Астана": "Astana",
      "Нур-Султан": "Nur-Sultan", "Єлисаветград": "Yelisavetgrad", "Зінов'євськ": "Zinovievsk", "Кірово": "Kirovo", "Кіровоград": "Kirovohrad",
      "Кропивницький": "Kropyvnytskyi", "Александровка": "Aleksandrovka", "Юзовка": "Yuzovka", "Юзівка": "Yuzivka", "Сталін": "Stalin",
      "Сталіно": "Stalino", "Донецьк": "Donetsk", "Рибница": "Ribnica", "Подгорица": "Podgorica", "Титоград": "Titograd",
      "Գյումրի": "Gyumri", "Ալեքսանդրապոլ": "Alexandropol", "Լենինական": "Leninakan", "Самара": "Samara", "Куйбышев": "Kuybyshev",
      "Екатеринбург": "Yekaterinburg", "Свердловск": "Sverdlovsk", "Тверь": "Tver", "Калинин": "Kalinin", "Павловск": "Pavlovsk",
      "Мариуполь": "Mariupol", "Маріуполь": "Mariupol", "Жданов": "Zhdanov", "Варна": "Varna", "Сталин": "Stalin",
      "Кацярынаслаў": "Yekaterinoslav", "Наварасейск": "Novorossiysk", "Новоросійськ": "Novorossiysk", "Катеринослав": "Katerynoslav",
      "Дніпропетровськ": "Dnipropetrovsk", "Дніпро": "Dnipro", "Biskek": "Bishkek"}
tr = lambda s: TR.get(s, s)
PICK = [("st_petersburg", "Saint Petersburg"), ("volgograd", "Volgograd"), ("nizhny", "Nizhny Novgorod"), ("vladikavkaz", "Vladikavkaz"),
        ("luhansk", "Luhansk"), ("rybinsk", "Rybinsk"), ("kropyvnytskyi", "Kropyvnytskyi"), ("donetsk", "Donetsk"),
        ("astana", "Astana"), ("gyumri", "Gyumri"), ("podgorica", "Podgorica"), ("chemnitz", "Chemnitz")]
fig = plt.figure(figsize=(13, 9.4)); parchment(fig)
ax = fig.add_axes([0.16, 0.09, 0.80, 0.77])
A0, A1 = 1900, 2026
for j, (k, lab) in enumerate(PICK):
    ch = R["ex"][k]["chain"]
    y = len(PICK) - 1 - j
    segs = [(A0, ch[0]["year"], tr(ch[0]["old"]), None)]
    for i, c in enumerate(ch):
        y1 = ch[i + 1]["year"] if i + 1 < len(ch) else A1
        segs.append((c["year"], y1, tr(c["new"]), c["wave"]))
    for a, b, nm, w in segs:
        a2, b2 = max(a, A0), min(b, A1)
        if b2 <= A0: continue
        col = "#E9DDBE" if w is None or w == "other" else WAVE_COL[w]
        ax.add_patch(plt.Rectangle((a2, y - 0.32), b2 - a2, 0.64, fc=col, ec=INKC, lw=0.5, alpha=0.95 if w else 0.8))
        if b2 - a2 >= 11:
            light = w in ("communist", "war", "nation", "other") and w is not None
            ax.text(a2 + 1, y, nm, fontproperties=FELL, fontsize=10.5, color="#FBF5E4" if light and w not in ("other",) else INKC, va="center", ha="left", clip_on=True)
    ax.text(A0 - 2, y, lab, fontproperties=FELL, fontsize=12.5, color=INKC, va="center", ha="right")
ax.set_xlim(A0, A1); ax.set_ylim(-0.7, len(PICK) - 0.3)
ax.set_yticks([]); ax.set_xticks(range(1900, 2030, 20))
for t in ax.get_xticklabels(): t.set_fontproperties(FELL); t.set_fontsize(11)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
for x in range(1900, 2030, 10): ax.axvline(x, color="#E2D3AE", lw=0.5, zorder=0)
fig.text(0.04, 0.955, "Twelve name histories", fontproperties=FELL, fontsize=23, color=INKC, va="center")
fig.text(0.04, 0.918, "Each bar is one official name, coloured by the wave of the renaming that gave it (names from Wikidata, transliterated)",
         fontproperties=FELL, fontsize=12.5, color=MUT, va="center")
lx = 0.16
for w in ("communist", "reversal", "nation"):
    fig.patches.append(plt.Rectangle((lx, 0.025), 0.018, 0.022, fc=WAVE_COL[w], ec=INKC, lw=0.5, transform=fig.transFigure))
    fig.text(lx + 0.024, 0.036, SHORT[w], fontproperties=FELL, fontsize=11, color=INKC, va="center")
    lx += 0.27
out(fig, "chains")

# ---------- 5. countries
C = pd.read_csv(f"{DATA}/countries.csv").head(15).iloc[::-1]
fig = plt.figure(figsize=(12, 8.2)); parchment(fig)
ax = fig.add_axes([0.20, 0.09, 0.50, 0.78])
left = np.zeros(len(C))
for w in WAVES:
    v = C[w].values if w in C else np.zeros(len(C))
    ax.barh(range(len(C)), v, left=left, color=WAVE_COL[w], edgecolor=INKC, lw=0.35, height=0.7)
    left += v
ax.set_yticks(range(len(C))); ax.set_yticklabels(C.country, fontproperties=FELL, fontsize=12)
for t in ax.get_xticklabels(): t.set_fontproperties(FELL); t.set_fontsize(11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#E2D3AE", lw=0.6); ax.set_axisbelow(True)
for i, r in enumerate(C.itertuples()):
    ax.text(r.n + 15, i, f"{r.n:,}", fontproperties=FELL, fontsize=11, va="center", color=INKC)
fig.text(0.04, 0.955, "Where the renamings are", fontproperties=FELL, fontsize=23, color=INKC, va="center")
fig.text(0.04, 0.918, f"The fifteen countries with most renamings in the data (present-day borders); the top five hold {R['top5_pc']:.0f}%", fontproperties=FELL, fontsize=12.5, color=MUT, va="center")
legend(ax, 1.06, 0.95, fs=11, dy=0.065, counts=False)
out(fig, "countries")

# ---------- 6. from name changes to renamings
n = R["n"]
rows = [("Name changes on places in the data", n["events_core"], "#8C6A43"),
        ("Same name, new spelling or transliteration", n["spelling"], "#C9BFA6"),
        ("Same name, new status (village to town, town to city)", n["status"], "#C9BFA6"),
        ("Same name with a qualifier added or dropped", n["qualifier"], "#C9BFA6"),
        ("Galician gazetteer revision dated 2026", n["galician"], "#B9B2A0"),
        ("Recorded twice (one item or two)", n["dup_same"] + n["dup_two"] + n["overridden"], "#B9B2A0"),
        ("Renamings: a new name", n["renamings"], RED)]
fig = plt.figure(figsize=(12, 6)); parchment(fig)
ax = fig.add_axes([0.40, 0.08, 0.52, 0.76])
for i, (lab, v, colr) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.barh(y, v, color=colr, edgecolor=INKC, lw=0.4, height=0.66)
    ax.text(v + 150, y, f"{v:,}", fontproperties=FELL, fontsize=12, va="center", color=INKC)
    ax.text(-300, y, lab, fontproperties=FELL, fontsize=12, va="center", ha="right", color=INKC)
ax.set_xlim(0, n["events_core"] * 1.12); ax.set_yticks([]); ax.set_xticks([])
for s in ax.spines.values(): s.set_visible(False)
fig.text(0.04, 0.94, "Most changes of official name are not new names", fontproperties=FELL, fontsize=23, color=INKC, va="center")
fig.text(0.04, 0.895, f"{n['minor_pc']:.0f}% of the dated name changes on places keep the name; {n['renaming_pc']:.0f}% are true renamings", fontproperties=FELL, fontsize=12.5, color=MUT, va="center")
out(fig, "funnel")

# ---------- header 1200 x 630
fig = plt.figure(figsize=(12, 6.3)); parchment(fig, seed=9)
ax = fig.add_axes([0.36, 0.0, 0.66, 1.0])
ext, f = ink_base(ax, EUR, (-8, 82, 33, 66), ripple_m=(30e3, 70e3), coast_lw=0.45, min_area=4e8)
dots(ax, f, REN, s=5)
ax.set_xlim(-2.4e6, 3.0e6); ax.set_ylim(-2.2e6, 2.1e6)
fig.text(0.04, 0.80, "The renamed", fontproperties=HAND, fontsize=44, color=INKC, va="center")
fig.text(0.04, 0.68, "world", fontproperties=HAND, fontsize=56, color=RED, va="center")
fig.text(0.045, 0.52, f"{R['n']['renamings']:,} official renamings", fontproperties=FELL, fontsize=19, color=INKC, va="center")
fig.text(0.045, 0.45, "Tsaritsyn, Stalingrad, Volgograd", fontproperties=FELLIT, fontsize=16, color=MUT, va="center")
fig.text(0.045, 0.39, f"Romania, 1964: {R['romania']['y1964']} villages in a year", fontproperties=FELLIT, fontsize=16, color=MUT, va="center")
fig.text(0.045, 0.33, f"Ukraine, 2016 and 2024: {R['ukraine']['y2016'] + R['ukraine']['y2024']}", fontproperties=FELLIT, fontsize=16, color=MUT, va="center")
fig.text(0.045, 0.08, "Dr Tristan Hotham · maps.tristanhotham.com/renamed-world", fontproperties=FELL, fontsize=12, color=MUT, va="center")
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=fig.get_facecolor()); plt.close(fig)
assert Image.open(f"{ROOT}/header.png").size == (1200, 630)
print("figures done")
