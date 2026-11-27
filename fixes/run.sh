#!/usr/bin/env bash
# Applies the review fixes (patches/<repo>.patch) to each repo: branch fix/review-2026-11, push,
# PR, then squash-merge (title + description) once the CI is green.
#
#   cd fixes && ./run.sh              # every patch
#   ./run.sh ha-light-card ha-pc-card # only these
#
# Needs: git, gh (logged in as juju35). Idempotent: an existing PR is reused; a merged one is skipped.
set -uo pipefail
cd "$(dirname "$0")"
BR=fix/review-2026-11
WORK=${WORK:-$(mktemp -d)}
repos=("$@")
[ ${#repos[@]} -eq 0 ] && repos=($(ls patches | sed 's/\.patch$//'))

for R in "${repos[@]}"; do
  P="$PWD/patches/$R.patch"
  [ -f "$P" ] || { echo "$R: no patch"; continue; }
  if [ -n "$(gh pr list -R "juju35/$R" --head "$BR" --state merged --json number -q '.[0].number')" ]; then
    echo "$R: already merged"; continue
  fi
  N=$(gh pr list -R "juju35/$R" --head "$BR" --state open --json number -q '.[0].number')
  if [ -z "$N" ]; then
    rm -rf "$WORK/$R"
    git clone -q --depth 1 "https://github.com/juju35/$R" "$WORK/$R" || { echo "$R: clone failed"; continue; }
    ( cd "$WORK/$R" &&
      git checkout -q -b "$BR" &&
      git -c user.name=juju35 -c user.email=julienstephan29@gmail.com am -q "$P" ) || { echo "$R: patch does not apply (main moved?) — see $WORK/$R"; continue; }
    ( cd "$WORK/$R" && git push -q -u origin "$BR" ) || { echo "$R: push failed"; continue; }
    TITLE=$(git -C "$WORK/$R" log -1 --format=%s)
    BODY="$(git -C "$WORK/$R" log -1 --format=%b | sed '/^Co-Authored-By:/d;/^Claude-Session:/d')

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
    gh pr create -R "juju35/$R" --head "$BR" --base main --title "$TITLE" --body "$BODY" >/dev/null || { echo "$R: PR failed"; continue; }
    N=$(gh pr list -R "juju35/$R" --head "$BR" --state open --json number -q '.[0].number')
  fi
  echo "$R: PR #$N"
  # Squash with the PR title + description (the repos' rule), once every check is green.
  if gh pr merge -R "juju35/$R" "$N" --squash --auto >/dev/null 2>&1; then
    echo "$R: auto-merge on"
  else
    gh pr checks -R "juju35/$R" "$N" --watch --fail-fast >/dev/null 2>&1 \
      && gh pr merge -R "juju35/$R" "$N" --squash --subject "$(gh pr view -R "juju35/$R" "$N" --json title -q .title) (#$N)" \
           --body "$(gh pr view -R "juju35/$R" "$N" --json body -q .body)" \
      && echo "$R: merged" || echo "$R: checks failed or merge refused — look at the PR"
  fi
done
