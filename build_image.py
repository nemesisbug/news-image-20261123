#!/usr/bin/env python3
"""Draw the 23 November 2026 front page as a single 1024x1024 PNG.

Everything here is drawn from scratch with Pillow: masthead, lead story
with a cracked-globe panel, seven story cards, a schematic world map with
the day's datelines, a numbers strip, a WIB timeline and a date-check box.
No network, no clock reads, no randomness: the same input always renders
the same bytes.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

PAPER = (246, 241, 231)
INK = (22, 22, 28)
NAVY = (22, 38, 77)
NAVY_SOFT = (38, 58, 104)
GOLD = (198, 158, 74)
RED = (178, 34, 34)
RED_SOFT = (214, 90, 80)
CARD = (255, 255, 255)
RULE = (190, 182, 168)
MUTED = (96, 94, 88)
LAND = (148, 168, 188)
SEA = (232, 238, 242)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Split text into lines that fit width, measured with fnt."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, width, leading=None):
    """Draw wrapped text; return the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    x, y = xy
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, xy, text, color=RED, size=15):
    fnt = font(SANS_B, size)
    draw.text(xy, text, font=fnt, fill=color)
    return fnt


def draw_globe(draw, cx, cy, r):
    """A cream globe on navy, with a jagged red crack across it."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 232, 210),
                 outline=(240, 232, 210), width=2)
    # Latitude bands, drawn as arcs whose chord stays inside the disc.
    for dy, half in ((-r // 2, 0.86), (0, 1.0), (r // 2, 0.86)):
        wdt = int(r * half)
        draw.arc([cx - wdt, cy + dy - 10, cx + wdt, cy + dy + 10],
                 0, 360, fill=NAVY_SOFT, width=2)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(240, 232, 210),
                 width=3)
    # The crack: a zig-zag from the top of the disc to the bottom.
    crack = [(cx - 12, cy - r + 6), (cx + 8, cy - r // 2), (cx - 10, cy - 6),
             (cx + 12, cy + r // 3), (cx - 4, cy + r - 8)]
    draw.line(crack, fill=RED, width=5, joint="curve")
    for px, py in crack[1:-1]:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED)


def draw_stamp(base, cx, cy, angle=-16):
    """A tilted red NO DEAL stamp, drawn on its own layer."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fnt = font(SANS_B, 36)
    label = "NO DEAL"
    probe = ImageDraw.Draw(layer)
    tw = probe.textlength(label, font=fnt)
    pad_x, pad_y = 26, 12
    box_w, box_h = int(tw) + pad_x * 2, 44 + pad_y * 2
    stamp = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([3, 3, box_w - 3, box_h - 3], radius=8,
                         outline=(178, 34, 34, 235), width=5)
    sd.text((pad_x, pad_y + 2), label, font=fnt, fill=(178, 34, 34, 235))
    stamp = stamp.rotate(angle, expand=True, resample=Image.BICUBIC)
    layer.alpha_composite(stamp, (cx - stamp.width // 2,
                                  cy - stamp.height // 2))
    base.alpha_composite(layer)


def draw_card(draw, box, kick, head, deck, icon):
    """One story card: kicker, headline, deck, tiny drawn icon."""
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=6, fill=CARD, outline=RULE, width=1)
    draw.line([x0 + 12, y0 + 34, x1 - 12, y0 + 34], fill=RULE, width=1)
    kicker(draw, (x0 + 12, y0 + 10), kick, size=13)
    icon(draw, x1 - 44, y0 + 6, 26)
    hf = font(SERIF_B, 19)
    y = text_block(draw, (x0 + 12, y0 + 42), head, hf, INK, x1 - x0 - 24,
                   leading=23)
    df = font(SANS, 13)
    text_block(draw, (x0 + 12, y + 3), deck, df, MUTED, x1 - x0 - 24,
               leading=16)


def icon_robot(d, x, y, s):
    d.rounded_rectangle([x, y + s * 0.25, x + s, y + s * 0.8], radius=3,
                        outline=NAVY_SOFT, width=2)
    d.ellipse([x + s * 0.25, y + s * 0.4, x + s * 0.42, y + s * 0.57],
              fill=NAVY_SOFT)
    d.ellipse([x + s * 0.58, y + s * 0.4, x + s * 0.75, y + s * 0.57],
              fill=NAVY_SOFT)
    d.line([x + s * 0.5, y, x + s * 0.5, y + s * 0.25], fill=NAVY_SOFT,
           width=2)


def icon_flame(d, x, y, s):
    pts = [(x + s * 0.5, y), (x + s * 0.85, y + s * 0.55),
           (x + s * 0.65, y + s * 0.55), (x + s * 0.75, y + s * 0.8),
           (x + s * 0.5, y + s), (x + s * 0.25, y + s * 0.8),
           (x + s * 0.35, y + s * 0.55), (x + s * 0.15, y + s * 0.55)]
    d.polygon(pts, fill=RED_SOFT)


def icon_target(d, x, y, s):
    d.ellipse([x, y, x + s, y + s], outline=NAVY_SOFT, width=2)
    d.ellipse([x + s * 0.28, y + s * 0.28, x + s * 0.72, y + s * 0.72],
              fill=RED_SOFT)


def icon_bat(d, x, y, s):
    d.line([x + s * 0.2, y + s * 0.85, x + s * 0.75, y + s * 0.3],
           fill=NAVY_SOFT, width=4)
    d.ellipse([x + s * 0.55, y, x + s, y + s * 0.45], fill=RED_SOFT)


def icon_chart(d, x, y, s):
    d.line([x, y + s, x + s, y + s], fill=NAVY_SOFT, width=2)
    d.line([x, y + s, x + s, y], fill=NAVY_SOFT, width=2)
    pts = [(x + s * 0.1, y + s * 0.7), (x + s * 0.4, y + s * 0.45),
           (x + s * 0.6, y + s * 0.6), (x + s * 0.9, y + s * 0.15)]
    d.line(pts, fill=RED, width=3, joint="curve")


def icon_hat(d, x, y, s):
    d.pieslice([x, y + s * 0.15, x + s, y + s * 0.75], 180, 360,
               fill=NAVY_SOFT)
    d.rectangle([x - s * 0.08, y + s * 0.6, x + s * 1.08, y + s * 0.72],
                fill=NAVY_SOFT)


def icon_paw(d, x, y, s):
    d.ellipse([x + s * 0.28, y + s * 0.45, x + s * 0.72, y + s * 0.85],
              fill=NAVY_SOFT)
    for cx in (0.22, 0.5, 0.78):
        d.ellipse([x + s * (cx - 0.11), y + s * 0.08,
                   x + s * (cx + 0.11), y + s * 0.32], fill=NAVY_SOFT)


# Rough continent outlines as (lon, lat) polygons, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-75, 58), (-65, 60), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21), (-97, 26), (-105, 20), (-110, 23),
     (-115, 30), (-125, 40), (-125, 48), (-135, 58), (-155, 58),
     (-165, 60)],
    # South America
    [(-80, 10), (-75, 7), (-65, 10), (-55, 6), (-50, 0), (-45, -5),
     (-38, -8), (-35, -15), (-40, -22), (-48, -28), (-55, -35),
     (-62, -41), (-68, -50), (-70, -54), (-73, -45), (-73, -35),
     (-72, -20), (-78, -5)],
    # Africa
    [(-18, 15), (-15, 27), (-10, 31), (0, 36), (10, 37), (20, 32),
     (30, 31), (35, 28), (40, 20), (43, 12), (48, 11), (51, 12),
     (45, 0), (40, -10), (36, -18), (32, -28), (25, -34), (18, -34),
     (14, -22), (10, -5), (9, 4), (-8, 5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 55),
     (18, 56), (21, 59), (28, 60), (30, 65), (40, 68), (45, 68),
     (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (20, 40),
     (15, 44), (10, 44), (5, 43), (0, 39)],
    # Asia
    [(-10, 36), (10, 37), (20, 36), (30, 36), (36, 36), (40, 42),
     (45, 48), (50, 52), (55, 55), (60, 60), (70, 68), (80, 72),
     (95, 76), (110, 76), (125, 72), (140, 72), (160, 70), (178, 66),
     (170, 60), (160, 55), (150, 59), (140, 50), (135, 43), (128, 38),
     (122, 32), (115, 22), (108, 15), (105, 10), (100, 8), (97, 16),
     (92, 22), (88, 26), (80, 20), (77, 8), (72, 20), (66, 25),
     (60, 25), (55, 26), (50, 29), (45, 30), (40, 30), (35, 28)],
    # Australia
    [(114, -22), (118, -20), (124, -15), (130, -12), (136, -12),
     (142, -11), (146, -19), (150, -22), (153, -27), (150, -37),
     (146, -39), (140, -38), (135, -35), (130, -32), (124, -33),
     (118, -35), (114, -30)],
]


