# ha-saint-of-the-day

- Kind: integration
- Reviewed revision: `ef548b24c7`
- Versions: CHANGELOG.md=1.3.5, manifest.json=1.3.5, JS *_VERSION=1.3.5
- Findings to act on: **0** (major 0, minor 0)

| Sev | Area | Finding | Status |
|---|---|---|---|
| info | visual | banner-height: `illustration: false` header is 64 px (other cards: no banner at all) — harmonise the non-illustrated header | auto |
| info | code | biome: lint/complexity/useOptionalChain ×1 (src/) | auto |
| info | code | biome: lint/correctness/noUnusedVariables ×1 (test/) | auto |
| info | code | biome: lint/complexity/useOptionalChain ×1 (test/) | auto |
| info | visual | `illustration: false` keeps a 64 px 'classic' banner; other cards render no banner at all. VISUAL-MANUAL V8. | verified |
