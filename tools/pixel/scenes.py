"""Generate the pixel-art terminal scenes and sprites used by the site.

Run from the repo root (needs Pillow):  python tools/pixel/scenes.py
Output goes to images/pixel/. Every scene is 720x168 and is shown in the
browser at an integer scale (2x or 3x) with image-rendering: pixelated.

The art is an original, generic modern terminal (curved roof, glass wall,
check-in islands) loosely inspired by NAIA Terminal 3. It uses no real
airport or airline branding.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageOps

OUT = os.path.join("images", "pixel")
W, H = 720, 168

C = {
    "sky": [(15, 21, 48), (24, 34, 74), (36, 52, 102), (51, 70, 125),
            (90, 90, 138), (160, 100, 122), (224, 138, 90), (242, 179, 106)],
    "hill": (28, 36, 64), "apron": (43, 47, 58), "apron2": (58, 63, 74),
    "yellow": (255, 204, 0), "amber": (255, 182, 39), "blue_l": (110, 160, 255),
    "roof": (232, 230, 223), "roof2": (214, 211, 202), "skylight": (255, 251, 232),
    "truss": (184, 188, 196), "beam": (141, 146, 155), "mull": (74, 82, 96),
    "floor": (46, 42, 37), "floor2": (56, 51, 44), "floor3": (70, 64, 56),
    "base": (29, 27, 24), "wood": (138, 106, 74), "wood2": (110, 82, 56),
    "counter": (217, 212, 200), "top": (241, 239, 232), "panel": (107, 111, 120),
    "screen": (29, 42, 68), "screen2": (60, 90, 140), "ink": (17, 17, 17),
    "plant": (63, 143, 79), "plant2": (42, 94, 54), "trunk": (110, 82, 56),
    "seat": (59, 111, 209), "seat2": (42, 79, 160), "seat_hi": (96, 146, 232),
    "skin": (198, 138, 94), "skin2": (141, 90, 59), "hair": (30, 24, 20),
    "red": (210, 75, 60), "blue": (59, 111, 209), "white": (230, 228, 220),
    "pants": (40, 44, 60), "shoe": (20, 20, 24),
    "tower": (42, 51, 80), "tower2": (52, 62, 94), "win": (255, 210, 122),
    "jet": (154, 160, 168), "jet2": (120, 126, 136),
    "fuse": (236, 236, 240), "fuse2": (196, 198, 206), "tail": (59, 111, 209),
    "sil": (12, 14, 18), "sil2": (22, 25, 31), "sil3": (32, 36, 44),
}

# 3x5 pixel font for the little signs drawn into the art.
GLYPHS = {
    "A": ".#. #.# ### #.# #.#", "C": "### #.. #.. #.. ###", "D": "##. #.# #.# #.# ##.",
    "E": "### #.. ##. #.. ###", "G": "### #.. #.# #.# ###", "H": "#.# #.# ### #.# #.#",
    "I": "### .#. .#. .#. ###", "K": "#.# #.# ##. #.# #.#", "L": "#.. #.. #.. #.. ###", "F": "### #.. ##. #.. #..",
    "N": "##. #.# #.# #.# #.#", "O": "### #.# #.# #.# ###", "P": "##. #.# ##. #.. #..",
    "R": "##. #.# ##. #.# #.#", "S": "### #.. ### ..# ###", "T": "### .#. .#. .#. .#.",
    "U": "#.# #.# #.# #.# ###", "1": ".#. ##. .#. .#. ###", "2": "### ..# ### #.. ###", "3": "### ..# .## ..# ###",
    "-": "... ... ### ... ...", " ": "... ... ... ... ...",
}
ARROWS = {
    ">": ["..#..", "...#.", "#####", "...#.", "..#.."],
    "<": ["..#..", ".#...", "#####", ".#...", "..#.."],
}


def rect(d, x0, y0, x1, y1, c):
    d.rectangle([x0, y0, x1, y1], fill=c)


def text(d, x, y, s, c, scale=1):
    """Draw s with the 3x5 font. Returns the width drawn."""
    cx = x
    for ch in s:
        if ch in ARROWS:
            for r, row in enumerate(ARROWS[ch]):
                for col, v in enumerate(row):
                    if v == "#":
                        rect(d, cx + col * scale, y + r * scale,
                             cx + col * scale + scale - 1, y + r * scale + scale - 1, c)
            cx += 6 * scale
            continue
        for r, row in enumerate(GLYPHS[ch].split()):
            for col, v in enumerate(row):
                if v == "#":
                    rect(d, cx + col * scale, y + r * scale,
                         cx + col * scale + scale - 1, y + r * scale + scale - 1, c)
        cx += 4 * scale
    return cx - x - scale


def text_width(s, scale=1):
    return sum((6 if ch in ARROWS else 4) * scale for ch in s) - scale


# Shared pieces ---------------------------------------------------------

def sky(d, horizon, seed=3):
    """Dusk sky in bands, dithered where the bands meet, with a few stars."""
    w = d.im.size[0]
    bands = C["sky"]
    edges = [round(horizon * f) for f in (0, .3, .5, .66, .78, .86, .92, .97)]
    for y in range(horizon):
        i = max(k for k, e in enumerate(edges) if e <= y)
        for x in range(w):
            col = bands[i]
            if i > 0 and y - edges[i] < 2 and (x + y) % 2 == 0:
                col = bands[i - 1]
            d.point((x, y), fill=col)
    rnd = random.Random(seed)
    for _ in range(46):
        d.point((rnd.randrange(w), rnd.randrange(int(horizon * .45))),
                fill=rnd.choice([(230, 232, 255), (170, 180, 230)]))


def skyline(d, base, seed=5):
    w = d.im.size[0]
    rnd = random.Random(seed)
    x = 0
    while x < w:
        w = rnd.randint(6, 16)
        h = rnd.randint(3, 10)
        rect(d, x, base - h, x + w, base, C["hill"])
        if h > 6 and rnd.random() < .5:
            d.point((x + w // 2, base - h + 2), fill=C["win"])
        x += w + 1


def apron(d, y0, y1):
    w = d.im.size[0]
    rect(d, 0, y0, w - 1, y1, C["apron"])
    for x in range(0, w, 12):
        rect(d, x, y0 + 6, x + 6, y0 + 6, C["yellow"])
    for x in range(4, w, 16):
        d.point((x, y0 + 1), fill=C["amber"])
        d.point((x + 8, y0 + 3), fill=C["blue_l"])


def runway(d, top):
    """Distant runway strip, 4px tall, with centreline and edge lights. Planes roll with wheels at top + 2."""
    w = d.im.size[0]
    rect(d, 0, top, w - 1, top + 3, (52, 56, 66))
    for x in range(0, w, 10):
        rect(d, x, top + 1, x + 4, top + 1, C["white"])
    for x in range(2, w, 8):
        d.point((x, top), fill=C["amber"])
        d.point((x + 4, top + 3), fill=C["white"])


def layered(sky_im, mid_im, name):
    """Save sky and apron layers for the live canvas, plus the combined image the no-JS fallback uses."""
    sky_im.save(f"{OUT}/{name}-sky.png")
    mid_im.save(f"{OUT}/{name}-apron.png")
    both = sky_im.copy()
    both.alpha_composite(mid_im)
    both.save(f"{OUT}/{name}-back.png")


def tower(d, x, top, base):
    rect(d, x - 3, top + 8, x + 3, base, C["tower"])
    rect(d, x - 1, top + 8, x - 1, base, C["tower2"])
    rect(d, x - 8, top, x + 8, top + 7, C["tower2"])
    rect(d, x - 7, top + 2, x + 7, top + 4, C["win"])
    for k in range(-5, 8, 4):
        d.point((x + k, top + 3), fill=C["tower"])
    rect(d, x - 9, top - 1, x + 9, top - 1, C["beam"])


def parked_tail(d, x, y, colour):
    rect(d, x - 6, y, x + 34, y + 5, C["fuse"])
    rect(d, x - 6, y + 4, x + 34, y + 5, C["fuse2"])
    d.polygon([(x - 6, y), (x + 4, y), (x - 2, y - 11), (x - 7, y - 11)], fill=colour)


def plane(d, x, y, length, h, tail_colour, livery=True, gear=None):
    """Generic airliner, side view, nose to the right. (x, y) is the top-left of the body."""
    rect(d, x, y, x + length, y + h, C["fuse"])
    rect(d, x, y + h - 2, x + length, y + h, C["fuse2"])
    n = x + length
    d.polygon([(n, y), (n + h * .55, y + h * .35), (n + h * .7, y + h * .75),
               (n + h * .45, y + h), (n, y + h)], fill=C["fuse"])
    rect(d, n + 1, y + 2, n + round(h * .4), y + 3, C["screen"])
    d.polygon([(x, y), (x, y + h), (x - h * .9, y + h * .45), (x - h * .9, y + 1)], fill=C["fuse"])
    d.polygon([(x + h * 1.5, y + 1), (x + h * .2, y + 1), (x - h * .5, y - h * 1.6),
               (x + h * .3, y - h * 1.6)], fill=tail_colour)
    if livery:
        d.polygon([(x + h * .9, y + 1), (x + h * .5, y + 1), (x + h * .05, y - h * .9),
                   (x + h * .4, y - h * .9)], fill=C["yellow"])
        rect(d, x + h, y + h - 5, n, y + h - 4, tail_colour)
    for wx in range(x + h * 2, n - 6, 4):
        d.point((wx, y + max(2, h // 3)), fill=C["screen"])
    wx = x + length * .38
    d.polygon([(wx, y + h - 1), (wx + length * .26, y + h - 1),
               (wx + length * .16, y + h + h * .45), (wx - length * .04, y + h + h * .45)], fill=C["jet"])
    ex = round(x + length * .5)
    rect(d, ex, y + h + 1, ex + max(6, h), y + h + max(4, h // 2), C["fuse2"])
    rect(d, ex, y + h + 1, ex + 1, y + h + max(4, h // 2), C["jet2"])
    # gear = leg length in pixels; None = fully down, 0 = retracted (no wheels).
    leg = max(5, h // 2) if gear is None else gear
    if leg <= 0:
        return
    bottom = y + h + leg
    for gx in (x + length * .45, n - 4):
        rect(d, gx, y + h, gx + 1, bottom, C["jet2"])
        rect(d, gx - 1, bottom, gx + 2, bottom + 1, C["shoe"])


def roof(d):
    """Curved terminal roof with trusses and skylights. Returns the roof's lower edge per column."""
    w = d.im.size[0]
    edge = [20 + round(8 * ((x % 720 - 360) / 360) ** 2) for x in range(w)]
    for x in range(w):
        rect(d, x, 0, x, edge[x], C["roof"])
        rect(d, x, edge[x] - 3, x, edge[x], C["roof2"])
    for x0 in range(18, w, 90):
        rect(d, x0, 5, x0 + 44, 8, C["skylight"])
    for i in range(-30, w + 30, 24):
        for t in range(40):
            for x, y in ((i + t, 3 + t), (i + 24 - t, 3 + t)):
                if 0 <= x < w and y < edge[x] - 1:
                    d.point((x, y), fill=C["truss"])
    for x in range(w):
        rect(d, x, edge[x] + 1, x, edge[x] + 2, C["beam"])
    return edge


