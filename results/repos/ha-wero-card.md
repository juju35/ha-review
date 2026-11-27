# ha-wero-card

- Kind: card
- Reviewed revision: `b0b917c156`
- Versions: CHANGELOG.md=1.14.5, package.json=1.14.5, package-lock.json=1.14.5, package-lock.json packages['']=1.14.5
- Findings to act on: **2** (major 0, minor 2)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | readme: no `/local/community/` resource path in install section | auto |
| minor | code | Mini card: `disconnectedCallback` (src/core.js:34) does not reset `_zoomed` — after a view change the card comes back expanded (convention: detail view back to compact when the card leaves the page). Fix: `this._setZoom(false)` like ha-flight-board-card `mini-card.js:35`. | verified |
| info | code | biome: lint/complexity/useOptionalChain ×2 (src/) | auto |
| info | code | biome: lint/complexity/noCommaOperator ×6 (test/) | auto |
