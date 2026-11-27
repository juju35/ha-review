#!/usr/bin/env python3
"""Dynamic test: does a card keep the scroll (page and inner lists) and its DOM when `hass` updates?

For every card type a repo registers in window.customCards:
  1. render it in Chrome with a mocked Home Assistant (stub ha-card/ha-icon…, a generic `hass` with ~45
     entities of every common domain), config from `getStubConfig()` (else `{type}`);
  2. scroll the page so the card sits above the viewport top, and scroll every scrollable box inside the card;
  3. send a `hass` that is a new object with the same states  ("no-op" update), then three updates where
     every state object is new (numbers +1, `last_updated` changed) ("state" updates);
  4. measure: share of the card's DOM nodes kept, inner scrollTop kept, window.scrollY kept, card height
     changes seen by a ResizeObserver during the updates (a dip = the page jumps).

Prerequisite: every repo built (`npm run build`), Python Playwright, Chrome. Repos with a screenshot mock
(`scripts/mock*.mjs`) get its states too: `node scripts/dump_fixtures.mjs ../src ../fixtures` first.
Usage: python3 scripts/test_scroll_update.py [SRC_DIR] [repo ...] -> results/auto/scroll.json, results/SCROLL.md
"""
import glob
import json
import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.path.join(ROOT, "..", "src")
ONLY = [a for a in sys.argv[1:] if a.startswith("ha-")]
REPOS = ONLY or open(os.path.join(ROOT, "repos.txt")).read().split()
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")


def bundles(repo):
    out = []
    for pat in ("dist/*.js", "custom_components/*/frontend/*.js", "custom_components/*/www/*.js"):
        for p in sorted(glob.glob(os.path.join(repo, pat))):
            b = os.path.basename(p)
            if ".i18n." in b or "vendor" in p or b.endswith((".min.js",)) or "badge" in b or "header" in b and "dashboard" not in repo:
                continue
            out.append(p)
    return out


STUBS = r"""
(() => {
  const simple = (tag, extra) => { if (!customElements.get(tag)) customElements.define(tag, class extends HTMLElement { constructor(){super(); extra && extra(this);} }); };
  ["ha-card","ha-icon","ha-svg-icon","ha-state-icon","ha-switch","ha-slider","mwc-button","ha-button","ha-icon-button",
   "ha-circular-progress","ha-spinner","ha-chip","ha-assist-chip","ha-textfield","ha-select","ha-list-item","ha-formfield",
   "ha-checkbox","ha-radio","ha-entity-picker","ha-form","ha-dialog","ha-tooltip","ha-relative-time","state-badge",
   "ha-camera-stream","ha-hls-player","ha-markdown","hui-image","ha-ripple","mwc-icon-button","ha-tab","ha-tabs"]
   .forEach((t) => simple(t));
  window.loadCardHelpers = async () => ({ createCardElement: (c) => { const e = document.createElement("div"); e.setConfig = () => {}; return e; } });
  window.__errors = [];
  window.addEventListener("error", (e) => window.__errors.push(String(e.message)));
  window.addEventListener("unhandledrejection", (e) => window.__errors.push(String(e.reason)));
})();
"""

