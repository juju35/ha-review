# ha-notify-hub

- Kind: panel-integration
- Reviewed revision: `2b9d23b265`
- Versions: CHANGELOG.md=0.10.0, manifest.json=0.10.0, const.py=0.10.0, JS *_VERSION=0.10.0
- Findings to act on: **3** (major 0, minor 3)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | visual | ground-bar: ground bar 6px (charter: same thickness as flight/train, 10 px) | auto |
| minor | visual | palette: `--*-warn` = `var(--warning-color, #f59e0b)` (charter: `var(--warning-color, #ffa600)`) | auto |
| minor | visual | Same as maintenance: flat header without a scene, ground bar 6 px, warn `#f59e0b`. See VISUAL-MANUAL V1. | verified |
| info | code | lifecycle: 4 observers created, 3 `.disconnect()` calls | auto |
| info | code | biome: lint/style/useTemplate ×1 (src/) | auto |
| info | code | biome: lint/complexity/useOptionalChain ×2 (src/) | auto |
| info | code | biome: lint/correctness/noUnusedFunctionParameters ×1 (src/) | auto |
