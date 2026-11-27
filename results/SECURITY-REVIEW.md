# Security review — ha-* repositories

Scope: the 110 repos of `repos.txt`. Automatic leads from `scripts/audit_security.py`
([SECURITY.md](SECURITY.md)) and from the code phase ([CODE.md](CODE.md)), then triage by reading the code.

## Verdict
**No critical or major vulnerability found.** The integrations follow good practice almost
everywhere; what remains is hardening and consistency.

## What was checked, and the result

### Backend (26 integrations + 2 card repos with a backend)
| Check | Result |
|---|---|
| WebSocket commands that change state without `@require_admin` | **None.** All mutating commands are admin-only (decorator above `websocket_command`, which `functools.wraps` keeps). Only `house_rules/timer` and `house_rules/presence` act on entities without being admin-only (non-admins may call services anyway; inconsistent, not a hole). |
| HTTP views with `requires_auth = False` | None. |
| Static paths exposing the config folder | None (only each integration's `frontend/`). |
| Diagnostics of entries holding credentials | All redact (`async_redact_data` or allow-list): educartable, ent-one, family-link, findmy, iptv, orange, parcel, public-transport, reverse-proxy, tapo. |
| Secrets in logs | None: the hits only mention the word "token"/"cookie", never a value. |
| Credentials exposure (IPTV) | `get_credentials` is an admin service, passwords are never sent to the recorder, notifications or the panel. Xtream puts them in URLs by protocol design. |
| Shell / subprocess | Only system-hub (git sync, ssh-keygen): `create_subprocess_exec` with argument lists, no shell, URLs stripped of userinfo before logging, `StrictHostKeyChecking=accept-new`. Good. |
| File writes from callers | system-hub CSV export checks the config folder / `allowlist_external_dirs` and refuses hidden folders; smart-comfort writes a fixed file name. Good. |
| Unsafe deserialisation | ruamel `YAML()` (round-trip, safe) in smart-comfort; `pickle.load` of public-transport's own `.storage` cache (written locally, never downloaded) — acceptable, see note. |
| TLS verification disabled | hp only, towards the printer (self-signed certificates) — justified. |
| Blocking I/O in the event loop | None (the hits were inside `async_add_executor_job` lambdas). |

### Frontend (cards and panels)
| Check | Result |
|---|---|
| HTML injection (`innerHTML` templates) | Every repo has an escape helper and uses it on entity names/attributes; ~60 raw `${…}` hits sampled — internal values (CSS classes, schema keys). 20 repos use lit (auto-escaped). |
| `javascript:` URLs in `href`/`src` from data | Mostly guarded (`webUrl()`, `safeHref`, `^https?://` tests). Two unguarded but fed by trusted integration data: github `b.pr.url`, proxmox `node.url`. |
| Reverse tabnabbing | **3 real cases**: `window.open(url)` without `noopener` in the ENT cards (ent-one, educartable, skolengo) for portal attachments. |
| Secrets in `localStorage` | None. |
| Remote code / third-party calls from the browser | None (maplibre / three.js are vendored). |
| `eval` / `new Function` | Only inside vendored maplibre (vehicle-card, vacuum-map). |

### CI / supply chain
| Check | Result |
|---|---|
| `pull_request_target` | Not used anywhere. |
| Top-level `permissions:` in every workflow | Yes, all 110 repos. |
| Actions pinned to a commit SHA | Yes, everywhere. |
| Untrusted event text interpolated in `run:` | None (the feat/fix gate uses `startsWith(...)` in `if:` only). |
| Fork PRs and the screenshots App token | Guarded: fork PRs are rendered but never get the token / never committed. |
| Dependabot | Present in all 110 repos. |

### Secrets committed
None. Hits: the public Family Link web-app API key (sent by every browser — not a secret) and a
`-----BEGIN PRIVATE KEY-----` placeholder string in a reverse-proxy test fixture.

## To do (hardening)
| # | Repos | Action | Effort |
|---|---|---|---|
| S1 | ent-one, ent-educartable, ent-skolengo | `window.open(url, "_blank", "noopener,noreferrer")` | trivial |
| S2 | github, proxmox | Run `b.pr.url` / `node.url` through the existing http(s) link helper | trivial |
| S3 | all 110 | Add a short `SECURITY.md` (how to report a vulnerability privately — GitHub private vulnerability reporting) | small, scriptable |
| S4 | house-rules | Make `timer` / `presence` admin-only like the other commands, or document why not | trivial |
| S5 | public-transport | Optional: replace the pickle cache with JSON/msgpack to remove the class of risk | small |
| S6 | iptv | README: warn that Xtream credentials travel in clear when the provider URL is `http://` | trivial |