HASS = r"""
window.__mkHass = (gen) => {
  const now = new Date(Date.now() + gen * 1000).toISOString();
  const S = (id, state, attributes = {}) => [id, { entity_id: id, state: String(state), attributes, last_changed: now, last_updated: now, context: { id: "c" + gen } }];
  const n = (v) => (typeof v === "number" ? v + gen : v);
  const list = [
    S("sun.sun", "above_horizon", { next_rising: now, next_setting: now, elevation: 30 }),
    S("light.living_room", "on", { friendly_name: "Living room", brightness: n(128), color_mode: "brightness", supported_color_modes: ["brightness"] }),
    S("light.kitchen", "off", { friendly_name: "Kitchen" }),
    S("switch.plug", "on", { friendly_name: "Plug" }),
    S("sensor.temperature", n(21.5), { friendly_name: "Temperature", unit_of_measurement: "°C", device_class: "temperature", state_class: "measurement" }),
    S("sensor.humidity", n(48), { friendly_name: "Humidity", unit_of_measurement: "%", device_class: "humidity" }),
    S("sensor.power", n(350), { friendly_name: "Power", unit_of_measurement: "W", device_class: "power" }),
    S("sensor.energy", n(12.3), { friendly_name: "Energy", unit_of_measurement: "kWh", device_class: "energy", state_class: "total_increasing" }),
    S("sensor.battery", n(64), { friendly_name: "Battery", unit_of_measurement: "%", device_class: "battery" }),
    S("sensor.co2", n(650), { friendly_name: "CO2", unit_of_measurement: "ppm", device_class: "carbon_dioxide" }),
    S("binary_sensor.front_door", "off", { friendly_name: "Front door", device_class: "door" }),
    S("binary_sensor.window", "on", { friendly_name: "Window", device_class: "window" }),
    S("binary_sensor.motion", "on", { friendly_name: "Motion", device_class: "motion" }),
    S("binary_sensor.smoke", "off", { friendly_name: "Smoke", device_class: "smoke" }),
    S("binary_sensor.leak", "off", { friendly_name: "Leak", device_class: "moisture" }),
    S("lock.front_door", "locked", { friendly_name: "Front door lock" }),
    S("cover.living_room", "open", { friendly_name: "Shutter", current_position: n(60), supported_features: 15, device_class: "shutter" }),
    S("climate.living_room", "heat", { friendly_name: "Thermostat", current_temperature: n(20), temperature: 21, hvac_modes: ["off", "heat"], min_temp: 7, max_temp: 30 }),
    S("water_heater.tank", "eco", { friendly_name: "Water heater", current_temperature: n(52), temperature: 55, operation_list: ["eco", "boost"] }),
    S("fan.purifier", "on", { friendly_name: "Purifier", percentage: n(40) }),
    S("humidifier.bedroom", "on", { friendly_name: "Humidifier", humidity: 45 }),
    S("media_player.living_room", "playing", { friendly_name: "Living room TV", media_title: "Song " + gen, media_artist: "Artist", volume_level: 0.4, media_duration: 200, media_position: n(20), media_position_updated_at: now, source_list: ["TV"] }),
    S("vacuum.robot", "docked", { friendly_name: "Robot", battery_level: n(80), fan_speed: "standard", fan_speed_list: ["quiet", "standard"] }),
    S("lawn_mower.mower", "docked", { friendly_name: "Mower" }),
    S("alarm_control_panel.home", "disarmed", { friendly_name: "Alarm", code_arm_required: false, supported_features: 63 }),
    S("camera.front", "idle", { friendly_name: "Front camera", entity_picture: "data:image/gif;base64,R0lGODlhAQABAAAAACw=" }),
    S("person.alex", "home", { friendly_name: "Alex", latitude: 48.1, longitude: -1.6 }),
    S("person.sam", "not_home", { friendly_name: "Sam" }),
    S("device_tracker.phone", "home", { friendly_name: "Phone", battery_level: n(70), source_type: "gps", latitude: 48.1, longitude: -1.6 }),
    S("zone.home", "1", { friendly_name: "Home", latitude: 48.1, longitude: -1.6, radius: 100 }),
    S("weather.home", "sunny", { friendly_name: "Home", temperature: n(18), humidity: 50, wind_speed: 10, pressure: 1015, forecast: [] }),
    S("calendar.family", "off", { friendly_name: "Family", message: "Event", start_time: now, end_time: now }),
    S("todo.shopping", "3", { friendly_name: "Shopping", supported_features: 15 }),
    S("timer.kitchen", "active", { friendly_name: "Kitchen timer", duration: "0:10:00", remaining: "0:05:00", finishes_at: now }),
    S("input_boolean.guest", "off", { friendly_name: "Guest" }),
    S("input_number.target", n(5), { friendly_name: "Target", min: 0, max: 100, step: 1 }),
    S("number.level", n(5), { friendly_name: "Level", min: 0, max: 100, step: 1 }),
    S("select.mode", "auto", { friendly_name: "Mode", options: ["auto", "eco"] }),
    S("scene.movie", now, { friendly_name: "Movie" }),
    S("script.coffee", "off", { friendly_name: "Coffee" }),
    S("automation.lights", "on", { friendly_name: "Lights", last_triggered: now }),
    S("update.core", "off", { friendly_name: "Core", installed_version: "2026.11.0", latest_version: "2026.11.0" }),
    S("button.restart", now, { friendly_name: "Restart" }),
    S("event.doorbell", now, { friendly_name: "Doorbell", event_type: "ring" }),
    S("valve.garden", "closed", { friendly_name: "Garden valve" }),
    S("remote.tv", "on", { friendly_name: "TV remote" }),
    S("image.map", now, { friendly_name: "Map", entity_picture: "data:image/gif;base64,R0lGODlhAQABAAAAACw=" }),
  ];
  const states = Object.fromEntries(list);
  const fx = window.__fixture;
  if (fx) {
    for (const [id, st] of Object.entries(fx.states || {})) {
      const num = st.state !== "" && !isNaN(Number(st.state));
      states[id] = { entity_id: id, last_changed: now, last_updated: now, context: { id: "c" + gen }, ...st,
        attributes: { ...(st.attributes || {}) }, state: num ? String(Number(st.state) + gen) : String(st.state) };
    }
  }
  const entities = Object.fromEntries(list.map(([id]) => [id, { entity_id: id, device_id: "dev_" + id.split(".")[0], area_id: "living_room", platform: "demo" }]));
  if (fx) { Object.assign(entities, fx.entities || {}); }
  return {
    states, entities,
    devices: fx && Object.keys(fx.devices || {}).length ? { ...fx.devices } : Object.fromEntries(list.map(([id]) => ["dev_" + id.split(".")[0], { id: "dev_" + id.split(".")[0], name: id, area_id: "living_room", manufacturer: "Demo", model: "X" }])),
    areas: fx && Object.keys(fx.areas || {}).length ? { ...fx.areas } : { living_room: { area_id: "living_room", name: "Living room" } }, floors: {},
    language: "en", selectedLanguage: "en", locale: { language: "en", number_format: "language", time_format: "24", date_format: "language", first_weekday: "monday" },
    themes: { darkMode: false, theme: "default", themes: {} }, selectedTheme: null,
    user: { id: "u1", name: "Admin", is_admin: true, is_owner: true },
    config: { unit_system: { temperature: "°C", length: "km", mass: "kg", volume: "L" }, time_zone: "Europe/Paris", currency: "EUR", components: ["demo"], latitude: 48.1, longitude: -1.6, version: "2026.11.0", location_name: "Home", state: "RUNNING" },
    panels: {}, services: {}, dockedSidebar: "docked", connected: true,
    localize: (k) => k,
    formatEntityState: (s, st) => (st ?? s?.state ?? "") + (s?.attributes?.unit_of_measurement ? " " + s.attributes.unit_of_measurement : ""),
    formatEntityAttributeValue: (s, a) => String(s?.attributes?.[a] ?? ""), formatEntityAttributeName: (s, a) => a,
    formatEntityName: (s) => s?.attributes?.friendly_name ?? "",
    callService: async () => ({}), callWS: async () => [], callApi: async () => ({}), fetchWithAuth: async () => new Response("{}"),
    hassUrl: (p) => p, auth: { data: { access_token: "x" } },
    connection: { subscribeMessage: async () => () => {}, subscribeEvents: async () => () => {}, sendMessagePromise: async () => [], addEventListener() {} },
  };
};
"""

