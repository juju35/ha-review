# ha-safety-card

- Kind: card
- Reviewed revision: `26db83aa25`
- Versions: CHANGELOG.md=1.5.3, package.json=1.5.3, package-lock.json=1.5.3, package-lock.json packages['']=1.5.3
- Findings to act on: **2** (major 0, minor 2)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | readme: no `/local/community/` resource path in install section | auto |
| minor | docs | `hide_when_off` / `only_on` read in `src/shared/base-card.js:486` — light/power logic copied from another card, never reachable from the documented options (dead code) | verified |
| info | code | lifecycle: 3 observers created, 1 `.disconnect()` calls | auto |
| info | code | biome: lint/complexity/useOptionalChain ×1 (test/) | auto |
