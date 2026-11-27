#!/usr/bin/env python3
"""Phase 3 — visual-consistency audit (static analysis of the card JS/CSS).

Usage: python3 scripts/audit_visual.py [SRC_DIR]
Writes results/auto/visual.json and results/VISUAL.md.
Heuristic: every hit is a lead to check by eye, not a proven defect.
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "src")
REPOS = open(os.path.join(ROOT, "repos.txt")).read().split()
SKIP = {".git", "node_modules", "screenshots", "dist", "__pycache__", "test", "tests", "scripts", "i18n", "translations"}
QR_OK = {"ha-wero-card", "ha-wifi-card"}

CANON = {  # status palette agreed in the tile charter (room-overview "B")
    "ok": "var(--success-color, #43a047)",
    "warn": "var(--warning-color, #ffa600)",
    "alert": "var(--error-color, #db4437)",
    "active": "var(--info-color, #039be5)",
}


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$|(?<=[;{}\s])//[^\n'\"`]*$", "", t)


def card_js(repo):
    out = {}
    for base in ("src", "custom_components"):
        for d, dirs, files in os.walk(os.path.join(repo, base)):
            dirs[:] = [x for x in dirs if x not in SKIP]
            for f in files:
                if f.endswith(".js") and not f.endswith(".min.js"):
                    p = os.path.join(d, f)
                    try:
                        out[os.path.relpath(p, repo)] = open(p, encoding="utf-8", errors="replace").read()
                    except OSError:
                        pass
    return out


def in_at_rule(css, pos):
    """True when the rule at pos sits inside an @container / @media block."""
    depth = 0
    i = pos - 1
    hops = 0
    while i >= 0 and hops < 4:
        c = css[i]
        if c == "}":
            depth += 1
        elif c == "{":
            if depth == 0:
                head = css[max(0, i - 160):i]
                head = re.split(r"[;}]", head)[-1]
                if "@container" in head or "@media" in head:
                    return True
                hops += 1
            else:
                depth -= 1
        i -= 1
    return False


def blocks(css, selector_re, responsive=False):
    """Yield (selector, body) of CSS rules whose selector list matches selector_re.
    Rules inside @container/@media are skipped unless responsive=True."""
    for m in re.finditer(r"([^{}]{1,200})\{([^{}]*)\}", css):
        sel = m.group(1).strip()
        if re.search(selector_re, sel):
            if not responsive and in_at_rule(css, m.start(1)):
                continue
            yield sel, m.group(2)


def px(body, prop):
    m = re.search(r"(?<![\w-])" + prop + r"\s*:\s*(\d+(?:\.\d+)?)px", body)
    return float(m.group(1)) if m else None


def audit(name):
    repo = os.path.join(SRC, name)
    files = card_js(repo)
    res = {"repo": name, "files": len(files), "metrics": {}, "issues": []}
    if not files:
        res["skipped"] = "no card/panel JS"
        return res
    code = {p: strip_comments(t) for p, t in files.items()}
    allc = "\n".join(code.values())
    allraw = "\n".join(files.values())
    M = res["metrics"]

    def bad(sev, codev, msg):
        res["issues"].append({"sev": sev, "code": codev, "msg": msg})

    # ---- illustrated header ------------------------------------------------
    has_banner = bool(re.search(r"class=\\?[\"'`]banner|classList\.add\(['\"]banner|\bbanner\$\{|banner\s*:\s*\{", allc)) \
        or bool(re.search(r"(?<![\w-])\.banner\s*[{,]", allc))
    M["banner"] = has_banner
    if has_banner:
        hs, mhs = set(), set()
        for sel, body in blocks(allc, r"(?:^|,|\s)\.banner(?:\s*$|\s*,|\.mini\b|\.compact\b)"):
            if re.search(r"\.banner\s+\S", sel):
                continue
            for prop, s in (("height", hs), ("min-height", mhs)):
                v = px(body, prop)
                if v is not None:
                    s.add(v)
        for m in re.finditer(r"--(?:banner|ih|illus|header)-h(?:eight)?\s*:\s*(\d+)px", allc):
            hs.add(float(m.group(1)))
        M["banner_heights"] = sorted(hs | mhs)
        classic = re.search(r"\.banner\.(classic|plain)\s*\{[^}]*--banner-h\s*:\s*(\d+)px", allc)
        if classic:
            hs.discard(float(classic.group(2)))
            M["classic_header_h"] = float(classic.group(2))
            bad("info", "banner-height", f"`illustration: false` header is {classic.group(2)} px (other cards: no banner at all) — harmonise the non-illustrated header")
        off = sorted(v for v in hs | mhs if v != 90)
        if off and 90 not in hs | mhs:
            bad("major", "banner-height", f"illustrated header is not 90 px (found {', '.join(f'{v:g}px' for v in off)})")
        elif off:
            bad("info", "banner-height", f"header heights besides 90 px: {', '.join(f'{v:g}px' for v in off)} (check mini/compact variants)")
        # ground bar
        gh = set()
        for sel, body in blocks(allc, r"\.(ground|floor|runway|track|road|soil|grass|deck|base-bar|groundbar)\b"):
            if ".banner" in sel or sel.startswith(".ground") or sel.startswith(".runway") or "ground" in sel:
                v = px(body, "height")
                if v is not None and v <= 20:
                    gh.add(v)
        for m in re.finditer(r"--(?:runway|ground|floor|track|soil)-h\s*:\s*(\d+)px", allc):
            gh.add(float(m.group(1)))
        M["ground_heights"] = sorted(gh)
        if gh and 10 not in gh:
            bad("minor", "ground-bar", f"ground bar {', '.join(f'{v:g}px' for v in sorted(gh))} (charter: same thickness as flight/train, 10 px)")
        if not gh and not re.search(r"ground|runway|floor|soil|track", allc):
            bad("minor", "ground-bar", "no ground bar found at the bottom of the illustrated header")
        # night mode
        night_fns = re.findall(r"_night\s*\([^)]*\)\s*\{(.{0,600}?)\n\s{2}\}", allc, re.S)
        if any("sun.sun" in f or "below_horizon" in f for f in night_fns):
            bad("major", "night-mode", "`_night()` still reads `sun.sun` (charter: HA theme only, `illustration_theme` forces)")
        elif re.search(r"below_horizon", allc):
            bad("info", "night-mode", "`sun.sun` read (verified use: content such as solar production or sun times, not the banner look — recheck if it changes)")
        if not re.search(r"themes\??\.darkMode|darkMode", allc):
            bad("minor", "night-mode", "header never reads `hass.themes.darkMode`")
        if re.search(r"sun\.sun|below the horizon", allraw) and not re.search(r"sun\.sun", allc):
            bad("info", "stale-comment", "comments still describe the old `sun.sun` night rule")
        if "illustration_theme" not in allc:
            bad("info" if not re.search(r"-card['\"]", allc) else "minor", "night-mode", "no `illustration_theme: day|night` override")
    else:
        if re.search(r"scene|hero|illustration", allc) and "90px" in allc:
            bad("info", "banner", "illustrated header built with its own class names (scene/hero/header), not the shared `.banner` structure — height and ground bar not checked automatically")
        else:
            bad("minor", "banner", "no illustrated header found (plain header)")

    # ---- status pill ---------------------------------------------------------
    pill = bool(re.search(r"class=\\?[\"'`](?:st|pill|status-pill|status|dot|state-dot)\b", allc)) or "::before" in allc and "border-radius: 50%" in allc
    M["status_pill"] = pill
    if not pill:
        bad("minor", "status-pill", "no status pill found in the header")

    # ---- mini cards / zoom button -------------------------------------------
    mini = bool(re.search(r"-mini-card['\"]", allc))
    M["mini"] = mini
    if mini:
        zoom = [b for s, b in blocks(allc, r"\.(zoom|expand|detail|detail-btn|toggle-detail)\b(?![-\w])")]
        if not zoom:
            bad("minor", "mini-zoom", "mini card without a `.zoom` detail button")
        else:
            pos = " ".join(zoom)
            if "top" not in pos and "inset" not in pos and "margin-left: auto" not in pos and "margin-inline-start: auto" not in pos:
                bad("info", "mini-zoom", "detail button position not obviously top-right")
        # icon shrink in mini
        for sel, body in blocks(allc, r"mini[^,]*(head|banner|header)[^,]*\.(icon|badge|hicon|logo)\b|\.mini\s+\.(logo|hicon)\b"):
            w = px(body, "width")
            if w is not None and w < 40 and w >= 24:
                bad("minor", "mini-icon", f"mini card shrinks the header icon to {w:g}px (`{sel[:50]}`)")
                break

    # ---- header icon 40px --------------------------------------------------------
    sizes = collections.Counter()
    for sel, body in blocks(allc, r"(head|banner|header|top)[^,]*\.(hicon|logo|badge|icon|ico|pill-icon)\b|\.(hicon|head-icon|header-icon|icon-pill)\b"):
        w = px(body, "width")
        if w and 30 <= w <= 56 and "border-radius: 50%" in body:
            sizes[w] += 1
    M["round_icon_sizes"] = dict(sizes)
    if sizes and 40 not in sizes:
        bad("info" if all(k > 40 for k in sizes) else "minor", "header-icon", f"round header icon not 40 px ({', '.join(f'{k:g}' for k in sizes)})")

    # ---- buttons: no filled buttons --------------------------------------------------
    filled = []
    for sel, body in blocks(allc, r"button|\.btn\b|\.primary\b|\.action\b|\.cta\b"):
        if re.search(r"(?<![\w-])background(?:-color)?\s*:\s*var\(--(?:primary|accent)-color[^)]*\)\s*(?:;|$|!)", body) \
                and "color-mix" not in body:
            filled.append(sel[:60])
    if filled:
        bad("major", "filled-button", f"filled button(s): {', '.join(sorted(set(filled))[:4])}")

    # ---- popups at the top of the card -------------------------------------------------
    centered = []
    for sel, body in blocks(allc, r"\.(popup|dialog|modal|overlay|sheet|confirm|backdrop|pop)\b"):
        if re.search(r"align-items\s*:\s*center", body) and re.search(r"position\s*:\s*(fixed|absolute)", body) \
                and not re.search(r"align-items\s*:\s*(flex-)?start", body):
            centered.append(sel[:50])
        if re.search(r"top\s*:\s*50%", body) and "translate" in body:
            centered.append(sel[:50])
    if centered and name not in QR_OK:
        bad("major", "popup-position", f"popup centred instead of top of the card: {', '.join(sorted(set(centered))[:3])}")

    # ---- leaving the page closes popups ---------------------------------------------------
    has_popup = bool(re.search(r"_popup|_dialog|_confirm|_modal|_sheet", allc))
    if has_popup and "disconnectedCallback" not in allc:
        bad("major", "popup-disconnect", "popups but no `disconnectedCallback` (popup must close when the card leaves the page)")
    M["disconnected"] = "disconnectedCallback" in allc

    # ---- status palette --------------------------------------------------------------
    pal = collections.defaultdict(set)
    for m in re.finditer(r"--[a-z0-9]{1,6}-(ok|warn|alert|danger|error|active|idle|na|off)\s*:\s*([^;\n]+)", allc):
        pal[m.group(1)].add(m.group(2).strip().rstrip(",").strip())
    M["palette"] = {k: sorted(v) for k, v in pal.items()}
    for k, canon in CANON.items():
        for v in pal.get(k, ()):
            if v.replace(" ", "") != canon.replace(" ", "") and "${" not in v:
                bad("minor", "palette", f"`--*-{k}` = `{v}` (charter: `{canon}`)")
    idle = pal.get("idle", set())
    M["idle_token"] = sorted(idle)
    # hard-coded status hex outside the palette
    hexes = collections.Counter(h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", allc))
    M["distinct_hex"] = len(hexes)

    # ---- radii / font sizes ---------------------------------------------------------------
    radii = collections.Counter()
    for sel, body in blocks(allc, r"\.tile\b"):
        v = px(body, "border-radius")
        if v is not None:
            radii[v] += 1
    M["tile_radius"] = dict(radii)
    if radii and not ({10, 12} & set(radii)):
        bad("info" if name == "ha-wall-panel" else "minor", "tile-radius", f"tile radius {', '.join(f'{k:g}px' for k in radii)} (most cards: 10 or 12 px)")
    title_fs = collections.Counter()
    for sel, body in blocks(allc, r"\.(title|name|head-title|t1)\b"):
        v = px(body, "font-size")
        if v is not None and ".tile" not in sel:
            title_fs[v] += 1
    M["title_font"] = dict(title_fs)
    hover_subgrid = bool(re.search(r":hover[^{]*\{[^}]*subgrid|subgrid", allc))
    if hover_subgrid:
        bad("info", "webkit", "uses `subgrid` — check the :hover rendering under Safari/WebKit")
    # card radius uses HA var
    if re.search(r"ha-card\s*\{[^}]*border-radius\s*:\s*\d+px", allc):
        bad("minor", "card-radius", "`ha-card` border-radius hard-coded instead of `var(--ha-card-border-radius)`")
    # important
    imp = allc.count("!important")
    M["important"] = imp
    if imp > 15:
        bad("info", "css", f"{imp} `!important` in card CSS")
    return res


def main():
    res = [audit(r) for r in REPOS]
    json.dump(res, open(os.path.join(ROOT, "results", "auto", "visual.json"), "w"), indent=1)
    order = {"major": 0, "minor": 1, "info": 2}
    agg = collections.defaultdict(list)
    for r in res:
        for i in r["issues"]:
            agg[(i["sev"], i["code"])].append(r["repo"])
    # cross-repo distributions
    def dist(key):
        c = collections.Counter()
        for r in res:
            for k, v in (r["metrics"].get(key) or {}).items():
                c[k] += 1
        return c
    idle = collections.Counter(v for r in res for v in r["metrics"].get("idle_token", []))
    gh = collections.Counter(v for r in res for v in r["metrics"].get("ground_heights", []))
    bh = collections.Counter(v for r in res for v in r["metrics"].get("banner_heights", []))
    out = ["# Visual-consistency audit (automatic)", "",
           "Generated by `scripts/audit_visual.py` (static analysis of card/panel JS and CSS). Leads to check by eye.", "",
           "## Cross-repo distributions", "",
           f"- Illustrated header present: {sum(1 for r in res if r['metrics'].get('banner'))} / {sum(1 for r in res if r['metrics'])} repos with card JS",
           "- Header heights found (px → repos): " + ", ".join(f"{k:g}→{v}" for k, v in sorted(bh.items())),
           "- Ground-bar heights (px → repos): " + ", ".join(f"{k:g}→{v}" for k, v in sorted(gh.items())),
           "- Tile radius (px → repos): " + ", ".join(f"{k}→{v}" for k, v in sorted(dist('tile_radius').items())),
           "- Title font size (px → repos): " + ", ".join(f"{k}→{v}" for k, v in sorted(dist('title_font').items())),
           "- Idle token: " + "; ".join(f"`{k}`→{v}" for k, v in idle.most_common()),
           "", "## By rule", "", "| Sev | Rule | Repos | Which |", "|---|---|---|---|"]
    for (sev, codev), repos in sorted(agg.items(), key=lambda x: (order[x[0][0]], -len(x[1]))):
        which = ", ".join(r.replace("ha-", "") for r in sorted(set(repos)))
        out.append(f"| {sev} | {codev} | {len(set(repos))} | {which} |")
    out += ["", "## By repo", ""]
    for r in res:
        if r.get("skipped"):
            out.append(f"- **{r['repo']}** — skipped ({r['skipped']})")
            continue
        if not r["issues"]:
            out.append(f"- **{r['repo']}** — nothing flagged")
            continue
        out.append(f"### {r['repo']}")
        for i in sorted(r["issues"], key=lambda i: order[i["sev"]]):
            out.append(f"- [{i['sev']}] {i['code']}: {i['msg']}")
        out.append("")
    open(os.path.join(ROOT, "results", "VISUAL.md"), "w").write("\n".join(out) + "\n")
    for sev in order:
        print(sev, sum(1 for r in res for i in r["issues"] if i["sev"] == sev))


if __name__ == "__main__":
    main()
