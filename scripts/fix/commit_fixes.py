#!/usr/bin/env python3
"""Bump (when shipped code changed), write the CHANGELOG entry and commit the review fixes in each clone.

Usage: python3 scripts/fix/commit_fixes.py SRC_DIR [repo ...]
Reads results/auto/fix_mechanical.json and the per-repo notes below; writes results/auto/fix_commits.json
({repo: {"bump": "X.Y.Z" | null, "title": ..., "body": ...}}) for open_prs.py.
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = sys.argv[1]
REPOS = sys.argv[2:] or open(os.path.join(ROOT, "repos.txt")).read().split()
TODAY = datetime.date(2026, 11, 27).isoformat()
MECH = json.load(open(os.path.join(ROOT, "results", "auto", "fix_mechanical.json")))
TRAILER = ("Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
           "Claude-Session: https://claude.ai/code/session_01F4sAn1x21MmgHHeW1MLKJ5")

# (section, text) per fix — section is a CHANGELOG heading; None = not in the CHANGELOG (repo-only change)
TEXT = {
    "idle": ("Fixes", "Idle states use the theme's secondary text colour (`--secondary-text-color`), like every ha-* card."),
    "radius": ("Fixes", "Tiles have the 10 px corner radius shared by the ha-* cards."),
    "security": (None, "`SECURITY.md`: how to report a vulnerability privately."),
    "resource": (None, "README: the Marketplace section names the dashboard resource (`/local/community/…`)."),
    "biome": (None, "Biome 2.6.8, like the other ha-* repos (schema and pre-commit)."),
}
NOTES = {
    "ha-wero-card": [("Fixes", "Mini card: back to the compact view when it leaves the page (another view, a conditional card hidden), like the other mini cards.")],
    "ha-camera": [("Fixes", "Mini card: back to the compact view when it leaves the page (another view, a conditional card hidden), like the other mini cards.")],
    "ha-safety-card": [("Maintenance", "Dead code inherited from the light cards removed (`hide_when_off`, `only_on`, the toggle base card): nothing changes for users.")],
    "ha-ent-one": [("Fixes", "Opening a document: the new tab no longer keeps a link back to the Home Assistant page (`opener` cut).")],
    "ha-ent-educartable": [("Fixes", "Opening a document: the new tab no longer keeps a link back to the Home Assistant page (`opener` cut).")],
    "ha-ent-skolengo": [("Fixes", "Opening a document: the new tab no longer keeps a link back to the Home Assistant page (`opener` cut).")],
    "ha-github": [("Fixes", "Panel, Branches tab: the pull-request link only opens a github.com address."),
                  ("Fixes", "The `create_repository` action has its icon (`icons.json`).")],
    "ha-proxmox": [("Fixes", "Panel: the links to the Proxmox web interface only open http(s) addresses.")],
    "ha-house-rules": [("Fixes", "Illustrated header (cards and panel): the ground bar is 10 px thick, like on the other ha-* cards."),
                       (None, "README: which panel actions are for administrators, which for every user.")],
    "ha-maintenance": [("Fixes", "Illustrated header (card and panel): the ground bar is 10 px thick and the warning colour is the theme's `--warning-color` (fallback `#ffa600`), like on the other ha-* cards.")],
    "ha-notify-hub": [("Fixes", "Illustrated header (card and panel): the ground bar is 10 px thick and the warning colour is the theme's `--warning-color` (fallback `#ffa600`), like on the other ha-* cards.")],
    "ha-vehicle-consumption": [("Fixes", "The OK level uses the theme's success colour (green) instead of the primary colour, like on the other ha-* cards.")],
    "ha-alarm-card": [("Fixes", "Open sensors: the tile background stays neutral, the tinted icon and the state line show the state (card charter).")],
    "ha-tracker-card": [("Fixes", "Items away, with a low battery or not seen: the tile background stays neutral, the tinted icon, border and state show it (card charter).")],
    "ha-media-server-card": [("Fixes", "Counters: neutral tile background, the colour stays on the icon and the figures (card charter).")],
    "ha-wall-panel": [("Fixes", "Loading the card twice (two resources) no longer throws: its elements and picker entry are registered once.")],
    "ha-power-device-card": [(None, "Tests: the full-card test pins the clock in the afternoon (it failed between midnight and 05:30).")],
    "ha-family-link": [(None, "Screenshots named like every ha-* repo (light unsuffixed, `-dark` twins), light first in the README.")],
    "ha-hp": [(None, "README shows the Printer card captures from ha-printer-scanner-card instead of copies that could drift.")],
    "ha-tapo": [(None, "README shows the Camera card captures from ha-camera instead of copies that could drift.")],
    "ha-renault-picture": [(None, "README shows the Vehicle card captures from ha-vehicle-card instead of copies that could drift.")],
    "ha-orange-internet-on-the-move": [(None, "README shows the Vehicle card captures from ha-vehicle-card instead of copies that could drift.")],
    "ha-iptv": [(None, "README: security note on Xtream credentials over `http://`.")],
    "ha-weather-card": [(None, "README: the animation GIFs have a bounded width.")],
}
COMMENT_ONLY = {"ha-cover-card", "ha-dns-filter-card", "ha-doorbell-card", "ha-ecowatt-card", "ha-room-card", "ha-wall-panel"}


def git(repo, *a, check=True):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=check).stdout


def shipped_changed(repo):
    files = git(repo, "status", "--porcelain").splitlines()
    paths = [f[3:].split(" -> ")[-1] for f in files]
    return [p for p in paths if (p.startswith("src/") or p.startswith("custom_components/")) and "/test" not in p]


def bump_version(v):
    a, b, c = (int(x) for x in v.split("."))
    return f"{a}.{b}.{c + 1}"


def set_versions(repo, old, new):
    pj = os.path.join(repo, "package.json")
    mf = glob.glob(os.path.join(repo, "custom_components", "*", "manifest.json"))
    if mf:
        for m in mf:
            t = open(m).read()
            open(m, "w").write(re.sub(r'("version"\s*:\s*")[^"]+(")', rf"\g<1>{new}\2", t, count=1))
        for c in glob.glob(os.path.join(repo, "custom_components", "*", "const.py")):
            t = open(c).read()
            open(c, "w").write(re.sub(r"(?m)^(VERSION(?::\s*Final)?\s*=\s*['\"])\d+\.\d+\.\d+(['\"])", rf"\g<1>{new}\2", t))
    if os.path.exists(pj) and not mf:
        for f in ("package.json", "package-lock.json"):
            p = os.path.join(repo, f)
            if not os.path.exists(p):
                continue
            j = json.load(open(p))
            j["version"] = new
            if "packages" in j and "" in j["packages"]:
                j["packages"][""]["version"] = new
            raw = open(p).read()
            indent = 2 if raw.startswith("{\n  ") else 4
            open(p, "w").write(json.dumps(j, indent=indent, ensure_ascii=False) + "\n")
    elif os.path.exists(pj) and mf:
        # an integration with a frontend package: keep package.json in step when it carries the version
        for f in ("package.json", "package-lock.json"):
            p = os.path.join(repo, f)
            if os.path.exists(p):
                j = json.load(open(p))
                if j.get("version") == old:
                    j["version"] = new
                    if "packages" in j and "" in j["packages"]:
                        j["packages"][""]["version"] = new
                    open(p, "w").write(json.dumps(j, indent=2, ensure_ascii=False) + "\n")
    # every JS version constant (cards, panels, sub-cards) follows the release
    for p in glob.glob(os.path.join(repo, "src", "**", "*.js"), recursive=True) + \
            glob.glob(os.path.join(repo, "custom_components", "*", "**", "*.js"), recursive=True):
        if "/i18n/" in p or "/vendor/" in p:
            continue
        t = open(p, encoding="utf-8").read()
        n = re.sub(r"(\b([A-Z][A-Z0-9_]*VERSION)\s*=\s*['\"])(\d+\.\d+\.\d+)(['\"])",
                   lambda m: f"{m.group(1)}{new}{m.group(4)}" if m.group(3) == old or re.search(r"_(CARD|CARDS|PANEL)_VERSION$|^[A-Z]{2}_VERSION$", m.group(2)) else m.group(0), t)
        if n != t:
            open(p, "w", encoding="utf-8").write(n)


def current_version(repo):
    mf = glob.glob(os.path.join(repo, "custom_components", "*", "manifest.json"))
    if mf:
        return json.load(open(mf[0]))["version"]
    pj = os.path.join(repo, "package.json")
    if os.path.exists(pj):
        return json.load(open(pj))["version"]
    m = re.search(r"^##\s*(\d+\.\d+\.\d+)", open(os.path.join(repo, "CHANGELOG.md")).read(), re.M)
    return m.group(1)


def main():
    out = {}
    for name in REPOS:
        repo = os.path.join(SRC, name)
        items = [TEXT[f] for f in MECH.get(name, {}).get("fixes", [])] + NOTES.get(name, [])
        if name in COMMENT_ONLY:
            items.append((None, "Comments describe the current night rule (the HA theme alone, no `sun.sun`)."))
        git(repo, "add", "-A")
        if not git(repo, "diff", "--cached", "--name-only").strip():
            continue
        shipped = [p for p in git(repo, "diff", "--cached", "--name-only").splitlines()
                   if (p.startswith("src/") or p.startswith("custom_components/")) and "/test" not in p]
        user_visible = [i for i in items if i[0] in ("Fixes", "Maintenance")]
        bump = None
        if shipped and user_visible:
            old = current_version(repo)
            bump = bump_version(old)
            set_versions(repo, old, bump)
            cl = os.path.join(repo, "CHANGELOG.md")
            t = open(cl).read()
            secs = {}
            for s, txt in user_visible:
                secs.setdefault(s, []).append(txt)
            entry = f"## {bump} - {TODAY}\n\n" + "\n".join(
                f"### {s}\n" + "\n".join(f"- {x}" for x in secs[s]) + "\n" for s in ("Fixes", "Maintenance") if s in secs)
            m = re.search(r"^## ", t, re.M)
            t = t[:m.start()] + entry + "\n" + t[m.start():] if m else t + "\n" + entry
            open(cl, "w").write(t)
            if os.path.exists(os.path.join(repo, "package-lock.json")) is False and os.path.exists(os.path.join(repo, "package.json")):
                pass
            git(repo, "add", "-A")
        title = f"fix: apply the november review fixes ({bump})" if bump else "chore: apply the november review fixes"
        body = "Fixes from the review of the ha-* repositories (juju35/ha-review).\n\n" + \
               "\n".join(f"- {t}" for _, t in items) + \
               ("\n\nNo version bump: nothing users install changes." if not bump else "")
        subprocess.run(["git", "-C", repo, "commit", "-q", "-m", f"{title}\n\n{body}\n\n{TRAILER}"], check=True)
        out[name] = {"bump": bump, "title": title, "body": body}
        print(name, bump or "-")
    path = os.path.join(ROOT, "results", "auto", "fix_commits.json")
    prev = json.load(open(path)) if os.path.exists(path) else {}
    prev.update(out)
    json.dump(prev, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
