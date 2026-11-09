"""Step 5: index.html from code/page_template.html, filled from data/results.json, with the full-screen snippet.
10.5281/zenodo.24075301, https://doi.org/10.5281/zenodo.24075301 and https://blog.tristanhotham.com/2026/10/31/renamed-world/ stay as placeholders for the publisher."""
from common import *

R = jload(f"{DATA}/results.json")
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
# facts stated in words on the page
assert R["peak_decades"][0]["decade"] == 1960 and R["peak_years"][0]["year"] == 1964 and R["peak_years"][0]["iso"] == "RO"
assert R["peak_years"][1]["year"] == 2016 and R["peak_years"][1]["iso"] == "UA"
assert R["most_renamed"][0]["label"] == "Astana" and R["most_renamed"][0]["n"] >= R["most_renamed"][1]["n"]
assert [c["new"] for c in R["ex"]["vladikavkaz"]["chain"]] == ["Орджоникидзе", "Дзауджикау", "Орджоникидзе", "Владикавказ"]
assert [c["new"] for c in R["ex"]["luhansk"]["chain"]].count("Ворошиловград") == 2
assert [c["new"] for c in R["ex"]["rybinsk"]["chain"]][-4:] == ["Щербаков", "Рыбинск", "Андропов", "Рыбинск"]
assert [c["new"] for c in R["ex"]["st_petersburg"]["chain"]] == ["Петроград", "Ленинград", "Санкт-Петербург"]
assert R["ex"]["volgograd"]["chain"][0]["old"] == "Tsaritsyn"
assert R["ireland"]["events"] == 0 and R["n"]["overridden"] == 2
assert R["uk"]["merger"] >= 0.6 * R["uk"]["renamings"]
assert R["ex"]["lyon"]["chain"][0]["new"] == "Commune-Affranchie" and R["ex"]["bordeaux"]["chain"][0]["new"] == "Commune-Franklin"
assert R["waves"]["other"]["top"][0][0] in ("FR", "JP") and R["waves"]["communist"]["n"] > R["waves"]["nation"]["n"] > R["waves"]["merger"]["n"]
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
CN = {c["iso"]: c["country"] for c in R["countries"]}
most = []
for m in R["most_renamed"][:20]:
    names = [m["chain"][0]["old"]] + [c["new"] for c in m["chain"]]
    most.append([m["label"], m["iso"], m["n"], " > ".join(names)])
t = t.replace("{{MOST}}", json.dumps(most, ensure_ascii=False))
t = t.replace("{{REPO}}", REPO).replace("{{AI}}", AI).replace("{{BYLINE}}", BYLINE).replace("{{VERSION}}", "20261108")
t = re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), t)
left = set(re.findall(r"\{\{([^}]+)\}\}", t))
assert left <= KEEP, left
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
