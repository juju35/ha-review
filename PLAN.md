# Review plan — ha-* repositories (Nov 2026)

## Scope
- Every **non-archived** `juju35/ha-*` repository — **110 repos**, listed in [`repos.txt`](repos.txt).
- **Excluded** (still in development): `ha-routine-card`, `ha-timeline-card`, `ha-guest-card`,
  `ha-tide-card`, `ha-tv-guide-card`, `ha-airing-card`, `ha-energy-ranking-card`.
- Excluded (archived): `ha-integration-watchdog`, `ha-marketplace-refresh`, `ha-git-sync`,
  `ha-automation-monitor-card`, `ha-orphan-entities`, `ha-battery-monitor`, `ha-system-monitor-card`.
- `ha-review` itself (this repo) is the review workspace.

Revision reviewed: the `main` HEAD of each repo at clone time, recorded in `progress.json` (`sha`).

## Phases
| # | Phase | Output | How |
|---|-------|--------|-----|
| 1 | Inventory | `repos.txt`, `progress.json` | `scripts/clone.sh` |
| 2 | Conventions & CI audit (automatic) | `results/auto/conventions.json`, `results/CONVENTIONS.md` | `scripts/audit_conventions.py` |
| 3 | Visual consistency audit (automatic) | `results/auto/visual.json`, `results/VISUAL.md` | `scripts/audit_visual.py` |
| 4 | Code review — lint + risky patterns (automatic) | `results/auto/code.json`, `results/CODE.md` | `scripts/audit_code.py`, biome, ruff |
| 4c | Security audit (backend, frontend, CI / supply chain, secrets) | `results/auto/security.json`, `results/SECURITY.md`, `results/SECURITY-REVIEW.md` | `scripts/audit_security.py` + triage |
| 5 | Code review — manual reading of flagged spots | `results/repos/<repo>.md` | by hand, per repo |
| 6 | Summary & action list | `SUMMARY.md` | from phases 2–5 |

## What is checked

### Conventions / CI (from the agreed ha-* conventions)
- `CLAUDE.md`, `LICENSE` (holder `juju35`), `commitlint.config.js`, pre-commit with
  `commit-msg` hook type, commitlint, biome, `screenshots-used` hook.
- Workflows: validate, lint, release (`workflow_dispatch` + feat/fix gate), screenshots
  (Debian 12 container, App token), cleanup-branches.
- No JS committed in `dist/`.
- Version consistency: cards → `package.json` / `package-lock.json` / `CHANGELOG.md`;
  integrations → `manifest.json` / `const.py` / `CHANGELOG.md` (+ panel JS constant).
- `manifest.json` has Marketplace `categories`; France-only repos have `"country"` in `hacs.json`.
- README: English, own logo under badges, bounded image sizes, Marketplace install section
  (no stale HACS wording), Buy Me a Coffee, `## Supported integrations` where relevant.
- Translations: the 22 languages (en, fr, de, es, it, nl, pt, pl, sr, sr-Latn, ro, da, sv, bg,
  ru, uk, hu, sk, cs, sl, lv, el), split per language.
- Card picker: `preview: true` + `pickerDefine()`.

### Visual consistency (the card charter)
- Illustrated header 90 px (full and mini), ground bar, status pill everywhere.
- Night mode from the HA theme only (no `sun.sun` rule).
- Header icon: 40 px tinted round pill; icon colour follows status.
- No filled buttons; popups anchored at the top of the card (QR exception).
- Mini cards: expand button top-right; same icon size as full card.
- Popup/details closed on `disconnectedCallback`.
- Status palette and radii/font sizes compared across repos (outliers flagged).

### Security
- Backend: websocket admin checks, HTTP auth, static paths, diagnostics redaction, secrets in logs,
  subprocess/shell, file paths from callers, unsafe deserialisation, TLS.
- Frontend: HTML injection, `javascript:` URLs, `noopener`, secrets in storage, remote code.
- CI: `pull_request_target`, permissions, SHA pinning, script injection, fork PRs, Dependabot.
- Committed secrets.

### Code
- Biome lint (repo config), ruff (repo config).
- Risky patterns: unescaped `innerHTML` interpolation, timers/listeners not cleared,
  blocking I/O in async Python, websocket commands without admin check, broad excepts,
  secrets in logs, missing unload, etc. Each automatic hit is triaged by hand in phase 5.

## Resuming after an interruption
1. `bash scripts/clone.sh` (re-clones into `src/`, ignored by git).
2. Look at `progress.json`: each repo has a status per phase (`todo` / `done`).
3. Re-run the phase scripts — they are idempotent and rewrite their result files.
4. For phase 5, continue with the repos whose `manual` status is `todo`.
5. Commit and push after each batch (`chore: progress …`).
