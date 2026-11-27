# ha-vacuum-map

- Kind: integration
- Reviewed revision: `1682fe1852`
- Versions: CHANGELOG.md=1.6.3, manifest.json=1.6.3, const.py=1.6.3, JS *_VERSION=1.6.3
- Findings to act on: **2** (major 0, minor 2)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | picker: customCards without `pickerDefine()` light previews | auto |
| minor | conventions | picker: `preview: false` still present in customCards | auto |
| info | code | console: custom_components/vacuum_map/frontend/vendor/three.min.js:2 console.log left in shipped code | auto |
| info | code | size: custom_components/vacuum_map/frontend/vendor/three.min.js is 4226 lines | auto |
| minor | conventions | build: bundle is minified (convention: no minification) | false positive |
