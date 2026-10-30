#!/usr/bin/env python3
"""Rasterise the vinOS mark into a fastfetch logo using quadrant block glyphs.

    python3 tools/render_ascii.py > fastfetch/vinos.txt

$1 is the heavy stroke, $2 the hairline (colours set in fastfetch/config.jsonc).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_branding import THICK, THIN  # noqa: E402

COLS, ROWS = 30, 15          # terminal cells; cells are ~2x taller than wide
SUB = 6                      # samples per quadrant edge
QUADS = " ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█"    # index = TL | TR<<1 | BL<<2 | BR<<3


def inside(poly, x, y):
    n, hit = len(poly), False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def coverage(poly, x0, y0, w, h):
    hits = sum(
        inside(poly, x0 + (i + .5) * w / SUB, y0 + (j + .5) * h / SUB)
        for i in range(SUB) for j in range(SUB)
    )
    return hits / SUB ** 2


lines = []
cw, ch = 100 / COLS, 100 / ROWS
for r in range(ROWS):
    out, cur = "", None
    for c in range(COLS):
        bits, thick_w, thin_w = 0, 0.0, 0.0
        for q, (dx, dy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
            x0, y0 = c * cw + dx * cw / 2, r * ch + dy * ch / 2
            a = coverage(THICK, x0, y0, cw / 2, ch / 2)
            b = coverage(THIN, x0, y0, cw / 2, ch / 2)
            if max(a, b) >= 0.5:
                bits |= 1 << q
            thick_w += a
            thin_w += b
        glyph = QUADS[bits]
        if glyph != " ":
            color = "$1" if thick_w >= thin_w else "$2"
            if color != cur:
                out += color
                cur = color
        out += glyph
    lines.append(out.rstrip())
print("\n".join(lines))
