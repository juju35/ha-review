# Review summary — ha-* repositories (27 Nov 2026)

110 non-archived repos (82 cards, 13 integrations, 13 panel integrations, 2 themes); the 7 repos in
development and the 7 archived ones are out of scope (see [PLAN.md](PLAN.md)).
Details: [INDEX.md](results/INDEX.md) (one report per repo), [CONVENTIONS.md](results/CONVENTIONS.md),
[VISUAL.md](results/VISUAL.md) + [VISUAL-MANUAL.md](results/VISUAL-MANUAL.md), [CODE.md](results/CODE.md),
[OPTIONS.md](results/OPTIONS.md), [SECURITY-REVIEW.md](results/SECURITY-REVIEW.md).

## Overall
- **No major finding** left after triage — no bug that breaks a card, no security hole.
- **89 minor findings** across 65 repos; **45 repos have nothing to act on**.
- Conventions (CLAUDE.md, commitlint, release on feat/fix, SHA-pinned actions, App-token screenshots,
  Debian 12 container, version consistency, 22 languages, Marketplace README) are applied almost
  everywhere. Biome: a few warnings, mostly in tests; ruff is clean everywhere.
- The visual charter is respected by the large majority: 90 px illustrated header (78 repos on the
  shared `.banner`), status pill, 40 px icon pill, calm tiles, 10 px ground bar.

## Action list, by priority

### 1. Behaviour (small bugs)
| Repo | Fix |
|---|---|
| wero-card, camera | Mini card: reset `_zoomed` in `disconnectedCallback` (the card comes back expanded after a view change) |
| safety-card | Remove the dead `hide_when_off` / `only_on` branch copied from a light/power card (`src/shared/base-card.js:486`) |

### 2. Security hardening ([details](results/SECURITY-REVIEW.md))
| Repo | Fix |
|---|---|
| ent-one, ent-educartable, ent-skolengo | `window.open(url, "_blank", "noopener,noreferrer")` |
| github, proxmox | Pass `b.pr.url` / `node.url` through the http(s) link helper |
| all | Add a `SECURITY.md` (private vulnerability reporting) |
| house-rules | `timer` / `presence` websocket commands admin-only (or document why not) |
| iptv | README: warn about `http://` Xtream providers (credentials in clear) |

### 3. Visual charter
| Repo | Fix |
|---|---|
| maintenance, notify-hub | Illustrated header with a scene, 10 px ground bar, warn `#ffa600`, tile radius 10/12 px |
| house-rules | Ground bar 5 px → 10 px (cards and panel) |
| alarm-card, tracker-card, waste-card, media-server-card | Neutral tile background; colour only on the icon pill / state line |
| vehicle-consumption | `--*-ok` → `--success-color` |
| opening-card | Tile radius 14 → 10/12 px |
| family-link | Screenshots: unsuffixed = light, `-dark` twins, light first in README |
| all (choice to make) | One idle token (`--disabled-text-color` ×39 vs `--secondary-text-color` ×24) and one tile radius (10 ×49 vs 12 ×39) |
| 6 repos | Comments still describe the old `sun.sun` night rule (cover, dns-filter, doorbell, ecowatt, room, wall-panel) |

### 4. Conventions / docs
| Repo | Fix |
|---|---|
| 39 cards | README Marketplace section: add the `/local/community/<repo>/<card>.js` resource line (as cover-card) |
| hp, tapo, renault-picture, orange-internet-on-the-move, neutral, liquid-glass | Screenshots are static copies (no generator / workflow): regenerate from the source repo or generate here; themes have no tests |
| findmy, hp, orange, renault-picture, tapo | No biome in pre-commit (fine while they ship no JS) |
| github | `icons.json` for the actions |
| orange-internet-on-the-move | README own logo not centred at the top |
| weather-card | 18 README images without width/height bound |
| system-hub | Sub-card version constants (2.11.0 / 1.0.0) lag behind 3.15.2 |
| all | Biome pinned from 2.6.3 to 2.6.8 depending on the repo (schema + pre-commit): align with Dependabot |
| ha-repos conventions | Add orange-internet-on-the-move to the France-only list |

### 5. Nice to have
- Shared markup for the header (nas, parcel, printer-scanner, todo use their own class names) and
  for the mini detail button (`.zoom` vs `.detail`).
- dashboard-header: replace the global 1.5 s polling by event-driven updates.
- public-transport: JSON/msgpack cache instead of pickle.

## Method and limits
- Static analysis of every repo's `main` (SHA in `progress.json`), contact sheets of the README
  screenshots, and reading of every flagged spot; false positives are recorded in `results/triage.json`.
- Not done: running each repo's test suite / build (CI already does it on every PR), live rendering in
  Safari, checking the GitHub "Website" field (API not reachable from this session).
