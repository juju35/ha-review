#!/usr/bin/env python3
"""Phase 4b — README option tables vs options read by the card code.
Usage: python3 scripts/audit_options.py [SRC_DIR] -> results/auto/options.json, results/OPTIONS.md"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "src")
REPOS = open(os.path.join(ROOT, "repos.txt")).read().split()
COMMON = {"type", "entity", "entities", "name", "title", "icon", "grid_options", "view_layout", "card_mod", "visibility"}
res = []
for r in REPOS:
    repo = os.path.join(SRC, r)
    if not os.path.isdir(os.path.join(repo, "src")):
        continue
    rd = open(os.path.join(repo, "README.md"), encoding="utf-8").read()
    doc = set(re.findall(r"^\|\s*`([a-z][a-z0-9_]*)`\s*\|", rd, re.M))
    code = ""
    allcode = ""
    for d, dirs, fs in os.walk(repo):
        dirs[:] = [x for x in dirs if x not in ("i18n", ".git", "node_modules", "translations", "test", "tests")]
        for f in fs:
            if f.endswith(".py"):
                allcode += open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
    for d, dirs, fs in os.walk(os.path.join(repo, "src")):
        dirs[:] = [x for x in dirs if x != "i18n"]
        for f in fs:
            if f.endswith(".js"):
                code += open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
    used = set(re.findall(r"""(?:config|_config|cfg|_cfg|conf|this\._c|\bc)\??\.([a-z][a-z0-9_]*)\b""", code))
    used |= set(re.findall(r"""(?:config|_config|cfg|_cfg|conf|\bc)\[\s*['"]([a-z][a-z0-9_]*)['"]\s*\]""", code))
    quoted = set(re.findall(r"""['"`]([a-z][a-z0-9_]{2,})['"`]""", code))
    dead = sorted(o for o in doc - COMMON if o not in used and o not in quoted and o not in code and o not in allcode)
    undocumented = sorted(o for o in used - doc - COMMON if re.search(r"(show_|hide_|_entity$|_entities$|^illustration)", o))
    res.append({"repo": r, "documented": len(doc), "doc_not_in_code": dead, "used_not_documented": undocumented})
json.dump(res, open(os.path.join(ROOT, "results", "auto", "options.json"), "w"), indent=1)
out = ["# README options vs code (automatic)", "",
       "`doc_not_in_code`: option in a README table whose name never appears in the card source (stale doc or typo).",
       "`used_not_documented`: `show_*` / `hide_*` / `*_entity` / `illustration*` options read by the code but absent from the README tables.", ""]
for x in res:
    if x["doc_not_in_code"] or x["used_not_documented"]:
        out.append(f"- **{x['repo']}** — documented but absent from code: {', '.join(f'`{o}`' for o in x['doc_not_in_code']) or '—'}; read but undocumented: {', '.join(f'`{o}`' for o in x['used_not_documented']) or '—'}")
open(os.path.join(ROOT, "results", "OPTIONS.md"), "w").write("\n".join(out) + "\n")
print(sum(1 for x in res if x["doc_not_in_code"]), "repos with stale docs;", sum(1 for x in res if x["used_not_documented"]), "with undocumented options")
