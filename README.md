# ha-review

Review workspace for the `juju35/ha-*` repositories: plan, scripts, results and progress.

- [SUMMARY.md](SUMMARY.md) — conclusions and action list
- [PLAN.md](PLAN.md) — scope, phases, how to resume
- [progress.json](progress.json) — status per repo and per phase
- [results/](results/) — automatic outputs, eye review, security review, one report per repo

Re-run everything: `bash scripts/clone.sh && for s in conventions visual code options security; do python3 scripts/audit_$s.py; done && python3 scripts/contact_sheets.py && python3 scripts/build_reports.py`
