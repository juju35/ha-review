#!/usr/bin/env python3
"""Phase 4c — security audit: backend (integrations), frontend (cards/panels), CI / supply chain, secrets.

Usage: python3 scripts/audit_security.py [SRC_DIR] -> results/auto/security.json, results/SECURITY.md
Each hit is a lead; the triage is in results/triage.json (section "security").
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "src")
REPOS = open(os.path.join(ROOT, "repos.txt")).read().split()
SKIP = {".git", "node_modules", "dist", "__pycache__", "screenshots", "i18n", "translations", "vendor"}


def walk(repo, exts, tests=False):
    for d, dirs, fs in os.walk(repo):
        dirs[:] = [x for x in dirs if x not in SKIP and (tests or x not in ("test", "tests"))]
        for f in fs:
            if f.endswith(exts):
                p = os.path.join(d, f)
                yield os.path.relpath(p, repo), open(p, encoding="utf-8", errors="replace").read()


def ln(t, pos):
    return t.count("\n", 0, pos) + 1


SECRET_RE = re.compile(
    r"(-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{60,}|"
    r"AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|sk-[A-Za-z0-9]{32,})")


def audit(name):
    repo = os.path.join(SRC, name)
    out = []

    def add(sev, area, code, msg):
        out.append({"sev": sev, "area": area, "code": code, "msg": msg})

    # ---------------- secrets committed (all text files, tests included) ----------------
    for p, t in walk(repo, (".py", ".js", ".mjs", ".json", ".yaml", ".yml", ".md", ".txt", ".sh", ".toml"), tests=True):
        for m in SECRET_RE.finditer(t):
            add("major", "secrets", "committed-secret", f"{p}:{ln(t, m.start())} looks like a secret (`{m.group(0)[:12]}…`)")

    # ---------------- backend ----------------
    py = {p: t for p, t in walk(repo, (".py",)) if p.startswith("custom_components")}
    allpy = "\n".join(py.values())
    for p, t in py.items():
        for m in re.finditer(r"yaml\.load\((?![^)]*SafeLoader)|pickle\.loads?\(|marshal\.loads", t):
            add("major", "backend", "unsafe-deser", f"{p}:{ln(t, m.start())} unsafe deserialisation `{m.group(0)}`")
        for m in re.finditer(r"requires_auth\s*=\s*False", t):
            add("major", "backend", "http-noauth", f"{p}:{ln(t, m.start())} HTTP view without authentication")
        for m in re.finditer(r"StaticPathConfig\(\s*([^,]+),\s*([^,)]+)", t):
            target = m.group(2)
            if re.search(r"config_dir|hass\.config\.path\(\s*\)|/config", target):
                add("major", "backend", "static-path", f"{p}:{ln(t, m.start())} static path serves `{target.strip()}`")
        for m in re.finditer(r"(?:params|url)\s*=\s*[^\n]*(?:token|api_key|apikey|password)=", t, re.I):
            add("minor", "backend", "secret-in-url", f"{p}:{ln(t, m.start())} secret passed in a URL query string (ends up in proxy/server logs)")
        for m in re.finditer(r"Template\(\s*(?:call\.data|msg\[|data\[)", t):
            add("minor", "backend", "template-injection", f"{p}:{ln(t, m.start())} template built from caller data")
        for m in re.finditer(r"(open|write_text|write_bytes|Path)\(\s*(?:call\.data|msg\[|data\[)['\"]?(path|file|filename)", t):
            if "is_allowed_path" not in t and "relative_to" not in t:
                add("major", "backend", "path-traversal", f"{p}:{ln(t, m.start())} file path from caller data without an allowed-path check")
        for m in re.finditer(r"create_subprocess_shell|os\.system\(|subprocess\.[a-z_]+\([^)]*shell\s*=\s*True", t):
            add("major", "backend", "shell", f"{p}:{ln(t, m.start())} shell command")
        for m in re.finditer(r"(verify_ssl|ssl|verify)\s*=\s*False", t):
            add("minor", "backend", "tls-off", f"{p}:{ln(t, m.start())} TLS verification disabled")
        for m in re.finditer(r"http://(?!localhost|127\.0\.0\.1|\{|homeassistant|example)[a-z0-9.-]+\.[a-z]{2,}", t):
            add("info", "backend", "cleartext", f"{p}:{ln(t, m.start())} plain-http endpoint `{m.group(0)}`")
    # diagnostics redaction when credentials exist
    cf = "\n".join(t for p, t in py.items() if p.endswith("config_flow.py"))
    if re.search(r"CONF_PASSWORD|CONF_TOKEN|CONF_API_KEY|password|token|cookie", cf):
        diag = "\n".join(t for p, t in py.items() if p.endswith("diagnostics.py"))
        if not diag:
            add("info", "backend", "diagnostics", "credentials in the config flow and no diagnostics.py (fine) — if one is added, redact")
        elif "redact" not in diag.lower() and "**REDACTED**" not in diag:
            add("major", "backend", "diagnostics", "diagnostics.py without redaction while the entry holds credentials")
    # services touching files / admin
    for m in re.finditer(r"async_register_admin_service|async_register\(", allpy):
        pass
    if py and re.search(r"hass\.services\.async_register\(", allpy) and re.search(r"(path|filename|file)['\"]?\s*\)?\s*:\s*cv\.(string|path)", allpy):
        if "async_register_admin_service" not in allpy and "require_admin" not in allpy and "is_admin" not in allpy:
            add("minor", "backend", "file-service", "a service takes a file path but no admin restriction found")

    # ---------------- frontend ----------------
    js = {p: t for p, t in walk(repo, (".js",)) if p.startswith(("src", "custom_components"))}
    for p, t in js.items():
        for m in re.finditer(r"""(href|src)=\\?["']\$\{\s*([^}]*?(attributes|url|link|href|entity_picture)[^}]*)\}""", t):
            expr = m.group(2)
            if not re.search(r"safeUrl|safeHref|isSafeUrl|https?:|encodeURI|\w*[Ss]afe\w*\(|sanitize", expr):
                back = t[max(0, m.start() - 1500):m.start()]
                if not re.search(r"javascript:|safeUrl|isSafe|/\^https\?|startsWith\(['\"]http|new URL\(", back):
                    add("minor", "frontend", "url-scheme", f"{p}:{ln(t, m.start())} `{m.group(1)}` from data `${{{expr.strip()[:50]}}}` without a scheme check (javascript: URLs)")
        for m in re.finditer(r"window\.open\(([^,)]*)", t):
            if "noopener" not in t[m.start():m.start() + 200]:
                add("minor", "frontend", "noopener", f"{p}:{ln(t, m.start())} window.open without `noopener`")
        for m in re.finditer(r"target=\\?[\"']_blank\\?[\"'](?![^>]{0,120}rel=\\?[\"'][^\"']*noopener)", t):
            add("info", "frontend", "noopener", f"{p}:{ln(t, m.start())} target=_blank without rel=noopener")
        for m in re.finditer(r"addEventListener\(\s*['\"]message['\"]", t):
            if not re.search(r"\.origin\b", t[m.start():m.start() + 600]):
                add("minor", "frontend", "postmessage", f"{p}:{ln(t, m.start())} message listener without an origin check")
        for m in re.finditer(r"localStorage\.setItem\([^)]*(token|password|secret|cookie)", t, re.I):
            add("major", "frontend", "storage-secret", f"{p}:{ln(t, m.start())} secret written to localStorage")
        for m in re.finditer(r"\beval\(|new Function\(", t):
            add("minor", "frontend", "eval", f"{p}:{ln(t, m.start())} eval / new Function")
        for m in re.finditer(r"fetch\(\s*[`'\"]https?://(?!raw\.githubusercontent|api\.github)([^/`'\"$]+)", t):
            add("info", "frontend", "third-party", f"{p}:{ln(t, m.start())} browser calls a third-party host `{m.group(1)}` (privacy: the user's IP leaves the LAN)")
        for m in re.finditer(r"<script[^>]+src=\\?[\"']https?://|import\(\s*[`'\"]https?://", t):
            add("minor", "frontend", "remote-code", f"{p}:{ln(t, m.start())} code loaded from a remote host")

    # ---------------- CI / supply chain ----------------
    for f in glob.glob(os.path.join(repo, ".github", "workflows", "*.y*ml")):
        t = open(f, encoding="utf-8").read()
        b = os.path.basename(f)
        if "pull_request_target" in t:
            add("major", "ci", "prt", f"{b}: pull_request_target")
        if not re.search(r"^permissions:", t, re.M):
            add("minor", "ci", "permissions", f"{b}: no top-level `permissions:` (token defaults may be write)")
        for m in re.finditer(r"\$\{\{\s*github\.event\.(pull_request\.(title|body|head\.ref)|issue\.(title|body)|comment\.body|head_commit\.message)[^}]*\}\}", t):
            line = t[t.rfind("\n", 0, m.start()) + 1:t.find("\n", m.start())]
            if re.search(r"^\s*(run:|-?\s*run:)|^\s{6,}\S", line) and "if:" not in line and "startsWith" not in line:
                add("major", "ci", "script-injection", f"{b}:{ln(t, m.start())} untrusted `{m.group(0)}` interpolated in a run script")
        for m in re.finditer(r"uses:\s*([\w.-]+/[\w./-]+)@([\w.-]+)", t):
            if not re.fullmatch(r"[0-9a-f]{40}", m.group(2)) and not m.group(1).startswith("./"):
                add("minor", "ci", "unpinned", f"{b}: `{m.group(1)}@{m.group(2)}` not pinned to a SHA")
        if "persist-credentials: false" not in t and "actions/checkout" in t and re.search(r"permissions:[\s\S]{0,80}contents:\s*write", t) is None:
            pass
    if not os.path.exists(os.path.join(repo, ".github", "dependabot.yml")):
        add("minor", "ci", "dependabot", "no dependabot.yml")
    if not os.path.exists(os.path.join(repo, "SECURITY.md")):
        add("info", "policy", "security-md", "no SECURITY.md (how to report a vulnerability)")
    return out


