"""Sum up 20 November 2026 in one image.

A pure-stdlib Python program. It draws a newspaper front page for
Friday 20 November 2026 and writes it, deterministically, to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).

No network, no randomness, no time, no external files: the same run
always writes the same bytes.

Stories, all reported on 20 November 2026:
  * Russia launches a major overnight missile attack on Kyiv.
    Three bridges across the Dnipro are struck. Kyiv's mayor
    reports 8 people killed and 28 injured across nine regions.
    Ukraine's drones strike the Dorogobuzh chemical plant in
    Russia's Smolensk region.
  * A day after the Shenzhen summit, Germany's Chancellor Merz
    rejects a new Yalta deal over Europe's future, saying Europe
    will not accept a settlement made without it. The EU and the
    UK meet in Brussels for their second summit.
  * COP31 in Antalya: the draft deal drops any call to phase out
    fossil fuels.
  * A Houthi missile damages the sovereign wealth fund tower in
    Riyadh. In the Strait of Hormuz a tanker catches fire after
    hitting a mine, as the Iran war enters its ninth month.
  * Markets fall for a fifth straight day. The S and P 500 loses
    about 2 percent and Japan's Nikkei falls 4.8 percent after
    Anthropic's debut.
  * Israeli forces cross the Yellow Line ceasefire boundary in
    central Gaza, the first such incursion since the truce.
Also in the ticker: 34 suspected gang members killed in Haiti,
Kenya discharges its last Ebola patient, Cyclone Akvan hits
India's east coast, Denmark approves a Greenland security deal
with the US, and Russia is reported to have violated Poland's
airspace.
"""

