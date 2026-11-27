#!/usr/bin/env python3
"""Phase 4 — automatic code review: risky patterns in the card JS and the integration Python.

Usage: python3 scripts/audit_code.py [SRC_DIR]
Writes results/auto/code.json and results/CODE.md. Every hit is a lead for the manual phase 5.
"""
import ast
import collections
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "src")
REPOS = open(os.path.join(ROOT, "repos.txt")).read().split()
BIOME = os.environ.get("BIOME", os.path.join(ROOT, "..", "tools", "node_modules", ".bin", "biome"))
SKIP = {".git", "node_modules", "dist", "__pycache__", "screenshots", "i18n", "translations"}


def files(repo, ext, include_tests=False):
    for d, dirs, fs in os.walk(repo):
        dirs[:] = [x for x in dirs if x not in SKIP and (include_tests or x not in ("test", "tests", "scripts"))]
        for f in fs:
            if f.endswith(ext):
                p = os.path.join(d, f)
                yield os.path.relpath(p, repo), open(p, encoding="utf-8", errors="replace").read()


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def js_checks(repo, add):
    src = dict(files(repo, ".js"))
    if not src:
        return
    allc = "\n".join(src.values())
    # escaping helper
    has_esc = bool(re.search(r"\b\w*[eE]sc(ape)?\w*\s*=\s*(\(|function)|function\s+\w*[eE]sc\w*\s*\(", allc))
    for p, t in src.items():
        # raw user-controlled strings into HTML templates
        for m in re.finditer(r"\$\{\s*([^}]*?(friendly_name|\.attributes\.(?!unit)[a-z_]+|\.state\b|\bname\b)[^}]*)\}", t):
            expr = m.group(1).strip()
            if not re.fullmatch(r"[\w.?$\[\]'\"]+", expr):
                continue  # a call / ternary: the callee decides (escaping helpers, formatters)
            if not re.search(r"friendly_name|attributes", expr):
                continue  # `.state` / `.name` hits were sampled: internal values (CSS classes, schema keys)
            if re.search(r"^[A-Z_]+\[", expr):
                continue  # constant lookup (icon tables)
            last = re.split(r"[.?]+", expr)[-1]
            first = re.split(r"[.?\[]+", expr)[0]
            back = t[max(0, m.start() - 2500):m.start()]
            if re.search(r"\b(" + re.escape(first) + r"|" + re.escape(last) + r")\s*[:=]\s*[^;\n]{0,80}?\w*[eE]sc\w*\(", back):
                continue  # value escaped where it was built
            if re.search(r"(\w*[eE]sc\w*\(|encodeURIComponent|Number|Math\.|fmt|format|toFixed|_t\(|t\(|svgIcon|cls|class)", expr):
                continue
            ctx = t[max(0, m.start() - 300):m.start()]
            if "innerHTML" in ctx or "`<" in ctx or re.search(r"<[a-z][^>]*>[^`]*$", ctx):
                add("minor", "xss", f"{p}:{lineno(t, m.start())} unescaped `${{{expr.strip()[:60]}}}` in an HTML template")
        for m in re.finditer(r"\beval\(|new Function\(", t):
            add("major", "eval", f"{p}:{lineno(t, m.start())} eval/new Function")
        for m in re.finditer(r"console\.log\(", t):
            add("info", "console", f"{p}:{lineno(t, m.start())} console.log left in shipped code")
    if not has_esc and re.search(r"innerHTML", allc):
        add("minor", "xss", "innerHTML templates but no HTML-escape helper found")
    # timers / listeners lifecycle
    si, ci = len(re.findall(r"\bsetInterval\(", allc)), len(re.findall(r"\bclearInterval\(", allc))
    if si > ci:
        add("info", "lifecycle", f"setInterval ×{si} but clearInterval ×{ci}")
    ga = len(re.findall(r"(window|document)\.addEventListener\(", allc))
    gr = len(re.findall(r"(window|document)\.removeEventListener\(", allc))
    if ga > gr:
        add("info", "lifecycle", f"window/document addEventListener ×{ga} but removeEventListener ×{gr}")
    ro = len(re.findall(r"new (ResizeObserver|IntersectionObserver|MutationObserver)\(", allc))
    rd = len(re.findall(r"\.disconnect\(\)", allc))
    if ro > rd:
        add("info", "lifecycle", f"{ro} observers created, {rd} `.disconnect()` calls")
    sub = len(re.findall(r"subscribeEvents|subscribeMessage", allc))
    unsub = len(re.findall(r"unsub|Unsub|_unsubscribe", allc))
    if sub and not unsub:
        add("major", "lifecycle", "websocket subscriptions without any unsubscribe")
    if re.search(r"customElements\.define\(", allc) and not re.search(r"customElements\.get\(", allc):
        add("minor", "define", "customElements.define without a customElements.get guard (double load throws)")
    # service calls without error handling
    calls = len(re.findall(r"callService\(", allc))
    caught = len(re.findall(r"callService\([^;]*?\)\s*\.catch|try\s*\{[^}]{0,300}callService", allc, re.S))
    if calls >= 3 and caught == 0:
        add("info", "errors", f"{calls} hass.callService calls, none with .catch/try (a failure is silent)")
    big = [(p, t.count("\n")) for p, t in src.items() if t.count("\n") > 1500]
    for p, n in big:
        add("info", "size", f"{p} is {n} lines")


