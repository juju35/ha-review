# Decisions taken during the review (27 Nov 2026)

- **Idle colour token**: `var(--secondary-text-color, #9e9e9e)` everywhere — the charter model (room-overview)
  uses it, and in Home Assistant `--disabled-*` means *unavailable*, not *idle* (the "na" state keeps
  `--disabled-color`). Asked: "choose the most coherent".
- **Tile radius**: 10 px everywhere (charter model, majority).
- **maintenance / notify-hub headers**: design proposals first (2–3 scenes), the rest of their fixes go ahead.
- After the review: **fix everything** (one branch + PR per repo, repo conventions: English conventional
  commits as juju35, patch bump + CHANGELOG for shipped changes, version in the PR title).
