#!/usr/bin/env python3
"""HackWithZach carousel builder. 1080x1350 PNG slides from a JSON spec.
Brand: black #0a0a0a, red #C8102E, white text, DejaVu Sans Bold.
Usage: python3 make_carousel.py spec.json outdir
"""
import json, sys, os, textwrap
from xml.sax.saxutils import escape
import cairosvg

W, H = 1080, 1350
BLACK, RED, WHITE, GREY = "#0a0a0a", "#C8102E", "#ffffff", "#b8b8b8"
FONT = "DejaVu Sans"

def wrap(text, width):
    return textwrap.wrap(text, width=width)

def text_block(lines, x, y, size, color=WHITE, weight="bold", lh=1.22, accent=None):
    out, cy = [], y
    for ln in lines:
        if accent and accent in ln:
            pre, post = ln.split(accent, 1)
            out.append(f'<text x="{x}" y="{cy}" font-family="{FONT}" font-weight="{weight}" font-size="{size}" fill="{color}">{escape(pre)}<tspan fill="{RED}">{escape(accent)}</tspan>{escape(post)}</text>')
        else:
            out.append(f'<text x="{x}" y="{cy}" font-family="{FONT}" font-weight="{weight}" font-size="{size}" fill="{color}">{escape(ln)}</text>')
        cy += size * lh
    return "\n".join(out), cy

def chips(labels, x, y):
    out, cx = [], x
    for lab in labels:
        w = 34 + len(lab) * 15
        out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="46" rx="23" fill="none" stroke="{RED}" stroke-width="3"/>')
        out.append(f'<text x="{cx + w/2}" y="{y+31}" text-anchor="middle" font-family="{FONT}" font-weight="bold" font-size="22" fill="{WHITE}">{escape(lab)}</text>')
        cx += w + 14
    return "\n".join(out)

def slide(spec, idx, total):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="{BLACK}"/>',
             f'<rect x="0" y="0" width="{W}" height="14" fill="{RED}"/>']
    y = 150
    if spec.get("eyebrow"):
        parts.append(f'<text x="80" y="{y}" font-family="{FONT}" font-weight="bold" font-size="30" letter-spacing="4" fill="{RED}">{escape(spec["eyebrow"].upper())}</text>')
        y += 70
    hs = spec.get("headline_size", 74)
    hl = []
    for para in spec.get("headline", "").split("\n"):
        hl += wrap(para, int(920 / (hs * 0.64)))
    blk, y = text_block(hl, 80, y + hs, hs, accent=spec.get("accent"))
    parts.append(blk)
    y += 40
    if spec.get("bullets"):
        for b in spec["bullets"]:
            parts.append(f'<rect x="80" y="{y-6}" width="16" height="16" fill="{RED}"/>')
            bl = wrap(b, 44)
            blk, y2 = text_block(bl, 120, y + 8, 36, color=WHITE, weight="normal", lh=1.3)
            parts.append(blk)
            y = y2 + 22
    if spec.get("body"):
        bl = []
        for para in spec["body"].split("\n"):
            bl += wrap(para, 46) + [""]
        blk, y = text_block(bl, 80, y + 20, 36, color=GREY, weight="normal", lh=1.35)
        parts.append(blk)
    if spec.get("chips"):
        parts.append(chips(spec["chips"], 80, H - 330))
    if spec.get("cta"):
        parts.append(f'<rect x="80" y="{H-270}" width="{W-160}" height="96" rx="12" fill="{RED}"/>')
        parts.append(f'<text x="{W/2}" y="{H-208}" text-anchor="middle" font-family="{FONT}" font-weight="bold" font-size="38" fill="{WHITE}">{escape(spec["cta"])}</text>')
    # footer
    parts.append(f'<rect x="80" y="{H-130}" width="{W-160}" height="2" fill="#333"/>')
    parts.append(f'<text x="80" y="{H-72}" font-family="{FONT}" font-weight="bold" font-size="30" letter-spacing="3" fill="{WHITE}">HACKWITHZACH</text>')
    parts.append(f'<text x="{W-80}" y="{H-72}" text-anchor="end" font-family="{FONT}" font-weight="normal" font-size="28" fill="{GREY}">hackwithzach.com</text>')
    parts.append(f'<text x="{W-80}" y="{H-1250}" text-anchor="end" font-family="{FONT}" font-weight="bold" font-size="26" fill="{GREY}">{idx}/{total}</text>')
    if idx < total:
        parts.append(f'<text x="{W-80}" y="{H-150}" text-anchor="end" font-family="{FONT}" font-weight="bold" font-size="30" fill="{RED}">swipe</text>')
    parts.append("</svg>")
    return "\n".join(parts)

def main():
    spec = json.load(open(sys.argv[1]))
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    slides = spec["slides"]
    for i, s in enumerate(slides, 1):
        svg = slide(s, i, len(slides))
        path = os.path.join(outdir, f"{spec['slug']}-{i:02d}.png")
        cairosvg.svg2png(bytestring=svg.encode(), write_to=path, output_width=W, output_height=H)
        print(path)

if __name__ == "__main__":
    main()
