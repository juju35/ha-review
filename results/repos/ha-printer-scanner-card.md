# ha-printer-scanner-card

- Kind: card
- Reviewed revision: `9133d48c6e`
- Versions: CHANGELOG.md=2.18.0, package.json=2.18.0, package-lock.json=2.18.0, package-lock.json packages['']=2.18.0
- Findings to act on: **0** (major 0, minor 0)

| Sev | Area | Finding | Status |
|---|---|---|---|
| info | visual | banner: illustrated header built with its own class names (scene/hero/header), not the shared `.banner` structure — height and ground bar not checked automatically | auto |
| info | code | errors: 3 hass.callService calls, none with .catch/try (a failure is silent) | auto |
| info | code | biome: lint/style/useTemplate ×7 (src/) | auto |
| info | code | biome: lint/complexity/useOptionalChain ×1 (src/) | auto |
