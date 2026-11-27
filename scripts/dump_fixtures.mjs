// Dump each repo's screenshot mock (scripts/mock*.mjs) as JSON for test_scroll_update.py.
// Usage: node scripts/dump_fixtures.mjs SRC_DIR OUT_DIR
import { readdirSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
const [src, out] = process.argv.slice(2);
for (const repo of readdirSync(src).filter((r) => r.startsWith("ha-"))) {
  const dir = join(src, repo, "scripts");
  if (!existsSync(dir)) continue;
  const mocks = readdirSync(dir).filter((f) => /^mock.*\.mjs$/.test(f));
  const fx = { states: {}, entities: {}, devices: {}, areas: {} };
  for (const f of mocks) {
    try {
      const m = await import(pathToFileURL(join(dir, f)));
      const cands = [m, m.default, ...Object.values(m)].filter((x) => x && typeof x === "object");
      for (const c of cands) {
        for (const k of ["states", "entities", "devices", "areas"]) {
          const v = c[k] ?? (k === "states" && c.STATES) ?? null;
          if (v && typeof v === "object" && !Array.isArray(v)) Object.assign(fx[k], v);
        }
        // a plain map of entity_id -> state object
        if (Object.values(c).length && Object.values(c).every((s) => s && typeof s === "object" && "state" in s && "entity_id" in s)) Object.assign(fx.states, c);
      }
    } catch (e) { console.error(repo, f, String(e).slice(0, 120)); }
  }
  if (Object.keys(fx.states).length) {
    writeFileSync(join(out, `${repo}.json`), JSON.stringify(fx));
    console.log(repo, Object.keys(fx.states).length);
  }
}
