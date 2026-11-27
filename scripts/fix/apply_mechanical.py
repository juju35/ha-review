#!/usr/bin/env python3
"""Apply the mechanical fixes of the review to the local clones (no git operation).

Fixes (see SUMMARY.md / DECISIONS.md):
  security   SECURITY.md (every repo)
  idle       idle colour token -> var(--secondary-text-color, #9e9e9e)
  radius     .tile border-radius -> 10px
  resource   README Marketplace section names the /local/community/ resource
  biome      biome 2.6.8 everywhere (biome.json $schema, pre-commit rev + additional_dependencies)
Usage: python3 scripts/fix/apply_mechanical.py SRC_DIR [repo ...]
Prints, per repo, the fixes applied and whether shipped code changed (=> version bump).
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = sys.argv[1]
REPOS = sys.argv[2:] or open(os.path.join(ROOT, "repos.txt")).read().split()
BIOME = "2.6.8"

SECURITY = """# Security policy

## Reporting a vulnerability

Please **do not open a public issue** for a security problem.

Report it privately with GitHub's
[private vulnerability reporting](https://github.com/juju35/{repo}/security/advisories/new)
(Security tab → *Report a vulnerability*). Include what is affected, how to reproduce it and the
version you use.

You will get an answer within a few days. Once fixed, the fix ships in a release and the advisory
is published with credit to the reporter, unless you prefer to stay anonymous.

## Supported versions

Only the latest release receives fixes. Update through the Home Assistant Marketplace.
"""


def src_js(repo):
    for p in glob.glob(os.path.join(repo, "src", "**", "*.js"), recursive=True):
        if "/i18n/" not in p:
            yield p


def edit(path, fn):
    t = open(path, encoding="utf-8").read()
    n = fn(t)
    if n != t:
        open(path, "w", encoding="utf-8").write(n)
        return True
    return False


def fix_tile_radius(t):
    def rule(m):
        sel, body = m.group(1), m.group(2)
        sels = [s.strip() for s in sel.split(",")]
        if not any(re.fullmatch(r"(?:[\w.:#\[\]=\"'-]*\s+)?\.tile(?:[.:][\w-]+(?:\([^)]*\))?)*", s) for s in sels):
            return m.group(0)
        nb = re.sub(r"(?<![\w-])border-radius\s*:\s*(12|14)px", "border-radius: 10px", body)
        return sel + "{" + nb + "}"
    return re.sub(r"([^{}]{1,200})\{([^{}]*)\}", rule, t)


def apply(name):
    repo = os.path.join(SRC, name)
    done, shipped = [], False
    # security policy
    p = os.path.join(repo, "SECURITY.md")
    if not os.path.exists(p):
        open(p, "w").write(SECURITY.replace("{repo}", name))
        done.append("security")
    # idle token
    for f in src_js(repo):
        if edit(f, lambda t: re.sub(r"(--[a-z0-9]{1,6}-idle\s*:\s*)var\(--disabled-text-color,\s*#9e9e9e\)",
                                    r"\1var(--secondary-text-color, #9e9e9e)", t)):
            if "idle" not in done:
                done.append("idle")
            shipped = True
    # tile radius
    for f in src_js(repo):
        if edit(f, fix_tile_radius):
            if "radius" not in done:
                done.append("radius")
            shipped = True
    # README resource line (cards)
    hj = os.path.join(repo, "hacs.json")
    rd = os.path.join(repo, "README.md")
    if os.path.exists(hj) and os.path.exists(rd) and not os.path.isdir(os.path.join(repo, "custom_components")):
        fname = json.load(open(hj)).get("filename")
        if fname:
            def res(t):
                if "/local/community/" in t:
                    return t
                return re.sub(r"(Then click \*\*Install\*\*, and reload your browser when the Marketplace asks you to\.)(?! The resource)",
                              rf"\1 The resource is `/local/community/{name}/{fname}`.", t, count=1)
            if edit(rd, res):
                done.append("resource")
    # biome version
    bj = os.path.join(repo, "biome.json")
    if os.path.exists(bj) and edit(bj, lambda t: re.sub(r"schemas/2\.\d+\.\d+/schema\.json", f"schemas/{BIOME}/schema.json", t)):
        done.append("biome")
    pc = os.path.join(repo, ".pre-commit-config.yaml")
    if os.path.exists(pc) and edit(pc, lambda t: re.sub(r"@biomejs/biome@2\.\d+\.\d+", f"@biomejs/biome@{BIOME}",
                                                       re.sub(r'(biomejs/pre-commit\s*\n\s*rev:\s*"?)v2\.\d+\.\d+', rf"\1v{BIOME}", t))):
        if "biome" not in done:
            done.append("biome")
    return done, shipped


if __name__ == "__main__":
    out = {}
    for r in REPOS:
        d, s = apply(r)
        out[r] = {"fixes": d, "shipped": s}
        print(r, d, "BUMP" if s else "")
    json.dump(out, open(os.path.join(ROOT, "results", "auto", "fix_mechanical.json"), "w"), indent=1)
