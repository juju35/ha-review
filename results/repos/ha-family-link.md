# ha-family-link

- Kind: integration
- Reviewed revision: `63b6060094`
- Versions: CHANGELOG.md=1.2.8, manifest.json=1.2.8, JS *_VERSION=1.2.8
- Findings to act on: **1** (major 0, minor 1)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | visual | Screenshot naming inverted (unsuffixed = dark, `-light` twins) and README leads with the dark captures. VISUAL-MANUAL V7. | verified |
| info | code | secrets: custom_components/family_link/coordinator.py:277 log line mentions a secret: `_LOGGER.warning('Google refused both the session and its cookie rotation: the session is b` | auto |
| info | code | secrets: custom_components/family_link/api.py:317 log line mentions a secret: `_LOGGER.warning('Google accepts the cookie rotation but no longer renews the short-lived s` | auto |
| info | code | secrets: custom_components/family_link/api.py:297 log line mentions a secret: `_LOGGER.debug('Cookie rotation: HTTP %s, changed: %s, next in %ss', response.status, chang` | auto |
| info | code | secrets: custom_components/family_link/api.py:305 log line mentions a secret: `_LOGGER.debug('Cookie rotation failed: %s', err)` | auto |
| info | code | biome: lint/complexity/useOptionalChain ×1 (src/) | auto |
| info | security | `API_KEY` in api.py:60 is the public key of the Family Link web app (sent by every browser) — not a secret; diagnostics use an allow-list (no cookie values). | verified |
| major | security | committed-secret: custom_components/family_link/api.py:60 looks like a secret (`AIzaSyAQb1gu…`) | false positive |
