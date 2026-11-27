#!/usr/bin/env python3
"""Interaction check after the in-place redraw: with the mocked Home Assistant of test_scroll_update.py, a card gets
three state updates, then
  - a tap (pointerdown + pointerup + click) on each of its first tiles/buttons calls at most one service;
  - for a card with a `zoom` option: zoom in, zoom out, zoom in again — each click flips the view (full ↔ compact)
    and the zoom button's icon follows.
Usage: python3 scripts/test_interactions.py [SRC_DIR] repo:card-type[:json-config] ...
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_scroll_update as T  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.path.join(T.ROOT, "..", "src")
SPECS = [a for a in sys.argv[1:] if ":" in a]

PROBE = r"""
async ([type, extra]) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const out = { type };
  window.__reg = null;
  let hass = window.__mkHass(0);
  const Cls = customElements.get(type);
  let cfg = { type: "custom:" + type };
  if (Cls?.getStubConfig) { const s = await Cls.getStubConfig(hass, Object.keys(hass.states), Object.keys(hass.states)); if (s) cfg = { ...s, type: "custom:" + type }; }
  cfg = { ...cfg, ...extra };
  const el = document.createElement(type);
  el.setConfig(cfg);
  document.getElementById("host").replaceChildren(el);
  el.hass = hass;
  await sleep(500);
  for (let g = 1; g <= 3; g++) { hass = window.__mkHass(g); el.hass = hass; await sleep(250); }
  const root = el.shadowRoot;
  const fire = (n, t, C = PointerEvent) => n.dispatchEvent(new C(t, { bubbles: true, composed: true, cancelable: true, pointerId: 1, isPrimary: true, button: 0 }));
  // taps
  const targets = [...root.querySelectorAll(".tile, button, [role=button], [role=switch]")].filter((n) => !n.closest(".zoom") && !n.classList.contains("zoom")).slice(0, 6);
  out.taps = [];
  for (const n of targets) {
    window.__calls = [];
    fire(n, "pointerdown"); await sleep(20); fire(n, "pointerup"); fire(n, "click", MouseEvent);
    await sleep(80);
    out.taps.push(window.__calls.length);
    document.querySelectorAll("ha-more-info-dialog,ha-dialog").forEach((d) => d.remove());
    el.hass = window.__mkHass(9); await sleep(120);
  }
  // zoom
  // the compact and the full views differ in height
  const view = () => Math.round(el.getBoundingClientRect().height);
  const icon = () => root.querySelector(".zoom ha-icon")?.getAttribute("icon") ?? null;
  out.zoom = [];
  for (let i = 0; i < 3; i++) {
    const z = root.querySelector(".zoom");
    if (!z) break;
    const before = [view(), icon()];
    z.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true, detail: 1 }));
    await sleep(120);
    el.hass = window.__mkHass(10 + i); await sleep(150);
    out.zoom.push([before, [view(), icon()], root.querySelectorAll(".zoom").length]);
  }
  out.errors = window.__errors.slice(-3);
  return out;
}
"""


def main():
    by_repo = {}
    for spec in SPECS:
        repo, card, *cfg = spec.split(":", 2)
        by_repo.setdefault(repo, []).append((card, json.loads(cfg[0]) if cfg else {}))
    bad = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=T.CHROME, args=["--no-sandbox"])
        for repo, cards in by_repo.items():
            page = browser.new_page(viewport={"width": 900, "height": 900})
            page.set_content('<html><body style="margin:0"><div id="host" style="width:500px"></div></body></html>')
            page.add_script_tag(content=T.STUBS)
            page.add_script_tag(content=T.HASS)
            for f in T.bundles(os.path.join(SRC, repo)):
                try:
                    page.add_script_tag(path=f)
                except Exception:  # noqa: BLE001
                    page.add_script_tag(path=f, type="module")
            page.evaluate("window.__errors = []")
            page.wait_for_timeout(300)
            for card, extra in cards:
                r = page.evaluate(PROBE, [card, extra])
                taps_ok = all(n <= 1 for n in r["taps"])
                zoom_ok = all(a[0] != b[0] and a[1] != b[1] and n == 1 for a, b, n in r["zoom"])
                ok = taps_ok and zoom_ok and not r["errors"]
                bad += not ok
                print(f"{'ok ' if ok else 'BAD'} {repo} {card} taps={r['taps']} zoom={r['zoom']} errors={r['errors']}")
            page.close()
        browser.close()
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
