# ha-nas-card

- Kind: card
- Reviewed revision: `0cc5a6e78c`
- Versions: CHANGELOG.md=1.27.5, package.json=1.27.5, package-lock.json=1.27.5, package-lock.json packages['']=1.27.5
- Findings to act on: **1** (major 0, minor 1)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | readme: no `/local/community/` resource path in install section | auto |
| info | visual | banner: illustrated header built with its own class names (scene/hero/header), not the shared `.banner` structure — height and ground bar not checked automatically | auto |
| info | visual | webkit: uses `subgrid` — check the :hover rendering under Safari/WebKit | auto |
| minor | security | url-scheme: src/shared-styles.js:846 `href` from data `${esc(href)}` without a scheme check (javascript: URLs) | false positive |
| minor | security | url-scheme: src/illustrated-header.js:32 `href` from data `${esc(href)}` without a scheme check (javascript: URLs) | false positive |
