# ha-hp

- Kind: integration
- Reviewed revision: `5b1e84beef`
- Versions: CHANGELOG.md=1.2.4, manifest.json=1.2.4, const.py=1.2.4
- Findings to act on: **1** (major 0, minor 1)

| Sev | Area | Finding | Status |
|---|---|---|---|
| minor | conventions | screenshots: screenshots/ present but no screenshots.yml workflow — static copies that can drift from the card/theme they show | auto |
| info | code | TLS verification disabled towards the printer (`verify_ssl=False`): justified (printers use self-signed certificates); keep it limited to the printer host. | verified |
| minor | code | tls: custom_components/hp/__init__.py:39 TLS verification disabled (`verify_ssl=False`) | false positive |
| minor | code | tls: custom_components/hp/config_flow.py:67 TLS verification disabled (`verify_ssl=False`) | false positive |
| minor | code | tls: custom_components/hp/api.py:161 TLS verification disabled (`ssl=False`) | false positive |
| minor | code | tls: custom_components/hp/api.py:193 TLS verification disabled (`ssl=False`) | false positive |
