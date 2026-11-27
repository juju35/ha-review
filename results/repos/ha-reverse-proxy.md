# ha-reverse-proxy

- Kind: integration
- Reviewed revision: `8e73a4c0e2`
- Versions: CHANGELOG.md=2.5.5, manifest.json=2.5.5, JS *_VERSION=2.5.5
- Findings to act on: **0** (major 0, minor 0)

| Sev | Area | Finding | Status |
|---|---|---|---|
| info | code | secrets: custom_components/reverse_proxy/api.py:314 log line mentions a secret: `_LOGGER.debug('Nginx Proxy Manager: token expired on %s, logging in again', endpoint)` | auto |
| info | code | biome: lint/complexity/noThisInStatic ×1 (src/) | auto |
| info | code | biome: lint/complexity/noCommaOperator ×3 (test/) | auto |
