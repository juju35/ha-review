#!/usr/bin/env bash
# Push the review branch of one repo, open its PR and turn on auto-merge (squash) — usage: open_pr.sh REPO [--no-auto]
set -euo pipefail
R=$1; AUTO=${2:-}
cd "$(dirname "$0")/../../../src/$R"
BR=$(git rev-parse --abbrev-ref HEAD)
git -c push.negotiate=true push -q -u origin "$BR" 2>&1 | grep -v "negotiat\|^fatal: expected\|^remote:" || true
TITLE=$(git log -1 --format=%s)
BODY="$(git log -1 --format=%b | sed '/^Co-Authored-By:/d;/^Claude-Session:/d')

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01F4sAn1x21MmgHHeW1MLKJ5"
N=$(gh api "repos/juju35/$R/pulls?head=juju35:$BR&state=open" --jq '.[0].number' 2>/dev/null || true)
if [ -z "$N" ]; then
  N=$(gh api "repos/juju35/$R/pulls" -f title="$TITLE" -f head="$BR" -f base=main -f body="$BODY" --jq .number)
fi
if [ "$AUTO" != "--no-auto" ]; then
  gh api -X PUT "repos/juju35/$R/pulls/$N/ccr/auto_merge" -f merge_method=squash >/dev/null 2>&1 && A=auto || A=no-auto
else A=review; fi
echo "$R #$N $A"
