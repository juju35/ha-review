// In-place redraw for the room-card family (light, power-device, water-heater): every whole-content rewrite of a
// card (`this.shadowRoot.innerHTML = …;`) becomes `rcMorph(this.shadowRoot, …); this._rewire();`, and every listener
// put on a node of the drawing gets the abort signal of that drawing (`this._on`), so that a node kept from one
// drawing to the next is never wired twice. Listeners on the root, the window, the document, the card itself, the
// editor form, and on nodes the script creates itself (kept across drawings, data-rc-own) are left alone.
// Usage: node morph_listeners.mjs FILE...   (rewrites the files in place, prints what it changed)
import { readFileSync, writeFileSync } from "node:fs";
import { parse } from "/tmp/node_modules/acorn/dist/acorn.mjs";

const SKIP_OBJ = new Set(["root", "window", "document", "this", "this.shadowRoot", "this._form", "this.renderRoot", "globalThis"]);
const src = (code, n) => code.slice(n.start, n.end);

const walk = (node, fn, parents = []) => {
  if (!node || typeof node.type !== "string") return;
  fn(node, parents);
  for (const k of Object.keys(node)) {
    const v = node[k];
    if (Array.isArray(v)) v.forEach((c) => walk(c, fn, [...parents, node]));
    else if (v && typeof v.type === "string") walk(v, fn, [...parents, node]);
  }
};

for (const file of process.argv.slice(2)) {
  let code = readFileSync(file, "utf8");
  const ast = parse(code, { ecmaVersion: "latest", sourceType: "module" });
  const edits = [];
  // Names bound to document.createElement(...): the script's own nodes.
  const created = new Set();
  walk(ast, (n) => {
    if (n.type === "VariableDeclarator" && n.init?.type === "CallExpression" && /document\.createElement$/.test(src(code, n.init.callee))) created.add(n.id.name);
  });
  walk(ast, (n) => {
    // sinks
    if (n.type === "ExpressionStatement" && n.expression.type === "AssignmentExpression" && src(code, n.expression.left) === "this.shadowRoot.innerHTML") {
      const indent = code.slice(code.lastIndexOf("\n", n.start) + 1, n.start);
      edits.push([n.start, n.end, `rcMorph(this.shadowRoot, ${src(code, n.expression.right)});\n${indent}this._rewire();`, "sink"]);
    }
    // listeners
    if (n.type === "CallExpression" && n.callee.type === "MemberExpression" && n.callee.property.name === "addEventListener" && n.arguments.length === 2) {
      const obj = src(code, n.callee.object).replace(/\?$/, "");
      if (SKIP_OBJ.has(obj) || created.has(obj)) return;
      const last = n.arguments[1];
      edits.push([last.end, last.end, ", this._on", `listener on ${obj}`]);
    }
    // the script's own nodes, kept by rcMorph
    if (n.type === "VariableDeclarator" && created.has(n.id?.name) && n.init?.type === "CallExpression") {
      const stmtEnd = code.indexOf(";", n.end) + 1;
      const indent = (() => {
        const ls = code.lastIndexOf("\n", n.start) + 1;
        return code.slice(ls, ls + (code.slice(ls).length - code.slice(ls).trimStart().length));
      })();
      edits.push([stmtEnd, stmtEnd, `\n${indent}${n.id.name}.setAttribute?.("data-rc-own", "");`, `own node ${n.id.name}`]);
    }
  });
  edits.sort((a, b) => b[0] - a[0]);
  for (const [s, e, text] of edits) code = code.slice(0, s) + text + code.slice(e);
  writeFileSync(file, code);
  console.log(file, edits.map((x) => x[3]).join(", ") || "(nothing)");
}
