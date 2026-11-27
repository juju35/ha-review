#!/usr/bin/env python3
"""Room-card family: helper in src/shared, imported by the files that draw, `_rewire()` on the base card, and
rcBindNav(head, path, on) wiring with the drawing's signal. Usage: finish_rc_family.py REPO_DIR"""
import os, re, shutil, sys
repo = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
sh = os.path.join(repo, "src", "shared")
shutil.copy(os.path.join(here, "in-place-redraw.js"), os.path.join(sh, "in-place-redraw.js"))
idx = os.path.join(sh, "index.js")
t = open(idx).read()
if "in-place-redraw" not in t:
    t = t.replace('import "./helpers.js";\n', 'import "./helpers.js";\nimport "./in-place-redraw.js";\n', 1)
    assert "in-place-redraw" in t
    open(idx, "w").write(t)
# imports where rcMorph is used
for dp, _, fs in os.walk(os.path.join(repo, "src")):
    for f in fs:
        p = os.path.join(dp, f)
        if not f.endswith(".js") or f == "in-place-redraw.js":
            continue
        s = open(p).read()
        if "rcMorph(" in s and "from \"" not in s.split("rcMorph")[0][-2000:] + "" or ("rcMorph(" in s and "in-place-redraw" not in s):
            rel = os.path.relpath(os.path.join(sh, "in-place-redraw.js"), dp)
            rel = rel if rel.startswith(".") else "./" + rel
            imports = list(re.finditer(r'^import [^\n]*;\n', s, re.M))
            at = imports[-1].end() if imports else 0
            s = s[:at] + f'import {{ rcMorph }} from "{rel}";\n' + s[at:]
            open(p, "w").write(s)
# _rewire on the base card, before _paint
p = os.path.join(sh, "base-card.js")
s = open(p).read()
if "_rewire()" not in s.split("_paint(")[0] and "  _rewire() {" not in s:
    i = s.index("  _paint(")
    s = s[:i] + '''  // The listeners of the previous drawing dropped, and the options ({ signal }) of the new ones (`this._on`): the
  // nodes drawn in place (see rcMorph) are wired again for the items they now show, never twice.
  _rewire() {
    this._ac?.abort();
    this._ac = typeof AbortController === "function" ? new AbortController() : null;
    this._on = this._ac ? { signal: this._ac.signal } : undefined;
    return this._on;
  }

''' + s[i:]
    open(p, "w").write(s)
# rcBindNav(head, path) -> (head, path, on)
p = os.path.join(sh, "helpers.js")
s = open(p).read()
m = re.search(r"export const rcBindNav = \((\w+), (\w+)\) => \{\n([\s\S]*?)\n\};", s)
if m:
    head, path, body = m.groups()
    # the listeners' closing `);` at the statement level (a line starting at two spaces, or the same line)
    out = []
    for line in body.split("\n"):
        if line.startswith(f"  {head}.addEventListener(") and line.endswith(");"):
            line = line[:-2] + ", on);"
        elif line == "  });":
            line = "  }, on);"
        out.append(line)
    body = "\n".join(out)
    s = s[:m.start()] + f"export const rcBindNav = ({head}, {path}, on) => {{\n{body}\n}};" + s[m.end():]
    open(p, "w").write(s)
for dp, _, fs in os.walk(os.path.join(repo, "src")):
    for f in fs:
        p = os.path.join(dp, f)
        if f.endswith(".js") and "editor" not in f:
            s = open(p).read()
            n = re.sub(r"rcBindNav\(([^;]*?), ((?:c|nav|this\._config)\.?navigation_path|nav)\)", r"rcBindNav(\1, \2, this._on)", s)
            if n != s:
                open(p, "w").write(n)
print("ok", repo)
