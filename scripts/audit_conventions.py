#!/usr/bin/env python3
"""Phase 2 — conventions / CI audit of every repo in repos.txt.

Usage: python3 scripts/audit_conventions.py [SRC_DIR]
Writes results/auto/conventions.json and results/CONVENTIONS.md.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "src")
REPOS = open(os.path.join(ROOT, "repos.txt")).read().split()
LANGS = ["en", "fr", "de", "es", "it", "nl", "pt", "pl", "sr", "sr-Latn", "ro", "da", "sv",
         "bg", "ru", "uk", "hu", "sk", "cs", "sl", "lv", "el"]
FR_ONLY = {"ha-carburants-france", "ha-tempo-card", "ha-ecowatt-card", "ha-zlinky-card",
           "ha-pronote-card", "ha-ent-one", "ha-ent-educartable", "ha-ent-skolengo",
           "ha-family-day-card", "ha-saint-of-the-day", "ha-public-transport"}
SKIP_DIRS = {".git", "node_modules", "screenshots", "dist", "__pycache__"}


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def walk(repo, exts):
    for d, dirs, files in os.walk(repo):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith(exts):
                yield os.path.join(d, f)


def kind_of(repo):
    if os.path.isdir(os.path.join(repo, "themes")):
        return "theme"
    if glob.glob(os.path.join(repo, "custom_components", "*", "manifest.json")):
        for p in walk(os.path.join(repo, "custom_components"), (".py",)):
            t = read(p) or ""
            if "async_register_built_in_panel" in t or "panel_custom" in t:
                return "panel-integration"
        return "integration"
    return "card"


def changelog_version(repo):
    t = read(os.path.join(repo, "CHANGELOG.md")) or ""
    m = re.search(r"^##\s*\[?v?(\d+\.\d+\.\d+)", t, re.M)
    return m.group(1) if m else None


def audit(name):
    repo = os.path.join(SRC, name)
    k = kind_of(repo)
    issues = []  # (severity, code, message)

    def bad(sev, code, msg):
        issues.append({"sev": sev, "code": code, "msg": msg})

    # --- repo hygiene -----------------------------------------------------
    for f in ["CLAUDE.md", "LICENSE", "README.md", "CHANGELOG.md", "commitlint.config.js", "hacs.json"]:
        if f == "commitlint.config.js" and glob.glob(os.path.join(repo, "commitlint.config.*")):
            continue
        if not os.path.exists(os.path.join(repo, f)):
            bad("major" if f in ("README.md", "LICENSE", "hacs.json") else "minor", "missing-file", f"`{f}` missing")
    lic = read(os.path.join(repo, "LICENSE")) or ""
    if lic and "juju35" not in lic:
        bad("minor", "license-holder", "LICENSE holder is not `juju35`")
    pc = read(os.path.join(repo, ".pre-commit-config.yaml"))
    if pc is None:
        bad("minor", "pre-commit", "no `.pre-commit-config.yaml`")
    else:
        if "commit-msg" not in pc or "commitlint" not in pc:
            bad("minor", "pre-commit", "pre-commit lacks commitlint / commit-msg hook type")
        if "screenshots-used" not in pc and os.path.isdir(os.path.join(repo, "screenshots")):
            bad("minor", "pre-commit", "pre-commit lacks the `screenshots-used` hook")
        has_js = os.path.isdir(os.path.join(repo, "src")) or glob.glob(os.path.join(repo, "custom_components", "*", "frontend"))
        if k != "theme" and has_js and "biome" not in pc:
            bad("minor", "pre-commit", "pre-commit lacks biome")
        if k in ("integration", "panel-integration") and "ruff" not in pc:
            bad("minor", "pre-commit", "pre-commit lacks ruff")
    if k in ("integration", "panel-integration"):
        if not os.path.exists(os.path.join(repo, ".vulture_whitelist.py")):
            bad("minor", "lint", "no `.vulture_whitelist.py` (vulture)")
    if k != "theme" and not os.path.exists(os.path.join(repo, ".jscpd.json")):
        bad("minor", "lint", "no `.jscpd.json`")

    # dist committed
    dist_js = [p for p in glob.glob(os.path.join(repo, "dist", "**", "*.js"), recursive=True)]
    if dist_js:
        bad("major", "dist-committed", f"JS committed in dist/ ({len(dist_js)} files)")

    # --- workflows ----------------------------------------------------------
    wf = os.path.join(repo, ".github", "workflows")
    wfs = {os.path.basename(p): read(p) for p in glob.glob(os.path.join(wf, "*.y*ml"))}
    for need in ["validate.yml", "release.yml", "cleanup-branches.yml"]:
        if need not in wfs:
            bad("major" if need == "release.yml" else "minor", "workflow", f"workflow `{need}` missing")
    if k != "theme" and "lint.yml" not in wfs:
        bad("minor", "workflow", "workflow `lint.yml` missing")
    rel = wfs.get("release.yml") or ""
    if rel:
        if "workflow_dispatch" not in rel:
            bad("major", "release", "release.yml has no workflow_dispatch")
        if "startsWith(github.event.head_commit.message, 'feat')" not in rel:
            bad("major", "release", "release.yml not gated on feat/fix squash titles")
    shot = wfs.get("screenshots.yml")
    if os.path.isdir(os.path.join(repo, "screenshots")):
        if shot is None:
            bad("minor", "screenshots", "screenshots/ present but no screenshots.yml workflow — static copies that can drift from the card/theme they show")
        else:
            if "bookworm" not in shot and "debian:12" not in shot:
                bad("minor", "screenshots", "screenshots.yml not in a Debian 12 container")
            if "create-github-app-token" not in shot:
                bad("major", "screenshots", "screenshots.yml does not use the GitHub App token")
            if "[skip ci]" in shot:
                bad("minor", "screenshots", "screenshots.yml still adds `[skip ci]`")
            if "pull_request" not in shot:
                bad("minor", "screenshots", "screenshots.yml not triggered on pull_request")
            if re.search(r"push:\s*\n\s*branches:\s*\[?\s*main", shot):
                bad("major", "screenshots", "screenshots.yml pushes on main")
    # unpinned actions
    unpinned = set()
    for n, t in wfs.items():
        for m in re.finditer(r"uses:\s*([\w.-]+/[\w./-]+)@([\w.-]+)", t or ""):
            if not re.fullmatch(r"[0-9a-f]{40}", m.group(2)):
                unpinned.add(f"{m.group(1)}@{m.group(2)}")
    if unpinned:
        bad("minor", "actions-pin", "actions not pinned to a SHA: " + ", ".join(sorted(unpinned)[:5]))

    # --- versions -----------------------------------------------------------
    cl = changelog_version(repo)
    versions = {"CHANGELOG.md": cl}
    if k == "card":
        pj = read(os.path.join(repo, "package.json"))
        pl = read(os.path.join(repo, "package-lock.json"))
        if pj:
            versions["package.json"] = json.loads(pj).get("version")
        else:
            bad("major", "version", "no package.json")
        if pl:
            j = json.loads(pl)
            versions["package-lock.json"] = j.get("version")
            versions["package-lock.json packages['']"] = j.get("packages", {}).get("", {}).get("version")
        # card version constant(s)
        consts = set()
        for p in walk(os.path.join(repo, "src"), (".js",)):
            for m in re.finditer(r"[A-Z_]*VERSION\s*=\s*['\"](\d+\.\d+\.\d+)['\"]", read(p) or ""):
                consts.add(m.group(1))
        if consts:
            versions["src *_VERSION"] = ",".join(sorted(consts))
    elif k in ("integration", "panel-integration"):
        for mf in glob.glob(os.path.join(repo, "custom_components", "*", "manifest.json")):
            j = json.loads(read(mf))
            versions["manifest.json"] = j.get("version")
            if not j.get("categories") and "categories" not in j:
                # Marketplace categories (convention nov. 2026)
                bad("minor", "manifest", "manifest.json has no Marketplace `categories`")
            for key in ("documentation", "issue_tracker", "codeowners", "iot_class", "config_flow"):
                if key not in j:
                    bad("minor", "manifest", f"manifest.json has no `{key}`")
            cdir = os.path.dirname(mf)
            ct = read(os.path.join(cdir, "const.py")) or ""
            m = re.search(r"VERSION[^=\n]*=\s*['\"](\d+\.\d+\.\d+)['\"]", ct)
            versions["const.py"] = m.group(1) if m else None
            consts = set()
            for p in walk(repo, (".js",)):
                if "/test" in p or "/scripts/" in p:
                    continue
                for mm in re.finditer(r"[A-Z_]*VERSION\s*=\s*['\"](\d+\.\d+\.\d+)['\"]", read(p) or ""):
                    consts.add(mm.group(1))
            if consts:
                versions["JS *_VERSION"] = ",".join(sorted(consts))
            # services.yaml vs translations services
            if os.path.exists(os.path.join(cdir, "services.yaml")) and not os.path.exists(os.path.join(cdir, "icons.json")):
                bad("minor", "manifest", "services.yaml present but no icons.json (service icons)")
            # translations of the integration
            tr = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(cdir, "translations", "*.json"))}
            miss = [lg for lg in LANGS if lg not in tr]
            if miss:
                bad("minor", "i18n", "integration translations missing: " + ", ".join(miss))
            if os.path.exists(os.path.join(cdir, "strings.json")) is False and tr and "en" not in tr:
                bad("major", "i18n", "integration has no en.json")
    main_v = {v for kk, v in versions.items() if v and "_VERSION" not in kk}
    js_v = set()
    for kk, v in versions.items():
        if v and "_VERSION" in kk:
            js_v.update(v.split(","))
    if len(main_v) == 1 and js_v and not (main_v & js_v):
        bad("major", "version", "no JS *_VERSION constant matches the release version: " + ", ".join(f"{a}={b}" for a, b in versions.items()))
    elif len(main_v) == 1 and len(js_v) > 1:
        bad("info", "version", "several JS *_VERSION values (sub-cards lag behind): " + versions.get("JS *_VERSION", versions.get("src *_VERSION", "")))
    flat = main_v
    if len(flat) > 1:
        bad("major", "version", "version mismatch: " + ", ".join(f"{a}={b}" for a, b in versions.items()))
    if not cl:
        bad("minor", "version", "no `## X.Y.Z` section in CHANGELOG.md")

    # --- hacs.json ------------------------------------------------------------
    hj = read(os.path.join(repo, "hacs.json"))
    if hj:
        try:
            h = json.loads(hj)
            if name in FR_ONLY and "country" not in h:
                bad("minor", "hacs", "France-only repo without `country` in hacs.json")
            if name not in FR_ONLY and "country" in h:
                bad("info", "hacs", f"`country` {h['country']} set — check it is intended")
            if "name" not in h:
                bad("minor", "hacs", "hacs.json has no `name`")
        except json.JSONDecodeError:
            bad("major", "hacs", "hacs.json is not valid JSON")

    # --- README -----------------------------------------------------------------
    rd = read(os.path.join(repo, "README.md")) or ""
    if rd:
        low = rd.lower()
        if "buymeacoffee" not in low:
            bad("minor", "readme", "no Buy Me a Coffee link")
        if "marketplace" not in low:
            bad("major", "readme", "no Marketplace install section")
        hacs_words = [m.group(0) for m in re.finditer(r"[^\n]*\bHACS\b[^\n]*", rd)
                      if "hacs.yml" not in m.group(0) and "hacs/action" not in m.group(0)
                      and "img.shields.io" not in m.group(0) and "hacs/default" not in m.group(0)
                      and "HACS Validation" not in m.group(0) and "and HACS on" not in m.group(0)
                      and "Before Home Assistant 2026.11" not in m.group(0)]
        if hacs_words:
            bad("minor", "readme", f"stale HACS wording ({len(hacs_words)} lines), e.g. `{hacs_words[0].strip()[:90]}`")
        if "/local/community/" not in rd and k == "card":
            bad("minor", "readme", "no `/local/community/` resource path in install section")
        if "Settings → Marketplace" not in rd and "Settings -> Marketplace" not in rd and "Settings > Marketplace" not in rd:
            bad("minor", "readme", "no `Settings → Marketplace → Add from link` instruction")
        intro = "\n".join(rd.splitlines()[:40])
        if re.search(r"\b(Rennes)\b", intro) and "STAR" not in intro:
            bad("minor", "readme", "README intro mentions the author's city")
        # own logo centered under badges
        head = "\n".join(rd.splitlines()[:25])
        if not re.search(r'<p align="center">\s*<img[^>]+(icon|logo)\.(svg|png)', head, re.S):
            bad("minor", "readme", "own logo not centered at the top of the README")
        imgs = re.findall(r"<img[^>]*>", rd)
        unbounded = [i for i in imgs if "width" not in i and "height" not in i and "shields.io" not in i
                     and "badge" not in i and "buymeacoffee" not in i.lower()]
        md_imgs = re.findall(r"!\[[^\]]*\]\((?!https://img\.shields)[^)]+\)", rd)
        md_imgs = [m for m in md_imgs if "shields.io" not in m and "badge" not in m.lower()
                   and "my.home-assistant.io" not in m and "buymeacoffee" not in m.lower()]
        if unbounded or md_imgs:
            bad("minor", "readme", f"{len(unbounded) + len(md_imgs)} README image(s) without width/height bound")
        if k in ("card", "panel-integration") and "## Supported integrations" not in rd:
            # only relevant when the card is built on other integrations
            if re.search(r"integration", low) and k == "card":
                bad("info", "readme", "no `## Supported integrations` section (check whether relevant)")
        if re.search(r"##\s*Supported Integrations\b", rd):
            bad("minor", "readme", "`Supported Integrations` capitalisation differs from `Supported integrations`")
        # screenshots referenced
        shots = glob.glob(os.path.join(repo, "screenshots", "*"))
        unref = [os.path.basename(s) for s in shots if os.path.basename(s) not in rd]
        if unref:
            bad("minor", "screenshots", f"{len(unref)} screenshot(s) not shown in README: {', '.join(unref[:4])}")
        # dark/light twins
        names = {os.path.basename(s) for s in shots}
        orphans = []
        for n in names:
            if "-dark" in n and n.replace("-dark", "-light") not in names and n.replace("-dark", "") not in names:
                orphans.append(n)
        if orphans:
            bad("minor", "screenshots", f"dark screenshots without light twin: {', '.join(sorted(orphans)[:4])}")
        brokenlinks = [m for m in re.findall(r"\]\((?!https?:|#|mailto:)([^)\s]+)\)", rd)
                       if not os.path.exists(os.path.join(repo, m.split("#")[0]))]
        if brokenlinks:
            bad("major", "readme", f"broken relative link(s): {', '.join(brokenlinks[:4])}")
        for m in re.findall(r'src="(?!https?:)([^"]+)"', rd):
            if not os.path.exists(os.path.join(repo, m)):
                bad("major", "readme", f"broken image `{m}`")

    # --- card JS (cards or integrations shipping cards) ----------------------------
    js_files = [p for p in walk(os.path.join(repo, "src"), (".js",))] if os.path.isdir(os.path.join(repo, "src")) else []
    alljs = "\n".join(read(p) or "" for p in js_files)
    if js_files:
        if "customCards" in alljs:
            if "pickerDefine" not in alljs:
                bad("minor", "picker", "customCards without `pickerDefine()` light previews")
            if re.search(r"preview:\s*false", alljs):
                bad("minor", "picker", "`preview: false` still present in customCards")
        # i18n split
        i18n_dirs = {os.path.dirname(p) for p in glob.glob(os.path.join(repo, "src", "**", "i18n", "*.js"), recursive=True)}
        i18n_dirs = {d for d in i18n_dirs if len(glob.glob(os.path.join(d, "*.js"))) > 3}
        if not i18n_dirs and k != "theme":
            if re.search(r"\bfr\s*:\s*\{", alljs):
                bad("info" if len(alljs) < 120000 and not re.search(r"\bfr\s*:\s*\{[^}]{400,}", alljs) else "minor", "i18n", "translations inlined in the bundle (not split per language)")
        for d in i18n_dirs:
            have = {os.path.basename(p)[:-3] for p in glob.glob(os.path.join(d, "*.js"))}
            miss = [lg for lg in LANGS if lg not in have]
            if miss and have - {"index", "table"}:
                bad("minor", "i18n", f"{os.path.relpath(d, repo)} missing languages: {', '.join(miss)}")
        if not glob.glob(os.path.join(repo, "scripts", "bundle.mjs")) and not glob.glob(os.path.join(repo, "scripts", "build*.mjs")):
            bad("info", "build", "no scripts/bundle.mjs / build.mjs (ES-module split build)")
        bld = "\n".join(read(p) or "" for p in glob.glob(os.path.join(repo, "scripts", "*.mjs")))
        if re.search(r"minify\s*:\s*true", bld):
            bad("minor", "build", "bundle is minified (convention: no minification)")
    # theme specific
    if k == "theme":
        if not glob.glob(os.path.join(repo, "themes", "*.yaml")):
            bad("major", "theme", "no themes/*.yaml")
    # tests
    if not (glob.glob(os.path.join(repo, "test", "*.mjs")) or glob.glob(os.path.join(repo, "tests", "*.py"))):
        bad("minor", "tests", "no test suite (test/*.mjs or tests/*.py)")

    return {"repo": name, "kind": k, "versions": versions, "issues": issues}


def main():
    res = [audit(r) for r in REPOS]
    os.makedirs(os.path.join(ROOT, "results", "auto"), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, "results", "auto", "conventions.json"), "w"), indent=1)
    # summary markdown
    codes = {}
    for r in res:
        for i in r["issues"]:
            codes.setdefault((i["sev"], i["code"], re.sub(r"`[^`]*`|\d+|:.*", "…", i["msg"])), []).append(r["repo"])
    out = ["# Conventions & CI audit (automatic)", "",
           "Generated by `scripts/audit_conventions.py`. `info` items need a human look; they are not violations.", "",
           "## By rule", "", "| Sev | Rule | Repos | Which |", "|---|---|---|---|"]
    order = {"major": 0, "minor": 1, "info": 2}
    for (sev, code, msg), repos in sorted(codes.items(), key=lambda x: (order[x[0][0]], -len(x[1]))):
        which = ", ".join(r.replace("ha-", "") for r in sorted(repos)) if len(repos) <= 25 else f"{len(repos)} repos (see JSON)"
        out.append(f"| {sev} | {code}: {msg} | {len(repos)} | {which} |")
    out += ["", "## By repo", ""]
    for r in res:
        if not r["issues"]:
            out.append(f"- **{r['repo']}** ({r['kind']}) — clean")
            continue
        out.append(f"### {r['repo']} ({r['kind']})")
        for i in sorted(r["issues"], key=lambda i: order[i["sev"]]):
            out.append(f"- [{i['sev']}] {i['code']}: {i['msg']}")
        out.append("")
    open(os.path.join(ROOT, "results", "CONVENTIONS.md"), "w").write("\n".join(out) + "\n")
    tot = sum(len(r["issues"]) for r in res)
    print(f"{len(res)} repos, {tot} findings")
    for sev in order:
        print(sev, sum(1 for r in res for i in r["issues"] if i["sev"] == sev))


if __name__ == "__main__":
    main()
