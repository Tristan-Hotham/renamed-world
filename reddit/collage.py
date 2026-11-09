"""Reddit collage (r/dataisbeautiful style): the map of renamings, the decades and twelve name histories, on parchment.
Built from the blog figures made by code/04_figures.py (which carry their own legends on paper, not over land).
Output: reddit/renamed_world_collage.png (2700 x 4500 px)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
from figstyle import *
from PIL import Image

R = jload(f"{DATA}/results.json")
B = os.path.join(ROOT, "release", "blog")
fig = plt.figure(figsize=(9, 15), dpi=300); parchment(fig, seed=4, alpha=0.05)
fig.text(0.04, 0.978, "The renamed world", fontproperties=HAND, fontsize=34, color=RED, va="center")
fig.text(0.04, 0.956, f"{R['n']['renamings']:,} official renamings of towns, villages and regions in Wikidata, and why they happened",
         fontproperties=FELL, fontsize=12, color=INKC, va="center")
fig.text(0.04, 0.942, f"after setting aside {R['n']['minor']:,} changes that kept the name (new spelling, new status, a qualifier added)",
         fontproperties=FELL, fontsize=10.5, color=MUT, va="center")


def panel(fn, box, crop=None):
    im = Image.open(f"{B}/{fn}").convert("RGB")
    if crop:
        w, h = im.size; im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    ax = fig.add_axes(box); ax.imshow(im, aspect="auto"); ax.axis("off")
    return im.size


w, h = panel("b_europe.png", [0.01, 0.59, 0.98, 0.98 * 9 * 0.557 / 15], crop=(0.05, 0.13, 0.95, 0.86))
from rules import WAVES, WAVE_COL
SH = {"colonial": "Decolonisation", "communist": "Revolution and communism", "reversal": "Undoing revolutionary and communist names",
      "war": "War and new borders", "nation": "Nation-building and language", "merger": "Mergers and admin reform", "other": "Other renamings"}
for i, wv in enumerate(WAVES):
    x, y = 0.05 + (i % 3) * 0.31, 0.575 - (i // 3) * 0.016
    fig.patches.append(plt.Circle((x, y), 0.0042, fc=WAVE_COL[wv], ec=INKC, lw=0.4, transform=fig.transFigure))
    fig.text(x + 0.012, y, f"{SH[wv]}  {R['waves'][wv]['n']:,}", fontproperties=FELL, fontsize=9.5, color=INKC, va="center")
panel("b_decades.png", [0.01, 0.235, 0.98, 0.28], crop=(0, 0.13, 1, 1))
fig.text(0.04, 0.522, "Renamings by decade since 1800", fontproperties=FELLSC, fontsize=12, color=RED, va="center")
fig.text(0.04, 0.215, "Some name histories", fontproperties=FELLSC, fontsize=12, color=RED, va="center")
Y = lambda k: [c["year"] for c in R["ex"][k]["chain"]]
assert Y("volgograd") == [1925, 1961] and Y("st_petersburg") == [1914, 1924, 1991] and Y("vladikavkaz") == [1931, 1944, 1954, 1990]
assert Y("luhansk")[-4:] == [1935, 1958, 1970, 1990] and Y("astana")[-5:] == [1961, 1992, 1998, 2019, 2022] and Y("chemnitz") == [1953, 1990]
assert Y("kinshasa") == [1966] and Y("harare") == [1982]
lines = ["Tsaritsyn  >  Stalingrad (1925)  >  Volgograd (1961)",
         "St Petersburg  >  Petrograd (1914)  >  Leningrad (1924)  >  St Petersburg (1991)",
         "Vladikavkaz  >  Ordzhonikidze (1931)  >  Dzaudzhikau (1944)  >  Ordzhonikidze (1954)  >  Vladikavkaz (1990)",
         "Luhansk  >  Voroshilovgrad (1935)  >  Luhansk (1958)  >  Voroshilovgrad (1970)  >  Luhansk (1990)",
         "Ak-Mola  >  Akmolinsk (1832)  >  Tselinograd (1961)  >  Akmola (1992)  >  Astana (1998)  >  Nur-Sultan (2019)  >  Astana (2022)",
         "Chemnitz  >  Karl-Marx-Stadt (1953)  >  Chemnitz (1990)",
         "Léopoldville  >  Kinshasa (1966);   Salisbury  >  Harare (1982)",
         f"Romania, 1964: {R['romania']['y1964']} villages renamed in a single year;   Ukraine: {R['ukraine']['y2016']} in 2016, {R['ukraine']['y2024']} in 2024"]
for i, l in enumerate(lines):
    fig.text(0.05, 0.195 - i * 0.02, l, fontproperties=FELL, fontsize=10.5, color=INKC, va="center")
fig.text(0.04, 0.014, "Data: Wikidata (CC0), official names (P1448) with start and end dates; waves by my rules. Coverage is uneven:",
         fontproperties=FELL, fontsize=8.5, color=MUT)
fig.text(0.04, 0.004, "the former USSR is well recorded, Africa and the UK hardly at all.   maps.tristanhotham.com/renamed-world",
         fontproperties=FELL, fontsize=8.5, color=MUT)
fig.savefig(os.path.join(ROOT, "reddit", "renamed_world_collage.png"), dpi=300, facecolor=fig.get_facecolor())
print(Image.open(os.path.join(ROOT, "reddit", "renamed_world_collage.png")).size)
