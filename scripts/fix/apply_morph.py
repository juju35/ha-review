#!/usr/bin/env python3
"""Swap a card's whole-content rewrite (`this.shadowRoot.innerHTML = html;`) for the in-place redraw (rcMorph).
Usage: apply_morph.py REPO_DIR SINK_FILE  — copies scripts/fix/in-place-redraw.js to src/, imports it, replaces the sink."""
import os, re, shutil, sys
repo, sink = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(repo, "src")
shutil.copy(os.path.join(here, "in-place-redraw.js"), os.path.join(src, "in-place-redraw.js"))
p = os.path.join(repo, sink)
s = open(p).read()
rel = os.path.relpath(os.path.join(src, "in-place-redraw.js"), os.path.dirname(p))
rel = rel if rel.startswith(".") else "./" + rel
if "rcMorph" not in s.split("\n\n")[0] and 'from "' + rel + '"' not in s:
    imports = list(re.finditer(r'^import [^\n]*;\n', s, re.M))
    at = imports[-1].end() if imports else 0
    s = s[:at] + f'import {{ rcMorph }} from "{rel}";\n' + s[at:]
old = "    this.shadowRoot.innerHTML = html;\n"
assert s.count(old) == 1, (p, s.count(old))
s = s.replace(old, "    // In place (see rcMorph): the nodes stay, so the card keeps its height, its animations and its focus.\n    rcMorph(this.shadowRoot, html);\n")
open(p, "w").write(s)
idx = os.path.join(src, "index.js")
if os.path.exists(idx):
    t = open(idx).read()
    if "in-place-redraw" not in t:
        side = list(re.finditer(r'^import "\./[^"]+";\n', t, re.M))
        assert side, "index.js has no side-effect imports"
        # right after the helpers (or the first module), before any card class
        h = next((m for m in side if "helper" in m.group(0)), side[0])
        t = t[:h.end()] + 'import "./in-place-redraw.js";\n' + t[h.end():]
        open(idx, "w").write(t)
print("ok", p)