def glass_and_floor(d, edge, sill=109):
    """Glass wall (transparent with a light tint), mullions, lights and the polished floor."""
    w = d.im.size[0]
    for x in range(w):
        rect(d, x, edge[x] + 3, x, sill - 1, (111, 160, 208, 26))
    for x in range(0, w, 40):
        rect(d, x, edge[x] + 3, x + 1, sill, C["mull"])
    rect(d, 0, 64, w - 1, 65, C["mull"])
    for x in range(30, w, 60):
        rect(d, x, edge[x] + 3, x, edge[x] + 7, C["beam"])
        rect(d, x - 1, edge[x] + 8, x + 1, edge[x] + 9, C["amber"])
    rect(d, 0, sill, w - 1, sill + 1, C["base"])
    rect(d, 0, sill + 2, w - 1, H - 1, C["floor"])
    rect(d, 0, sill + 2, w - 1, sill + 3, C["floor3"])
    for y in (122, 136, 154):
        rect(d, 0, y, w - 1, y, C["floor2"])
    mid = w // 2
    for k in range(-(mid // 26) - 1, mid // 26 + 2):
        d.line([(mid + k * 26, sill + 2), (mid + k * 52, H - 1)], fill=C["floor2"])
    for x in range(0, w, 40):
        for y in range(sill + 4, sill + 26, 2):
            d.point((x, y), fill=C["floor3"])


def hanging_sign(d, edge, cx, y, label):
    w = text_width(label) + 8
    x0, x1 = cx - w // 2, cx - w // 2 + w
    for rx in (x0 + 3, x1 - 3):
        rect(d, rx, edge[rx] + 3, rx, y - 1, C["beam"])
    rect(d, x0, y, x1, y + 10, C["yellow"])
    rect(d, x0, y + 10, x1, y + 10, (200, 160, 0))
    text(d, x0 + 4, y + 3, label, C["ink"])


def palm(d, x, ground):
    rect(d, x - 7, ground - 10, x + 7, ground, C["panel"])
    rect(d, x - 8, ground - 11, x + 8, ground - 10, C["top"])
    tx = x
    for t in range(26):
        tx = x + round(2 * math.sin(t / 8))
        rect(d, tx, ground - 12 - t, tx + 1, ground - 12 - t, C["trunk"] if t % 3 else C["wood2"])
    top = ground - 38
    for direction in (-1, 1):
        for length, lift in ((15, 3), (11, 7), (8, 10)):
            for i in range(length):
                px = tx + direction * i
                py = top - lift + round(lift * 2 * (i / length) ** 2)
                d.point((px, py), fill=C["plant"])
                d.point((px, py + 1), fill=C["plant2"])
    rect(d, tx - 1, top - 11, tx + 2, top - 9, C["plant"])


def checkin_island(d, cx):
    rect(d, cx - 56, 72, cx + 56, 109, C["wood"])
    rect(d, cx - 56, 72, cx + 56, 73, C["wood2"])
    rect(d, cx - 40, 76, cx + 40, 86, C["yellow"])
    text(d, cx - text_width("CHECK-IN") // 2, 79, "CHECK-IN", C["ink"])
    for i in range(4):
        sx = cx - 50 + i * 26
        rect(d, sx, 90, sx + 16, 98, C["screen"])
        rect(d, sx + 1, 91, sx + 15, 91, C["screen2"])
    for ax, shirt in ((cx - 33, C["white"]), (cx + 19, C["blue"])):
        rect(d, ax, 96, ax + 3, 99, C["skin"])
        rect(d, ax, 95, ax + 3, 95, C["hair"])
        rect(d, ax - 1, 100, ax + 4, 103, shirt)
    rect(d, cx - 60, 102, cx + 60, 103, C["top"])
    rect(d, cx - 60, 104, cx + 60, 118, C["panel"])
    rect(d, cx - 60, 110, cx + 60, 111, C["counter"])
    rect(d, cx - 60, 119, cx + 60, 120, C["base"])


def seat_row(d, x0, x1, y):
    for x in range(x0, x1, 9):
        rect(d, x, y, x + 6, y + 7, C["seat"])
        rect(d, x, y, x + 6, y, C["seat_hi"])
        rect(d, x - 1, y + 8, x + 7, y + 10, C["seat2"])
        rect(d, x + 3, y + 11, x + 3, y + 14, C["beam"])
    rect(d, x0 - 1, y + 13, x1 - 2, y + 14, C["panel"])


def new(transparent=True, width=W):
    im = Image.new("RGBA", (width, H), (0, 0, 0, 0) if transparent else (0, 0, 0, 255))
    return im, ImageDraw.Draw(im)


# Scenes ----------------------------------------------------------------

def hall():
    back, d = new(False)
    sky(d, 100)
    skyline(d, 99)
    tower(d, 560, 56, 99)
    for x, c in ((70, C["red"]), (190, C["tail"]), (610, C["yellow"]), (668, C["red"])):
        parked_tail(d, x, 95, c)
    apron(d, 100, 112)
    back.save(f"{OUT}/hall-back.png")

    front, d = new()
    edge = roof(d)
    glass_and_floor(d, edge)
    hanging_sign(d, edge, 200, 34, "< GATES")
    hanging_sign(d, edge, 360, 34, "DEPARTURES")
    hanging_sign(d, edge, 540, 34, "CHECK-IN >")
    for cx in (130, 360, 590):
        checkin_island(d, cx)
    for x in (24, 254, 466, 698):
        palm(d, x, 128)
    front.save(f"{OUT}/hall-front.png")


def gate():
    back, d = new(False)
    sky(d, 100, seed=8)
    skyline(d, 95, seed=9)
    runway(d, 96)
    mid, d = new()
    apron(d, 100, 112)
    plane(d, 130, 72, 250, 18, C["tail"])
    rect(d, 404, 66, W - 1, 86, C["jet"])
    rect(d, 404, 66, W - 1, 67, C["fuse2"])
    for x in range(412, W, 14):
        rect(d, x, 72, x + 7, 76, C["screen"])
    rect(d, 388, 68, 406, 90, C["jet2"])
    for x in (470, 600):
        rect(d, x, 87, x + 3, 100, C["jet2"])
    layered(back, mid, "gate")

    front, d = new()
    edge = roof(d)
    glass_and_floor(d, edge)
    x0, x1 = 330, 390
    for rx in (x0 + 4, x1 - 4):
        rect(d, rx, edge[rx] + 3, rx, 31, C["beam"])
    rect(d, x0, 32, x1, 60, C["yellow"])
    rect(d, x0, 60, x1, 60, (200, 160, 0))
    text(d, 360 - text_width("GATE") // 2, 35, "GATE", C["ink"])
    text(d, 360 - text_width("D1", 3) // 2, 43, "D1", C["ink"], 3)
    rect(d, 324, 98, 396, 99, C["top"])
    rect(d, 326, 100, 394, 118, C["counter"])
    rect(d, 326, 106, 394, 108, C["yellow"])
    rect(d, 340, 92, 352, 98, C["screen"])
    rect(d, 366, 93, 369, 96, C["skin"])
    rect(d, 366, 92, 369, 92, C["hair"])
    rect(d, 365, 97, 370, 98, C["red"])
    rect(d, 326, 119, 394, 120, C["base"])
    rect(d, 420, 104, 452, 106, C["top"])
    rect(d, 434, 107, 437, 124, C["panel"])
    rect(d, 428, 125, 444, 126, C["base"])
    rect(d, 427, 102, 445, 103, C["jet"])
    rect(d, 430, 95, 442, 101, C["screen"])
    for y in (126, 146):
        seat_row(d, 22, 300, y)
        seat_row(d, 474, 712, y)
        seated_passengers(d, 22, 300, y, seed=y)
        seated_passengers(d, 474, 712, y, seed=y + 1)
    palm(d, 310, 128)
    palm(d, 462, 128)
    front.save(f"{OUT}/gate-front.png")


def apron_view():
    back, d = new(False)
    sky(d, 126, seed=11)
    skyline(d, 121, seed=12)
    runway(d, 122)
    mid, d = new()
    rect(d, 0, 72, 236, 126, (60, 66, 80))
    for x in range(237):
        top = 72 - round(7 * math.sin(math.pi * x / 236))
        rect(d, x, top, x, 72, C["roof2"])
    rnd = random.Random(4)
    for x in range(4, 230, 10):
        for y in range(80, 122, 8):
            rect(d, x, y, x + 7, y + 5, C["win"] if rnd.random() < .35 else (44, 74, 110))
    # Jet bridge from the terminal, with a rotunda column at the building end,
    # a drive leg on a wheeled bogie near the outer end, and a cab at the tip.
    rect(d, 190, 100, 300, 108, C["jet"])
    rect(d, 190, 100, 300, 101, C["fuse2"])
    for x in range(198, 296, 9):
        rect(d, x, 103, x + 4, 105, C["screen"])
    rect(d, 296, 98, 306, 110, C["jet2"])
    rect(d, 297, 99, 305, 99, C["fuse2"])
    rect(d, 205, 109, 210, 126, (110, 114, 122))
    rect(d, 205, 109, 205, 126, (140, 144, 152))
    rect(d, 272, 109, 275, 121, C["jet2"])
    rect(d, 270, 109, 277, 110, C["jet2"])
    rect(d, 267, 122, 280, 123, C["jet2"])
    rect(d, 268, 124, 271, 126, C["shoe"])
    rect(d, 276, 124, 279, 126, C["shoe"])
    tower(d, 520, 30, 126)
    rect(d, 516, 40, 524, 126, C["tower"])
    rect(d, 518, 40, 518, 126, C["tower2"])
    rect(d, 504, 26, 536, 39, C["tower2"])
    rect(d, 506, 29, 534, 34, C["win"])
    rect(d, 519, 14, 519, 25, C["beam"])
    rect(d, 0, 126, W - 1, H - 1, C["apron"])
    for x in range(0, W, 3):
        if x % 9 == 0:
            d.point((x, 127), fill=C["amber"])
    for t in range(60):
        x = 280 + t * 4
        y = 166 - round(34 * math.sin(math.pi / 2 * t / 60))
        rect(d, x, y, x + 2, y, C["yellow"])
    rect(d, 300, 160, 460, 160, C["white"])
    layered(back, mid, "apron")

    front, d = new()
    for x in range(W):
        for y in range(138, H):
            if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                d.point((x, y), fill=(150, 155, 165, 190))
    rect(d, 0, 136, W - 1, 137, (120, 125, 135))
    for x in range(10, W, 90):
        rect(d, x, 128, x + 2, H - 1, (90, 95, 105))
    for x in range(W):
        if x % 4 < 2:
            d.point((x, 132 + (x % 8 < 4)), fill=(110, 115, 125))
    front.save(f"{OUT}/apron-front.png")


def window():
    front, d = new()
    rect(d, 0, 0, W - 1, 15, C["sil2"])
    for x in range(30, W, 60):
        rect(d, x - 1, 13, x + 1, 14, C["amber"])
    for x in range(0, W + 1, 120):
        rect(d, x - 2, 16, x + 2, 118, C["sil"])
    rect(d, 0, 16, W - 1, 18, C["sil"])
    rect(d, 0, 70, W - 1, 72, C["sil"])
    for px in range(0, W, 120):
        for t in range(26):
            x, y = px + 30 + t, 22 + t * 2
            if y < 69:
                d.point((x, y), fill=(255, 255, 255, 30))
                d.point((x + 3, y), fill=(255, 255, 255, 18))
    rect(d, 0, 112, W - 1, 113, C["sil3"])
    for x in range(0, W, 30):
        rect(d, x, 113, x + 1, 124, C["sil3"])
    rect(d, 0, 118, W - 1, 124, C["sil2"])
    rect(d, 0, 125, W - 1, H - 1, C["sil"])
    for x in range(6, W, 22):
        rect(d, x + 1, 134, x + 15, 134, C["sil3"])
        rect(d, x, 135, x + 16, H - 1, C["sil3"])
        rect(d, x + 2, 137, x + 14, H - 1, C["sil2"])
    front.save(f"{OUT}/window-front.png")


# Sprites ---------------------------------------------------------------

def person(d, x, y, frame, shirt, pants=None, skin=None, hair=None, bag=None, pack=None, arms=True):
    """One 14x20 traveler facing right. frame 0 = legs apart, 1 = legs together.
    bag = rolling suitcase colour, pack = backpack colour. arms=False leaves the arms
    for the caller to draw (the marshaller's wand signals)."""
    pants, skin, hair = pants or C["pants"], skin or C["skin"], hair or C["hair"]
    o = x + 4
    if bag:
        rect(d, o - 4, y + 12, o - 1, y + 18, bag)
        rect(d, o - 2, y + 9, o - 2, y + 11, C["ink"])
        d.point((o - 4, y + 19), fill=C["shoe"])
        d.point((o - 1, y + 19), fill=C["shoe"])
    rect(d, o + 3, y, o + 6, y + 3, skin)
    rect(d, o + 3, y, o + 6, y, hair)
    d.point((o + 3, y + 1), fill=hair)
    rect(d, o + 2, y + 4, o + 7, y + 11, shirt)
    swing = 1 if frame == 0 else -1
    if arms:
        rect(d, o + 1, y + 5, o + 1, y + 9 + swing, shirt)
        d.point((o + 1, y + 10 + swing), fill=skin)
        rect(d, o + 8, y + 5, o + 8, y + 9 - swing, shirt)
        d.point((o + 8, y + 10 - swing), fill=skin)
    if pack:
        rect(d, o, y + 4, o + 1, y + 10, pack)
    if frame == 0:
        legs = [(o + 3, 12, 14), (o + 2, 15, 18), (o + 6, 12, 14), (o + 7, 15, 18)]
    else:
        legs = [(o + 4, 12, 18), (o + 5, 12, 18)]
    for lx, y0, y1 in legs:
        rect(d, lx, y + y0, lx, y + y1, pants)
    for lx in ({l[0] for l in legs if l[2] == 18}):
        d.point((lx, y + 19), fill=C["shoe"])
        d.point((lx + 1, y + 19), fill=C["shoe"])


def walker(name, shirt, bag=None):
    fw, fh = 14, 20
    im = Image.new("RGBA", (fw * 2, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for f in range(2):
        person(d, f * fw, 0, f, shirt, bag=bag)
    im.save(f"{OUT}/{name}.png")


# Travellers for the game crowd: (shirt, pants, skin, hair, suitcase, backpack, kid)
CROWD = [
    (C["red"], C["pants"], C["skin"], C["hair"], C["yellow"], None, False),
    (C["blue"], (70, 64, 52), C["skin2"], C["hair"], None, (90, 60, 40), False),
    (C["white"], C["pants"], (222, 176, 136), (110, 70, 40), C["pants"], None, False),
    ((63, 143, 79), (50, 54, 70), C["skin"], C["hair"], None, None, False),
    ((236, 150, 60), (40, 44, 60), (222, 176, 136), (200, 170, 90), (180, 60, 120), None, False),
    ((150, 90, 180), (60, 60, 70), C["skin2"], C["hair"], None, (60, 120, 200), False),
    ((240, 210, 60), (60, 90, 160), C["skin"], C["hair"], None, None, True),
    ((230, 110, 140), (50, 54, 70), (222, 176, 136), (110, 70, 40), None, (240, 210, 60), True),
]


def crowd_sheet():
    """8 rows (one per traveller) x 2 walk frames, each 14x20. Kids are drawn smaller."""
    fw, fh = 14, 20
    im = Image.new("RGBA", (fw * 2, fh * len(CROWD)), (0, 0, 0, 0))
    for row, (shirt, pants, skin, hair, bag, pack, kid) in enumerate(CROWD):
        for f in range(2):
            cell = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
            person(ImageDraw.Draw(cell), 0, 0, f, shirt, pants, skin, hair, bag, pack)
            if kid:
                small = cell.resize((10, 14), Image.NEAREST)
                cell = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
                cell.paste(small, (3, fh - 14))
            im.paste(cell, (f * fw, row * fh))
    im.save(f"{OUT}/crowd.png")


def crowd_dark_sheet():
    """The crowd as dark silhouettes, for people walking in front of the bright window."""
    im = Image.open(f"{OUT}/crowd.png").convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3]:
                px[x, y] = (34, 38, 48, 255)
    im.save(f"{OUT}/crowd-dark.png")


def crew_sheet():
    """Rows: ground crew in an orange vest, ground crew in a yellow vest, a plane spotter with a camera."""
    fw, fh = 14, 20
    rows = [((255, 140, 0), (40, 44, 60), C["yellow"], None),
            ((240, 210, 60), (40, 44, 60), C["white"], None),
            ((90, 92, 100), (50, 54, 70), C["hair"], True)]
    im = Image.new("RGBA", (fw * 2, fh * len(rows)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for row, (shirt, pants, hat, camera) in enumerate(rows):
        for f in range(2):
            x, y = f * fw, row * fh
            person(d, x, y, f, shirt, pants, hair=hat)
            if camera:
                rect(d, x + 10, y + 1, x + 12, y + 3, C["shoe"])
                d.point((x + 13, y + 2), fill=(96, 102, 116))
            else:
                rect(d, x + 7, y, x + 10, y, hat)
                rect(d, x + 6, y + 6, x + 11, y + 6, C["white"])
    im.save(f"{OUT}/crew.png")


def flight_crew_sheet():
    """Airline crew at traveller scale (14x20, 2 walk frames), each pulling a roller bag.
    Rows: captain, first officer, flight attendant (red), flight attendant (navy)."""
    fw, fh = 14, 20
    navy, gold, white = (28, 36, 66), (232, 184, 64), (236, 236, 240)
    bag, stockings = (78, 84, 100), (44, 38, 46)
    crew = [
        ("pilot", white, navy, C["skin"], C["hair"]),
        ("pilot", white, navy, C["skin2"], C["hair"]),
        ("attendant", (190, 40, 52), (190, 40, 52), (222, 176, 136), (60, 36, 24)),
        ("attendant", navy, navy, C["skin"], C["hair"]),
    ]
    im = Image.new("RGBA", (fw * 2, fh * len(crew)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for row, (role, top, bottom, skin, hair) in enumerate(crew):
        for f in range(2):
            x, y = f * fw, row * fh
            o = x + 4
            legs = stockings if role == "attendant" else bottom
            person(d, x, y, f, top, legs, skin, hair, bag=bag)
            if role == "pilot":
                # Cap with a gold badge and peak, black tie, gold epaulettes.
                rect(d, o + 3, y, o + 6, y, navy)
                rect(d, o + 5, y + 1, o + 7, y + 1, C["ink"])
                d.point((o + 5, y), fill=gold)
                rect(d, o + 5, y + 5, o + 5, y + 9, C["ink"])
                d.point((o + 2, y + 4), fill=gold)
                d.point((o + 7, y + 4), fill=gold)
            else:
                # Hair in a bun, yellow scarf at the neck, uniform skirt.
                d.point((o + 2, y + 1), fill=hair)
                rect(d, o + 4, y + 4, o + 5, y + 4, C["yellow"])
                rect(d, o + 2, y + 12, o + 7, y + 13, bottom)
    im.save(f"{OUT}/flight-crew.png")


def traffic_sheet():
    """Distant airliners for take-offs and landings. Columns: 4 pitch angles (0, 4, 8, 12
    degrees nose-up). Rows: 3 liveries x 4 landing-gear positions (down, 3/4, 1/4, up), so
    row = livery * 4 + gear step. Each cell is 56x28 with the plane centred."""
    cw, ch = 56, 28
    gear_steps = (5, 3, 1, 0)
    im = Image.new("RGBA", (cw * 4, ch * 3 * len(gear_steps)), (0, 0, 0, 0))
    for livery, colour in enumerate((C["tail"], C["red"], C["yellow"])):
        for step, leg in enumerate(gear_steps):
            row = livery * len(gear_steps) + step
            base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            plane(ImageDraw.Draw(base), 13, 12, 34, 5, colour, livery=False, gear=leg)
            for col, angle in enumerate((0, 4, 8, 12)):
                cell = base.rotate(angle, resample=Image.NEAREST, center=(cw / 2, ch / 2))
                im.paste(cell, (col * cw, row * ch), cell)
    im.save(f"{OUT}/traffic.png")


def far_plane():
    im = Image.new("RGBA", (64, 18), (0, 0, 0, 0))
    plane(ImageDraw.Draw(im), 10, 8, 40, 5, C["red"], livery=False)
    ImageOps.mirror(im).save(f"{OUT}/plane-far.png")


def pushback():
    im = Image.new("RGBA", (170, 52), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    plane(d, 22, 26, 112, 13, C["tail"])
    rect(d, 140, 46, 156, 48, C["jet2"])
    rect(d, 154, 40, 166, 47, C["yellow"])
    rect(d, 158, 37, 163, 40, C["screen"])
    rect(d, 155, 48, 157, 49, C["shoe"])
    rect(d, 163, 48, 165, 49, C["shoe"])
    im.save(f"{OUT}/pushback.png")


# Pilot page stand: the plane and tug from pushback() as separate sprites, so the
# tug can drive in, hook up, push back and leave. TUG_AT is where tug.png sits
# relative to stand-plane.png when hooked up (must match TUG_DX/TUG_DY in airport.js).
TUG_AT = (138, 36)


def stand_sheets():
    im = Image.new("RGBA", (170, 52 * 3), (0, 0, 0, 0))
    for row, colour in enumerate((C["tail"], C["red"], C["yellow"])):
        cell = Image.new("RGBA", (170, 52), (0, 0, 0, 0))
        plane(ImageDraw.Draw(cell), 22, 26, 112, 13, colour)
        im.paste(cell, (0, row * 52))
    im.save(f"{OUT}/stand-plane.png")

    tug = Image.new("RGBA", (30, 15), (0, 0, 0, 0))
    d = ImageDraw.Draw(tug)
    ox, oy = TUG_AT
    rect(d, 140 - ox, 46 - oy, 156 - ox, 48 - oy, C["jet2"])
    rect(d, 154 - ox, 40 - oy, 166 - ox, 47 - oy, C["yellow"])
    rect(d, 158 - ox, 37 - oy, 163 - ox, 40 - oy, C["screen"])
    rect(d, 155 - ox, 48 - oy, 157 - ox, 49 - oy, C["shoe"])
    rect(d, 163 - ox, 48 - oy, 165 - ox, 49 - oy, C["shoe"])
    tug.save(f"{OUT}/tug.png")


def marshaller():
    """Ground crew with lit wands, 20x24 frames: 0 wands up, 1 wands out, 2 arms down."""
    fw, fh = 20, 24
    vest, wand, skin = (255, 140, 0), (255, 70, 40), C["skin"]
    im = Image.new("RGBA", (fw * 3, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for f in range(3):
        x = f * fw + 3
        o = x + 4
        person(d, x, 4, 1, vest, (40, 44, 60), hair=C["yellow"], arms=(f == 2))
        rect(d, o + 6, 4, o + 9, 4, C["yellow"])
        rect(d, o + 2, 10, o + 7, 10, C["white"])
        if f == 0:
            for ax in (o + 1, o + 8):
                rect(d, ax, 4, ax, 9, vest)
                d.point((ax, 3), fill=skin)
                rect(d, ax, 0, ax, 2, wand)
        elif f == 1:
            rect(d, o - 2, 9, o + 1, 9, vest)
            rect(d, o + 8, 9, o + 10, 9, vest)
            d.point((o - 3, 9), fill=skin)
            d.point((o + 11, 9), fill=skin)
            rect(d, o - 6, 9, o - 4, 9, wand)
            rect(d, o + 12, 9, o + 12, 9, wand)
    im.save(f"{OUT}/marshaller.png")


def photographer():
    fw, fh = 26, 62
    im = Image.new("RGBA", (fw * 2, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = (8, 9, 12)
    for f in range(2):
        o = f * fw
        rect(d, o + 9, 2, o + 16, 11, body)
        rect(d, o + 10, 0, o + 15, 1, body)
        rect(d, o + 4, 14, o + 21, fh - 1, body)
        rect(d, o + 6, 12, o + 19, 13, body)
        if f == 0:
            rect(d, o + 3, 15, o + 6, 22, body)
            rect(d, o + 19, 15, o + 22, 22, body)
            rect(d, o + 7, 5, o + 18, 10, (40, 44, 52))
            rect(d, o + 11, 6, o + 14, 9, (70, 76, 88))
        else:
            rect(d, o + 3, 15, o + 5, 30, body)
            rect(d, o + 20, 15, o + 22, 30, body)
            rect(d, o + 8, 24, o + 17, 29, (40, 44, 52))
            rect(d, o + 11, 25, o + 14, 28, (70, 76, 88))
    im.save(f"{OUT}/photographer.png")


# Page-transition loader: A320 flight deck ---------------------------------
# 320x180, laid out from a 1920x1080 reference screenshot at exactly 1/6 scale.
# Screens are left dark here; assets/js/transition.js draws their content and
# the thrust levers (positions must match SCREENS / LEVERS in that file).

# Screen rectangles (x, y, w, h); keep in sync with SCREENS in assets/js/transition.js.
COCKPIT_SCREENS = (
    (97, 95, 18, 16), (117, 95, 17, 16),     # captain PFD, ND
    (151, 94, 18, 17), (151, 113, 18, 17),   # upper and lower ECAM
    (186, 95, 17, 16), (205, 95, 18, 16),    # first officer ND, PFD
    (142, 101, 6, 7),                        # standby instrument
)


def cockpit():
    cw, ch = 320, 180
    im = Image.new("RGBA", (cw, ch), (36, 41, 52, 255))
    d = ImageDraw.Draw(im)
    rnd = random.Random(320)
    panel, panel_hi, panel_lo = (132, 144, 170), (156, 167, 192), (104, 115, 140)
    frame, frame_hi, gap = (150, 160, 182), (178, 188, 206), (26, 29, 37)
    trim, ceiling = (58, 64, 78), (40, 44, 54)
    seat, seat_hi, seat_lo, stripe = (34, 62, 104), (52, 86, 136), (22, 40, 70), (46, 80, 128)
    knob, switch, amber = (210, 214, 222), (24, 26, 32), (255, 168, 40)

    def mirror(points):
        return [(cw - 1 - x, y) for x, y in points]

    def speckle(box, base, n):
        x0, y0, x1, y1 = box
        for _ in range(n):
            c = tuple(max(0, min(255, v + rnd.randint(-10, 10))) for v in base)
            d.point((rnd.randint(x0, x1), rnd.randint(y0, y1)), fill=c)

    # Sky behind every window: gradient plus a few clouds (outside is kept simple).
    sky = Image.new("RGBA", (cw, ch))
    sd = ImageDraw.Draw(sky)
    for y in range(ch):
        t = min(1, max(0, (y - 18) / 74))
        sd.line([(0, y), (cw, y)], fill=(int(108 + 98 * t), int(166 + 60 * t), int(228 + 18 * t), 255))
    for cx, cy, rx, ry in ((70, 40, 16, 5), (100, 55, 22, 6), (205, 48, 26, 7), (250, 62, 18, 5), (130, 66, 14, 4), (30, 58, 12, 4), (292, 44, 12, 4)):
        sd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(236, 241, 250, 255))
        sd.ellipse([cx - rx + 4, cy - ry - 3, cx + rx - 6, cy + 1], fill=(250, 252, 255, 255))
    windows = [
        [(46, 25), (152, 43), (152, 74), (76, 79), (56, 88)],  # left windscreen
        [(0, 19), (26, 23), (50, 88), (24, 91), (0, 94)],       # left side window
    ]
    mask = Image.new("L", (cw, ch), 0)
    md = ImageDraw.Draw(mask)
    for poly in windows:
        md.polygon(poly, fill=255)
        md.polygon(mirror(poly), fill=255)
    im.paste(sky, (0, 0), mask)

    # Ceiling, overhead panel and the dark trim band above the windscreens.
    rect(d, 0, 0, cw - 1, 17, ceiling)
    d.polygon([(0, 18), (cw - 1, 18), (cw - 1, 21), (300, 26), (170, 28), (160, 27), (150, 28), (20, 26), (0, 21)], fill=trim)
    rect(d, 88, 0, 232, 17, (86, 96, 116))
    rect(d, 88, 17, 232, 18, gap)
    for x in range(122, 200, 1):
        if x % 26 == 0:
            rect(d, x, 0, x, 17, gap)
    for row, y in enumerate((2, 7, 12)):
        for x in range(92, 229, 5):
            if rnd.random() < 0.7:
                if rnd.random() < 0.35:
                    d.point((x, y), fill=knob)
                    d.point((x + 1, y + 1), fill=(150, 154, 162))
                else:
                    rect(d, x, y, x + 1, y + 2, switch)
                    if rnd.random() < 0.15:
                        d.point((x, y), fill=rnd.choice([amber, (240, 240, 240), (90, 220, 120)]))
    rect(d, 147, 27, 172, 38, (112, 122, 144))
    rect(d, 155, 32, 164, 34, gap)

    # Window frames: pillars between windows, centre post with its warning lights.
    for poly in ([(24, 22), (30, 22), (56, 88), (50, 89)], [(0, 94), (24, 91), (26, 96), (0, 100)]):
        d.polygon(poly, fill=frame)
        d.polygon(mirror(poly), fill=frame)
    d.polygon([(26, 22), (46, 24), (46, 27), (28, 25)], fill=frame_hi)
    d.polygon(mirror([(26, 22), (46, 24), (46, 27), (28, 25)]), fill=frame_hi)
    rect(d, 153, 38, 166, 74, frame)
    rect(d, 153, 38, 154, 74, frame_hi)
    rect(d, 157, 61, 158, 62, (230, 40, 40))
    d.point((160, 62), fill=(240, 240, 240))
    # Round air vents on the upper window frames.
    for cx in (30, cw - 31):
        d.ellipse([cx - 2, 31, cx + 2, 35], fill=frame_hi)
        d.point((cx, 33), fill=(70, 76, 90))

    # Glareshield: dark coaming, FCU and EFIS control panels with amber readouts.
    d.polygon([(56, 88), (76, 79), (160, 76), (244, 79), (264, 88), (264, 92), (56, 92)], fill=(48, 54, 66))
    rect(d, 86, 79, 234, 87, (112, 124, 148))
    rect(d, 126, 78, 191, 87, (66, 70, 82))
    for x in (144, 162, 180):
        rect(d, x - 4, 79, x + 3, 80, amber)
    for x in (130, 137, 151, 158, 168, 175, 186):
        d.point((x, 83), fill=knob)
        d.point((x, 84), fill=(120, 124, 132))
    for x0 in (126, 175):
        rect(d, x0, 78, x0 + 15, 87, (74, 78, 92))
        rect(d, x0 + 10, 79, x0 + 13, 80, amber)
        for kx in (x0 + 3, x0 + 7):
            d.point((kx, 83), fill=knob)
    for x in range(92, 124, 6):
        rect(d, x, 82, x + 1, 83, switch)
    for x in range(196, 230, 6):
        rect(d, x, 82, x + 1, 83, switch)

    # Main instrument panel with the six display bezels (screens drawn in JS).
    d.polygon([(64, 92), (256, 92), (256, 131), (64, 131)], fill=panel)
    rect(d, 64, 92, 256, 92, panel_hi)
    speckle((64, 93, 256, 130), panel, 900)
    # Six displays at their reference positions (x, y, w, h), each in a grey bezel:
    # PFD, ND | upper and lower ECAM | ND, PFD, plus the small standby instrument.
    for x, y, w, h in COCKPIT_SCREENS:
        rect(d, x - 2, y - 2, x + w + 1, y + h + 1, (70, 76, 90))
        rect(d, x - 1, y - 1, x + w, y + h, (30, 33, 40))
        rect(d, x, y, x + w - 1, y + h - 1, (6, 8, 10))
    for side in (1, -1):
        for x, y in ((86, 98), (89, 98), (86, 103), (90, 106), (139, 113), (139, 117)):
            px = x if side == 1 else cw - 1 - x
            d.point((px, y), fill=knob)
    rect(d, 172, 108, 174, 120, (220, 224, 230))
    rect(d, 171, 106, 175, 108, (240, 240, 244))
    d.ellipse([177, 114, 183, 120], fill=(34, 36, 44))
    d.point((180, 117), fill=(230, 230, 230))
    rect(d, 137, 122, 145, 129, (24, 27, 34))
    rect(d, 174, 122, 182, 129, (24, 27, 34))
    for x0 in (83, 117, 188, 222):
        rect(d, x0, 117, x0 + 13, 119, (226, 230, 236))
        rect(d, x0, 119, x0 + 13, 119, panel_lo)
    for side in (1, -1):
        cx = 74 if side == 1 else cw - 75
        d.ellipse([cx - 4, 113, cx + 4, 121], fill=(196, 190, 176))
        for k in range(-3, 4, 2):
            d.point((cx + k, 117), fill=(150, 144, 132))

    # Side consoles, EFB tablets and sidesticks.
    for poly in ([(24, 96), (64, 92), (64, 131), (40, 150), (20, 150)],):
        d.polygon(poly, fill=(70, 80, 100))
        d.polygon(mirror(poly), fill=(70, 80, 100))
    rect(d, 16, 88, 32, 109, (14, 15, 19))
    rect(d, 18, 90, 30, 107, (22, 24, 30))
    rect(d, 286, 88, 314, 113, (14, 15, 19))
    rect(d, 288, 90, 312, 111, (22, 24, 30))
    rect(d, 40, 120, 43, 134, (18, 18, 22))
    d.point((41, 120), fill=(230, 40, 40))
    rect(d, 36, 134, 47, 137, (50, 54, 62))
    rect(d, 271, 118, 275, 136, (16, 16, 20))
    rect(d, 272, 120, 273, 121, (230, 40, 40))
    for k in range(4):
        rect(d, 266 - k, 137 + k * 2, 280 + k, 138 + k * 2, (200 - k * 12, 204 - k * 12, 212 - k * 12))

    # Pedestal: MCDUs, thrust-lever quadrant (levers drawn in JS), radio panels.
    d.polygon([(132, 131), (188, 131), (213, 179), (107, 179)], fill=panel_lo)
    speckle((134, 146, 186, 179), panel_lo, 300)
    for x0 in (133, 172):
        rect(d, x0, 132, x0 + 14, 144, (40, 44, 54))
        rect(d, x0 + 1, 133, x0 + 13, 138, (8, 12, 10))
        for ky in range(140, 157, 3):
            for kx in range(x0, x0 + 15, 3):
                d.point((kx, ky), fill=(200, 204, 212))
    rect(d, 148, 146, 172, 179, (60, 66, 80))
    for y in range(148, 179, 3):
        rect(d, 151, y, 169, y, (80, 120, 96))
    rect(d, 158, 148, 162, 152, (44, 46, 54))
    for x0 in (124, 176):
        rect(d, x0, 158, x0 + 20, 179, (54, 60, 74))
        rect(d, x0 + 2, 160, x0 + 8, 161, amber)
        rect(d, x0 + 12, 160, x0 + 18, 161, amber)
        for ky in range(164, 179, 4):
            for kx in range(x0 + 2, x0 + 19, 4):
                d.point((kx, ky), fill=(190, 194, 200))

    # Seats: blue fabric backs at the edges, striped cushions and armrests in front.
    left_back = [(0, 24), (10, 26), (18, 60), (22, 180), (0, 180)]
    left_seat = [(48, 150), (110, 148), (116, 180), (52, 180)]
    left_arm = [(96, 146), (112, 146), (114, 180), (100, 180)]
    left_shell = [(0, 96), (20, 92), (54, 150), (60, 180), (0, 180)]
    for poly, colour in ((left_shell, seat_lo), (left_back, seat), (left_seat, seat), (left_arm, (40, 64, 98))):
        d.polygon(poly, fill=colour)
        d.polygon(mirror(poly), fill=colour)
    for y in range(152, 180, 2):
        rect(d, 54, y, 108, y, stripe)
        rect(d, cw - 1 - 108, y, cw - 1 - 54, y, stripe)
    d.line([(10, 26), (18, 60), (22, 179)], fill=seat_hi)
    d.line([(cw - 11, 26), (cw - 19, 60), (cw - 23, 179)], fill=seat_hi)

    im.save(f"{OUT}/cockpit.png")


# Game level (main page) -------------------------------------------------

LEVEL_W = 1440
GATES = (("D1", 760, C["tail"]), ("P2", 1000, C["red"]), ("A3", 1240, C["yellow"]))
INFO_X = 520


def seated_passengers(d, x0, x1, y, seed):
    """Fill about 40% of a seat row with people (head and shoulders above the seat back)."""
    rnd = random.Random(seed)
    for x in range(x0, x1, 9):
        if rnd.random() > 0.4:
            continue
        shirt, _, skin, hair, *_ = rnd.choice(CROWD)
        rect(d, x + 2, y - 5, x + 4, y - 2, skin)
        rect(d, x + 2, y - 6, x + 4, y - 5, hair)
        rect(d, x + 1, y - 1, x + 5, y + 5, shirt)


def concourse():
    """The playable concourse: check-in hall, info desk, then gates D1, P2, A3.
    Gate and desk x positions must match ZONES in assets/js/game.js."""
    # Far layer: sky, skyline and the runway. Moving traffic is drawn on top of this
    # in game.js, then the apron layer covers it, so planes pass behind the gates.
    back, d = new(False, LEVEL_W)
    sky(d, 100, seed=21)
    skyline(d, 95, seed=22)
    rect(d, 0, 96, LEVEL_W - 1, 99, (52, 56, 66))
    for x in range(0, LEVEL_W, 10):
        rect(d, x, 97, x + 4, 97, C["white"])
    for x in range(2, LEVEL_W, 8):
        d.point((x, 96), fill=C["amber"])
        d.point((x + 4, 99), fill=C["white"])
    back.save(f"{OUT}/concourse-sky.png")

    mid, d = new(True, LEVEL_W)
    tower(d, 430, 56, 99)
    for x, c in ((90, C["red"]), (230, C["tail"]), (330, C["yellow"])):
        parked_tail(d, x, 95, c)
    apron(d, 100, 112)
    for code, gx, colour in GATES:
        plane(d, gx - 168, 76, 118, 11, colour)
        rect(d, gx - 34, 72, gx - 14, 82, C["jet"])
        rect(d, gx - 34, 72, gx - 14, 73, C["fuse2"])
    mid.save(f"{OUT}/concourse-apron.png")

    front, d = new(True, LEVEL_W)
    edge = roof(d)
    glass_and_floor(d, edge)
    rect(d, 0, edge[0], 11, 110, C["roof2"])
    rect(d, LEVEL_W - 12, edge[-1], LEVEL_W - 1, 110, C["roof2"])
    hanging_sign(d, edge, 240, 34, "CHECK-IN")
    hanging_sign(d, edge, 640, 34, "GATES >")
    for cx in (150, 330):
        checkin_island(d, cx)

    # Info desk with an agent.
    hanging_sign(d, edge, INFO_X, 40, "INFO")
    rect(d, INFO_X - 9, 92, INFO_X - 6, 95, C["skin"])
    rect(d, INFO_X - 9, 91, INFO_X - 6, 91, C["hair"])
    rect(d, INFO_X - 10, 96, INFO_X - 5, 99, C["red"])
    rect(d, INFO_X - 30, 98, INFO_X + 30, 99, C["top"])
    rect(d, INFO_X - 28, 100, INFO_X + 28, 118, C["counter"])
    rect(d, INFO_X - 28, 106, INFO_X + 28, 108, C["blue"])
    rect(d, INFO_X - 28, 119, INFO_X + 28, 120, C["base"])

    for code, gx, _ in GATES:
        # Jet bridge door in the glass wall.
        rect(d, gx - 16, 66, gx + 16, 109, C["jet2"])
        rect(d, gx - 13, 69, gx + 13, 109, (24, 22, 20))
        rect(d, gx - 1, 69, gx, 109, C["jet2"])
        # Big hanging gate sign (kept below the lowest point of the roof).
        x0, x1 = gx - 22, gx + 22
        for rx in (x0 + 4, x1 - 4):
            rect(d, rx, edge[rx] + 3, rx, 33, C["beam"])
        rect(d, x0, 34, x1, 62, C["yellow"])
        rect(d, x0, 62, x1, 62, (200, 160, 0))
        text(d, gx - text_width("GATE") // 2, 37, "GATE", C["ink"])
        text(d, gx - text_width(code, 3) // 2, 45, code, C["ink"], 3)
        # Gate podium.
        rect(d, gx + 26, 98, gx + 58, 99, C["top"])
        rect(d, gx + 28, 100, gx + 56, 118, C["counter"])
        rect(d, gx + 28, 106, gx + 56, 108, C["yellow"])
        rect(d, gx + 28, 119, gx + 56, 120, C["base"])
        seat_row(d, gx + 70, gx + 170, 112)
        seated_passengers(d, gx + 70, gx + 170, 112, seed=gx)
    for x in (442, 600, 880, 1120, 1380):
        palm(d, x, 128)
    front.save(f"{OUT}/concourse-front.png")


def player():
    """You, in a pilot's uniform: captain's cap with a gold badge, white short-sleeved
    shirt with gold-striped epaulettes, wings and a black tie, black belt.
    Frame 0 idle, 1-4 walk. 16x32 each, facing right."""
    fw, fh = 16, 32
    navy, navy_hi, cap = (28, 36, 66), (48, 60, 102), (18, 22, 40)
    gold, white, tie = (232, 184, 64), (236, 236, 240), (14, 14, 18)
    shade = (200, 204, 214)
    pants, shoe, shine = (22, 26, 44), (10, 10, 12), (70, 74, 86)
    skin, hair = (176, 120, 82), (24, 20, 18)
    legs = [(0, 0), (2, -2), (0, 0), (-2, 2), (0, 0)]
    arms = [0, 1, 0, -1, 0]
    bob = [0, 0, 1, 0, 1]
    im = Image.new("RGBA", (fw * 5, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for f in range(5):
        o, b = f * fw, bob[f]
        # Captain's cap: crown, band, peak to the front, gold badge.
        rect(d, o + 5, 0 + b, o + 10, 1 + b, cap)
        rect(d, o + 4, 2 + b, o + 11, 2 + b, navy_hi)
        rect(d, o + 7, 3 + b, o + 12, 3 + b, tie)
        rect(d, o + 8, 1 + b, o + 9, 1 + b, gold)
        # Head with a little hair showing under the cap at the back.
        rect(d, o + 5, 3 + b, o + 6, 5 + b, hair)
        rect(d, o + 5, 4 + b, o + 10, 9 + b, skin)
        rect(d, o + 5, 4 + b, o + 5, 5 + b, hair)
        d.point((o + 9, 6 + b), fill=hair)
        rect(d, o + 8, 8 + b, o + 9, 8 + b, (120, 76, 50))
        rect(d, o + 7, 10 + b, o + 8, 10 + b, skin)
        # White shirt with a shaded back edge, black tie, gold wings and a belt.
        rect(d, o + 4, 11 + b, o + 11, 20 + b, white)
        rect(d, o + 4, 12 + b, o + 4, 20 + b, shade)
        rect(d, o + 7, 11 + b, o + 8, 11 + b, shade)
        rect(d, o + 7, 12 + b, o + 8, 17 + b, tie)
        rect(d, o + 9, 14 + b, o + 10, 14 + b, gold)
        rect(d, o + 4, 21 + b, o + 11, 21 + b, tie)
        d.point((o + 8, 21 + b), fill=gold)
        # Epaulettes: navy with a gold stripe on each shoulder.
        rect(d, o + 4, 11 + b, o + 5, 11 + b, navy)
        rect(d, o + 10, 11 + b, o + 11, 11 + b, navy)
        d.point((o + 5, 11 + b), fill=gold)
        d.point((o + 10, 11 + b), fill=gold)
        # Arms swing: short white sleeves, then bare forearms.
        a = arms[f]
        rect(d, o + 3, 12 + b, o + 3, 14 + b, white)
        rect(d, o + 3, 15 + b, o + 3, 20 + b + a, skin)
        rect(d, o + 12, 12 + b, o + 12, 14 + b, white)
        rect(d, o + 12, 15 + b, o + 12, 20 + b - a, skin)
        # Legs: upper half shifts half as far as lower half. Polished shoes.
        for base, dx in ((5, legs[f][0]), (9, legs[f][1])):
            rect(d, o + base + dx // 2, 22 + b, o + base + 1 + dx // 2, 25 + b, pants)
            rect(d, o + base + dx, 26 + b, o + base + 1 + dx, 29, pants)
            rect(d, o + base + dx, 30, o + base + 2 + dx, 31, shoe)
            d.point((o + base + 2 + dx, 30), fill=shine)
    im.save(f"{OUT}/player.png")


def portrait():
    """32x32 pixel portrait from your ID-style photo, for dialog boxes."""
    src = Image.open(os.path.join("images", "face", "face-2.jpg")).convert("RGB")
    face = src.crop((125, 35, 365, 275)).resize((32, 32), Image.BOX)
    face = face.quantize(colors=14, method=Image.Quantize.MEDIANCUT).convert("RGBA")
    face.save(f"{OUT}/portrait.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    hall()
    gate()
    apron_view()
    window()
    walker("walker-a", C["red"], bag=C["yellow"])
    walker("walker-b", C["blue"])
    walker("walker-c", C["white"], bag=C["pants"])
    far_plane()
    pushback()
    photographer()
    concourse()
    cockpit()
    stand_sheets()
    marshaller()
    crowd_sheet()
    crowd_dark_sheet()
    crew_sheet()
    flight_crew_sheet()
    traffic_sheet()
    player()
    portrait()
    print("Wrote", len(os.listdir(OUT)), "files to", OUT)