def py_checks(repo, add):
    src = dict(files(repo, ".py"))
    src = {p: t for p, t in src.items() if p.startswith("custom_components")}
    if not src:
        return
    allc = "\n".join(src.values())
    for p, t in src.items():
        try:
            tree = ast.parse(t)
        except SyntaxError as e:
            add("major", "syntax", f"{p}: {e}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                def direct(n):
                    for ch in ast.iter_child_nodes(n):
                        if isinstance(ch, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef)):
                            continue  # executor jobs / nested helpers
                        yield ch
                        yield from direct(ch)
                for sub in direct(node):
                    if isinstance(sub, ast.Call):
                        f = ast.unparse(sub.func)
                        if f in ("time.sleep", "open", "requests.get", "requests.post", "urllib.request.urlopen",
                                 "subprocess.run", "subprocess.check_output", "os.listdir", "os.walk", "shutil.copy",
                                 "shutil.rmtree", "json.load", "Path.read_text") or f.endswith((".read_text", ".write_text", ".read_bytes")):
                            # awaited executor wrappers are fine: skip calls inside lambda/def nested
                            add("major" if f in ("time.sleep", "requests.get", "requests.post") else "minor", "blocking",
                                f"{p}:{sub.lineno} `{f}()` inside async `{node.name}` (blocks the event loop)")
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    add("minor", "except", f"{p}:{node.lineno} bare `except:`")
            if isinstance(node, ast.Call):
                f = ast.unparse(node.func)
                for kw in node.keywords:
                    if kw.arg in ("verify_ssl", "ssl", "verify") and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        add("minor", "tls", f"{p}:{node.lineno} TLS verification disabled (`{kw.arg}=False`)")
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        add("major", "shell", f"{p}:{node.lineno} subprocess with shell=True")
                if f in ("aiohttp.ClientSession", "ClientSession"):
                    add("minor", "session", f"{p}:{node.lineno} own aiohttp ClientSession (prefer async_get_clientsession)")
                if re.match(r"_LOGGER\.(debug|info|warning|error|exception)", f):
                    txt = ast.unparse(node)
                    if re.search(r"(password|token|api_key|secret|cookie)\b", txt, re.I) and not re.search(r"redact|\*\*\*|len\(", txt):
                        add("info", "secrets", f"{p}:{node.lineno} log line mentions a secret: `{txt[:90]}`")
        # websocket commands without admin
        for m in re.finditer(r"((?:@[^\n]+\n\s*)*)@websocket_api\.websocket_command\((.{0,400}?)\)\s*\n((?:\s*@[^\n]+\n)*)\s*(?:async\s+)?def\s+(\w+)", t, re.S):
            decos = m.group(1) + m.group(3)
            body = t[m.end():m.end() + 1500]
            if re.search(r"is_admin|Unauthorized|require_admin", body.split("\ndef ")[0].split("\nasync def ")[0]):
                continue
            cmd = re.search(r"['\"]type['\"]\s*:\s*f?['\"]([^'\"]+)", m.group(2))
            cmdn = cmd.group(1) if cmd else m.group(4)
            mutating = re.search(r"(set_|save|update|delete|remove|create|add|run|exec|reload|restart|write|push|commit|install|clear|reset|ack|toggle|import|allow)", cmdn.split("/")[-1], re.I)
            if "require_admin" not in decos and mutating:
                add("minor", "ws-admin", f"{p}:{lineno(t, m.start())} websocket `{cmdn}` changes state without `@require_admin`")
        # HTTP views
        for m in re.finditer(r"class\s+(\w+)\(HomeAssistantView\):(.{0,600})", t, re.S):
            if re.search(r"requires_auth\s*=\s*False", m.group(2)):
                add("major", "http-auth", f"{p}:{lineno(t, m.start())} view `{m.group(1)}` has requires_auth = False")
    if "async_setup_entry" in allc and "async_unload_entry" not in allc:
        add("major", "unload", "async_setup_entry without async_unload_entry")
    if re.search(r"hass\.data\[\s*DOMAIN\s*\]", allc) and "runtime_data" not in allc:
        add("info", "runtime-data", "uses hass.data[DOMAIN] (recommended: entry.runtime_data)")
    for m in re.finditer(r"hass\.services\.async_register\(([^)]*)\)", allc):
        args = [a.strip() for a in m.group(1).split(",") if a.strip()]
        if len(args) == 3 and "schema" not in m.group(1):
            add("minor", "service-schema", f"service `{args[1]}` registered without a schema")
    n_broad = len(re.findall(r"except\s+Exception\b", allc))
    if n_broad > 15:
        add("info", "except", f"{n_broad} `except Exception` blocks")


