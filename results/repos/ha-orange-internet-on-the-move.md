# ha-orange-internet-on-the-move

- Kind: integration
- Reviewed revision: `3e1d045263`
- Versions: CHANGELOG.md=1.0.3, manifest.json=1.0.3
- Findings to act on: **2** (major 0, minor 2)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | screenshots: screenshots/ present but no screenshots.yml workflow — static copies that can drift from the card/theme they show | auto |
| minor | conventions | readme: own logo not centered at the top of the README | auto |
| info | conventions | hacs: `country` ['FR'] set — check it is intended | auto |
| info | code | secrets: custom_components/orange_internet_on_the_move/api.py:202 log line mentions a secret: `_LOGGER.debug('Token rejected (HTTP %s), logging in again', response.status)` | auto |
| info | conventions | `country: FR` is right (French service) — add the repo to the France-only list of the conventions. | verified |
