# ha-wall-panel

- Kind: card
- Reviewed revision: `9a0eb51da0`
- Versions: CHANGELOG.md=1.2.1, package.json=1.2.1, package-lock.json=1.2.1, package-lock.json packages['']=1.2.1
- Findings to act on: **3** (major 0, minor 3)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | picker: customCards without `pickerDefine()` light previews | auto |
| minor | conventions | picker: `preview: false` still present in customCards | auto |
| minor | code | define: customElements.define without a customElements.get guard (double load throws) | auto |
| info | conventions | readme: no `## Supported integrations` section (check whether relevant) | auto |
| info | visual | stale-comment: comments still describe the old `sun.sun` night rule | auto |
| info | visual | tile-radius: tile radius 16px, 2px, 20px, 3px (most cards: 10 or 12 px) | auto |
| info | conventions | `preview: false` and no `pickerDefine()` (full-screen wall dashboard): probably intended; and `customElements.define` without a `customElements.get` guard (a double load throws). | verified |
