# ha-proxmox

- Kind: panel-integration
- Reviewed revision: `3d05e07000`
- Versions: CHANGELOG.md=1.7.1, manifest.json=1.7.1, const.py=1.7.1, JS *_VERSION=1.7.1
- Findings to act on: **2** (major 0, minor 2)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | security | url-scheme: src/proxmox-panel/panel.js:648 `href` from data `${esc(node.url)}` without a scheme check (javascript: URLs) | auto |
| minor | security | url-scheme: src/proxmox-panel/panel.js:756 `href` from data `${esc(g.url)}` without a scheme check (javascript: URLs) | auto |
| info | code | lifecycle: 5 observers created, 4 `.disconnect()` calls | auto |
| info | code | biome: lint/complexity/noThisInStatic ×1 (src/) | auto |
| info | security | `node.url` (proxmox-panel/panel.js:648) in an href without an http(s) scheme check (value from the integration config — low risk; other repos use a `webUrl()`/`safeHref` helper). | verified |
