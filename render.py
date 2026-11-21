#!/usr/bin/env python3
"""Render the Republic of Talmer passport spread to entry.png.

Deterministic, no network, no external assets: every pixel is drawn with
Pillow primitives from the data below. Output: 1024x640 PNG, well under 1 MiB.

The country: the Republic of Talmer, a North Atlantic island republic with
no airport. Every arrival is by ferry. The passport carries the proof: an
open-water endorsement, bilingual Talmeri/English labels, an Aurelia visa
sticker limited to ferry ports, and a ferry travel history whose dates all
agree (no stamp predates the 02 JUN 2023 issue; every return to Talmer falls
inside the 15 MAR - 15 OCT open-water season; the Aurelia arrival falls
inside its visa validity). The MRZ check digits are computed, not typed.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 640
OUT = "entry.png"

PAPER = (246, 241, 228)
PAPER_DARK = (238, 231, 214)
INK = (26, 36, 51)
BLUE = (31, 58, 95)
BLUE_SOFT = (70, 98, 138)
RED = (163, 59, 46)
GREEN = (58, 107, 79)
STAMP_BLUE = (46, 90, 138)
GREY = (110, 108, 96)

FDIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FDIR + name, size)


SERIF = lambda s: font("DejaVuSerif.ttf", s)          # noqa: E731
SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)   # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)            # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)     # noqa: E731
MONO = lambda s: font("DejaVuSansMono.ttf", s)        # noqa: E731
MONO_B = lambda s: font("DejaVuSansMono-Bold.ttf", s)  # noqa: E731


def spaced(d, xy, text, fnt, fill, tracking=2):
    """Draw text with letter tracking (for small-caps headers)."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking
    return x


def center(d, cx, y, text, fnt, fill, tracking=0):
    if tracking:
        widths = [d.textlength(c, font=fnt) + tracking for c in text]
        total = sum(widths) - tracking
        x = cx - total / 2
        for ch in text:
            d.text((x, y), ch, font=fnt, fill=fill)
            x += d.textlength(ch, font=fnt) + tracking
    else:
        d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- MRZ
