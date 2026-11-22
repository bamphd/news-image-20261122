"""news-image-20261122: one day's world news in one 1024x1024 image.

Deterministic Pillow program. No network, no time, no randomness.
Reads MAKEFUN_OUTPUT_DIR (else /output if it exists, else ./out) and
VARIANT (A front page / B picture-led / C map-first; default A).
Run: python3 main.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
DATE_LINE = "SUNDAY 22 NOVEMBER 2026"

# (headline, place, continent) - every story reported on 22 Nov 2026.
STORIES = [
    ("Iran strikes US bases in Bahrain; two hurt", "Bahrain", "Asia"),
    ("COP31 talks run into overtime over fossil fuels", "Turkey", "Europe"),
    ("Russian drone hits Kyiv flat; 14 missing", "Kyiv, Ukraine", "Europe"),
    ("Missile hits Kryvyi Rih; boy, 7, killed, 60 hurt", "Kryvyi Rih, Ukraine", "Europe"),
    ("Mexico captures 'El Chapo Isidro'; 11 killed", "Sinaloa, Mexico", "N. America"),
    ("World Court: Myanmar guilty of Rohingya genocide", "The Hague", "Europe"),
    ("S&P 500 falls 3.7%, into correction", "New York", "N. America"),
    ("EU and Indonesia sign landmark trade deal", "Brussels", "Europe"),
    ("Candy factory fire in Banten; 3 dead, 36 missing", "Banten, Indonesia", "Asia"),
    ("Korea minister quits over AI exam cheating", "Seoul", "Asia"),
    ("FBI crime database hacked; Trump confirms", "Washington", "N. America"),
    ("BepiColombo enters orbit around Mercury", "Mercury", "Europe"),
    ("Trump-Xi-Putin summit fallout: 'friend' row", "Shenzhen, China", "Asia"),
    ("Houthis fire missiles at Saudi Arabia", "Riyadh", "Asia"),
    ("Nigeria boat capsizes; 24 mourners dead", "Bayelsa, Nigeria", "Africa"),
    ("Denmark expels Russian attache over plot", "Copenhagen", "Europe"),
    ("Israeli strikes continue in Gaza; aid truck hit", "Gaza City", "Asia"),
    ("Amazon nears $7.5B deal for AI start-up Decart", "Seattle", "N. America"),
    ("IBM unveils 520-qubit Nighthawk r3", "New York", "N. America"),
    ("GTA 6 makes $3.79B on launch day", "New York", "N. America"),
    ("Leeds stun Chelsea 4-1 at Stamford Bridge", "London", "Europe"),
    ("Verstappen wins Las Vegas Grand Prix", "Las Vegas", "N. America"),
    ("Ukraine hits Crimean Bridge; Kyiv defends strike", "Crimea", "Europe"),
    ("Drones hit Russia's Ust-Luga port", "Ust-Luga, Russia", "Europe"),
    ("EU proposes 1.78T budget; 100B for Ukraine", "Brussels", "Europe"),
    ("UK to build Ukrainian-designed drones", "London", "Europe"),
    ("Armenia opens 'Trump Highway' project", "Yerevan", "Asia"),
    ("Sudan: RSF accused of Blue Nile killings", "Blue Nile, Sudan", "Africa"),
    ("Bangladesh: Awami League homes torched", "Dhaka", "Asia"),
    ("Iraq: blast at Basra power plant probed", "Basra, Iraq", "Asia"),
    ("Myanmar rejects World Court ruling", "Naypyidaw", "Asia"),
    ("China-Japan ties sour over Taiwan, minerals", "Beijing / Tokyo", "Asia"),
    ("US edge over China at lowest since 2018", "Washington", "N. America"),
    ("Spain heads to 29 Nov vote; Vox rising", "Madrid", "Europe"),
    ("UK polls turn against Brexit", "London", "Europe"),
    ("G20 in Florida: 'top 20 leaders' expected", "Florida", "N. America"),
    ("West Bank arson hits five villages", "West Bank", "Asia"),
    ("Killer-robot talks extended to 2028", "Geneva", "Europe"),
    ("Cost-of-living protests spread in Europe", "Europe", "Europe"),
    ("Fiji quake M4.9; Alaska M1.6", "Fiji", "Oceania"),
    ("CRISPR therapy cuts bad cholesterol 52%", "United States", "N. America"),
    ("Bolsonaro in intensive care", "Brasilia", "S. America"),
    ("Pilotless air taxi carries passenger in Japan", "Yamanashi, Japan", "Asia"),
    ("Princess Kate: in remission from cancer", "London", "Europe"),
    ("Turkey takes over last big independent channel", "Istanbul", "Asia"),
    ("Kansas City Current win first NWSL title", "Kansas City", "N. America"),
    ("Alcaraz reaches ATP Finals final", "Turin", "Europe"),
    ("Phumzile Mlambo-Ngcuka dies at 71", "South Africa", "Africa"),
    ("Study may rewrite human family tree", "Melbourne", "Oceania"),
    ("Shuri Castle hall restored after fire", "Naha, Japan", "Asia"),
]

# (key, title, sub, tint) - 12 illustrated panels.
PANELS = [
    ("bahrain", "IRAN HITS US BASES", "Bahrain - 2 hurt", "#FDECEA"),
    ("cop31", "COP31 IN OVERTIME", "No fossil-fuel deal", "#E8F0E4"),
    ("kyiv", "KYIV FLAT HIT", "14 missing", "#FDECEA"),
    ("kryvyi", "MISSILE HITS HOMETOWN", "Boy, 7, killed", "#FDECEA"),
    ("sinaloa", "'EL CHAPO ISIDRO' HELD", "11 killed in raid", "#E9EEF5"),
    ("hague", "GENOCIDE VERDICT", "Myanmar guilty", "#E9EEF5"),
    ("markets", "STOCKS IN CORRECTION", "S&P -3.7%", "#FBF3DF"),
    ("mercury", "MERCURY ORBIT", "BepiColombo arrives", "#EAE6F5"),
    ("banten", "FACTORY FIRE", "3 dead, 36 missing", "#FDEFE3"),
    ("seoul", "MINISTER QUITS", "AI cheating row", "#E8EEF7"),
    ("fbi", "FBI DATABASE HACKED", "NCIC breach", "#E8EEF7"),
    ("vegas", "VERSTAPPEN WINS", "Las Vegas GP", "#E4F2EC"),
]

FIGURES = [
    ("-3.7%", "S&P 500"),
    ("-5.3%", "NASDAQ"),
    ("14", "MISSING IN KYIV"),
    ("60", "HURT IN KRYVYI RIH"),
    ("11", "KILLED IN SINALOA"),
    ("36", "MISSING IN BANTEN"),
    ("24", "DEAD IN NIGERIA"),
    ("$3.79B", "GTA 6 DAY ONE"),
]

# (lon, lat, numbered?) for the schematic map.
MAP_DOTS = [
    (50.5, 26.2, 1), (32.9, 39.9, 2), (30.5, 50.5, 3), (33.4, 47.9, 0),
    (-107.4, 25.6, 4), (4.3, 52.1, 5), (-74.0, 40.7, 6), (106.1, -6.2, 7),
    (127.0, 37.5, 0), (34.5, 31.5, 0), (46.7, 24.6, 0), (6.3, 4.9, 0),
    (12.6, 55.7, 0), (-47.9, -15.8, 0), (-0.1, 51.5, 0), (7.7, 45.1, 0),
    (-115.1, 36.2, 0), (178.0, -17.7, 0), (145.0, -37.8, 0), (127.7, 26.2, 0),
    (47.8, 30.5, 0), (90.4, 23.8, 0), (139.7, 35.7, 0), (6.1, 46.2, 0),
]

CONTINENTS = {
    "N. America": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
                   (-75, 62), (-60, 55), (-55, 47), (-65, 45), (-75, 35), (-80, 25),
                   (-90, 20), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
                   (-125, 48), (-140, 60), (-165, 60)],
    "S. America": [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-40, -10), (-35, -15),
                   (-40, -25), (-50, -35), (-60, -45), (-70, -55), (-75, -40),
                   (-75, -20), (-80, -5)],
    "Europe": [(-10, 36), (-5, 44), (0, 50), (5, 58), (10, 60), (20, 65),
               (30, 70), (40, 68), (30, 60), (25, 55), (20, 45), (15, 40),
               (10, 38), (0, 36)],
    "Africa": [(-18, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
               (35, 28), (40, 15), (48, 11), (51, 0), (40, -10), (35, -20),
               (30, -30), (20, -35), (15, -30), (12, -18), (8, 4), (-8, 5), (-15, 10)],
    "Asia": [(40, 70), (60, 72), (80, 73), (100, 76), (130, 72), (160, 70),
             (170, 66), (160, 60), (140, 55), (140, 40), (130, 35), (120, 25),
             (110, 10), (105, 0), (100, 8), (90, 15), (80, 8), (75, 20),
             (65, 25), (55, 25), (48, 30), (43, 38), (40, 45), (40, 60)],
    "Oceania": [(115, -20), (125, -15), (135, -12), (142, -10), (150, -20),
                (153, -28), (150, -37), (140, -38), (130, -32), (120, -30), (113, -22)],
}

PAPER = (244, 246, 248)
INK = (22, 35, 58)
RED = (180, 35, 24)
BLUE = (29, 78, 137)
GOLD = (176, 141, 26)
GREY = (90, 107, 124)
LINE = (199, 208, 218)
MAPLAND = (206, 219, 231)
MAPSEA = (234, 241, 247)

_FONTS = {}


def font(kind, size):
    key = (kind, size)
    if key in _FONTS:
        return _FONTS[key]
    cands = {
        "serif": ["/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
        "serif_b": ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
        "sans": ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
        "sans_b": ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    }[kind]
    f = None
    for p in cands:
        try:
            f = ImageFont.truetype(p, size)
            break
        except Exception:
            continue
    if f is None:
        f = ImageFont.load_default()
    _FONTS[key] = f
    return f


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def trunc(d, text, fnt, width):
    if d.textlength(text, font=fnt) <= width:
        return text
    while text and d.textlength(text + "...", font=fnt) > width:
        text = text.rsplit(" ", 1)[0] if " " in text else text[:-1]
    return text + "..."


def block(d, x, y, w, h, lines, fnt, fill, leading=None, align="left"):
    """Draw wrapped lines inside a box; fail loudly if they do not fit."""
    lh = leading or int(fnt.size * 1.25)
    assert len(lines) * lh <= h + 1, f"text overflow: {lines} in {h}px"
    for i, ln in enumerate(lines):
        if align == "center":
            tw = d.textlength(ln, font=fnt)
            d.text((x + (w - tw) / 2, y + i * lh), ln, font=fnt, fill=fill)
        else:
            d.text((x, y + i * lh), ln, font=fnt, fill=fill)
    return len(lines) * lh


def draw_masthead(d, y, h):
    kick = "SUNDAY  -  22 NOVEMBER 2026  -  50 STORIES  -  6 CONTINENTS"
    f_kick = font("sans_b", 13)
    tw = d.textlength(kick, font=f_kick)
    d.text(((W - tw) / 2, y + 8), kick, font=f_kick, fill=GREY)
    f_title = font("serif_b", 56)
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, y + 26), title, font=f_title, fill=INK)
    d.rectangle([24, y + h - 18, W - 24, y + h - 14], fill=RED)
    sub = "One day's world news, in one picture - from Bahrain to Brisbane."
    f_sub = font("serif", 14)
    tw = d.textlength(sub, font=f_sub)
    d.text(((W - tw) / 2, y + h - 12), sub, font=f_sub, fill=GREY)


def draw_hero_art(d, x, y, w, h):
    # Dusk sky over the Gulf: bands, sea, skyline, missile arcs, bursts.
    bands = [(16, 28, 52), (28, 48, 84), (48, 72, 110), (74, 96, 128)]
    bh = h * 0.62 / len(bands)
    for i, c in enumerate(bands):
        d.rectangle([x, y + i * bh, x + w, y + (i + 1) * bh + 1], fill=c)
    sea_y = y + h * 0.62
    d.rectangle([x, sea_y, x + w, y + h], fill=(24, 68, 104))
    d.rectangle([x, sea_y, x + w, sea_y + 2], fill=(120, 170, 210))
    # Skyline silhouettes.
    import math
    towers = [(0.02, 0.30), (0.10, 0.42), (0.18, 0.26), (0.26, 0.48), (0.36, 0.34),
              (0.46, 0.55), (0.56, 0.30), (0.66, 0.44), (0.76, 0.28), (0.86, 0.40)]
    for fx, fh in towers:
        tx = x + fx * w
        th = fh * (sea_y - y)
        d.rectangle([tx, sea_y - th, tx + w * 0.06, sea_y], fill=(10, 18, 34))
    # Missile arcs with glowing heads.
    for fx0, fy0, fx1, fy1 in [(0.08, 0.15, 0.42, 0.55), (0.30, 0.08, 0.62, 0.50),
                               (0.55, 0.18, 0.88, 0.58)]:
        pts = []
        for t in range(21):
            tt = t / 20
            px = x + (fx0 + (fx1 - fx0) * tt) * w
            py = y + (fy0 + (fy1 - fy0) * tt - 0.18 * math.sin(math.pi * tt)) * h
            pts.append((px, py))
        d.line(pts, fill=(255, 214, 130), width=3)
        hx, hy = pts[-1]
        d.ellipse([hx - 5, hy - 5, hx + 5, hy + 5], fill=(255, 236, 180))
    # Explosion bursts.
    for fx, fy, r in [(0.42, 0.55, 16), (0.62, 0.50, 13), (0.88, 0.58, 15)]:
        cx, cy = x + fx * w, y + fy * h
        for k in range(8):
            ang = k * math.pi / 4
            d.line([cx, cy, cx + r * math.cos(ang), cy + r * math.sin(ang)],
                   fill=(255, 170, 60), width=3)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 200, 90))
    # Sea reflection streaks.
    for fx in (0.42, 0.62, 0.88):
        d.line([x + fx * w, sea_y + 4, x + fx * w, sea_y + 18], fill=(255, 190, 90), width=2)


def draw_hero(d, x, y, w, h):
    art_w = int(w * 0.48)
    draw_hero_art(d, x, y, art_w, h)
    tx = x + art_w + 20
    tw = x + w - tx
    f_h = font("serif_b", 30 if h >= 170 else 26)
    lines = wrap(d, "IRAN STRIKES US BASES IN BAHRAIN", f_h, tw)
    used = block(d, tx, y + 2, tw, 78, lines, f_h, INK, leading=34)
    f_deck = font("sans", 14)
    deck = ("Missiles and drones hit American bases; a civilian plant was "
            "struck and two people hurt. Tehran claims two Patriot radars destroyed.")
    lines = wrap(d, deck, f_deck, tw)
    block(d, tx, y + 4 + used, tw, 60, lines, f_deck, (44, 58, 78), leading=18)
    f_s = font("sans_b", 14)
    sy = y + h - 44
    d.rectangle([tx, sy, tx + 10, sy + 10], fill=RED)
    block(d, tx + 18, sy - 2, tw - 18, 20,
          wrap(d, "COP31 talks run into overtime over fossil fuels", f_s, tw - 18),
          f_s, INK, leading=17)
    sy += 24
    d.rectangle([tx, sy, tx + 10, sy + 10], fill=BLUE)
    block(d, tx + 18, sy - 2, tw - 18, 20,
          wrap(d, "Russian drone hits Kyiv flat; 14 missing", f_s, tw - 18),
          f_s, INK, leading=17)


def draw_icon(d, key, x, y, w, h):
    cx, cy = x + w / 2, y + h / 2
    if key == "bahrain":
        d.ellipse([x + 6, y + 4, x + 26, y + 24], fill=(255, 200, 90))
        for a, b in [(0.2, 0.7), (0.45, 0.5), (0.7, 0.75)]:
            d.line([x + a * w, y + h * 0.15, x + b * w, y + h * 0.8],
                   fill=RED, width=2)
        d.rectangle([x + 8, y + h - 14, x + w - 8, y + h - 4], fill=BLUE)
    elif key == "cop31":
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=BLUE, width=3)
        d.ellipse([cx - 20, cy - 6, cx + 20, cy + 6], outline=BLUE, width=2)
        d.line([cx - 20, cy - 20, cx + 20, cy + 20], fill=RED, width=3)
    elif key == "kyiv":
        d.rectangle([x + 14, y + 8, x + w - 14, y + h - 6], fill=(90, 107, 124))
        d.polygon([(x + w - 14, y + 8), (x + w - 4, y + 18), (x + w - 14, y + 22)],
                  fill=(40, 50, 66))
        for wx in (20, 32, 44):
            for wy in (14, 26):
                d.rectangle([x + wx, y + wy, x + wx + 7, y + wy + 7],
                            fill=(255, 220, 130))
        d.ellipse([x + w - 16, y + 0, x + w - 6, y + 10], fill=(150, 160, 175))
        d.ellipse([x + w - 12, y + 8, x + w - 2, y + 18], fill=(175, 184, 196))
    elif key == "kryvyi":
        d.line([x + 6, y + 8, x + w - 10, y + h - 10], fill=RED, width=3)
        d.polygon([(x + w - 16, y + h - 16), (x + w - 4, y + h - 10),
                   (x + w - 10, y + h - 4)], fill=RED)
        d.rectangle([x + 8, y + h - 16, x + 30, y + h - 6], fill=(90, 107, 124))
    elif key == "sinaloa":
        d.ellipse([cx - 16, cy - 14, cx + 16, cy + 14], outline=GOLD, width=4)
        for k in range(5):
            import math
            a = -math.pi / 2 + k * 2 * math.pi / 5
            d.ellipse([cx + 12 * math.cos(a) - 2, cy + 12 * math.sin(a) - 2,
                       cx + 12 * math.cos(a) + 2, cy + 12 * math.sin(a) + 2],
                      fill=GOLD)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=GOLD)
    elif key == "hague":
        d.rectangle([cx - 22, cy - 4, cx + 6, cy + 4], fill=(120, 84, 40))
        d.rectangle([cx + 6, cy - 10, cx + 22, cy + 2], fill=(150, 105, 50))
        d.line([cx - 8, cy + 4, cx - 16, cy + 18], fill=(120, 84, 40), width=4)
        d.rectangle([x + 10, y + h - 8, x + w - 10, y + h - 4], fill=(120, 84, 40))
    elif key == "markets":
        pts = [(x + 6, y + 10), (x + w * 0.35, y + 16), (x + w * 0.6, y + 26),
               (x + w - 8, y + h - 10)]
        d.line(pts, fill=RED, width=3)
        d.polygon([(x + w - 8, y + h - 10), (x + w - 20, y + h - 12),
                   (x + w - 10, y + h - 22)], fill=RED)
        d.line([x + 6, y + h - 8, x + w - 6, y + h - 8], fill=GREY, width=1)
    elif key == "mercury":
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(205, 110, 60))
        d.ellipse([cx - 26, cy - 10, cx + 26, cy + 10], outline=BLUE, width=2)
        d.ellipse([cx + 20, cy - 14, cx + 24, cy - 10], fill=BLUE)
        d.ellipse([x + 8, y + 6, x + 11, y + 9], fill=GREY)
        d.ellipse([x + w - 12, y + h - 12, x + w - 9, y + h - 9], fill=GREY)
    elif key == "banten":
        d.rectangle([x + 8, y + 16, x + w - 8, y + h - 6], fill=(90, 107, 124))
        for i in range(3):
            bx = x + 12 + i * 14
            d.polygon([(bx, y + 16), (bx + 7, y + 6), (bx + 14, y + 16)], fill=(60, 72, 90))
        d.polygon([(cx - 12, y + 16), (cx, y + 0), (cx + 12, y + 16)],
                  fill=(255, 140, 40))
        d.polygon([(cx - 6, y + 16), (cx, y + 6), (cx + 6, y + 16)],
                  fill=(255, 200, 90))
        d.ellipse([cx + 14, y + 2, cx + 22, y + 10], fill=(150, 160, 175))
    elif key == "seoul":
        d.rectangle([x + 14, y + 10, x + w - 14, y + h - 10], fill=(255, 255, 255),
                    outline=GREY, width=1)
        d.line([x + 20, y + 18, x + w - 20, y + 18], fill=GREY, width=2)
        d.line([x + 20, y + 26, x + w - 26, y + 26], fill=GREY, width=2)
        d.line([x + 20, y + 34, x + w - 30, y + 34], fill=GREY, width=2)
        d.line([x + w - 24, y + h - 20, x + w - 12, y + h - 8], fill=RED, width=3)
        d.line([x + w - 12, y + h - 20, x + w - 24, y + h - 8], fill=RED, width=3)
    elif key == "fbi":
        d.polygon([(cx, y + 4), (cx + 16, y + 10), (cx + 16, y + 24),
                   (cx, y + h - 4), (cx - 16, y + 24), (cx - 16, y + 10)],
                  outline=BLUE, width=3)
        d.rectangle([cx - 7, cy - 2, cx + 7, cy + 10], outline=BLUE, width=2)
        d.ellipse([cx - 4, cy - 8, cx + 4, cy + 0], outline=BLUE, width=2)
        d.line([cx - 8, cy + 12, cx + 8, cy + 2], fill=RED, width=2)
    elif key == "vegas":
        for i in range(4):
            for j in range(2):
                if (i + j) % 2 == 0:
                    d.rectangle([x + 8 + i * 9, y + 6 + j * 9,
                                 x + 17 + i * 9, y + 15 + j * 9], fill=INK)
        d.rounded_rectangle([x + 10, y + h - 20, x + w - 10, y + h - 8],
                            radius=4, fill=RED)
        d.ellipse([x + 16, y + h - 10, x + 24, y + h - 2], fill=INK)
        d.ellipse([x + w - 24, y + h - 10, x + w - 16, y + h - 2], fill=INK)


def draw_panels(d, x, y, w, h, cols, rows):
    gap = 8
    cw = (w - gap * (cols - 1)) // cols
    ch = (h - gap * (rows - 1)) // rows
    f_t = font("sans_b", 11)
    f_s = font("sans", 10)
    for i, (key, title, sub, tint) in enumerate(PANELS[:cols * rows]):
        px = x + (i % cols) * (cw + gap)
        py = y + (i // cols) * (ch + gap)
        d.rectangle([px, py, px + cw, py + ch], fill=(255, 255, 255),
                    outline=LINE, width=1)
        icon_h = ch - 36
        d.rectangle([px + 1, py + 1, px + cw - 1, py + icon_h], fill=tint)
        draw_icon(d, key, px, py + 2, cw, icon_h - 2)
        tlines = wrap(d, title, f_t, cw - 10)
        block(d, px + 5, py + icon_h + 3, cw - 10, 26, tlines[:2], f_t, INK,
              leading=12)
        d.text((px + 5, py + ch - 13), sub, font=f_s, fill=GREY)


def project(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 170) / 360 * w, y0 + (75 - lat) / 130 * h)


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=MAPSEA, outline=LINE, width=1)
    # White header strip so labels never sit on the land polygons.
    d.rectangle([x + 1, y + 1, x + w - 1, y + 21], fill=(255, 255, 255))
    d.line([x + 1, y + 21, x + w - 1, y + 21], fill=LINE, width=1)
    f_l = font("sans_b", 11)
    d.text((x + 8, y + 5), "WHERE IT HAPPENED", font=f_l, fill=INK)
    f_n = font("sans", 10)
    note = "RED DOTS: BIGGEST STORIES"
    tw = d.textlength(note, font=f_n)
    d.text((x + w - 8 - tw, y + 6), note, font=f_n, fill=GREY)
    for pts in CONTINENTS.values():
        poly = [project(lon, lat, x, y + 24, w, h - 24) for lon, lat in pts]
        d.polygon(poly, fill=MAPLAND, outline=(140, 158, 176))
    for lon, lat, num in MAP_DOTS:
        px, py = project(lon, lat, x, y + 24, w, h - 24)
        r = 7 if num else 4
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        if num:
            f_num = font("sans_b", 9)
            tw = d.textlength(str(num), font=f_num)
            d.text((px - tw / 2, py - 5), str(num), font=f_num,
                   fill=(255, 255, 255))


def draw_figures(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=INK)
    d.text((x + 10, y + 6), "BY THE NUMBERS", font=font("sans_b", 11),
           fill=(255, 255, 255))
    fw = (w - 150) // len(FIGURES)
    f_v = font("serif_b", 20)
    f_l = font("sans_b", 9)
    for i, (val, lab) in enumerate(FIGURES):
        fx = x + 150 + i * fw
        d.text((fx, y + 5), val, font=f_v, fill=(255, 200, 90))
        d.text((fx, y + 30), lab, font=f_l, fill=(200, 212, 224))


def draw_list(d, x, y, w, h, cols):
    f_h = font("sans_b", 12)
    d.text((x, y), "THE DAY, STORY BY STORY  -  50 STORIES, 6 CONTINENTS",
           font=f_h, fill=INK)
    d.rectangle([x, y + 18, x + w, y + 20], fill=RED)
    f_n = font("sans_b", 11)
    f_t = font("sans", 11)
    gap = 16
    cw = (w - gap * (cols - 1)) // cols
    per_col = (len(STORIES) + cols - 1) // cols
    row_h = (h - 26) / per_col
    for c in range(cols):
        cx = x + c * (cw + gap)
        for r in range(per_col):
            idx = c * per_col + r
            if idx >= len(STORIES):
                break
            title, place, _ = STORIES[idx]
            ry = y + 26 + r * row_h
            d.text((cx, ry), f"{idx + 1:2d}", font=f_n, fill=RED)
            txt = trunc(d, f"{title}  -  {place}", f_t, cw - 30)
            d.text((cx + 26, ry), txt, font=f_t, fill=INK)


def draw_footer(d, y):
    f_f = font("sans", 10)
    txt = ("All stories first reported on Sunday 22 November 2026  -  "
           "Sources: Reuters, AP, BBC, Al Jazeera, The Hague, One Turn")
    tw = d.textlength(txt, font=f_f)
    d.text(((W - tw) / 2, y), txt, font=f_f, fill=GREY)


def render(variant):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    if variant == "A":
        draw_masthead(d, 8, 100)
        draw_hero(d, 24, 116, W - 48, 180)
        draw_panels(d, 24, 304, W - 48, 188, 6, 2)
        draw_map(d, 24, 500, W - 48, 128)
        draw_figures(d, 24, 636, W - 48, 52)
        draw_list(d, 24, 696, W - 48, 300, 2)
        draw_footer(d, 1004)
    elif variant == "B":
        draw_masthead(d, 8, 100)
        draw_hero(d, 24, 116, W - 48, 262)
        draw_panels(d, 24, 386, W - 48, 236, 4, 3)
        draw_figures(d, 24, 630, W - 48, 52)
        draw_list(d, 24, 690, W - 48, 300, 3)
        draw_footer(d, 1004)
    else:
        draw_masthead(d, 8, 100)
        draw_hero(d, 24, 116, W - 48, 162)
        draw_map(d, 24, 286, 640, 250)
        f_h = font("sans_b", 12)
        d.text((680, 286), "TOP 10 TODAY", font=f_h, fill=INK)
        d.rectangle([680, 304, 1000, 306], fill=RED)
        f_t = font("sans", 12)
        for i in range(10):
            title, place, _ = STORIES[i]
            ry = 314 + i * 22
            d.text((680, ry), f"{i + 1}.", font=font("sans_b", 12), fill=RED)
            txt = trunc(d, title, f_t, 290)
            d.text((706, ry), txt, font=f_t, fill=INK)
        draw_panels(d, 24, 544, W - 48, 110, 6, 1)
        draw_figures(d, 24, 662, W - 48, 52)
        draw_list(d, 24, 722, W - 48, 274, 2)
        draw_footer(d, 1004)
    return im


def out_dir():
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return env
    if os.path.isdir("/output"):
        return "/output"
    return "out"


def main():
    variant = os.environ.get("VARIANT", "A").upper()
    if variant not in ("A", "B", "C"):
        variant = "A"
    im = render(variant)
    out = out_dir()
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    im.save(path, format="PNG")
    print(f"variant {variant}: wrote {path} "
          f"({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
