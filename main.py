"""World News - Saturday, 21 November 2026: one-image infographic.

Pure Python standard library only (os, pathlib, struct, zlib). No PIL,
no system fonts, no network, no file reads at run time. The program draws
a 1024x1024 newspaper-style infographic with its own minimal PNG encoder
and its own embedded 5x7 bitmap font, and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).

Run: python3 -P -s main.py
"""

import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY = (20, 38, 63)
INK = (26, 26, 26)
PAPER = (247, 243, 234)
CARD = (255, 255, 255)
GREY_LINE = (210, 205, 195)
MUTED = (110, 108, 100)
RED = (192, 57, 43)
WHITE = (255, 255, 255)
LIGHT = (226, 232, 240)

ACCENTS = {
    "WAR": (192, 57, 43),
    "HEALTH": (15, 118, 110),
    "SOCIETY": (109, 40, 217),
    "TECH": (30, 90, 168),
    "POLITICS": (180, 120, 10),
    "CONFLICT": (194, 94, 22),
}

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows, one int per row, bit 4 = leftmost column.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "—": (0, 0, 0, 0x1F, 0, 0, 0),
    "·": (0, 0, 0, 0x04, 0, 0, 0),
}

# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set_px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                j = base + (xx - x0) * 3
                self.px[j], self.px[j + 1], self.px[j + 2] = c

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set_px(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set_px(xx, yy, c)

    def ring(self, cx, cy, r, c, thick=3):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d2 <= (r + thick) * (r + thick):
                    self.set_px(xx, yy, c)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, c):
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    t = (yy - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.fill_rect(xa, yy, xb - xa + 1, 1, c)

    # ------------------------------------------------------------ text
    def text_w(self, s, scale):
        return len(s) * 6 * scale

    def draw_text(self, x, y, s, scale, c, bold=False):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
                        if bold:
                            self.fill_rect(cx + col * scale + 1,
                                           y + row * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def wrap(self, s, max_w, scale):
        lines, cur = [], ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def draw_wrapped(self, x, y, s, scale, c, max_w, line_h, bold=False,
                     max_lines=99):
        lines = self.wrap(s, max_w, scale)[:max_lines]
        for i, ln in enumerate(lines):
            self.draw_text(x, y + i * line_h, ln, scale, c, bold=bold)
        return len(lines)

# ------------------------------------------------------------- PNG output
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    Path(path).write_bytes(png)
    return len(png)

# ------------------------------------------------------------------- icons
def icon_war(cv, x, y, c):
    # missile flying up-right: body, nose, fins, flame
    cv.line(x + 8, y + 52, x + 44, y + 16, c, thick=5)
    cv.fill_triangle(x + 44, y + 16, x + 56, y + 10, x + 50, y + 26, c)
    cv.fill_triangle(x + 10, y + 46, x + 22, y + 50, x + 16, y + 58, c)
    cv.fill_triangle(x + 16, y + 40, x + 8, y + 52, x + 22, y + 48, c)
    cv.line(x + 4, y + 56, x + 0, y + 62, (240, 140, 40), thick=3)


def icon_health(cv, x, y, c):
    # capsule pill, tilted: thick diagonal body, round ends, white band
    cv.line(x + 20, y + 24, x + 44, y + 40, c, thick=20)
    cv.fill_circle(x + 20, y + 24, 10, c)
    cv.fill_circle(x + 44, y + 40, 10, c)
    cv.line(x + 26, y + 38, x + 38, y + 26, WHITE, thick=4)


def icon_society(cv, x, y, c):
    # three heads over shoulders: a crowd
    for hx in (14, 32, 50):
        cv.fill_circle(x + hx, y + 20, 8, c)
        cv.fill_rect(x + hx - 11, y + 30, 22, 14, c)
    cv.fill_rect(x + 3, y + 44, 58, 4, c)


def icon_tech(cv, x, y, c):
    # database stack: body with a light top face and two white shelves,
    # struck by a yellow lightning bolt
    cv.fill_rect(x + 14, y + 12, 36, 40, c)
    cv.fill_rect(x + 14, y + 12, 36, 9, LIGHT)
    cv.fill_rect(x + 14, y + 21, 36, 2, c)
    cv.fill_rect(x + 14, y + 29, 36, 3, WHITE)
    cv.fill_rect(x + 14, y + 41, 36, 3, WHITE)
    cv.line(x + 36, y + 8, x + 26, y + 30, (240, 200, 40), thick=4)
    cv.line(x + 26, y + 30, x + 36, y + 30, (240, 200, 40), thick=4)
    cv.line(x + 36, y + 30, x + 26, y + 54, (240, 200, 40), thick=4)


def icon_politics(cv, x, y, c):
    # flag on a pole
    cv.vline(x + 12, y + 8, 48, c)
    cv.fill_rect(x + 12, y + 8, 40, 26, c)
    cv.fill_rect(x + 18, y + 14, 28, 4, WHITE)
    cv.fill_rect(x + 18, y + 22, 20, 4, WHITE)
    cv.fill_circle(x + 12, y + 8, 4, c)


def icon_conflict(cv, x, y, c):
    # explosion starburst
    cx, cy = x + 32, y + 32
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 10, 30
        x1 = cx + int(r1 * math.cos(math.radians(ang)))
        y1 = cy + int(r1 * math.sin(math.radians(ang)))
        x2 = cx + int(r2 * math.cos(math.radians(ang)))
        y2 = cy + int(r2 * math.sin(math.radians(ang)))
        cv.line(x1, y1, x2, y2, c, thick=4)
    cv.fill_circle(cx, cy, 11, c)
    cv.fill_circle(cx, cy, 6, (240, 200, 40))


ICONS = {
    "WAR": icon_war,
    "HEALTH": icon_health,
    "SOCIETY": icon_society,
    "TECH": icon_tech,
    "POLITICS": icon_politics,
    "CONFLICT": icon_conflict,
}

# ------------------------------------------------------------------- stories
CARDS = [
    {
        "tag": "WAR",
        "headline": "RUSSIA'S BIGGEST BARRAGE YET",
        "body": "RUSSIA FIRED 400+ DRONES AND 110 MISSILES AT UKRAINE "
                "OVERNIGHT. 8 KILLED IN KYIV. MISSILES ALSO LANDED IN POLAND.",
        "stat": "KRYVYI RIH: 2 KILLED, 42 WOUNDED",
    },
    {
        "tag": "HEALTH",
        "headline": "CANCER PILL BREAKTHROUGH",
        "body": "A TRIAL OF THE PILL DARAXONRASIB MADE PANCREATIC CANCER "
                "UNDETECTABLE ON SCANS IN ONE IN 12 PATIENTS.",
        "stat": "1 IN 12 PATIENTS - TUMOURS GONE",
    },
    {
        "tag": "SOCIETY",
        "headline": "GEN Z PROTESTS SWEEP EUROPE",
        "body": "GEN Z PROTESTS SPREAD ACROSS 25 EUROPEAN COUNTRIES IN A "
                "COORDINATED WAVE OF STREET DEMONSTRATIONS.",
        "stat": "PROTESTS IN 25 COUNTRIES",
    },
    {
        "tag": "TECH",
        "headline": "FBI CRIME DATABASE HACKED",
        "body": "THE FBI'S CRIMINAL DATABASE WAS REPORTEDLY HACKED AS US "
                "OUTAGES CONTINUE. IT IS THE SECOND RECENT CYBERATTACK ON "
                "THE DATABASE.",
        "stat": "SECOND HACK IN WEEKS",
    },
    {
        "tag": "POLITICS",
        "headline": "DENMARK EXPELS RUSSIAN DIPLOMAT",
        "body": "DENMARK EXPELLED A RUSSIAN DIPLOMAT OVER A PLOT TO "
                "ASSASSINATE A UKRAINIAN RAPPER.",
        "stat": "PLOT TARGETED A RAPPER",
    },
    {
        "tag": "CONFLICT",
        "headline": "SALVADORANS KILLED IN HAITI",
        "body": "TWO SALVADORAN SOLDIERS SERVING IN HAITI WERE KILLED BY "
                "EXPLOSIVES, THE MILITARY SAID.",
        "stat": "2 SOLDIERS KILLED",
    },
]

FOOTER = [
    "COP31 CLIMATE TALKS RUN INTO OVERTIME OVER FOSSIL FUELS",
    "TRUMP THREATENS BAN ON US FIRMS BUILDING AI CENTRES ABROAD",
]

# --------------------------------------------------------------------- draw
def draw_card(cv, x, y, w, h, card):
    accent = ACCENTS[card["tag"]]
    cv.fill_rect(x, y, w, h, CARD)
    # thin grey border
    cv.hline(x, y, w, GREY_LINE)
    cv.hline(x, y + h - 1, w, GREY_LINE)
    cv.vline(x, y, h, GREY_LINE)
    cv.vline(x + w - 1, y, h, GREY_LINE)
    # coloured top bar
    cv.fill_rect(x, y, w, 8, accent)
    # tag box
    tag = card["tag"]
    tw = cv.text_w(tag, 2) + 16
    cv.fill_rect(x + 16, y + 20, tw, 24, accent)
    cv.draw_text(x + 24, y + 25, tag, 2, WHITE, bold=True)
    # icon, top right
    ICONS[card["tag"]](cv, x + w - 82, y + 16, accent)
    # headline, 2 lines max, width leaves the icon zone clear
    hy = y + 56
    n = cv.draw_wrapped(x + 16, hy, card["headline"], 2, INK,
                        w - 32 - 80, 17, bold=True, max_lines=2)
    # body
    by = hy + n * 17 + 10
    cv.draw_wrapped(x + 16, by, card["body"], 2, INK, w - 32, 17,
                    max_lines=4)
    # stat strip
    sy = y + h - 32
    cv.hline(x + 16, sy - 8, w - 32, GREY_LINE)
    cv.draw_text(x + 16, sy, card["stat"], 2, accent, bold=True)


def draw():
    cv = Canvas(W, H, PAPER)
    # header
    cv.fill_rect(0, 0, W, 112, NAVY)
    cv.draw_text(24, 16, "WORLD NEWS", 4, WHITE, bold=True)
    cv.draw_text(24, 66, "SATURDAY, 21 NOVEMBER 2026", 2, LIGHT)
    # LIVE badge + story count, right side
    cv.fill_rect(W - 24 - 140, 20, 140, 44, RED)
    cv.draw_text(W - 24 - 140 + 34, 30, "LIVE", 3, WHITE, bold=True)
    cv.draw_text(W - 24 - 104, 74, "6 STORIES", 2, LIGHT)
    # red rule under header
    cv.fill_rect(0, 112, W, 6, RED)
    # cards grid 2 x 3
    cw, ch, gx, gy = 478, 252, 20, 16
    for i, card in enumerate(CARDS):
        cx = 24 + (i % 2) * (cw + gx)
        cy = 132 + (i // 2) * (ch + gy)
        draw_card(cv, cx, cy, cw, ch, card)
    # footer
    fy = 940
    cv.hline(24, fy - 10, W - 48, GREY_LINE)
    for i, item in enumerate(FOOTER):
        yy = fy + i * 30
        cv.fill_rect(24, yy + 4, 12, 12, RED)
        cv.draw_text(48, yy, item, 2, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out = Path(out_dir) / "entry.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    size = write_png(draw(), out)
    print(f"wrote {out} ({size} bytes)")


if __name__ == "__main__":
    main()
