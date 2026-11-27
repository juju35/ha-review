# ha-github

- Kind: panel-integration
- Reviewed revision: `10956365d5`
- Versions: CHANGELOG.md=2.20.1, manifest.json=2.20.1, const.py=2.20.1, JS *_VERSION=2.20.1
- Findings to act on: **3** (major 0, minor 3)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | manifest: services.yaml present but no icons.json (service icons) | auto |
| minor | security | url-scheme: src/github-panel/panel.js:1497 `href` from data `${esc(b.pr.url)}` without a scheme check (javascript: URLs) | auto |
| minor | conventions | `services.yaml` without `icons.json`: the actions have no icon in the UI (other integrations ship one). | verified |
| info | visual | webkit: uses `subgrid` — check the :hover rendering under Safari/WebKit | auto |
| info | code | lifecycle: 5 observers created, 4 `.disconnect()` calls | auto |
| info | code | size: src/github-panel/panel.js is 2027 lines | auto |
| info | code | biome: lint/complexity/noCommaOperator ×1 (test/) | auto |
| info | security | `b.pr.url` (panel.js:1497) is put in an href without the `^https://github.com/` check used two functions above — data comes from the GitHub API (trusted), but align with `_ghLink`. | verified |
| minor | security | url-scheme: src/github-panel/panel.js:1282 `href` from data `${esc(url)}` without a scheme check (javascript: URLs) | false positive |
| minor | security | url-scheme: src/github-panel/panel.js:1698 `href` from data `${esc(r.url)}` without a scheme check (javascript: URLs) | false positive |
