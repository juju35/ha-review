# ha-github

- Kind: panel-integration
- Reviewed revision: `10956365d5`
- Versions: CHANGELOG.md=2.20.1, manifest.json=2.20.1, const.py=2.20.1, JS *_VERSION=2.20.1
- Findings to act on: **2** (major 0, minor 2)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | manifest: services.yaml present but no icons.json (service icons) | auto |
| minor | conventions | `services.yaml` without `icons.json`: the actions have no icon in the UI (other integrations ship one). | verified |
| info | visual | webkit: uses `subgrid` — check the :hover rendering under Safari/WebKit | auto |
| info | code | lifecycle: 5 observers created, 4 `.disconnect()` calls | auto |
| info | code | size: src/github-panel/panel.js is 2027 lines | auto |
| info | code | biome: lint/complexity/noCommaOperator ×1 (test/) | auto |
