# ha-house-rules

- Kind: panel-integration
- Reviewed revision: `c4b501b225`
- Versions: CHANGELOG.md=1.8.7, manifest.json=1.8.7, JS *_VERSION=1.8.7
- Findings to act on: **3** (major 0, minor 3)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | visual | ground-bar: ground bar 5px (charter: same thickness as flight/train, 10 px) | auto |
| minor | code | xss: src/house-rules-panel/panel.js:258 unescaped `${a.attributes.levels}` in an HTML template | auto |
| minor | visual | Ground bar 5 px in the cards and the panel (charter: 10 px). See VISUAL-MANUAL V2. | verified |
| info | code | lifecycle: setInterval ×3 but clearInterval ×2 | auto |
| info | code | lifecycle: 4 observers created, 3 `.disconnect()` calls | auto |
| info | code | Websocket `house_rules/timer` and `house_rules/presence` act on entities without `@require_admin` while every other mutating command of the repo is admin-only. Acceptable (non-admins may call services anyway) but inconsistent — document it or align. | verified |
