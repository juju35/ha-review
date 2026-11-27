# ha-maintenance

- Kind: panel-integration
- Reviewed revision: `bea3c3c684`
- Versions: CHANGELOG.md=0.5.4, manifest.json=0.5.4, const.py=0.5.4, JS *_VERSION=0.5.4
- Findings to act on: **4** (major 0, minor 4)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | visual | ground-bar: ground bar 6px (charter: same thickness as flight/train, 10 px) | auto |
| minor | visual | palette: `--*-warn` = `var(--warning-color, #f59e0b)` (charter: `var(--warning-color, #ffa600)`) | auto |
| minor | visual | tile-radius: tile radius 14px (most cards: 10 or 12 px) | auto |
| minor | visual | Header without a scene (flat gradient band + small icon cluster), ground bar 6 px, warn `#f59e0b`, tile radius 14 px — the card and the panel predate the charter alignment. See VISUAL-MANUAL V1. | verified |
| info | code | lifecycle: setInterval ×2 but clearInterval ×1 | auto |
| info | code | lifecycle: 4 observers created, 3 `.disconnect()` calls | auto |
