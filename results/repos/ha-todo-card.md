# ha-todo-card

- Kind: card
- Reviewed revision: `7dfef30c23`
- Versions: CHANGELOG.md=1.5.3, package.json=1.5.3, package-lock.json=1.5.3, package-lock.json packages['']=1.5.3
- Findings to act on: **0** (major 0, minor 0)

| Sev | Area | Finding | Status |
|---|---|---|---|
| info | visual | banner: illustrated header built with its own class names (scene/hero/header), not the shared `.banner` structure — height and ground bar not checked automatically | auto |
| info | code | lifecycle: 5 observers created, 4 `.disconnect()` calls | auto |
| info | code | biome: lint/suspicious/noTemplateCurlyInString ×1 (test/) | auto |
