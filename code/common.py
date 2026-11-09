"""Shared paths, constants and helpers for the renamed-world study ("The renamed world").

Raw input (read in place, never modified):
  RAW   /home/claude/newdata/raw_new9/renamed.tsv.gz
        Wikidata via QLever: items with coordinates (P625) that have official name (P1448) statements with a start time (P580)
        or end time (P582) qualifier. Columns ?item ?itemLabel (English label) ?coord ?country (P17) ?type (P31) ?name
        (the P1448 value, with its language tag) ?start ?end. One row per name statement and per type and country, so the rows
        are deduplicated here. End values given as an IRI under .well-known/genid are Wikidata "unknown value" dates.
  GEO   /home/claude/newdata/raw/geo/ne_10m_admin_0_countries.geojson (current country and continent of each point), ne_50m_land
        and ne_50m_admin_0_countries (figures). Natural Earth, public domain.
Intermediates go to WORK, outside the repo.
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("RW_RAW", "/home/claude/newdata/raw_new9/renamed.tsv.gz")
GEO = os.environ.get("RW_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("RW_FONTS", "/home/claude/ref/fonts")
INK = os.environ.get("RW_INK", "/home/claude/studies/ink-map")
INKFONTS = os.path.join(INK, "fonts", "ttf")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
WORK = os.environ.get("RW_WORK", "/home/claude/scratch/renamed-world/work")
for d in (DATA, IMG, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "renamed-world"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, list):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {k: nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None, nodash=True):
    obj = nonan(obj)
    if nodash:
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    raise ValueError(f)