def biome(repo, add):
    if not os.path.exists(os.path.join(repo, "biome.json")) or not os.path.exists(BIOME):
        return
    out = subprocess.run([BIOME, "lint", "--reporter=github", "."], cwd=repo, capture_output=True, text=True).stdout
    c = collections.Counter()
    for m in re.finditer(r"title=(lint/[\w/]+),file=[^,]+/(src|test|scripts|custom_components)[^,]*", out):
        c[(m.group(1), m.group(2))] += 1
    for (rule, where), n in c.items():
        add("info", "biome", f"{rule} ×{n} ({where}/)")


def main():
    res = []
    for r in REPOS:
        repo = os.path.join(SRC, r)
        issues = []

        def add(sev, code, msg):
            issues.append({"sev": sev, "code": code, "msg": msg})
        js_checks(repo, add)
        py_checks(repo, add)
        biome(repo, add)
        res.append({"repo": r, "issues": issues})
    json.dump(res, open(os.path.join(ROOT, "results", "auto", "code.json"), "w"), indent=1)
    order = {"major": 0, "minor": 1, "info": 2}
    agg = collections.defaultdict(set)
    for r in res:
        for i in r["issues"]:
            agg[(i["sev"], i["code"])].add(r["repo"])
    out = ["# Code review — automatic leads", "",
           "Generated by `scripts/audit_code.py`: risky patterns + biome (ruff is clean on every repo). "
           "Each lead is triaged by hand in `results/repos/<repo>.md`.", "",
           "| Sev | Rule | Repos | Which |", "|---|---|---|---|"]
    for (sev, code), repos in sorted(agg.items(), key=lambda x: (order[x[0][0]], -len(x[1]))):
        out.append(f"| {sev} | {code} | {len(repos)} | {', '.join(x.replace('ha-', '') for x in sorted(repos))} |")
    out += ["", "## By repo", ""]
    for r in res:
        if not r["issues"]:
            out.append(f"- **{r['repo']}** — nothing flagged")
            continue
        out.append(f"### {r['repo']}")
        for i in sorted(r["issues"], key=lambda i: order[i["sev"]]):
            out.append(f"- [{i['sev']}] {i['code']}: {i['msg']}")
        out.append("")
    open(os.path.join(ROOT, "results", "CODE.md"), "w").write("\n".join(out) + "\n")
    for sev in order:
        print(sev, sum(1 for r in res for i in r["issues"] if i["sev"] == sev))


if __name__ == "__main__":
    main()
