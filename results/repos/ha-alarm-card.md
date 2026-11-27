# ha-alarm-card

- Kind: panel-integration
- Reviewed revision: `45b835b70d`
- Versions: CHANGELOG.md=2.1.3, manifest.json=2.1.3, const.py=2.1.3
- Findings to act on: **1** (major 0, minor 1)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | visual | Open-sensor tile background tinted red (charter: alert in red without tinting the tile). See VISUAL-MANUAL V3. | verified |
| info | code | lifecycle: 5 observers created, 4 `.disconnect()` calls | auto |
| info | code | size: src/alarm-panel/panel.js is 2004 lines | auto |
| info | code | biome: lint/complexity/noCommaOperator ×1 (test/) | auto |
