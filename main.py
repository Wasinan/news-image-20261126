#!/usr/bin/env python3
"""Render the 26 November 2026 front page as a 1024x1024 PNG.

Layout: masthead, one lead story with a line-art illustration,
then three shorter stories in columns. Pure PIL, deterministic:
no clocks, no randomness, same bytes on every run.
"""

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 44
CONTENT_W = PAGE - 2 * MARGIN

PAPER = (246, 241, 231)
INK = (25, 25, 25)
FADED = (92, 88, 80)
FLAME = (179, 49, 31)
EMBER = (224, 123, 36)
WATER = (43, 94, 167)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def face(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_width):
    """Split text into lines that each fit max_width pixels."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def block(draw, x, y, text, font, max_width, leading, fill=INK):
    """Draw a wrapped paragraph at (x, y); return the y below it."""
    for line in wrap(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def centered(draw, y, text, font, fill=INK):
    width = draw.textlength(text, font=font)
    draw.text(((PAGE - width) / 2, y), text, font=font, fill=fill)


def rule(draw, y, weight=2, x0=MARGIN, x1=PAGE - MARGIN):
    draw.line([(x0, y), (x1, y)], fill=INK, width=weight)


# ---------------------------------------------------------------------------
# Line-art illustrations. Each takes a bounding box (x0, y0, x1, y1).
# ---------------------------------------------------------------------------

def draw_tanker_fire(d, box):
    x0, y0, x1, y1 = box
    road = y1 - 26
    d.line([(x0, road), (x1, road)], fill=INK, width=3)
    for tick in range(int(x0) + 14, int(x1) - 10, 34):
        d.line([(tick, road + 8), (tick + 16, road + 8)], fill=FADED, width=2)

    tank_left = x0 + 18
    tank_right = x1 - 118
    tank_top = road - 92
    tank_bot = road - 34
    d.rounded_rectangle([tank_left, tank_top, tank_right, tank_bot],
                        radius=26, outline=INK, width=3)
    d.line([(tank_left + 40, tank_top + 10), (tank_left + 40, tank_bot - 10)],
           fill=FADED, width=2)
    d.line([(tank_right - 44, tank_top + 10), (tank_right - 44, tank_bot - 10)],
           fill=FADED, width=2)

    cab_x = tank_right + 8
    d.polygon([(cab_x, road - 30), (cab_x, road - 78), (cab_x + 34, road - 78),
               (cab_x + 58, road - 52), (cab_x + 58, road - 30)],
              outline=INK, width=3)
    d.line([(cab_x + 8, road - 70), (cab_x + 30, road - 70)], fill=INK, width=2)

    for cx in (tank_left + 36, tank_right - 40, cab_x + 34):
        d.ellipse([cx - 13, road - 13, cx + 13, road + 13], outline=INK, width=3)
        d.ellipse([cx - 4, road - 4, cx + 4, road + 4], outline=INK, width=2)

    flame_base = tank_top + 4
    tongues = [(tank_left + 30, 46), (tank_left + 78, 66), (tank_left + 126, 52),
               (tank_left + 172, 72), (tank_left + 216, 44)]
    for fx, fh in tongues:
        d.polygon([(fx - 15, flame_base), (fx, flame_base - fh),
                   (fx + 15, flame_base)], outline=FLAME, width=3)
        d.polygon([(fx - 7, flame_base), (fx, flame_base - fh * 0.55),
                   (fx + 7, flame_base)], outline=EMBER, width=2)

    for sx, sy, sr in ((tank_left + 60, y0 + 26, 15), (tank_left + 120, y0 + 14, 19),
                       (tank_left + 188, y0 + 24, 13)):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], outline=FADED, width=2)


def draw_missile(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    h = y1 - y0
    ground = y1 - 6
    d.line([(x0 + 14, ground), (x1 - 14, ground)], fill=INK, width=3)
    d.polygon([(cx - 40, ground), (cx + 40, ground), (cx + 22, ground - h * 0.14),
               (cx - 22, ground - h * 0.14)], outline=INK, width=3)

    nose = y0 + 4
    body_top = y0 + h * 0.30
    body_bot = y0 + h * 0.70
    d.polygon([(cx - 12, body_top), (cx, nose), (cx + 12, body_top)],
              outline=INK, width=3)
    d.rectangle([cx - 12, body_top, cx + 12, body_bot], outline=INK, width=3)
    band = body_top + (body_bot - body_top) * 0.35
    d.line([(cx - 12, band), (cx + 12, band)], fill=FADED, width=2)
    d.polygon([(cx - 12, body_bot - h * 0.18), (cx - 27, body_bot + 4),
               (cx - 12, body_bot + 4)], outline=INK, width=3)
    d.polygon([(cx + 12, body_bot - h * 0.18), (cx + 27, body_bot + 4),
               (cx + 12, body_bot + 4)], outline=INK, width=3)
    d.polygon([(cx - 7, body_bot + 6), (cx, ground - h * 0.16), (cx + 7, body_bot + 6)],
              outline=EMBER, width=2)


def draw_jet(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2 + 3
    s = (y1 - y0) / 92.0
    outline = [(0, -42), (9, -8), (52, 22), (52, 34), (10, 16), (12, 38),
               (24, 44), (0, 36), (-24, 44), (-12, 38), (-10, 16), (-52, 34),
               (-52, 22), (-9, -8)]
    d.polygon([(cx + dx * s, cy + dy * s) for dx, dy in outline],
              outline=INK, width=3)
    d.ellipse([cx - 5 * s, cy - 30 * s, cx + 5 * s, cy - 16 * s],
              outline=INK, width=2)

    bx, by = x1 - 28, y0 + 16
    for dx, dy in ((0, -11), (8, -8), (11, 0), (8, 8), (0, 11), (-8, 8), (-11, 0), (-8, -8)):
        d.line([(bx, by), (bx + dx, by + dy)], fill=FLAME, width=2)


def draw_mine(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    h = y1 - y0
    surface = y0 + h * 0.36
    d.line([(x0 + 10, surface), (x1 - 10, surface)], fill=INK, width=3)
    d.polygon([(cx - 28, surface), (cx, y0 + 3), (cx + 28, surface)],
              outline=INK, width=3)
    d.line([(cx, y0 + 3), (cx, surface + h * 0.30)], fill=FADED, width=2)
    d.rectangle([cx - 7, surface + h * 0.27, cx + 7, surface + h * 0.40],
                outline=INK, width=2)

    shaft_l, shaft_r = cx - 20, cx + 20
    shaft_bot = y1 - 6
    d.line([(shaft_l, surface), (shaft_l, shaft_bot)], fill=INK, width=3)
    d.line([(shaft_r, surface), (shaft_r, shaft_bot)], fill=INK, width=3)

    wave_y = shaft_bot - h * 0.20
    points = []
    steps = 24
    for i in range(steps + 1):
        px = x0 + 14 + (x1 - x0 - 28) * i / steps
        py = wave_y + (5 if i % 2 else -5)
        points.append((px, py))
    d.line(points, fill=WATER, width=3)
    d.line([(px, py + 10) for px, py in points], fill=WATER, width=2)


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def masthead(d):
    centered(d, 30, "THE WORLD TODAY", face(SERIF_BOLD, 60))
    centered(d, 104, "Thursday 26 November 2026", face(SANS, 19), fill=FADED)
    rule(d, 138, weight=4)
    rule(d, 146, weight=1)


def lead_story(d):
    y = 164
    d.text((MARGIN, y), "CAIRO  ·  AP / CNN", font=face(SANS_BOLD, 15), fill=FLAME)
    y += 26
    y = block(d, MARGIN, y,
              "Fuel Tanker Explodes on Cairo Ring Road, 31 Dead",
              face(SERIF_BOLD, 45), CONTENT_W, 52)
    y = block(d, MARGIN, y + 2,
              "An overturned tanker in Giza's Al-Warraq district ignites an "
              "inferno that swallows 27 vehicles; 21 injured as the health "
              "minister calls the toll preliminary.",
              face(SERIF, 20), CONTENT_W, 26, fill=FADED)
    y += 12

    art = (PAGE - MARGIN - 356, y, PAGE - MARGIN, y + 176)
    draw_tanker_fire(d, art)
    block(d, art[0], art[3] + 6,
          "A fuel tanker burns after overturning on the Ring Road in Al-Warraq.",
          face(SANS, 12), 356, 15, fill=FADED)

    col_w = 262
    left_end = block(
        d, MARGIN, y,
        "A fuel tanker overturned on the Ring Road in Giza's Al-Warraq "
        "district on Thursday and burst into flames, setting off an inferno "
        "that engulfed 27 vehicles caught in traffic around it.",
        face(SERIF, 16), col_w, 21)
    right_end = block(
        d, MARGIN + col_w + 22, y,
        "Health Minister Khaled Abdel Ghaffar said 31 people were killed "
        "and 21 injured, warning the toll was preliminary as crews worked "
        "through the wreckage. The blaze shut one of the capital's busiest "
        "arteries for hours.",
        face(SERIF, 16), col_w, 21)
    return max(left_end, right_end, art[3] + 36)


def side_story(d, x, top, width, tag, headline, body, art_fn):
    art_fn(d, (x + 60, top, x + width - 60, top + 74))
    y = top + 86
    d.text((x, y), tag, font=face(SANS_BOLD, 12), fill=FLAME)
    y += 19
    y = block(d, x, y, headline, face(SERIF_BOLD, 22), width, 26)
    y += 3
    block(d, x, y, body, face(SERIF, 15), width, 19)


def main():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)

    masthead(d)
    bottom = lead_story(d)

    divider = bottom + 14
    rule(d, divider, weight=2)

    col_top = divider + 18
    gap = 26
    col_w = (CONTENT_W - 2 * gap) // 3
    xs = [MARGIN + i * (col_w + gap) for i in range(3)]

    side_story(
        d, xs[0], col_top, col_w, "SEOUL  ·  REUTERS",
        "Kim Orders Wider Tactical Nuclear Deployment",
        "Kim Jong Un inspected nuclear facilities on Wednesday and ordered "
        "tactical nuclear weapons deployed \"across multiple domains\", "
        "KCNA reported Thursday. \"Our nuclear capability is now a "
        "reality,\" Kim said, signalling a wider battlefield role.",
        draw_missile)
    side_story(
        d, xs[1], col_top, col_w, "REUTERS",
        "Ukraine Hits Russian Air Base, Five Jets Damaged",
        "Ukrainian drones struck the Savasleyka air base in Nizhny "
        "Novgorod, knocking out three MiG-31 interceptors that carry "
        "Kinzhal missiles and two Su-34 fighter-bombers. Fifth strike on "
        "the airfield since August 2024; Russia has not commented.",
        draw_jet)
    side_story(
        d, xs[2], col_top, col_w, "JAKARTA  ·  AP",
        "Nine Dead, 17 Trapped in Flooded Gold Mine",
        "Nine miners died and 17 remained trapped after the Ciseureuh "
        "River overflowed into a 100-metre shaft at an unauthorized gold "
        "mine in Bogor, West Java. Some 325 rescuers pumped water from "
        "the flooded pit near PT Antam's Pongkor unit.",
        draw_mine)

    rule(d, PAGE - 58, weight=1)
    centered(d, PAGE - 48,
             "Compiled from AP, CNN and Reuters reports  ·  Thursday 26 November 2026",
             face(SANS, 13), fill=FADED)

    img.save("news-image-20261126.png")


if __name__ == "__main__":
    main()
