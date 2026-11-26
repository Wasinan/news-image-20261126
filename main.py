#!/usr/bin/env python3
"""Build one 1024x1024 newspaper front page summing up 26 Nov 2026.

Renders the four verified stories of the day with PIL only: a masthead,
a full-width lead panel and three columns below it. Run it and it writes
news-image-20261126.png next to this script.
"""

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT_NAME = "news-image-20261126.png"

CANVAS = 1024
MARGIN = 36
PAPER = (245, 239, 224)
PANEL = (255, 253, 245)
INK = (26, 26, 26)
SOFT = (74, 74, 66)
RULE = (26, 26, 26)
RED = (178, 28, 28)
BLUE = (30, 58, 95)
GOLD = (176, 132, 30)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def pick(size, bold=False, serif=False):
    name = "DejaVuSerif-Bold.ttf" if serif else (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    )
    return ImageFont.truetype(str(FONT_DIR / name), size)


def wrap(draw, text, font, width):
    """Greedy word wrap measured with the real font."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=font) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def block(draw, xy, text, font, width, fill=INK, gap=6):
    """Draw wrapped text, return the y just below the last line."""
    x, y = xy
    for line in wrap(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + gap
    return y


def fit_block(draw, xy, text, size, width, max_bottom, fill=SOFT, gap=4):
    """Draw body text shrunk until it fits above max_bottom.

    Drops the font size step by step; as a last resort trims the text
    with an ellipsis so nothing ever spills past the panel edge.
    """
    x, y = xy
    while size >= 13:
        font = pick(size)
        lines = wrap(draw, text, font, width)
        if y + len(lines) * (size + gap) <= max_bottom:
            for line in lines:
                draw.text((x, y), line, font=font, fill=fill)
                y += size + gap
            return y
        size -= 1
    font = pick(13)
    lines = wrap(draw, text, font, width)
    room = max(1, (max_bottom - y) // (13 + gap))
    for line in lines[:room]:
        draw.text((x, y), line, font=font, fill=fill)
        y += 13 + gap
    if len(lines) > room and room > 0:
        draw.text((x, y - 13 - gap), lines[room - 1].rstrip(". ") + "…",
                  font=font, fill=fill)
    return y


def headline_fit(draw, text, font_size, width, bold=True):
    """Largest bold font (<= font_size) that wraps the headline in 3 lines."""
    size = font_size
    while size > 18:
        font = pick(size, bold=bold)
        if len(wrap(draw, text, font, width)) <= 3:
            return font
        size -= 2
    return pick(18, bold=bold)


def tanker(draw, x, y, width, height):
    """Overturned fuel tanker silhouette with a flame above the tank."""
    base = y + height
    # Tank body lying on its side.
    draw.rounded_rectangle(
        [x + 8, base - 44, x + width - 30, base - 14],
        radius=14, fill=INK,
    )
    # Cab crushed against the tank.
    draw.rectangle([x + width - 28, base - 30, x + width - 4, base - 8],
                   fill=INK)
    # Wheels off the ground line.
    draw.ellipse([x + 22, base - 14, x + 38, base + 2], fill=INK)
    draw.ellipse([x + width - 58, base - 14, x + width - 42, base + 2],
                 fill=INK)
    draw.line([x, base + 4, x + width, base + 4], fill=INK, width=2)
    # Flame above the tank.
    fx = x + width // 2 - 10
    flame = [
        (fx - 16, base - 44), (fx - 9, base - 72), (fx - 2, base - 58),
        (fx + 5, base - 84), (fx + 12, base - 62), (fx + 16, base - 44),
    ]
    draw.polygon(flame, fill=RED)
    inner = [
        (fx - 7, base - 46), (fx - 3, base - 62), (fx + 3, base - 54),
        (fx + 7, base - 46),
    ]
    draw.polygon(inner, fill=GOLD)
    # Smoke puffs drifting right.
    for sx, sy, r in ((width - 24, -78, 7), (width - 8, -92, 9)):
        draw.ellipse([x + sx - r, base + sy - r, x + sx + r, base + sy + r],
                     fill=SOFT)


def missile(draw, cx, cy, scale):
    """Short-range missile with fins and an exhaust plume."""
    s = scale
    body = [
        (cx, cy - 50 * s),
        (cx + 13 * s, cy - 18 * s),
        (cx + 13 * s, cy + 22 * s),
        (cx - 13 * s, cy + 22 * s),
        (cx - 13 * s, cy - 18 * s),
    ]
    draw.polygon(body, fill=INK)
    # Fins.
    draw.polygon([
        (cx - 13 * s, cy + 6 * s), (cx - 30 * s, cy + 28 * s),
        (cx - 13 * s, cy + 22 * s),
    ], fill=RED)
    draw.polygon([
        (cx + 13 * s, cy + 6 * s), (cx + 30 * s, cy + 28 * s),
        (cx + 13 * s, cy + 22 * s),
    ], fill=RED)
    # Warhead band.
    draw.rectangle([cx - 13 * s, cy - 20 * s, cx + 13 * s, cy - 12 * s],
                   fill=GOLD)
    # Exhaust plume.
    draw.polygon([
        (cx - 8 * s, cy + 22 * s), (cx, cy + 46 * s), (cx + 8 * s, cy + 22 * s),
    ], fill=RED)
    draw.polygon([
        (cx - 4 * s, cy + 22 * s), (cx, cy + 36 * s), (cx + 4 * s, cy + 22 * s),
    ], fill=GOLD)


def jet(draw, cx, cy, scale):
    """Fighter jet seen from above, with a burst beside it."""
    s = scale
    # Fuselage and nose.
    draw.polygon([
        (cx, cy - 46 * s),
        (cx + 10 * s, cy - 6 * s),
        (cx + 10 * s, cy + 30 * s),
        (cx - 10 * s, cy + 30 * s),
        (cx - 10 * s, cy - 6 * s),
    ], fill=INK)
    # Swept wings.
    draw.polygon([
        (cx - 10 * s, cy + 2 * s), (cx - 42 * s, cy + 26 * s),
        (cx - 42 * s, cy + 34 * s), (cx - 10 * s, cy + 24 * s),
    ], fill=INK)
    draw.polygon([
        (cx + 10 * s, cy + 2 * s), (cx + 42 * s, cy + 26 * s),
        (cx + 42 * s, cy + 34 * s), (cx + 10 * s, cy + 24 * s),
    ], fill=INK)
    # Tail fins.
    draw.polygon([
        (cx - 10 * s, cy + 26 * s), (cx - 22 * s, cy + 42 * s),
        (cx - 10 * s, cy + 36 * s),
    ], fill=INK)
    draw.polygon([
        (cx + 10 * s, cy + 26 * s), (cx + 22 * s, cy + 42 * s),
        (cx + 10 * s, cy + 36 * s),
    ], fill=INK)
    # Canopy.
    draw.ellipse([cx - 5 * s, cy - 34 * s, cx + 5 * s, cy - 16 * s],
                 fill=BLUE)
    # Burst star top-right.
    bx, by = cx + 40 * s, cy - 34 * s
    burst = []
    for i in range(8):
        ang = i * 3.14159 / 4
        r = (14 if i % 2 == 0 else 6) * s
        burst.append((bx + r * (1 if i in (0, 1, 7) else -1 if i in (3, 4, 5)
                             else 0),
                      by + r * (1 if i in (1, 2, 3) else -1 if i in (5, 6, 7)
                                else 0)))
    draw.polygon(burst, fill=RED)


def mine_shaft(draw, x, y, width, height):
    """Mine headframe over a flooded shaft."""
    base = y + height
    cx = x + width // 2
    # Headframe legs.
    draw.line([cx - 34, base, cx, y + 8], fill=INK, width=5)
    draw.line([cx + 34, base, cx, y + 8], fill=INK, width=5)
    draw.line([cx - 20, base - 22, cx + 20, base - 22], fill=INK, width=3)
    # Pulley wheel.
    draw.ellipse([cx - 8, y + 2, cx + 8, y + 18], outline=INK, width=3)
    # Cable down to the cage.
    draw.line([cx, y + 18, cx, base - 26], fill=INK, width=2)
    draw.rectangle([cx - 12, base - 26, cx + 12, base - 8], outline=INK,
                   width=3)
    # Flood water at the bottom.
    draw.rectangle([x + 6, base - 8, x + width - 6, base + 2], fill=BLUE)
    for wx in range(x + 14, x + width - 10, 18):
        draw.arc([wx, base - 12, wx + 14, base - 2], 180, 360, fill=BLUE,
                 width=2)


LEAD = {
    "kicker": "LEAD  ·  RING ROAD INFERNO",
    "title": "Fuel tanker explodes on Cairo ring road, 31 dead",
    "body": (
        "A tanker truck carrying petroleum products overturned on the Ring "
        "Road in Giza's Al-Warraq district on Wednesday night and burst "
        "into flames, killing at least 31 people and injuring 21, Egyptian "
        "authorities said. The fire, which broke out above Tunnel 10, "
        "engulfed 27 vehicles on the highway encircling Cairo. Health "
        "Minister Khaled Abdel Ghaffar called the toll preliminary and "
        "warned it could rise. The Petroleum Ministry said the privately "
        "operated tanker swerved off the road before exploding, about "
        "eight miles from the Pyramids of Giza. The road has since reopened."
    ),
}

COLUMNS = [
    {
        "kicker": "NORTH KOREA  ·  NUCLEAR PUSH",
        "title": "Kim orders wider tactical nuclear deployment",
        "body": (
            "Kim Jong Un inspected nuclear material production and weapons "
            "research facilities on Wednesday and said North Korea should "
            "focus on deploying tactical nuclear weapons across multiple "
            "domains, KCNA reported Thursday. 'Our nuclear capability is "
            "now a reality,' he said."
        ),
        "art": "missile",
    },
    {
        "kicker": "UKRAINE WAR  ·  DEEP STRIKE",
        "title": "Ukraine hits Russian air base, five jets damaged",
        "body": (
            "Ukrainian forces struck the Savasleyka air base in Russia's "
            "Nizhny Novgorod region, knocking out three MiG-31 jets that "
            "launch Kinzhal hypersonic missiles and two Su-34 "
            "fighter-bombers, Kyiv's General Staff said. It was the fifth "
            "strike on the airfield since August 2024. Russia did not "
            "comment."
        ),
        "art": "jet",
    },
    {
        "kicker": "INDONESIA  ·  MINE FLOOD",
        "title": "Nine dead, 17 trapped in flooded gold mine",
        "body": (
            "Rescuers recovered nine bodies from an unauthorized gold "
            "mine in Bogor, West Java, after the Ciseureuh River "
            "overflowed into a 100-metre shaft late Monday. Seventeen "
            "miners are still believed trapped; 325 rescuers are pumping "
            "water from the shafts near PT Antam's Pongkor unit."
        ),
        "art": "mine",
    },
]


def paint():
    img = Image.new("RGB", (CANVAS, CANVAS), PAPER)
    draw = ImageDraw.Draw(img)

    # Double outer frame.
    draw.rectangle([10, 10, CANVAS - 11, CANVAS - 11], outline=RULE, width=3)
    draw.rectangle([20, 20, CANVAS - 21, CANVAS - 21], outline=RULE, width=1)

    # Masthead.
    title_font = pick(58, serif=True)
    title = "THE WORLD IN ONE PAGE"
    tw = draw.textlength(title, font=title_font)
    draw.text(((CANVAS - tw) / 2, 34), title, font=title_font, fill=INK)
    draw.line([MARGIN, 118, CANVAS - MARGIN, 118], fill=RULE, width=3)
    date_font = pick(20, bold=True)
    dateline = "THURSDAY, 26 NOVEMBER 2026  ·  FOUR STORIES THAT MATTER"
    dw = draw.textlength(dateline, font=date_font)
    draw.text(((CANVAS - dw) / 2, 130), dateline, font=date_font, fill=RED)
    draw.line([MARGIN, 164, CANVAS - MARGIN, 164], fill=RULE, width=1)

    # Lead panel.
    lead_top, lead_bottom = 180, 528
    draw.rectangle(
        [MARGIN, lead_top, CANVAS - MARGIN, lead_bottom], fill=PANEL,
        outline=RULE, width=2
    )
    kick_font = pick(20, bold=True)
    draw.text((MARGIN + 22, lead_top + 16), LEAD["kicker"], font=kick_font,
              fill=RED)
    head_font = headline_fit(draw, LEAD["title"], 46, 680)
    y = block(
        draw,
        (MARGIN + 22, lead_top + 48),
        LEAD["title"],
        head_font,
        680,
        gap=2,
    )
    fit_block(draw, (MARGIN + 22, y + 10), LEAD["body"], 20, 680,
              lead_bottom - 16, gap=5)
    tanker(draw, 782, 330, 150, 92)
    cap_font = pick(15)
    caption = "AL-WARRAQ, GIZA, EGYPT"
    cw = draw.textlength(caption, font=cap_font)
    draw.text((852 - cw / 2, 440), caption, font=cap_font, fill=SOFT)

    # Divider between lead and columns.
    draw.line([MARGIN, 548, CANVAS - MARGIN, 548], fill=RULE, width=2)

    # Three columns.
    col_w = 300
    gap_x = 26
    col_top = 566
    col_bottom = 946
    for i, col in enumerate(COLUMNS):
        x0 = MARGIN + i * (col_w + gap_x)
        draw.rectangle([x0, col_top, x0 + col_w, col_bottom], fill=PANEL,
                       outline=RULE, width=2)
        inner = x0 + 18
        width = col_w - 36
        if col["art"] == "missile":
            missile(draw, x0 + col_w // 2, col_top + 52, 0.85)
        elif col["art"] == "jet":
            jet(draw, x0 + col_w // 2, col_top + 52, 0.85)
        else:
            mine_shaft(draw, inner + 30, col_top + 14, width - 60, 72)
        cy = col_top + 96
        ksize = 16
        while ksize > 11 and draw.textlength(
            col["kicker"], font=pick(ksize, bold=True)
        ) > width:
            ksize -= 1
        draw.text((inner, cy), col["kicker"], font=pick(ksize, bold=True),
                  fill=RED)
        cy += 28
        hfont = headline_fit(draw, col["title"], 27, width)
        cy = block(draw, (inner, cy), col["title"], hfont, width, gap=2)
        fit_block(draw, (inner, cy + 10), col["body"], 18, width,
                  col_bottom - 14, gap=4)

    # Footer.
    foot_font = pick(15)
    foot = "Sources: AP · Reuters · CNN  —  26 Nov 2026"
    fw = draw.textlength(foot, font=foot_font)
    draw.text(((CANVAS - fw) / 2, 964), foot, font=foot_font, fill=SOFT)

    out = HERE / OUT_NAME
    img.save(out, "PNG")
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"wrote {out} ({img.size[0]}x{img.size[1]})")
    print(f"sha256 {digest}")
    return out


if __name__ == "__main__":
    paint()
