# ha-camera

- Kind: panel-integration
- Reviewed revision: `340070831f`
- Versions: CHANGELOG.md=4.12.1, manifest.json=4.12.1, const.py=4.12.1, JS *_VERSION=4.12.1
- Findings to act on: **1** (major 0, minor 1)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | code | Mini card: `disconnectedCallback` (src/home-camera-card/mini-card.js:34) does not reset `_zoomed` — back on the view the mini card is still expanded (convention: compact again when it leaves the page). Same fix as wero. | verified |
| info | code | lifecycle: window/document addEventListener ×9 but removeEventListener ×7 | auto |
| info | code | size: src/home-camera-card/card.js is 2222 lines | auto |
| info | code | biome: lint/complexity/useOptionalChain ×2 (src/) | auto |
| info | code | biome: lint/complexity/noCommaOperator ×1 (test/) | auto |
