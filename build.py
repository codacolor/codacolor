#!/usr/bin/env python3
"""Build the codacolor GitHub profile README cards (dark + light SVG).

ASCII art of the Codacolor mark on the left, a neofetch-style panel on the right.
Run: python3 build.py   ->  writes dark_mode.svg, light_mode.svg next to this file.
"""
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

HERE = Path(__file__).parent
MARK = HERE / "mark.png"  # copy of Studio/brand/codacolor-design-system/assets/logos/mark.png

ART_COLS = 40          # width of the ASCII mark in characters
CHAR_ASPECT = 0.5      # monospace cell is ~2x taller than wide
RAMP = " .:-=+*%#@"    # coverage -> character, light to dense
PANEL_WIDTH = 58       # characters per panel line
FOUNDED = date(2016, 9, 10)  # Cody's chosen start date [Cody, 2026-10-09]

PERIWINKLE = "#5375f6"
THEMES = {
    "dark": {"bg": "#0d1117", "art": PERIWINKLE, "key": PERIWINKLE, "val": "#c9d1d9", "dots": "#484f58"},
    "light": {"bg": "#ffffff", "art": PERIWINKLE, "key": PERIWINKLE, "val": "#24292f", "dots": "#c0c4ca"},
}


def ascii_mark():
    im = Image.open(MARK).convert("RGBA").getchannel("A")
    w, h = im.size
    rows = round(ART_COLS * (h / w) * CHAR_ASPECT)
    small = im.resize((ART_COLS, rows), Image.BOX)  # BOX = mean coverage per cell
    lines = []
    for y in range(rows):
        line = "".join(RAMP[min(len(RAMP) - 1, small.getpixel((x, y)) * len(RAMP) // 256)] for x in range(ART_COLS))
        lines.append(line.rstrip())
    return lines


def uptime():
    today = date.today()
    months = (today.year - FOUNDED.year) * 12 + today.month - FOUNDED.month
    days = today.day - FOUNDED.day
    if days < 0:
        months -= 1
        prev = date(today.year, today.month, 1).toordinal() - 1
        days += date.fromordinal(prev).day
    years, months = divmod(months, 12)
    parts = ([f"{years} years"] if years else []) + [f"{months} months", f"{days} days"]
    return ", ".join(parts)


# (key, value); key None = section header; ("", "") = blank line
PANEL = [
    (None, "cody@codacolor"),
    ("OS", "Codacolor OS"),
    ("Uptime", uptime()),
    ("Host", "Codacolor LLC, Oregon"),
    ("Kernel", "Photography Educator"),
    ("Shell", "YouTube, Newsletter, Studio"),
    ("", ""),
    ("Programs", "Photo Flow Method, Codacolor Studio"),
    ("Approach", "First principles photography"),
    ("Gear", "Light"),
    ("Mission", "Get you past the camera, into flow"),
    ("", ""),
    (None, "Contact"),
    ("Web", "codacolor.com"),
    ("Studio", "codacolor.studio"),
    ("Newsletter", "newsletter.codacolor.com"),
]


def panel_spans(key, val):
    """Return a list of (text, role) for one panel line."""
    if key is None:
        head = f"{val} "
        return [(head, "key"), ("-" * (PANEL_WIDTH - len(head)), "dots")]
    if key == "":
        return [("", "val")]
    label = f". {key}:"
    fill = PANEL_WIDTH - len(label) - len(val) - 2
    return [(". ", "dots"), (f"{key}:", "key"), (" " + "." * max(fill, 1) + " ", "dots"), (val, "val")]


def svg(theme):
    c = THEMES[theme]
    art = ascii_mark()
    lh, cw, pad = 20, 9.6, 30  # line height, char width at 16px mono, padding
    n = max(len(art), len(PANEL))
    art_top = (n - len(art)) // 2
    panel_top = (n - len(PANEL)) // 2
    panel_x = pad + (ART_COLS + 4) * cw
    width = round(panel_x + PANEL_WIDTH * cw + pad)
    height = n * lh + pad * 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'width="{width}px" height="{height}px" font-size="16px">',
        f'<rect width="{width}px" height="{height}px" fill="{c["bg"]}" rx="15"/>',
        f'<text x="{pad}" y="{pad}" fill="{c["art"]}" xml:space="preserve">',
    ]
    for i, line in enumerate(art):
        out.append(f'<tspan x="{pad}" y="{pad + (art_top + i + 1) * lh}">{escape(line)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{panel_x}" y="{pad}" xml:space="preserve">')
    for i, (key, val) in enumerate(PANEL):
        y = pad + (panel_top + i + 1) * lh
        spans = panel_spans(key, val)
        out.append(f'<tspan x="{panel_x:.1f}" y="{y}">' + "".join(
            f'<tspan fill="{c[role]}">{escape(t)}</tspan>' for t, role in spans) + "</tspan>")
    out.append("</text></svg>")
    return "\n".join(out)


if __name__ == "__main__":
    for theme in THEMES:
        (HERE / f"{theme}_mode.svg").write_text(svg(theme))
    print("\n".join(ascii_mark()))
