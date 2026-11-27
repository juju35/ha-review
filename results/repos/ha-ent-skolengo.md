# ha-ent-skolengo

- Kind: card
- Reviewed revision: `9ab280a000`
- Versions: CHANGELOG.md=1.0.0, package.json=1.0.0, package-lock.json=1.0.0, package-lock.json packages['']=1.0.0
- Findings to act on: **1** (major 0, minor 1)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | security | `window.open(url)` without `'noopener'` (src/skolengo-card/lessons.js:410) on documents/attachments served by the ENT portal: the opened tab gets `window.opener` (reverse tabnabbing). Add `'_blank', 'noopener,noreferrer'`. | verified |
| info | code | lifecycle: 5 observers created, 4 `.disconnect()` calls | auto |
| info | code | biome: lint/complexity/noCommaOperator ×1 (test/) | auto |
| minor | security | noopener: src/skolengo-card/lessons.js:410 window.open without `noopener` | false positive |