import math
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (20, 33, 61)
RED = (193, 39, 45)
GOLD = (217, 164, 65)
TEAL = (15, 118, 110)
BLUE = (37, 99, 235)
WHITE = (255, 255, 255)
GREY = (90, 96, 110)
LIGHT = (232, 226, 210)
DARK = (13, 22, 40)
SKY = (178, 214, 235)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, pixels):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        start = y * W * 3
        raw += pixels[start:start + W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    Path(path).write_bytes(png)


class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER * W * H)

    def set(self, x, y, colour):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, colour)

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, colour)

    def ring(self, cx, cy, r, t, colour):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r + t:
                    self.set(xx, yy, colour)

    def line(self, x0, y0, x1, y1, t, colour):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            self.disc(x, y, max(t // 2, 1), colour)

    def poly(self, points, colour):
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
                if y0 == y1:
                    continue
                if min(y0, y1) <= y < max(y0, y1):
                    xs.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(a, b + 1):
                    self.set(x, y, colour)


FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".....", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".....", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "-": [".....", ".....", ".....", ".####", ".....", ".....", "....."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "(": ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ")": ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    "!": [".#...", ".#...", ".#...", ".#...", ".#...", ".....", ".#..."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "'": [".#...", ".#...", ".....", ".....", ".....", ".....", "....."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "%": ["#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, colour):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row, line in enumerate(glyph):
            for col, cell in enumerate(line):
                if cell in ("1", "#"):
                    cv.rect(cx + col * scale, y + row * scale,
                            scale, scale, colour)
        cx += 6 * scale
    return cx


def draw_centred(cv, cx, y, text, scale, colour):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, colour)


def wrap(cv, x, y, width, text, scale, colour, gap=6):
    words = text.split()
    line, cy = "", y
    for word in words:
        trial = (line + " " + word).strip()
        if text_width(trial, scale) <= width or not line:
            line = trial
        else:
            draw_text(cv, x, cy, line, scale, colour)
            cy += 7 * scale + gap
            line = word
    if line:
        draw_text(cv, x, cy, line, scale, colour)
        cy += 7 * scale + gap
    return cy


def panel(cv, x, y, w, h, label, accent):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 6, accent)
    cv.rect(x, y, 2, h, LIGHT)
    cv.rect(x + w - 2, y, 2, h, LIGHT)
    cv.rect(x, y + h - 2, w, 2, LIGHT)
    draw_text(cv, x + 16, y + 16, label, 2, accent)


def draw_masthead(cv):
    cv.rect(28, 24, 968, 126, DARK)
    cv.rect(28, 24, 968, 6, RED)
    draw_centred(cv, 512, 44, "THE WORLD IN ONE DAY", 4, GOLD)
    draw_centred(cv, 512, 78, "20 NOVEMBER 2026", 7, WHITE)
    draw_centred(cv, 512, 128, "FRIDAY  -  WORLD NEWS  -  ONE IMAGE", 2, LIGHT)


def draw_kyiv(cv, x, y, w, h):
    panel(cv, x, y, w, h, "KYIV  -  BRIDGES UNDER FIRE", RED)
    # River, bridge, and a blast over the middle span.
    cv.rect(x + 16, y + 120, w - 32, 54, SKY)
    cv.line(x + 16, y + 120, x + w - 16, y + 120, 4, INK)
    cv.line(x + 60, y + 120, x + 60, y + 66, 5, INK)
    cv.line(x + w - 60, y + 120, x + w - 60, y + 66, 5, INK)
    cv.line(x + 60, y + 66, x + w // 2, y + 44, 5, INK)
    cv.line(x + w - 60, y + 66, x + w // 2, y + 44, 5, INK)
    cv.disc(x + w // 2, y + 66, 26, GOLD)
    cv.disc(x + w // 2, y + 66, 14, RED)
    for a in range(0, 360, 45):
        dx = int(34 * math.cos(math.radians(a)))
        dy = int(34 * math.sin(math.radians(a)))
        cv.line(x + w // 2, y + 66, x + w // 2 + dx, y + 66 + dy, 3, GOLD)
    cv.line(x + 24, y + 142, x + w - 24, y + 142, 3, BLUE)
    cv.line(x + 24, y + 156, x + w - 24, y + 156, 3, BLUE)
    wrap(cv, x + 16, y + 196, w - 32,
         "RUSSIA HITS KYIV BRIDGES IN OVERNIGHT ATTACK", 3, INK, gap=4)
    wrap(cv, x + 16, y + 282, w - 32,
         "MAYOR: 8 KILLED, 28 HURT. UKRAINE HITS A CHEMICAL PLANT IN RUSSIA.",
         2, GREY, gap=4)


def draw_europe(cv, x, y, w, h):
    panel(cv, x, y, w, h, "EUROPE  -  AFTER SHENZHEN", BLUE)
    # A ring of stars for Europe, with a table below.
    cx = x + w // 2
    cv.disc(cx, y + 92, 52, BLUE)
    for a in range(0, 360, 30):
        sx = int(cx + 38 * math.cos(math.radians(a)))
        sy = int(y + 92 + 38 * math.sin(math.radians(a)))
        cv.disc(sx, sy, 4, GOLD)
    cv.disc(cx, y + 92, 10, GOLD)
    cv.rect(x + 40, y + 168, w - 80, 6, INK)
    wrap(cv, x + 16, y + 190, w - 32,
         "GERMANY: NO NEW YALTA", 3, INK, gap=4)
    wrap(cv, x + 16, y + 246, w - 32,
         "MERZ: NO DEAL WITHOUT EUROPE. EU AND UK MEET IN BRUSSELS.",
         2, GREY, gap=4)


def draw_cop31(cv, x, y, w, h):
    panel(cv, x, y, w, h, "ANTALYA  -  CLIMATE", TEAL)
    cv.disc(x + 58, y + 78, 26, GOLD)
    for a in range(0, 360, 45):
        dx = int(38 * math.cos(math.radians(a)))
        dy = int(38 * math.sin(math.radians(a)))
        cv.line(x + 58 + dx, y + 78 + dy,
                x + 58 + int(50 * math.cos(math.radians(a))),
                y + 78 + int(50 * math.sin(math.radians(a))), 4, GOLD)
    wrap(cv, x + 104, y + 52, w - 120,
         "COP31 DRAFT DROPS FOSSIL FUEL PHASE-OUT", 3, INK, gap=4)
    wrap(cv, x + 16, y + 128, w - 32,
         "NEGOTIATORS CUT THE CALL TO END FOSSIL FUEL USE.", 2, GREY, gap=4)


def draw_riyadh(cv, x, y, w, h):
    panel(cv, x, y, w, h, "RIYADH AND HORMUZ", RED)
    # Tower on the left, tanker on waves on the right side below.
    cv.rect(x + 30, y + 48, 44, 96, INK)
    cv.rect(x + 38, y + 40, 28, 8, GOLD)
    cv.line(x + 96, y + 40, x + 52, y + 84, 4, RED)
    cv.disc(x + 52, y + 84, 10, RED)
    cv.poly([(x + 130, y + 112), (x + 210, y + 112), (x + 196, y + 136),
             (x + 144, y + 136)], INK)
    cv.line(x + 124, y + 148, x + 216, y + 148, 3, BLUE)
    wrap(cv, x + 236, y + 52, w - 252,
         "MISSILE HITS RIYADH TOWER", 3, INK, gap=4)
    wrap(cv, x + 236, y + 108, w - 252,
         "TANKER HITS A MINE IN HORMUZ AND CATCHES FIRE.", 2, GREY, gap=4)


def draw_markets(cv, x, y, w, h):
    panel(cv, x, y, w, h, "MARKETS  -  THE SELL-OFF", GOLD)
    # A falling chart.
    cv.rect(x + 24, y + 44, 200, 104, LIGHT)
    cv.line(x + 32, y + 56, x + 72, y + 72, 4, RED)
    cv.line(x + 72, y + 72, x + 112, y + 68, 4, RED)
    cv.line(x + 112, y + 68, x + 152, y + 104, 4, RED)
    cv.line(x + 152, y + 104, x + 208, y + 132, 4, RED)
    cv.poly([(x + 208, y + 132), (x + 192, y + 130), (x + 204, y + 114)], RED)
    wrap(cv, x + 236, y + 52, w - 252,
         "STOCKS FALL FIFTH DAY", 3, INK, gap=4)
    wrap(cv, x + 236, y + 108, w - 252,
         "NIKKEI DOWN 4.8 PC. S AND P 500 DOWN ABOUT 2 PC.", 2, GREY, gap=4)


def draw_gaza(cv, x, y, w, h):
    panel(cv, x, y, w, h, "GAZA  -  THE CEASEFIRE", RED)
    cv.line(x + 24, y + 92, x + 220, y + 92, 4, GOLD)
    cv.line(x + 60, y + 140, x + 180, y + 50, 5, RED)
    cv.poly([(x + 180, y + 50), (x + 158, y + 52), (x + 176, y + 72)], RED)
    cv.line(x + 24, y + 152, x + 220, y + 152, 3, GREY)
    wrap(cv, x + 236, y + 52, w - 252,
         "ISRAEL CROSSES LINE", 3, INK, gap=4)
    wrap(cv, x + 236, y + 108, w - 252,
         "YELLOW LINE IN CENTRAL GAZA. FIRST INCURSION SINCE THE TRUCE.",
         2, GREY, gap=4)


def main():
    cv = Canvas()
    draw_masthead(cv)
    draw_kyiv(cv, 28, 162, 560, 358)
    draw_europe(cv, 612, 162, 384, 358)
    draw_cop31(cv, 28, 532, 472, 168)
    draw_riyadh(cv, 524, 532, 472, 168)
    draw_markets(cv, 28, 712, 472, 168)
    draw_gaza(cv, 524, 712, 472, 168)
    cv.rect(28, 892, 968, 108, INK)
    draw_text(cv, 44, 908, "ALSO ON 20 NOVEMBER:", 2, GOLD)
    wrap(cv, 44, 932, 968 - 32,
         "HAITI: 34 KILLED  -  KENYA: LAST EBOLA PATIENT OUT  -  CYCLONE AKVAN HITS INDIA  -  DENMARK GREENLAND DEAL  -  POLAND AIRSPACE VIOLATED",
         2, WHITE, gap=3)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    Path(out).mkdir(parents=True, exist_ok=True)
    write_png(Path(out) / "entry.png", cv.px)


if __name__ == "__main__":
    main()
