# ha-smart-comfort

- Kind: panel-integration
- Reviewed revision: `028c5c6ba7`
- Versions: CHANGELOG.md=2.4.0, manifest.json=2.4.0
- Findings to act on: **1** (major 0, minor 1)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | picker: `preview: false` still present in customCards | auto |
| info | code | lifecycle: setInterval ×3 but clearInterval ×0 | auto |
| info | code | lifecycle: window/document addEventListener ×5 but removeEventListener ×3 | auto |
| info | code | lifecycle: 7 observers created, 6 `.disconnect()` calls | auto |
| info | code | errors: 5 hass.callService calls, none with .catch/try (a failure is silent) | auto |
| info | code | biome: lint/correctness/noUnusedFunctionParameters ×1 (src/) | auto |
| info | conventions | `smart-comfort-activity-card` keeps `preview: false` (live activity feed): intended? The convention is light previews everywhere. | verified |
| major | security | unsafe-deser: custom_components/smart_comfort/yaml_file.py:218 unsafe deserialisation `yaml.load(` | false positive |
| major | security | unsafe-deser: custom_components/smart_comfort/yaml_file.py:220 unsafe deserialisation `yaml.load(` | false positive |