MRZ_VALUES = {c: (int(c) if c.isdigit() else (ord(c) - 55 if c.isalpha() else 0))
              for c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<"}
WEIGHTS = (7, 3, 1)


def mrz_check(s):
    return str(sum(MRZ_VALUES[c] * WEIGHTS[i % 3] for i, c in enumerate(s)) % 10)


def mrz_lines():
    line1 = "P<TLMSOLBERG<<ELIN<MARIT"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "TLM004821"
    birth, sex, expiry = "940314", "F", "330601"
    personal = "<" * 14
    line2 = (doc + mrz_check(doc) + "TLM" + birth + mrz_check(birth) + sex
             + expiry + mrz_check(expiry) + personal
             + mrz_check(personal))
    line2 = line2 + mrz_check(line2)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


# ---------------------------------------------------------------- arms
def draw_arms(d, cx, top, scale=1.0):
    """Coat of arms: shield, lighthouse over waves, one star."""
    w, h = int(46 * scale), int(54 * scale)
    x0, y0 = cx - w // 2, top
    pts = [(x0 + w // 2, y0 + h), (x0 + w, y0 + int(30 * scale)),
           (x0 + w, y0 + int(6 * scale)), (x0, y0 + int(6 * scale)),
           (x0, y0 + int(30 * scale))]
    d.polygon(pts, outline=BLUE, width=2)
    # star above the shield
    sx, sy, r = cx, y0 - 2, int(7 * scale)
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(star, fill=BLUE)
    # lighthouse
    lx0, lx1 = cx - int(5 * scale), cx + int(5 * scale)
    ly0, ly1 = y0 + int(14 * scale), y0 + int(38 * scale)
    d.rectangle([lx0, ly0, lx1, ly1], outline=BLUE, width=2)
    d.polygon([(lx0 - 1, ly0), (lx1 + 1, ly0), (cx, ly0 - int(7 * scale))],
              outline=BLUE, width=2)
    for dx, dy in ((-14, -4), (14, -4), (-16, 3), (16, 3)):
        d.line([(cx, ly0 - 4), (cx + dx, ly0 - 4 + dy)], fill=BLUE, width=1)
    # waves
    for j, wy in enumerate((int(42 * scale), int(47 * scale))):
        for k in range(3):
            ax = x0 + 6 + k * 12
            d.arc([ax, y0 + wy, ax + 12, y0 + wy + 8], 180, 360, fill=BLUE, width=1)


# ---------------------------------------------------------------- portrait
def draw_portrait(d, box):
    """Banknote-style engraved portrait of Elin Marit Solberg.

    Duotone line engraving, deliberately geometric: pale face, hatched
    shading, dark-blonde hair swept back, navy jacket. It is meant to read as
    an engraved portrait, not a photograph.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) // 2
    bg = (223, 231, 238)
    d.rectangle(box, fill=bg, outline=INK, width=2)
    d.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], outline=INK, width=1)
    # engraving hatch across the background
    for yy in range(y0 + 8, y1 - 6, 5):
        d.line([(x0 + 6, yy), (x1 - 6, yy)], fill=(196, 208, 220), width=1)

    skin = (236, 211, 176)
    skin_sh = (214, 182, 140)
    hair = (107, 90, 62)
    jacket = (44, 74, 107)

    # shoulders / jacket
    d.polygon([(x0 + 8, y1 - 5), (x1 - 8, y1 - 5), (x1 - 22, y1 - 42),
               (cx + 22, y1 - 52), (cx - 22, y1 - 52), (x0 + 22, y1 - 42)],
              fill=jacket)
    # white shirt V
    d.polygon([(cx - 13, y1 - 52), (cx + 13, y1 - 52), (cx, y1 - 22)],
              fill=(248, 246, 240))
    d.line([(cx - 13, y1 - 52), (cx, y1 - 22)], fill=INK, width=1)
    d.line([(cx + 13, y1 - 52), (cx, y1 - 22)], fill=INK, width=1)
    # jacket lapels
    d.line([(cx - 22, y1 - 52), (cx - 8, y1 - 20)], fill=(24, 48, 76), width=2)
    d.line([(cx + 22, y1 - 52), (cx + 8, y1 - 20)], fill=(24, 48, 76), width=2)

    # neck (short, set into the collar; top tucks under the chin)
    d.rectangle([cx - 11, y1 - 82, cx + 11, y1 - 50], fill=skin)
    d.line([(cx - 11, y1 - 82), (cx - 11, y1 - 50)], fill=skin_sh, width=2)
    d.line([(cx + 11, y1 - 82), (cx + 11, y1 - 50)], fill=skin_sh, width=2)

    # face: rounded shape, slightly longer than wide
    fx0, fy0, fx1, fy1 = cx - 29, y0 + 30, cx + 29, y0 + 114
    # hair first: a back mass the face overlaps, leaving a hair band
    d.ellipse([fx0 - 3, y0 + 16, fx1 + 3, y0 + 82], fill=hair)
    d.ellipse([fx0, fy0, fx1, fy1], fill=skin, outline=(120, 92, 66), width=1)
    # ears, flush to the face
    d.ellipse([fx0 - 3, y0 + 68, fx0 + 2, y0 + 82], fill=skin, outline=(120, 92, 66))
    d.ellipse([fx1 - 2, y0 + 68, fx1 + 3, y0 + 82], fill=skin, outline=(120, 92, 66))
    # soft shadow under the chin
    d.line([(cx - 12, fy1 - 2), (cx + 12, fy1 - 2)], fill=(206, 172, 132), width=1)
    # centre part line in the hair band
    d.line([(cx, y0 + 18), (cx, y0 + 32)], fill=(70, 58, 40), width=1)

    # brows, eyes, nose, mouth
    d.line([(cx - 19, y0 + 62), (cx - 7, y0 + 60)], fill=(70, 52, 36), width=2)
    d.line([(cx + 7, y0 + 60), (cx + 19, y0 + 62)], fill=(70, 52, 36), width=2)
    for ex in (cx - 13, cx + 13):
        d.line([(ex - 6, y0 + 68), (ex + 6, y0 + 68)], fill=(60, 44, 30), width=2)
        d.ellipse([ex - 2, y0 + 69, ex + 2, y0 + 74], fill=(58, 74, 92))
    d.line([(cx, y0 + 78), (cx - 2, y0 + 90)], fill=(150, 116, 84), width=1)
    d.line([(cx - 9, y0 + 102), (cx + 9, y0 + 102)], fill=(130, 88, 74), width=1)


# ---------------------------------------------------------------- stamps
def stamp_layer(country, port, kind, date, color, size=(218, 88)):
    """One ink stamp on its own layer, slightly rotated when pasted."""
    lay = Image.new("RGBA", (size[0] + 16, size[1] + 16), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle([4, 4, size[0] + 11, size[1] + 11], radius=10,
                         outline=color + (255,), width=3)
    dd.rounded_rectangle([8, 8, size[0] + 7, size[1] + 7], radius=7,
                         outline=color + (255,), width=1)
    cx = (size[0] + 16) // 2
    center(dd, cx, 12, country, SANS_B(13), color + (255,), tracking=1)
    center(dd, cx, 32, port, SANS(10), color + (255,), tracking=1)
    # ferry glyph: hull + cabin + waves
    fx = 26
    fy = 56
    dd.polygon([(fx, fy), (fx + 34, fy), (fx + 28, fy + 9), (fx + 6, fy + 9)],
               outline=color + (255,), width=2)
    dd.rectangle([fx + 11, fy - 9, fx + 23, fy], outline=color + (255,), width=2)
    dd.line([(fx - 2, fy + 14), (fx + 36, fy + 14)], fill=color + (255,), width=1)
    dd.line([(fx + 2, fy + 18), (fx + 32, fy + 18)], fill=color + (255,), width=1)
    center(dd, cx + 28, 48, kind, SANS_B(13), color + (255,), tracking=1)
    center(dd, cx + 28, 66, date, SANS_B(11), color + (255,))
    return lay


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), (58, 52, 44))  # desk shadow
    d = ImageDraw.Draw(img, "RGBA")

    # paper noise (seeded: deterministic)
    rnd = random.Random(20261121)
    noise = Image.new("RGB", (W, H), PAPER)
    nd = ImageDraw.Draw(noise)
    for _ in range(2600):
        x, y = rnd.randrange(W), rnd.randrange(H)
        v = rnd.choice((232, 240, 250, 244))
        nd.point((x, y), fill=(v, v - 4, v - 14))
    img.paste(noise, (0, 0))

    # two pages
    left = (10, 10, 508, 630)
    right = (516, 10, 1014, 630)
    for (x0, y0, x1, y1) in (left, right):
        d.rectangle([x0 + 3, y0 + 4, x1 + 3, y1 + 4], fill=(30, 26, 20, 160))
    for (x0, y0, x1, y1) in (left, right):
        d.rectangle([x0, y0, x1, y1], fill=PAPER, outline=(120, 110, 88), width=1)
        d.rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=BLUE, width=1)
    # gutter shadow
    d.rectangle([508, 10, 516, 630], fill=(0, 0, 0, 40))
    # faint guilloche: fine arcs in the page corners
    for (x0, y0, x1, y1) in (left, right):
        for r in range(30, 130, 12):
            d.arc([x1 - r, y1 - r, x1 + r, y1 + r], 180, 270,
                  fill=(190, 182, 158, 110), width=1)
            d.arc([x0 - r, y0 - r, x0 + r, y0 + r], 0, 90,
                  fill=(190, 182, 158, 110), width=1)

    d = ImageDraw.Draw(img)
    lx0, _, lx1, _ = left

    # ---------------- LEFT PAGE: data page ----------------
    draw_arms(d, (lx0 + lx1) // 2, 26, scale=0.9)
    center(d, (lx0 + lx1) // 2, 84, "REPUBLIC OF TALMER", SERIF_B(29), BLUE)
    center(d, (lx0 + lx1) // 2, 118, "L Ý Ð V E L D I Ð   T A L M E R E",
           SANS(10), BLUE_SOFT)
    d.line([(lx0 + 30, 140), (lx1 - 30, 140)], fill=BLUE, width=2)
    d.line([(lx0 + 30, 143), (lx1 - 30, 143)], fill=BLUE, width=1)
    center(d, (lx0 + lx1) // 2, 150, "PASSPORT  ·  PASSEPORT", SANS_B(11), INK,
           tracking=2)
    center(d, (lx0 + lx1) // 2, 168, "TYPE  P      CODE  TLM      No.  TLM 004 821 377",
           SANS(11), INK)

    # portrait + data columns
    draw_portrait(d, (lx0 + 26, 192, lx0 + 176, 382))
    dx = lx0 + 192
    rows = [
        ("SURNAME  /  ÆTTARNAMN", "SOLBERG"),
        ("GIVEN NAMES  /  FORNAFN", "ELIN MARIT"),
        ("NATIONALITY  /  ÞJÓÐERNI", "TALMERI"),
        ("DATE OF BIRTH  /  FÆÐINGARDAGUR", "14 MAR 1994"),
        ("PLACE OF BIRTH  /  FÆÐINGARSTAÐUR", "KIRKHAVEN, TALMER"),
        ("SEX  /  KYN", "F"),
        ("HEIGHT", "172 CM"),
    ]
    y = 196
    for label, value in rows:
        d.text((dx, y), label, font=SANS(8), fill=BLUE_SOFT)
        d.text((dx, y + 11), value, font=SANS_B(13), fill=INK)
        y += 27
    # signature under the portrait
    d.line([(lx0 + 26, 402), (lx0 + 176, 402)], fill=INK, width=1)
    d.text((lx0 + 26, 406), "Elin Marit Solberg", font=SERIF(14), fill=INK)
    d.text((lx0 + 26, 424), "HOLDER'S SIGNATURE / UNDIRSKRIFT",
           font=SANS(8), fill=GREY)

    # endorsement box
    ex0, ey0, ex1, ey1 = lx0 + 26, 448, lx1 - 26, 520
    d.rectangle([ex0, ey0, ex1, ey1], outline=RED, width=2)
    d.rectangle([ex0 + 3, ey0 + 3, ex1 - 3, ey1 - 3], outline=RED, width=1)
    d.text((ex0 + 10, ey0 + 6), "ENDORSEMENT  /  ÁRITUN", font=SANS_B(10), fill=RED)
    d.text((ex0 + 10, ey0 + 21),
           "VALID FOR SEA TRAVEL ONLY. TALMER HAS NO",
           font=SANS(10), fill=INK)
    d.text((ex0 + 10, ey0 + 34),
           "AIRPORT; ALL ARRIVALS BY FERRY. ENTRY",
           font=SANS(10), fill=INK)
    d.text((ex0 + 10, ey0 + 47),
           "15 MAR – 15 OCT; WINTER ENTRY BY",
           font=SANS(10), fill=INK)
    d.text((ex0 + 10, ey0 + 60),
           "ICEBREAKER PERMIT (FORM IB-7).",
           font=SANS(10), fill=INK)

    # issue block
    d.text((lx0 + 26, 530), "DATE OF ISSUE  02 JUN 2023",
           font=SANS_B(11), fill=INK)
    d.text((lx0 + 26, 547), "DATE OF EXPIRY  01 JUN 2033",
           font=SANS_B(11), fill=INK)
    d.text((lx0 + 26, 564), "AUTHORITY: MINISTRY OF THE INTERIOR, KIRKHAVEN",
           font=SANS(10), fill=INK)

    # MRZ
    l1, l2 = mrz_lines()
    d.text((lx0 + 26, 586), l1, font=MONO(13), fill=INK)
    d.text((lx0 + 26, 604), l2, font=MONO(13), fill=INK)

    # ---------------- RIGHT PAGE: visas & stamps ----------------
    rx0, _, rx1, _ = right
    center(d, (rx0 + rx1) // 2, 22, "VISAS  AND  STAMPS", SERIF_B(19), BLUE,
           tracking=2)
    center(d, (rx0 + rx1) // 2, 46, "VEGABRÉF  ·  ÁRITANIR", SANS(9), BLUE_SOFT)

    # Aurelia visa sticker
    vx0, vy0, vx1, vy1 = rx0 + 16, 66, rx1 - 16, 178
    d.rectangle([vx0, vy0, vx1, vy1], fill=(232, 238, 230),
                outline=GREEN, width=2)
    d.rectangle([vx0 + 4, vy0 + 4, vx1 - 4, vy1 - 4], outline=GREEN, width=1)
    d.text((vx0 + 12, vy0 + 8), "AURELIA — ENTRY VISA", font=SANS_B(13), fill=GREEN)
    d.text((vx0 + 12, vy0 + 28), "Issued 02 MAY 2026  ·  Valid 15 MAY – 15 JUN 2026",
           font=SANS(11), fill=INK)
    d.text((vx0 + 12, vy0 + 46), "Single entry  ·  Visa No. AU-2026-04117",
           font=SANS(11), fill=INK)
    d.text((vx0 + 12, vy0 + 64),
           "CONDITION: FERRY PORTS ONLY — LJOSUND",
           font=SANS_B(11), fill=GREEN)
    d.text((vx0 + 12, vy0 + 82), "Fee 25 AUR paid  ·  Port of Ljosund",
           font=SANS(11), fill=INK)
    # visa seal
    d.ellipse([vx1 - 66, vy0 + 10, vx1 - 14, vy0 + 62], outline=GREEN, width=2)
    d.ellipse([vx1 - 59, vy0 + 17, vx1 - 21, vy0 + 55], outline=GREEN, width=1)
    center(d, vx1 - 40, vy0 + 26, "AUR", SANS_B(10), GREEN)
    center(d, vx1 - 40, vy0 + 40, "★", SANS_B(10), GREEN)

    # stamps: 2 columns x 4 rows
    stamps = [
        ("TALMER", "KIRKHAVEN", "EXIT", "18 JUL 2023", RED, -2),
        ("AURELIA", "LJOSUND", "ENTRY", "19 JUL 2023", STAMP_BLUE, 2),
        ("AURELIA", "LJOSUND", "EXIT", "02 SEP 2023", STAMP_BLUE, -1),
        ("TALMER", "KIRKHAVEN", "ENTRY", "03 SEP 2023", RED, 1),
        ("OSTARA", "PORT VARDA", "ENTRY", "25 MAR 2024", GREEN, 2),
        ("TALMER", "KIRKHAVEN", "ENTRY", "03 APR 2024", RED, -2),
        ("AURELIA", "LJOSUND", "ENTRY", "15 MAY 2026", STAMP_BLUE, 1),
        ("TALMER", "KIRKHAVEN", "ENTRY", "29 MAY 2026", RED, -1),
    ]
    sw, sh = 218, 88
    gapx, gapy = 14, 8
    gx0, gy0 = rx0 + 16, 190
    for i, (country, port, kind, date, color, ang) in enumerate(stamps):
        col, row = i % 2, i // 2
        x = gx0 + col * (sw + gapx)
        y = gy0 + row * (sh + gapy)
        lay = stamp_layer(country, port, kind, date, color)
        lay = lay.rotate(ang, resample=Image.BICUBIC, expand=False)
        img.paste(lay, (x - 8, y - 8), lay)

    # fee stamp, bottom of the right page
    fy = 566
    d.rounded_rectangle([rx0 + 16, fy, rx1 - 16, fy + 44], radius=6,
                        outline=RED, width=2)
    center(d, (rx0 + rx1) // 2, fy + 6,
           "FEE PAID  40 TALM  ·  02 JUN 2023  ·  RECEIPT No. 88214",
           SANS_B(11), RED)
    center(d, (rx0 + rx1) // 2, fy + 24, "MINISTRY OF THE INTERIOR — KIRKHAVEN",
           SANS(9), RED)

    img.save(OUT, "PNG", optimize=True)
    import os
    print(f"wrote {OUT}: {img.size}, {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    build()
