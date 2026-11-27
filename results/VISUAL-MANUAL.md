# Visual review — by eye (contact sheets)

Source: `results/sheets/sheet-*.png` (first light screenshot of each README, built by
`scripts/contact_sheets.py`), cross-checked with the automatic leads of [VISUAL.md](VISUAL.md)
and with the code (each point below was confirmed in the source).

Overall: the charter is very well applied — illustrated 90 px header, status pill next to the
title, tinted round icon, calm neutral tiles, ground bar. The deviations are concentrated in a
handful of repos.

## Confirmed deviations from the charter

| # | Repo(s) | Deviation | Charter rule | Evidence |
|---|---|---|---|---|
| V1 | maintenance, notify-hub | Header is a flat gradient band with only a small icon cluster: no scene, ground bar 6 px, warn colour `#f59e0b`, tile radius 14 px | Illustrated header with a scene matching the theme, 10 px ground bar, status palette, tile radius 10/12 px | sheet-04; `src/*-card/card.js` `.ground { height: 6px }`, `--*-warn: var(--warning-color, #f59e0b)` |
| V2 | house-rules | Ground bar 5 px (card and panel) | Same thickness everywhere (flight/train: 10 px) | `src/house-rules-cards/styles.js:17`, `src/house-rules-panel/styles.js:8` |
| V3 | alarm-card | Open sensor tile ("Kitchen window — Open") has a red-tinted background | Alert shown in red **without tinting the tile background** (badge-pill only) | sheet-01 |
| V4 | tracker-card, waste-card, media-server-card | Tiles tinted by category/state (orange "Dog", blue "Bike/Suitcase", yellow bins, pink/blue/purple counters) | Neutral tile background; colour carried by the icon pill and the state line | sheets 08, 09, 04 |
| V5 | vehicle-consumption | `--*-ok` mapped to `--primary-color` (blue) | ok = `var(--success-color, #43a047)` | VISUAL.md palette |
| V6 | opening-card | Tile radius 14 px | 10/12 px like the other cards | VISUAL.md tile-radius |
| V7 | family-link | Screenshot naming inverted (unsuffixed = dark, `-light` suffix) and the README leads with the dark captures | Light first, `-dark` twins, like every other repo | `screenshots/`, README line 25 |
| V8 | saint-of-the-day | `illustration: false` gives a 64 px "classic" banner; other cards drop the banner entirely when not illustrated | One way of rendering a non-illustrated header | `card.js:293` |

## Cross-repo inconsistencies (no single rule broken, worth harmonising)

- **Idle colour token**: `var(--disabled-text-color, #9e9e9e)` in 39 repos vs
  `var(--secondary-text-color, #9e9e9e)` in 24 (and `#727272` / `#8a94a0` in 3). Pick one.
- **Tile radius**: 10 px (49 repos) vs 12 px (39 repos). The charter model (room-overview) uses 10 px.
- **Narrow-card icon shrink**: certificate (32 px under 239 px), docker/seedbox (32 px), reverse-proxy
  (28 px under 200 px), smart-appliance (28 px under 230 px) — same idea, different thresholds and sizes.
- **Panel top-bar icon**: ENT ONE / Educartable panels use 44 px, the cards 40 px.
- **Mini detail button class**: `.zoom` (majority) vs `.detail` (ENT ONE, Educartable, saint of the
  day) vs `.hbtn.zoom` / `.iconbtn.zoom` (assist, public-transport). Same look, but harder to keep aligned.
- **Header markup**: nas, parcel, printer-scanner and todo build the illustrated header with their own
  class names (`scene`, `hero`, `header banner`) rather than the shared `.banner` + `.ground` structure.
- **Alert rows**: printer-scanner / hp (alerts list), chores (overdue rows) and tempo (red day) tint whole
  rows. Tempo's colour is the data itself (acceptable); the alert rows could follow the tile rule.
- **Screenshot suffix**: 23 repos mix `-dark` and `-light` suffixes; the convention is unsuffixed light + `-dark`.

## Stale comments about the old night rule (`sun.sun`)
cover-card, dns-filter-card, doorbell-card, ecowatt-card, room-card (`src/scene.js:11`), wall-panel:
the code reads only `hass.themes.darkMode`, but comments still describe "sun below the horizon OR dark
theme". Comment-only fix.

## Checked and fine
- `sun.sun` in scheduler, solar-forecast, solar-roof, solar-router, water-heater: drives content (sun
  times, production, PV moon), not the banner — the banner follows the theme. OK.
- Wero / Wi-Fi QR popups centred on screen: agreed exception.
- Header height: 90 px in every repo using the shared `.banner` (78 repos), full and mini.