LAT_LO, LAT_HI = -60.0, 80.0


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 180.0) / 360.0 * w,
            y0 + (LAT_HI - lat) / (LAT_HI - LAT_LO) * h)


def draw_map(draw, box):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=6, fill=SEA, outline=RULE, width=1)
    draw.text((x0 + 12, y0 + 8), "WHERE IT HAPPENED", font=font(SANS_B, 13),
              fill=NAVY)
    mw, mh = x1 - x0 - 24, y1 - y0 - 34
    mx, my = x0 + 12, y0 + 28
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND)
    # (name, lon, lat, label dx, label dy) — offsets keep the clustered
    # European datelines from printing over each other.
    spots = [
        ("ANTALYA", 30.7, 36.9, -62, -16), ("KYIV", 30.5, 50.4, 8, -16),
        ("HORMUZ", 56.3, 26.5, 8, 8), ("ISTANBUL", 28.9, 41.0, -64, 2),
        ("WELLINGTON", 174.8, -41.3, -76, 8),
        ("MELBOURNE", 145.0, -37.8, -74, -15),
    ]
    sf = font(SANS_B, 9)
    for name, lon, lat, dx, dy in spots:
        px, py = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED,
                     outline=(255, 255, 255), width=1)
        draw.text((px + dx, py + dy), name, font=sf, fill=INK)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, W - 11, H - 11], outline=INK, width=2)

    # ---- Masthead ----
    draw.rectangle([28, 24, 996, 116], fill=NAVY)
    tf = font(SERIF_B, 46)
    title = "THE WORLD IN ONE IMAGE"
    tw = draw.textlength(title, font=tf)
    draw.text(((W - tw) / 2, 30), title, font=tf, fill=(255, 255, 255))
    sf = font(SANS_B, 16)
    sub = "MONDAY 23 NOVEMBER 2026  ·  THE DAY IN ONE PICTURE"
    sw = draw.textlength(sub, font=sf)
    draw.text(((W - sw) / 2, 84), sub, font=sf, fill=GOLD)

    # ---- Lead story ----
    draw.rounded_rectangle([28, 130, 996, 372], radius=6, fill=CARD,
                           outline=RULE, width=1)
    draw.rectangle([28, 130, 420, 372], fill=NAVY)
    draw_globe(draw, 224, 232, 78)
    cap = font(SANS, 13)
    draw.text((48, 330), "ANTALYA, TURKEY — THE LONGEST COP EVER",
              font=cap, fill=(200, 208, 224))
    kicker(draw, (448, 146), "CLIMATE  ·  COP31  ·  ANTALYA", size=14)
    hf = font(SERIF_B, 40)
    y = text_block(draw, (448, 168), "COP31 ends with\nno deal", hf, INK,
                   996 - 448 - 28, leading=42)
    df = font(SANS, 16)
    y = text_block(
        draw, (448, y + 6),
        "Talks collapse after the final text drops any mention of fossil "
        "fuels; the EU and Pacific islands refuse to sign.",
        df, INK, 996 - 448 - 28, leading=19)
    qf = font(SERIF, 17)
    y = text_block(draw, (448, y + 8),
                   "\u201cDifficult geopolitical times.\u201d\n"
                   "\u2014 Anthony Albanese, Australian PM, in Canberra",
                   qf, MUTED, 996 - 448 - 28, leading=20)
    gf = font(SANS, 13)
    draw.text((448, 354), "UN chief Ant\u00f3nio Guterres: \u201cdeeply "
              "disappointed\u201d.", font=gf, fill=MUTED)

    # ---- Story grid: 7 cards + verdict ----
    cards = [
        ("UNITED NATIONS", "Robot talks get\ntwo more years",
         "UN states keep negotiating limits on autonomous weapons.",
         icon_robot),
        ("ENERGY", "Tankers ablaze\nin Hormuz",
         "Fires burn aboard tankers in the busiest oil chokepoint.",
         icon_flame),
        ("UKRAINE", "14 missing after\nKyiv drone strike",
         "Rescuers search the rubble after a strike on the capital.",
         icon_target),
        ("SPORT", "India pile up a\nrecord 720/9d",
         "A record total in Wellington leaves the hosts chasing.",
         icon_bat),
        ("TECH", "Anthropic options\nbegin trading",
         "Options on the AI firm\u2019s shares debut, days after its "
         "listing.", icon_chart),
        ("OBITUARY", "Molly Meldrum\ndies at 83",
         "Countdown legend, 83, dies at 5:30am in Melbourne.",
         icon_hat),
        ("TURKEY", "A lion loose\nin Istanbul",
         "An escaped lion is spotted roaming the streets of the city.",
         icon_paw),
    ]
    gx, gy = 28, 386
    cw, ch, gap = 232, 136, 8
    for i, (kick, head, deck, ic) in enumerate(cards):
        cx = gx + (i % 4) * (cw + gap)
        cy = gy + (i // 4) * (ch + gap)
        draw_card(draw, (cx, cy, cx + cw, cy + ch), kick, head, deck, ic)
    # Verdict cell, last slot of the grid.
    vx = gx + 3 * (cw + gap)
    vy = gy + 1 * (ch + gap)
    draw.rounded_rectangle([vx, vy, vx + cw, vy + ch], radius=6, fill=NAVY,
                           outline=NAVY, width=1)
    draw.text((vx + 12, vy + 10), "THE VERDICT", font=font(SANS_B, 13),
              fill=GOLD)
    text_block(draw, (vx + 12, vy + 36),
               "A Monday of endings: a summit collapses, a music legend "
               "falls silent, and the world keeps score.",
               font(SERIF, 15), (255, 255, 255), cw - 24, leading=19)

    # ---- Map + numbers ----
    draw_map(draw, (28, 678, 660, 830))
    draw.rounded_rectangle([672, 678, 996, 830], radius=6, fill=CARD,
                           outline=RULE, width=1)
    draw.text((688, 688), "BY THE NUMBERS", font=font(SANS_B, 13), fill=NAVY)
    numbers = [
        ("720/9d", "India\u2019s record total"),
        ("14", "missing in Kyiv"),
        ("2 yrs", "robot talks extended"),
        ("83", "Meldrum\u2019s age"),
        ("1.5\u00b0C", "the limit at stake"),
    ]
    ny = 712
    for big, small in numbers:
        draw.text((688, ny), big, font=font(SERIF_B, 19), fill=RED)
        draw.text((800, ny + 4), small, font=font(SANS, 13), fill=MUTED)
        ny += 24

    # ---- WIB timeline ----
    draw.rounded_rectangle([28, 844, 996, 928], radius=6, fill=CARD,
                           outline=RULE, width=1)
    draw.text((44, 854), "MONDAY IN WIB", font=font(SANS_B, 13), fill=NAVY)
    draw.line([60, 896, 964, 896], fill=RULE, width=2)
    stops = [
        ("01:30", "Molly Meldrum dies\nin Melbourne (05:30 local)"),
        ("MORNING", "COP31 failure confirmed; Albanese: \u201cdifficult geopolitical times\u201d"),
        ("MIDDAY", "UN extends killer-robot\ntalks by two more years"),
        ("EVENING", "India declare on 720/9d\nin Wellington"),
    ]
    sx = 120
    for label, note in stops:
        draw.ellipse([sx - 6, 890, sx + 6, 902], fill=RED,
                     outline=(255, 255, 255), width=1)
        draw.text((sx - 40, 868), label, font=font(SANS_B, 13), fill=INK)
        nf = font(SANS, 10)
        text_block(draw, (sx - 40, 900), note, nf, MUTED, 230, leading=12)
        sx += 240

    # ---- Date check + footer ----
    draw.rounded_rectangle([28, 938, 996, 1000], radius=6, fill=(238, 232,
                                                                 216),
                           outline=RULE, width=1)
    draw.text((44, 948), "DATE CHECK — LEFT OUT ON PURPOSE:",
              font=font(SANS_B, 12), fill=NAVY)
    src = "SOURCES: AFP · BBC · REUTERS · AP · NPR · THE HINDU · JAGRAN JOSH"
    sw = draw.textlength(src, font=font(SANS_B, 10))
    draw.text((996 - 16 - sw, 950), src, font=font(SANS_B, 10), fill=MUTED)
    text_block(draw, (44, 966),
               "El Chapo \u201cIsidro\u201d (20 Nov) · Anthropic IPO "
               "(19 Nov) · Serang fire (21 Nov). COP31 collapsed late "
               "Sunday; Monday carries the fallout.",
               font(SANS, 12), MUTED, 940, leading=14)

    # The tilted stamp goes on last, over the lead panel.
    base = img.convert("RGBA")
    draw_stamp(base, 290, 245)
    base.convert("RGB").save(OUT_PATH, optimize=True)
    print("wrote", OUT_PATH)


if __name__ == "__main__":
    main()
