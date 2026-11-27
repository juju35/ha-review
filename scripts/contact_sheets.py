#!/usr/bin/env python3
"""Build contact sheets of the first (light) README screenshot of each repo, for an eye comparison.
Usage: python3 scripts/contact_sheets.py [SRC_DIR] -> results/sheets/sheet-NN.png"""
import os, re, sys
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "src")
REPOS = open(os.path.join(ROOT, "repos.txt")).read().split()
OUT = os.path.join(ROOT, "results", "sheets"); os.makedirs(OUT, exist_ok=True)
W, H, COLS = 420, 300, 4
picks = []
for r in REPOS:
    rd = open(os.path.join(SRC, r, "README.md"), encoding="utf-8").read()
    for m in re.finditer(r'(?:src="|\]\()(?:https://raw\.githubusercontent\.com/juju35/[^/]+/main/)?(screenshots/[^"\)\s]+\.png)', rd):
        f = m.group(1)
        if "dark" in f: continue
        p = os.path.join(SRC, r, f)
        if os.path.exists(p): picks.append((r, p)); break
for n in range(0, len(picks), 12):
    chunk = picks[n:n + 12]
    rows = (len(chunk) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * W, rows * (H + 22)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (r, p) in enumerate(chunk):
        im = Image.open(p).convert("RGB"); im.thumbnail((W - 10, H - 6))
        x, y = (i % COLS) * W, (i // COLS) * (H + 22)
        sheet.paste(im, (x + 5, y + 22)); d.text((x + 6, y + 5), r, fill="black")
    sheet.save(os.path.join(OUT, f"sheet-{n // 12 + 1:02d}.png"))
print(len(picks), "screenshots")
