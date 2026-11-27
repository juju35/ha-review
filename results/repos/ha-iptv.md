# ha-iptv

- Kind: panel-integration
- Reviewed revision: `c37baeaad4`
- Versions: CHANGELOG.md=3.38.5, manifest.json=3.38.5, const.py=3.38.5, JS *_VERSION=3.38.5
- Findings to act on: **0** (major 0, minor 0)

| Sev | Area | Finding | Status |
|---|---|---|---|
| info | visual | mini-zoom: detail button position not obviously top-right | auto |
| info | code | lifecycle: setInterval ×1 but clearInterval ×0 | auto |
| info | code | lifecycle: 6 observers created, 5 `.disconnect()` calls | auto |
| info | code | size: src/iptv-panel/panel.js is 1638 lines | auto |
| info | code | biome: lint/suspicious/noTemplateCurlyInString ×1 (test/) | auto |
| info | security | Xtream credentials travel in URLs (query/path) by protocol design, often over plain http to the provider; the integration keeps them server-side, admin-only for `get_credentials`, never in recorder/notifications. Fine — mention the http risk in the README. | verified |
