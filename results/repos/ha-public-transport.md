# ha-public-transport

- Kind: integration
- Reviewed revision: `825b01dee2`
- Versions: CHANGELOG.md=1.7.4, manifest.json=1.7.4, JS *_VERSION=1.7.4
- Findings to act on: **0** (major 0, minor 0)

| Sev | Area | Finding | Status |
|---|---|---|---|
| info | visual | mini-zoom: detail button position not obviously top-right | auto |
| info | code | biome: lint/style/useTemplate ×1 (src/) | auto |
| info | code | biome: lint/complexity/useOptionalChain ×1 (src/) | auto |
| info | code | biome: lint/complexity/noCommaOperator ×2 (test/) | auto |
| info | code | biome: lint/correctness/noUnusedFunctionParameters ×1 (test/) | auto |
| info | security | noopener: src/public-transport-card/public-transport-card-2.js:651 target=_blank without rel=noopener | auto |
| info | security | GTFS cache read with `pickle.load` (gtfs.py:777): file written by the integration in `.storage`, never downloaded — acceptable; a JSON/msgpack cache would remove the class of risk entirely. | verified |
| major | security | unsafe-deser: custom_components/public_transport/providers/gtfs.py:777 unsafe deserialisation `pickle.load(` | false positive |
