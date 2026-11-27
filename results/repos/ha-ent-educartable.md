# ha-ent-educartable

- Kind: panel-integration
- Reviewed revision: `cc3c99f609`
- Versions: CHANGELOG.md=1.2.0, manifest.json=1.2.0, JS *_VERSION=1.2.0
- Findings to act on: **0** (major 0, minor 0)

| Sev | Area | Finding | Status |
|---|---|---|---|
| info | visual | header-icon: round header icon not 40 px (44) | auto |
| info | code | lifecycle: setInterval ×1 but clearInterval ×0 | auto |
| info | code | lifecycle: 5 observers created, 4 `.disconnect()` calls | auto |
| info | code | errors: 14 hass.callService calls, none with .catch/try (a failure is silent) | auto |
| info | code | biome: lint/style/useTemplate ×153 (src/) | auto |
| info | code | biome: lint/style/useTemplate ×1 (test/) | auto |
| info | code | biome: lint/complexity/noCommaOperator ×2 (test/) | auto |
