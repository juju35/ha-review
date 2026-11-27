#!/usr/bin/env bash
# Squash-merge (PR title + description) every open review PR of fixes/opened.txt whose checks are all green.
cd "$(dirname "$0")/../.."
while read -r R N _; do
  N=${N#\#}
  read -r st merged sha < <(gh api "repos/juju35/$R/pulls/$N" --jq '"\(.state) \(.merged) \(.head.sha)"' 2>/dev/null)
  [ "$st" = open ] || continue
  runs=$(gh api "repos/juju35/$R/commits/$sha/check-runs?per_page=100" --jq '[.check_runs[] | (.conclusion // "pending")] | join(" ")')
  if [ -z "$runs" ] || echo "$runs" | grep -q pending; then echo "$R #$N pending"; continue; fi
  if echo "$runs" | grep -qE "failure|cancelled|timed_out|action_required"; then echo "$R #$N FAILED"; continue; fi
  title=$(gh api "repos/juju35/$R/pulls/$N" --jq .title); body=$(gh api "repos/juju35/$R/pulls/$N" --jq .body)
  gh api -X PUT "repos/juju35/$R/pulls/$N/merge" -f merge_method=squash -f commit_title="$title (#$N)" -f commit_message="$body" >/dev/null 2>&1 \
    && echo "$R #$N MERGED" || echo "$R #$N merge refused"
done < "${1:-fixes/opened.txt}"