PROBE = r"""
async ([type, mode]) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const all = (root) => { const out = []; const walk = (n) => { for (const c of n.children || []) { out.push(c); if (c.shadowRoot) walk(c.shadowRoot); walk(c); } }; if (root) walk(root); return out; };
  const res = { type };
  let el;
  try {
    el = document.createElement(type);
    let hass = window.__mkHass(0);
    const Cls = customElements.get(type);
    let cfg = { type: "custom:" + type };
    try { if (Cls?.getStubConfig) { const s = await Cls.getStubConfig(hass, Object.keys(hass.states), Object.keys(hass.states)); if (s && typeof s === "object") cfg = { ...s, type: "custom:" + type }; } } catch (e) { res.stub_error = String(e); }
    res.config = cfg;
    el.setConfig(cfg);
    const host = document.getElementById("host");
    host.innerHTML = ""; host.appendChild(el);
    el.hass = hass;
    await sleep(700);
    const root = el.shadowRoot || el;
    const nodes0 = all(root);
    res.nodes = nodes0.length;
    if (nodes0.length < 3) { res.verdict = "not-rendered"; res.errors = window.__errors.slice(-3); return res; }
    // page: the card above the viewport top
    const rect = el.getBoundingClientRect();
    window.scrollTo(0, document.getElementById("top").offsetHeight + rect.height * 0.5 + 200);
    // inner scrollable boxes
    const scrollers = nodes0.filter((n) => { const cs = getComputedStyle(n); return /(auto|scroll)/.test(cs.overflowY + cs.overflowX) && (n.scrollHeight > n.clientHeight + 4 || n.scrollWidth > n.clientWidth + 4); });
    for (const s of scrollers) { s.scrollTop = Math.min(40, s.scrollHeight - s.clientHeight); s.scrollLeft = Math.min(40, s.scrollWidth - s.clientWidth); }
    await sleep(50);
    const pos = scrollers.map((s) => [s.scrollTop, s.scrollLeft]);
    const y0 = window.scrollY;
    res.scrollers = scrollers.length;
    const heights = []; const h0 = el.getBoundingClientRect().height;
    const ro = new ResizeObserver((e) => heights.push(Math.round(e.at(-1).contentRect.height)));
    ro.observe(el);
    const marks = new WeakSet(nodes0); nodes0.forEach((n) => marks.add(n));
    const measure = () => {
      const now = all(root);
      const kept = nodes0.filter((n) => n.isConnected).length / nodes0.length;
      const inner = scrollers.map((s, i) => s.isConnected && Math.abs(s.scrollTop - pos[i][0]) < 2 && Math.abs(s.scrollLeft - pos[i][1]) < 2);
      return { kept: Math.round(kept * 100), inner_ok: inner.every(Boolean), page_dy: Math.round(window.scrollY - y0), nodes: now.length };
    };
    // no-op update: new hass object, same states
    const h = window.__mkHass(0); h.states = hass.states; el.hass = h;
    await sleep(400);
    res.noop = measure();
    // state updates
    for (let g = 1; g <= 3; g++) { el.hass = window.__mkHass(g); await sleep(400); }
    res.update = measure();
    ro.disconnect();
    const hs = heights.filter((x) => x > 0);
    res.height_min = hs.length ? Math.min(...hs) : Math.round(h0);
    res.height_dip = Math.round(h0) - res.height_min;
    res.errors = window.__errors.slice(-3);
  } catch (e) { res.verdict = "error"; res.error = String(e).slice(0, 200); }
  return res;
}
"""


