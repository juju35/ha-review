# ha-dashboard-header

- Kind: card
- Reviewed revision: `ba64ea03a6`
- Versions: CHANGELOG.md=1.6.0, package.json=1.6.0, package-lock.json=1.6.0, package-lock.json packages['']=1.6.0
- Findings to act on: **1** (major 0, minor 1)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | visual | banner: no illustrated header found (plain header) | auto |
| info | conventions | readme: no `## Supported integrations` section (check whether relevant) | auto |
| info | conventions | i18n: translations inlined in the bundle (not split per language) | auto |
| info | code | lifecycle: setInterval ×1 but clearInterval ×0 | auto |
| info | code | lifecycle: window/document addEventListener ×4 but removeEventListener ×0 | auto |
| info | code | size: src/core.js is 1843 lines | auto |
| info | code | biome: lint/complexity/noCommaOperator ×2 (test/) | auto |
| info | code | biome: lint/correctness/noUnusedFunctionParameters ×1 (test/) | auto |
| info | code | Global `setInterval` polling every 1.5 s (src/core.js:1836) to catch theme/dashboard changes — runs forever on every page while visible. Consider reacting to `hass` updates / `location-changed` instead. | verified |
