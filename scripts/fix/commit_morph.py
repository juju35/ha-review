#!/usr/bin/env python3
"""Bump, CHANGELOG and commit the in-place redraw (branch fix/in-place-redraw) in each clone.
Usage: python3 scripts/fix/commit_morph.py SRC_DIR repo ..."""
import os
import re
import subprocess
import sys

sys.argv = [sys.argv[0], sys.argv[1]] + sys.argv[2:]
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import commit_fixes as C  # noqa: E402

TEXT = ("Updates of Home Assistant no longer rewrite the whole card: it is brought up to date in place, so the page "
        "no longer jumps under you, the animations no longer start over and the focus, hover and inner scroll stay.")
EXTRA = {
    "ha-cover-card": "An update that changes nothing on the card no longer redraws it.",
    "ha-timer-card": "An update that changes nothing on the card no longer redraws it.",
    "ha-mower-card": "The live camera view is no longer moved (and reconnected) on every update.",
    "ha-light-card": "Compact card: the zoom button follows the view without being redrawn.",
    "ha-power-device-card": "Compact card: the zoom button follows the view without being redrawn.",
    "ha-water-heater-card": "Compact card: the zoom button follows the view without being redrawn.",
}

for name in sys.argv[2:]:
    repo = os.path.join(sys.argv[1], name)
    nm = os.path.join(repo, "node_modules")
    if os.path.islink(nm):
        os.remove(nm)
    old = C.current_version(repo)
    new = C.bump_version(old)
    C.set_versions(repo, old, new)
    items = [TEXT] + ([EXTRA[name]] if name in EXTRA else [])
    cl = os.path.join(repo, "CHANGELOG.md")
    t = open(cl).read()
    entry = f"## {new} - {C.TODAY}\n\n### Fixes\n" + "\n".join(f"- {x}" for x in items) + "\n"
    m = re.search(r"^## ", t, re.M)
    t = t[:m.start()] + entry + "\n" + t[m.start():] if m else t + "\n" + entry
    open(cl, "w").write(t)
    C.git(repo, "add", "-A")
    title = f"fix: redraw the card in place on updates ({new})"
    body = ("From the review of the ha-* repositories (juju35/ha-review, results/SCROLL.md): every `hass` update "
            "rewrote the card's whole content (innerHTML), which replaced every node.\n\n"
            + "\n".join(f"- {x}" for x in items)
            + "\n\nHow: `src/…/in-place-redraw.js` (rcMorph, the in-place redraw of ha-room-card) brings the nodes in line "
              "with the new markup — same node, text and attributes updated, items matched by their key. Listeners put on "
              "drawn nodes carry the drawing's abort signal, so a kept node is never wired twice; nodes the script places "
              "itself (data-rc-own) stay.\n\nChecked: unit tests; `scripts/test_scroll_update.py` (100 % of the nodes kept on "
              "updates, page and inner scroll kept, one click = at most one service call, same markup as a card drawn from "
              "scratch); `scripts/test_interactions.py` (taps and zoom after updates).")
    subprocess.run(["git", "-C", repo, "-c", "user.name=juju35", "-c", "user.email=julienstephan29@gmail.com",
                    "commit", "-q", "-m", f"{title}\n\n{body}\n\n{C.TRAILER}"], check=True)
    print(name, old, "->", new)