def verdict(r):
    if r.get("verdict"):
        return r["verdict"]
    issues = []
    if r["noop"]["kept"] < 95:
        issues.append(f"rewrites on a no-op hass ({r['noop']['kept']}% nodes kept)")
    if r["scrollers"] and not r["update"]["inner_ok"]:
        issues.append("inner scroll reset on update")
    if not r["noop"]["inner_ok"] and r["scrollers"]:
        issues.append("inner scroll reset on no-op")
    if abs(r["update"]["page_dy"]) > 1 or abs(r["noop"]["page_dy"]) > 1:
        issues.append(f"page scroll moved ({r['noop']['page_dy']}/{r['update']['page_dy']} px)")
    if r.get("height_dip", 0) > 2:
        issues.append(f"height dips by {r['height_dip']} px during the update (page jump)")
    if r["update"]["kept"] < 50:
        issues.append(f"full rewrite on state update ({r['update']['kept']}% nodes kept)")
    return "; ".join(issues) or "ok"


def main():
    out_path = os.path.join(ROOT, "results", "auto", "scroll.json")
    prev = {}
    if ONLY and os.path.exists(out_path):
        prev = {x["repo"]: x for x in json.load(open(out_path))}
    res = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        for name in REPOS:
            repo = os.path.join(SRC, name)
            files = bundles(repo)
            if not files:
                continue
            page = browser.new_page(viewport={"width": 900, "height": 700})
            page.set_content('<html><body style="margin:0"><div id="top" style="height:1500px"></div>'
                             '<div id="host" style="width:500px"></div><div style="height:3000px"></div></body></html>')
            page.add_script_tag(content=STUBS)
            fxp = os.path.join(os.environ.get("FIXTURES", os.path.join(ROOT, "..", "fixtures")), f"{name}.json")
            if os.path.exists(fxp):
                page.add_script_tag(content="window.__fixture = " + open(fxp).read() + ";")
            page.add_script_tag(content=HASS)
            load_err = []
            for f in files:
                try:
                    page.add_script_tag(path=f)
                except Exception as e:  # noqa: BLE001
                    try:
                        page.add_script_tag(path=f, type="module")
                    except Exception as e2:  # noqa: BLE001
                        load_err.append(f"{os.path.basename(f)}: {str(e2)[:120]}")
            page.wait_for_timeout(300)
            types = page.evaluate("(window.customCards||[]).map(c=>c.type).filter((t,i,a)=>a.indexOf(t)===i)")
            cards = []
            for t in types:
                if not page.evaluate(f"!!customElements.get({json.dumps(t)})"):
                    continue
                try:
                    r = page.evaluate(PROBE, [t, "card"])
                except Exception as e:  # noqa: BLE001
                    r = {"type": t, "verdict": "error", "error": str(e)[:200]}
                r["result"] = verdict(r)
                cards.append(r)
            page.close()
            res.append({"repo": name, "bundles": [os.path.relpath(f, repo) for f in files], "load_errors": load_err, "cards": cards})
            bad = [c for c in cards if c["result"] not in ("ok",)]
            print(f"{name}: {len(cards)} cards, {len(bad)} flagged", flush=True)
        browser.close()
    if prev:
        for r in res:
            prev[r["repo"]] = r
        res = [prev[k] for k in sorted(prev)]
    json.dump(res, open(out_path, "w"), indent=1)
    report(res)


