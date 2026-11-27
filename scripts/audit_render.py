#!/usr/bin/env python3
"""Static companion of test_scroll_update.py: how each card redraws on a hass update.
Appends a "Static check" section to results/SCROLL.md and writes results/auto/render.json."""
import glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "src")
REPOS = open(os.path.join(ROOT, "repos.txt")).read().split()
res = []
for r in REPOS:
    files = [p for p in glob.glob(os.path.join(SRC, r, "src", "**", "*.js"), recursive=True) if "/i18n/" not in p]
    cards = [p for p in files if "panel" not in p]
    if not cards:
        continue
    c = "\n".join(open(p, encoding="utf-8", errors="replace").read() for p in cards)
    morph = bool(re.search(r"Morph|morph\(|patchNode|inPlace", c))
    inner = len(re.findall(r"\.innerHTML\s*=", c))
    guard = bool(re.search(r"_sig\b|_changed\(|_lastSig|signature|_renderKey|_key\s*===", c))
    overflow = len(re.findall(r"overflow(?:-[xy])?\s*:\s*(?:auto|scroll)", c))
    restore = bool(re.search(r"scrollTop\s*=|scrollLeft\s*=", c))
    if morph:
        strategy = "in-place redraw (morph)"
    elif guard:
        strategy = "innerHTML behind a change signature"
    else:
        strategy = "innerHTML on every update"
    issues = []
    if not morph and inner:
        issues.append("no in-place redraw: each relevant state change rewrites the whole card (animations restart, ha-icon/ha-card re-upgrade, page can jump)")
    if not morph and overflow and not restore:
        issues.append(f"{overflow} scrollable box(es) and no scroll restore: their scroll resets on every redraw")
    res.append({"repo": r, "strategy": strategy, "innerHTML": inner, "overflow": overflow, "restore": restore, "issues": issues})
json.dump(res, open(os.path.join(ROOT, "results", "auto", "render.json"), "w"), indent=1)
md = open(os.path.join(ROOT, "results", "SCROLL.md")).read().split("\n## Static check")[0]
lines = ["", "## Static check — redraw strategy (`scripts/audit_render.py`)", "",
         f"In-place redraw (morph): {sum(1 for x in res if x['strategy'].startswith('in-place'))} repos · "
         f"innerHTML behind a signature: {sum(1 for x in res if 'signature' in x['strategy'])} · "
         f"innerHTML on every update: {sum(1 for x in res if 'every' in x['strategy'])}", "",
         "| Repo | Strategy | Issue |", "|---|---|---|"]
for x in res:
    if x["issues"]:
        lines.append(f"| {x['repo']} | {x['strategy']} | {'; '.join(x['issues'])} |")
open(os.path.join(ROOT, "results", "SCROLL.md"), "w").write(md.rstrip() + "\n" + "\n".join(lines) + "\n")
print(len([x for x in res if x["issues"]]), "repos flagged")
