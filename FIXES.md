# Fixes — status (27 Nov 2026)

One branch `fix/review-2026-11` and one PR per repo. Shipped changes are bumped as a patch release with a
CHANGELOG entry (`fix: apply the november review fixes (X.Y.Z)`); repo-only changes go as `chore:` without a
bump. Commits are authored by juju35, in English, conventional commits.

## What each PR contains (depending on the repo)
- `SECURITY.md` (all 110 repos).
- Idle colour → `var(--secondary-text-color, #9e9e9e)` (39 repos) and tile radius → 10 px (35 repos), per DECISIONS.md.
- README Marketplace section names the `/local/community/<repo>/<file>.js` resource (39 cards).
- Biome 2.6.8 everywhere (biome.json schema + pre-commit).
- Targeted fixes:
  - wero, camera: mini card compact again when it leaves the page;
  - safety: dead toggle code removed;
  - ENT one / educartable / skolengo: `opener` cut on the document tab;
  - github: PR link github.com only, plus `icons.json`;
  - proxmox: http(s) links only;
  - house-rules, maintenance, notify-hub: 10 px ground bar (maintenance and notify-hub also get warn `#ffa600`);
  - vehicle-consumption: ok = success colour;
  - alarm, tracker, media-server: neutral tiles;
  - wall-panel: guarded registration;
  - power-device: clock-independent test;
  - family-link: screenshot naming (light unsuffixed, `-dark` twins);
  - hp, tapo, renault-picture, orange: README shows the source card repo's captures (no drifting copies);
  - iptv: README security note;
  - house-rules: README admin note;
  - weather: README GIF widths;
  - 6 repos: stale `sun.sun` comments;
  - system-hub: sub-card versions follow the release.
- Verified before pushing: every repo builds; node test suites pass (same results as before the changes:
  only the Playwright layout tests that need a browser fail locally, as before); `check_screenshots.py` passes.

## Status
| State | Repos |
|---|---|
| **Merged — all 110 repos** | every PR listed in [fixes/opened.txt](fixes/opened.txt) is merged (squash, title + description, CI green): auto-merge where the repo allows it, otherwise `scripts/fix/merge_green.sh` |

Follow-up fixes pushed on the PR branches before merging (27 Nov):
- hp, orange-internet-on-the-move, renault-picture, tapo: the integration-only screenshot filter in
  `scripts/check_screenshots.py` used `%` formatting on a long line (ruff UP031 / E501 / format) → f-string, formatted.
- safety-card: extra trailing newline in `src/shared/base-card.js` (end-of-file-fixer); rebased onto CI's screenshot refresh.
- seedbox-card: render job hit a transient `curl: (16) HTTP2 framing` error → failed job re-run, green.

## In-place redraw (27 Nov, afternoon)
Harness first (`scripts/test_scroll_update.py`): registries keep their identity across updates as in Home Assistant
(room-card's flag was the mock's), visible content measured instead of `scrollY` (scroll anchoring is fine), plus a
click-once check and a "same markup as a card drawn from scratch" check; `scripts/test_interactions.py` taps tiles
and toggles the zoom after updates.

Shared helper: `scripts/fix/in-place-redraw.js` (rcMorph, keys unique among siblings, live form values, script-placed
nodes `data-rc-own`, `<img>` pictures set by script). Applied with `scripts/fix/apply_morph.py` (single render sink,
delegated listeners) or `scripts/fix/morph_listeners.mjs` + `finish_rc_family.py` (room-card family: listeners carry
the drawing's abort signal). PRs in [fixes/opened-morph.txt](fixes/opened-morph.txt):

| State | Repos |
|---|---|
| Merged | all 11: timer #19, light #19, power-device #28, water-heater #26 (auto-merge); cover #48, 3d-printer #32, energy #41, github #74, mower #36, pool #37, tempo #31 (on request) |
| No change needed | room-card (`room-card` flag came from the mock), vivarium (rebuilds its tank scene on purpose when a drawn part changes, so its animation restarts) |

## Header scenes — maintenance / notify-hub
Three proposals each, day/night, normal/alert: [proposals/headers.png](proposals/headers.png)
(source [proposals/headers.html](proposals/headers.html)). Chosen as the most consistent with the other cards and
today's illustrations: **A · Workshop** (maintenance 0.6.0, #22) and **A · Post** (notify-hub 0.11.0, #25), card and
panel, status pill moved next to the title on the cards. Both merged.

## Follow-ups (27 Nov, afternoon) — the items first left aside
| Repo | PR | Change |
|---|---|---|
| dashboard-header | #26 (1.6.1) | No more 1.5 s polling: `<html>` style/class observer (theme), `lovelace_updated` / `panels_updated` / `themes_updated` bus events (non-admin allowlist), `visibilitychange` |
| public-transport | #44 (1.7.6) | GTFS cache as plain JSON (`<network>.cache.json`, HA `json_bytes` / `json_loads`), old pickle deleted unread; networks-list script stubs the JSON helpers |
| saint-of-the-day | #27 (1.3.6) | `illustration: false` drops the banner for a plain header (`.titlebar`), as on the other cards |

All three green; waiting for the merge go.

## Not done on purpose
   - shared header / detail-button markup across repos: the repos stay independent, so this is a big refactor with nothing visible for users;
   - dashboard-header 1.5 s polling: works today, and the change is risky on every dashboard;
   - public-transport pickle cache: local file written by the integration, acceptable;
   - saint-of-the-day classic banner: a documented option.
