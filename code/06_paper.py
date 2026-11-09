"""Step 6: the paper. Fills code/paper_template.tex from data/results.json, adds tables, compiles with xelatex.
Output: release/paper/Hotham_Renamed_World.pdf and .tex beside the f_*.png figures.
The DOI stays a placeholder (https://doi.org/10.5281/zenodo.24075301 printed) unless the environment variable DOI is set: DOI=10.5281/zenodo.N python3 code/06_paper.py"""
import subprocess
import pandas as pd
from common import *
from rules import WAVES, WAVE_NAME

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Renamed_World"
CJK_RUN = re.compile(r"([\u3000-\u9fff\uac00-\ud7af]+)")
cjk = lambda s: CJK_RUN.sub(lambda m: "{\\cjk " + m.group(1) + "}", s)
import unicodedata
tex = lambda s: unicodedata.normalize("NFC", str(s)).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")
assert R["peak_years"][1]["year"] == 2016 and R["peak_years"][0]["year"] == 1964
assert R["most_renamed"][0]["label"] == "Astana" and R["ex"]["vladikavkaz"]["chain"][-1]["year"] == 1990
assert R["ex"]["lyon"]["chain"][-1]["year"] == 1814 and R["ex"]["bordeaux"]["chain"][-1]["year"] == 1814


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    return tex(str(v))


rows = "".join(f"{tex(WAVE_NAME[w])} & {R['waves'][w]['n']:,} & {R['waves'][w]['pc']:.1f} & {R['waves'][w]['countries']} & {R['waves'][w]['peak_decade']}s & "
               f"{', '.join(c for c, _ in R['waves'][w]['top'][:3])}\\\\\n" for w in WAVES)
TW = ("\\begin{table}[tbp]\\centering\\small\\caption{Renamings of places by wave: number, share, number of present-day countries, busiest decade and "
      "the three countries (ISO codes) with most.}\\label{tab:waves}\\begin{tabular}{lrrrrl}\\toprule Wave & n & \\% & Countries & Peak & Most in\\\\\\midrule\n"
      + rows + f"\\midrule All renamings & {R['n']['renamings']:,} & 100.0 & {R['n']['countries']} & {R['peak_decades'][0]['decade']}s & \\\\\n\\bottomrule\\end{{tabular}}\\end{{table}}")
RULES = [("1", "Undoing", "Communist name part in the old name and not in the new, in a country under communist rule at some time, 1953 on; every Ukrainian renaming of 2015 to 2017 (made under the decommunisation laws); and the French restorations of 1800 to 1815 of names given in the 1790s"),
         ("2", "Revolution and communism", "Communist name part in the new name during communist rule, or a French renaming of 1790 to 1799"),
         ("3", "War and new borders", "Poland 1918 to 1922 and 1945 to 1950; Czechia 1945 to 1950; Kaliningrad, Karelia and Sakhalin after 1940 or 1945; Klaipeda, Istria, Slovenia, South Tyrol, Alsace-Moselle, Romania 1918 to 1925, North Schleswig"),
         ("4", "Revolution and communism", "Any other renaming under communist rule (USSR 1917 to 1989, eastern Europe 1945 to 1988, China, Vietnam and others to 1980), with communist rule starting only in 1939 in western Ukraine and western Belarus, 1940 in Chernivtsi, southern Bessarabia and Karelia, and 1945 in Transcarpathia, Kaliningrad and southern Sakhalin; sovkhoz settlements given names"),
         ("5", "Mergers and reform", "Settlements and areas in municipal merger programmes (Japan 1888 to 1890, 1953 to 1961, 1999 to 2010; France 1971 to 1977, 2015 on; Belgium, Denmark, Sweden, Germany, the Netherlands, Quebec, Greece); administrative reforms (Ukraine 2018 to 2020, Russia 2004 to 2006, Georgia 2006); names joined with and, et, und"),
         ("6", "Decolonisation", "From three years before to 25 years after independence, in former colonies in Africa, Asia, Oceania and the Caribbean"),
         ("7", "Nation-building", "Ireland from 1916, India and South Asia after independence, the former Soviet republics after 1991, eastern Europe after 1989, Turkey, Greece, Israel, Finland, Norway, the Baltic states, Spanish regions with their own languages from 1975, South Africa from 1994; later renamings in former colonies"),
         ("8", "Mergers and reform", "Any other renaming of an administrative area"),
         ("9", "Other", "Everything else")]
TR = ("\\begin{table}[tbp]\\centering\\small\\caption{Rules for the waves, applied in order; the first that applies decides. Full lists in code/rules.py.}\\label{tab:rules}"
      "\\begin{tabular}{rlp{10.2cm}}\\toprule & Wave & Rule\\\\\\midrule\n" + "".join(f"{a} & {b} & {tex(c)}\\\\\n" for a, b, c in RULES) + "\\bottomrule\\end{tabular}\\end{table}")
C = pd.read_csv(f"{DATA}/countries.csv").head(15)
rows = "".join(f"{tex(r.country)} & {r.n:,} & {r.places:,} & " + " & ".join(str(int(getattr(r, w, 0))) for w in WAVES) + "\\\\\n" for r in C.itertuples())
TC = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{The fifteen countries with most renamings, by wave: decolonisation (Dec), revolution and communism (Com), "
      "undoing (Und), war (War), nation-building (Nat), mergers and reform (Mer), other (Oth).}\\label{tab:countries}\\begin{tabular}{lrrrrrrrrr}\\toprule Country & n & Places & Dec & Com & Und & War & Nat & Mer & Oth\\\\\\midrule\n"
      + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for m in R["most_renamed"][:20]:
    names = [m["chain"][0]["old"]] + [c["new"] for c in m["chain"]]
    yrs = ", ".join(str(c["year"]) for c in m["chain"])
    rows += f"{tex(m['label'])} & {m['iso']} & {m['n']} & {{\\ns {cjk(tex(' > '.join(names)))}}} & {yrs}\\\\\n"
TM = ("{\\footnotesize\\begin{longtable}{p{2.6cm}lrp{7.6cm}p{2.4cm}}\\caption{The places renamed most often (official names in the language of the renamings, "
      "as recorded in Wikidata).}\\label{tab:most}\\\\\\toprule Place & & n & Names & Years\\\\\\midrule\\endfirsthead\n"
      "\\multicolumn{5}{l}{\\small Table \\ref{tab:most}, continued}\\\\\\toprule Place & & n & Names & Years\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}}")
ov = pd.read_csv(f"{DATA}/overrides_applied.csv").fillna("")
rows = "".join(f"{r.qid} & {r.year} & {tex(r.action)} & {tex(r.reason)}\\\\\n" for r in ov.itertuples())
TO = ("\\begin{table}[tbp]\\centering\\small\\caption{Events corrected by hand.}\\label{tab:override}\\begin{tabular}{lllp{10cm}}\\toprule Item & Year & Action & Reason\\\\\\midrule\n"
      + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("\\usepackage{setspace}", "\\usepackage{setspace}\n\\newfontfamily\\ns{FreeSerif}\n\\newfontfamily\\cjk{Noto Serif CJK SC}")
t = t.replace("{{AI}}", AI).replace("{{PAGE}}", PAGE).replace("{{REPO}}", REPO)
t = t.replace("{{TABLE_WAVES}}", TW).replace("{{TABLE_RULES}}", TR).replace("{{TABLE_COUNTRIES}}", TC).replace("{{TABLE_MOST}}", TO + "\n" + TM)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24075301", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
