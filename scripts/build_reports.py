#!/usr/bin/env python3
"""Phase 5 — merge the automatic results with the manual triage into results/repos/<repo>.md.

Triage lives in results/triage.json:
  {"false_positive": {"<repo>": ["<substring of the finding>", ...]},
   "notes": {"<repo>": [{"sev": "...", "area": "...", "msg": "..."}]}}
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "results")
REPOS = open(os.path.join(ROOT, "repos.txt")).read().split()
conv = {x["repo"]: x for x in json.load(open(os.path.join(R, "auto", "conventions.json")))}
vis = {x["repo"]: x for x in json.load(open(os.path.join(R, "auto", "visual.json")))}
code = {x["repo"]: x for x in json.load(open(os.path.join(R, "auto", "code.json")))}
sec = {x["repo"]: {"issues": [i for i in x["issues"] if i["code"] != "security-md"]}
       for x in json.load(open(os.path.join(R, "auto", "security.json")))}
opts = {x["repo"]: x for x in json.load(open(os.path.join(R, "auto", "options.json")))}
tri = json.load(open(os.path.join(R, "triage.json")))
progress = json.load(open(os.path.join(ROOT, "progress.json")))
ORDER = {"major": 0, "minor": 1, "info": 2}
os.makedirs(os.path.join(R, "repos"), exist_ok=True)
index = []
for r in REPOS:
    fps = tri["false_positive"].get(r, []) + tri["false_positive"].get("*", [])
    rows = []
    for area, src in (("conventions", conv), ("visual", vis), ("code", code), ("security", sec)):
        for i in src.get(r, {}).get("issues", []):
            fp = any(s in i["msg"] or s == i["code"] for s in fps)
            rows.append((i["sev"], area, f"{i['code']}: {i['msg']}", "false positive" if fp else "auto"))
    o = opts.get(r)
    for n in tri.get("options_real", {}).get(r, []):
        rows.append(("minor", "docs", n, "verified"))
    for n in tri["notes"].get(r, []):
        rows.append((n["sev"], n["area"], n["msg"], "verified"))
    kind = conv.get(r, {}).get("kind", "?")
    real = [x for x in rows if x[3] != "false positive" and x[0] != "info"]
    lines = [f"# {r}", "", f"- Kind: {kind}", f"- Reviewed revision: `{progress[r]['sha'][:10]}`",
             f"- Versions: {', '.join(f'{k}={v}' for k, v in conv.get(r, {}).get('versions', {}).items() if v)}",
             f"- Findings to act on: **{len(real)}** (major {sum(1 for x in real if x[0] == 'major')}, minor {sum(1 for x in real if x[0] == 'minor')})", ""]
    if rows:
        lines += ["| Sev | Area | Finding | Status |", "|---|---|---|---|"]
        for sev, area, msg, st in sorted(rows, key=lambda x: (x[3] == "false positive", ORDER[x[0]])):
            lines.append(f"| {sev} | {area} | {msg.replace('|', '\\|')} | {st} |")
    else:
        lines.append("Nothing flagged by any phase.")
    open(os.path.join(R, "repos", f"{r}.md"), "w").write("\n".join(lines) + "\n")
    progress[r]["manual"] = "done"
    index.append((r, kind, len(real), sum(1 for x in real if x[0] == "major")))
json.dump(progress, open(os.path.join(ROOT, "progress.json"), "w"), indent=1)
out = ["# Per-repo reports", "", "| Repo | Kind | To act on | Major |", "|---|---|---|---|"]
for r, k, n, m in sorted(index, key=lambda x: (-x[3], -x[2], x[0])):
    out.append(f"| [{r}](repos/{r}.md) | {k} | {n} | {m} |")
open(os.path.join(R, "INDEX.md"), "w").write("\n".join(out) + "\n")
print(sum(x[2] for x in index), "findings to act on;", sum(1 for x in index if x[2] == 0), "repos with none")
