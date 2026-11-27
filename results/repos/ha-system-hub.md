# ha-system-hub

- Kind: panel-integration
- Reviewed revision: `37171b27b9`
- Versions: CHANGELOG.md=3.15.2, manifest.json=3.15.2, const.py=3.15.2, JS *_VERSION=1.0.0,2.11.0,3.15.2
- Findings to act on: **2** (major 0, minor 2)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | readme: stale HACS wording (1 lines), e.g. `\| `show_system_updates` \| `false` \| Also list the **System updates** above the Marketplace` | auto |
| minor | code | service-schema: service `SERVICE_NOTIFY` registered without a schema | auto |
| info | conventions | version: several JS *_VERSION values (sub-cards lag behind): 1.0.0,2.11.0,3.15.2 | auto |
| info | visual | webkit: uses `subgrid` — check the :hover rendering under Safari/WebKit | auto |
| info | visual | css: 349 `!important` in card CSS | auto |
| info | code | lifecycle: 31 observers created, 21 `.disconnect()` calls | auto |
| info | code | size: src/system-hub-panel/panel.js is 3903 lines | auto |
| info | code | except: 35 `except Exception` blocks | auto |
| info | code | biome: lint/complexity/useOptionalChain ×1 (src/) | auto |
| info | code | biome: lint/complexity/noCommaOperator ×1 (test/) | auto |
| info | security | noopener: src/system-hub-panel/panel.js:1763 target=_blank without rel=noopener | auto |
| info | security | noopener: src/system-hub-panel/panel.js:2948 target=_blank without rel=noopener | auto |
| info | code | Sub-card version constants lag behind the release (`*_CARD_VERSION = '2.11.0'`, `SECURITY_CARD_VERSION = '1.0.0'` vs 3.15.2): harmless for the release check (only the panel constant is read) but the console banner shows stale versions. | verified |
| minor | security | url-scheme: src/system-hub-panel/panel.js:1136 `href` from data `${shEsc(opts.href)}` without a scheme check (javascript: URLs) | false positive |