def main():
    res = [{"repo": r, "issues": audit(r)} for r in REPOS]
    json.dump(res, open(os.path.join(ROOT, "results", "auto", "security.json"), "w"), indent=1)
    order = {"major": 0, "minor": 1, "info": 2}
    agg = {}
    for r in res:
        for i in r["issues"]:
            agg.setdefault((i["sev"], i["area"], i["code"]), set()).add(r["repo"])
    lines = ["# Security audit — automatic leads", "",
             "Generated by `scripts/audit_security.py`. Triage and conclusions: [SECURITY-REVIEW.md](SECURITY-REVIEW.md).", "",
             "| Sev | Area | Rule | Repos | Which |", "|---|---|---|---|---|"]
    for (sev, area, code), repos in sorted(agg.items(), key=lambda x: (order[x[0][0]], -len(x[1]))):
        which = ", ".join(x.replace("ha-", "") for x in sorted(repos)) if len(repos) < 40 else f"{len(repos)} repos"
        lines.append(f"| {sev} | {area} | {code} | {len(repos)} | {which} |")
    lines += ["", "## By repo", ""]
    for r in res:
        iss = [i for i in r["issues"] if i["code"] != "security-md"]
        if not iss:
            continue
        lines.append(f"### {r['repo']}")
        for i in sorted(iss, key=lambda i: order[i["sev"]]):
            lines.append(f"- [{i['sev']}] {i['area']}/{i['code']}: {i['msg']}")
        lines.append("")
    open(os.path.join(ROOT, "results", "SECURITY.md"), "w").write("\n".join(lines) + "\n")
    for s in order:
        print(s, sum(1 for r in res for i in r["issues"] if i["sev"] == s))


if __name__ == "__main__":
    main()
