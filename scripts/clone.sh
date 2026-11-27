#!/usr/bin/env bash
# Shallow-clone (or refresh) every repo of repos.txt into ../src
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=${SRC:-../src}
mkdir -p "$SRC"
xargs -P 6 -I{} sh -c '
  if [ -d "'"$SRC"'/{}/.git" ]; then git -C "'"$SRC"'/{}" pull -q --ff-only || echo "PULL FAIL {}";
  else git clone -q --depth 1 https://github.com/juju35/{} "'"$SRC"'/{}" || echo "CLONE FAIL {}"; fi' < repos.txt