def report(res):
    lines = ["# Scroll & DOM stability on card updates (dynamic test)", "",
             "Generated by `scripts/test_scroll_update.py`: each card rendered in Chrome with a mocked Home Assistant, "
             "page scrolled so the card sits above the viewport, inner scrollable boxes scrolled, then one no-op `hass` "
             "(new object, same states) and three state updates.", "",
             "Pass criteria: ≥ 95 % of the DOM kept on a no-op update, inner scroll kept, page scroll kept, no height dip, "
             "no full rewrite on a state update.", ""]
    tot = sum(len(r["cards"]) for r in res)
    ok = sum(1 for r in res for c in r["cards"] if c["result"] == "ok")
    nr = sum(1 for r in res for c in r["cards"] if c["result"] in ("not-rendered", "error"))
    lines += [f"**{tot} cards tested in {len(res)} repos — {ok} ok, {tot - ok - nr} flagged, {nr} not rendered by the generic mock** "
              "(those need the repo's own fixtures; covered by the static check).", "",
              "| Repo | Card | Result | No-op kept | Update kept | Inner scrollers |", "|---|---|---|---|---|---|"]
    for r in res:
        for c in r["cards"]:
            if c["result"] == "ok":
                continue
            lines.append(f"| {r['repo']} | {c['type']} | {c['result']} | {c.get('noop', {}).get('kept', '—')} | "
                         f"{c.get('update', {}).get('kept', '—')} | {c.get('scrollers', '—')} |")
    lines += ["", "## Passing cards", ""]
    for r in res:
        okc = [c["type"] for c in r["cards"] if c["result"] == "ok"]
        if okc:
            lines.append(f"- **{r['repo']}**: {', '.join(okc)}")
    open(os.path.join(ROOT, "results", "SCROLL.md"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
