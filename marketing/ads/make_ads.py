#!/usr/bin/env python3
"""Render the Practical AI Co. website-services video ads (1080x1920, 30fps).

Usage:
  python3 make_ads.py               # render all ads to out/
  python3 make_ads.py 1 3           # render ads 1 and 3
  python3 make_ads.py --stills 2    # save preview PNGs of ad 2 (no video)

Needs: Python 3, Pillow, numpy, ffmpeg on PATH.
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ads import ADS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FD = os.path.join(HERE, "fonts")
W, H, FPS = 1080, 1920, 30

NAVY = (6, 13, 26)
PANEL = (12, 24, 42)
PANEL2 = (20, 38, 62)
LINE = (40, 70, 95)
TEAL = (20, 184, 166)
SKY = (14, 165, 233)
WHITE = (236, 242, 248)
MUTED = (148, 163, 184)
DIM = (90, 105, 125)
RED = (248, 113, 113)

# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def eo(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3

def eob(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def rgba(c, a=1.0):
    return (c[0], c[1], c[2], int(255 * clamp(a)))

# ---------------------------------------------------------------- fonts
# Static weights from the @fontsource npm packages (see README.md).
FONTS = {  # kind: (file, weight for variable fonts)
    "display": ("display.woff", 800),
    "body": ("body.woff", 500),
    "bodyb": ("bodyb.woff", 700),
    "mono": ("mono.woff", 500),
}
FALLBACK = {
    "display": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "body": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "bodyb": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
}
_fc = {}

def F(kind, size):
    key = (kind, size)
    if key in _fc:
        return _fc[key]
    fname, weight = FONTS[kind]
    path = os.path.join(FD, fname)
    f = None
    if os.path.exists(path):
        try:
            f = ImageFont.truetype(path, size)
            try:
                vals = []
                for ax in f.get_variation_axes():
                    nm = ax.get("name", b"")
                    nm = nm.decode() if isinstance(nm, bytes) else str(nm)
                    vals.append(weight if "weight" in nm.lower() else ax.get("default", 100))
                f.set_variation_by_axes(vals)
            except Exception:
                pass
        except Exception:
            f = None
    if f is None:
        f = ImageFont.truetype(FALLBACK[kind], size)
    _fc[key] = f
    return f

# ---------------------------------------------------------------- canvas
class C:
    """Thin drawing wrapper that supports per-element opacity."""

    def __init__(self, im):
        self.im = im
        self.d = ImageDraw.Draw(im)

    def _op(self, box, alpha, fn):
        x0, y0, x1, y1 = [int(v) for v in box]
        x0, y0 = max(0, x0 - 4), max(0, y0 - 4)
        x1, y1 = min(W, x1 + 4), min(H, y1 + 4)
        if x1 <= x0 or y1 <= y0 or alpha <= 0.004:
            return
        if alpha >= 0.996:
            fn(self.d, 0, 0)
            return
        tmp = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        fn(ImageDraw.Draw(tmp), -x0, -y0)
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * alpha)))
        self.im.alpha_composite(tmp, (x0, y0))

    def text(self, x, y, s, font, color=WHITE, alpha=1.0, anchor="la"):
        box = self.d.textbbox((x, y), s, font=font, anchor=anchor)
        self._op(box, alpha, lambda d, ox, oy: d.text((x + ox, y + oy), s, font=font, fill=rgba(color), anchor=anchor))

    def spaced(self, x, y, s, font, color=MUTED, alpha=1.0, sp=6, center=False):
        widths = [font.getlength(ch) for ch in s]
        total = sum(widths) + sp * (len(s) - 1)
        cx = x - total / 2 if center else x
        box = (cx, y - 4, cx + total, y + font.size * 1.3)

        def fn(d, ox, oy):
            xx = cx
            for ch, w in zip(s, widths):
                d.text((xx + ox, y + oy), ch, font=font, fill=rgba(color))
                xx += w + sp

        self._op(box, alpha, fn)
        return total

    def rrect(self, box, r, fill=None, outline=None, width=2, alpha=1.0):
        self._op(box, alpha, lambda d, ox, oy: d.rounded_rectangle(
            (box[0] + ox, box[1] + oy, box[2] + ox, box[3] + oy), r,
            fill=rgba(fill) if fill else None, outline=rgba(outline) if outline else None, width=width))

    def ellipse(self, box, fill=None, outline=None, width=2, alpha=1.0):
        self._op(box, alpha, lambda d, ox, oy: d.ellipse(
            (box[0] + ox, box[1] + oy, box[2] + ox, box[3] + oy),
            fill=rgba(fill) if fill else None, outline=rgba(outline) if outline else None, width=width))

    def line(self, pts, color, width=3, alpha=1.0):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        box = (min(xs) - width, min(ys) - width, max(xs) + width, max(ys) + width)
        self._op(box, alpha, lambda d, ox, oy: d.line([(p[0] + ox, p[1] + oy) for p in pts],
                                                      fill=rgba(color), width=width, joint="curve"))

    def check(self, cx, cy, r, alpha=1.0, fill=TEAL, tick=NAVY):
        self.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, alpha=alpha)
        self.line([(cx - r * .45, cy + r * .02), (cx - r * .1, cy + r * .36), (cx + r * .5, cy - r * .34)],
                  tick, width=max(3, int(r * .22)), alpha=alpha)

# ---------------------------------------------------------------- rich text
def parse_rich(text):
    """'Hello *world*' -> lines of [(word, accent)]. \n forces a break."""
    out = []
    for raw in text.split("\n"):
        words = []
        acc = False
        for w in raw.split(" "):
            if not w:
                continue
            start = w.startswith("*")
            w2 = w.lstrip("*")
            end = w2.endswith("*") or w2.rstrip(".,!?:").endswith("*")
            if start:
                acc = True
            word = w2.replace("*", "")
            words.append((word, acc))
            if end:
                acc = False
        out.append(words)
    return out

def layout(text, font, maxw):
    lines = []
    space = font.getlength(" ")
    for para in parse_rich(text):
        cur, cw = [], 0
        for word, acc in para:
            ww = font.getlength(word)
            add = ww if not cur else cw + space + ww
            if cur and add > maxw:
                lines.append((cur, cw))
                cur, cw = [(word, acc, ww)], ww
            else:
                cur.append((word, acc, ww))
                cw = add
        lines.append((cur, cw))
    return lines

def rich_height(text, font, maxw, lh=1.12):
    return len(layout(text, font, maxw)) * font.size * lh

def draw_rich(c, text, font, x, y, maxw, p=1.0, alpha=1.0, color=WHITE, accent=TEAL,
              align="left", lh=1.12, rise=34, underline=True):
    """Word-by-word reveal. p in [0,1] is reveal progress. Returns height."""
    lines = layout(text, font, maxw)
    n = sum(len(l[0]) for l in lines)
    space = font.getlength(" ")
    s = p * (n + 1.2)
    i = 0
    yy = y
    for words, lw in lines:
        xx = x if align == "left" else x + (maxw - lw) / 2
        for word, acc, ww in words:
            wp = eo(s - i)
            if wp > 0:
                c.text(xx, yy + (1 - wp) * rise, word, font, accent if acc else color, alpha * wp)
                if acc and underline and wp > 0.5:
                    up = eo((s - i - 0.5) * 1.4)
                    uy = yy + font.size * 1.06
                    c.rrect((xx, uy, xx + ww * up + 1, uy + max(5, font.size // 14)), 3, fill=accent, alpha=alpha * 0.55)
            xx += ww + space
            i += 1
        yy += font.size * lh
    return yy - y

def wrap_plain(text, font, maxw):
    return [" ".join(w for w, _, _ in l[0]) for l in layout(text.replace("*", ""), font, maxw)]

# ---------------------------------------------------------------- scenes
X0, MAXW = 90, 900

def sc_hook(c, t, d, p):
    size = p.get("size", 104)
    f = F("display", size)
    h = rich_height(p["text"], f, MAXW, 1.08)
    y = 900 - h / 2
    draw_rich(c, p["text"], f, X0, y, MAXW, p=clamp(t / min(1.5, d * 0.5)), lh=1.08, rise=50)

def sc_statement(c, t, d, p):
    fe, fh, fb = F("mono", 28), F("display", p.get("size", 80)), F("body", 42)
    hh = rich_height(p["head"], fh, MAXW)
    bl = wrap_plain(p.get("body", ""), fb, MAXW) if p.get("body") else []
    total = 60 + hh + (40 + len(bl) * 58 if bl else 0)
    y = 900 - total / 2
    if p.get("eyebrow"):
        a = eo(t / 0.4)
        c.rrect((X0, y + 8, X0 + 44 * a, y + 14), 3, fill=TEAL, alpha=a)
        c.spaced(X0 + 60, y, p["eyebrow"], fe, TEAL, a, sp=5)
    y += 60
    draw_rich(c, p["head"], fh, X0, y, MAXW, p=clamp((t - 0.15) / 1.1))
    y += hh + 40
    for k, ln in enumerate(bl):
        a = eo((t - 1.1 - k * 0.12) / 0.5)
        c.text(X0, y + (1 - a) * 20, ln, fb, MUTED, a)
        y += 58

def sc_ticks(c, t, d, p):
    fe, fh = F("mono", 28), F("display", 66)
    items = p["items"]
    badged = isinstance(items[0], (list, tuple))
    fi, fs, fbd = F("bodyb", 42 if not badged else 44), F("body", 32), F("mono", 24)
    rows = []
    for it in items:
        if badged:
            rows.append((it, 124))
        else:
            ls = wrap_plain(it, fi, MAXW - 90)
            rows.append((ls, 36 + len(ls) * 54))
    hh = rich_height(p["title"], fh, MAXW)
    total = 60 + hh + 50 + sum(r[1] for r in rows)
    y = 880 - total / 2
    a = eo(t / 0.4)
    c.rrect((X0, y + 8, X0 + 44 * a, y + 14), 3, fill=TEAL, alpha=a)
    c.spaced(X0 + 60, y, p["eyebrow"], fe, TEAL, a, sp=5)
    y += 60
    draw_rich(c, p["title"], fh, X0, y, MAXW, p=clamp((t - 0.1) / 0.9))
    y += hh + 50
    gap = min(1.25, (d - 2.6) / len(items))
    for k, (row, rh) in enumerate(rows):
        a = eob((t - 1.0 - k * gap) / 0.45)
        ax = clamp(a)
        off = (1 - a) * 60
        if badged:
            badge, title, sub = row
            bw = 130
            c.rrect((X0 + off, y + 10, X0 + bw + off, y + 96), 18, fill=PANEL2, outline=TEAL, width=2, alpha=ax)
            c.text(X0 + bw / 2 + off, y + 53, badge, fbd, TEAL, ax, anchor="mm")
            c.text(X0 + bw + 34 + off, y + 12, title, fi, WHITE, ax)
            c.text(X0 + bw + 34 + off, y + 66, sub, fs, MUTED, ax)
        else:
            c.check(X0 + 26 + off, y + 30, 24, alpha=ax)
            yy = y
            for ln in row:
                c.text(X0 + 80 + off, yy + 2, ln, fi, WHITE, ax)
                yy += 54
        y += rh

def sc_chat(c, t, d, p):
    ft = F("display", 54)
    if p.get("title"):
        draw_rich(c, p["title"], ft, X0, 330, MAXW, p=clamp(t / 0.8), align="center")
    a = eo(t / 0.5)
    top = 470 + (1 - a) * 60
    c.rrect((100, top, 980, 1470 + (1 - a) * 60), 44, fill=PANEL, outline=LINE, width=2, alpha=a)
    c.ellipse((140, top + 42, 196, top + 98), fill=TEAL, alpha=a)
    c.text(168, top + 70, p.get("initial", "Y"), F("bodyb", 30), NAVY, a, anchor="mm")
    c.text(216, top + 40, p.get("name", "Your Business"), F("bodyb", 34), WHITE, a)
    c.spaced(216, top + 84, "ONLINE · REPLIES INSTANTLY", F("mono", 20), TEAL, a, sp=3)
    c.line([(130, top + 130), (950, top + 130)], LINE, 2, a)
    fb = F("body", 34)
    y = top + 160
    for who, text, at in p["msgs"]:
        if who == "bot" and at - 0.9 < t < at:
            for k in range(3):
                ph = (t * 6 + k * 0.8) % 3
                c.ellipse((150 + k * 30, y + 26 - (6 if ph < 1 else 0), 166 + k * 30, y + 42 - (6 if ph < 1 else 0)), fill=MUTED)
        if t < at:
            break
        e = eob((t - at) / 0.35)
        lines = wrap_plain(text, fb, 540)
        bw = max(fb.getlength(l) for l in lines) + 52
        bh = len(lines) * 46 + 36
        if who == "user":
            x0, fill, out = 940 - bw, (14, 116, 164), None
        else:
            x0, fill, out = 140, PANEL2, TEAL
        yo = (1 - e) * 30
        c.rrect((x0, y + yo, x0 + bw, y + bh + yo), 28, fill=fill, outline=out, width=2, alpha=clamp(e))
        for k, ln in enumerate(lines):
            c.text(x0 + 26, y + 16 + k * 46 + yo, ln, fb, WHITE, clamp(e))
        y += bh + 26

def sc_checkout(c, t, d, p):
    ft = F("display", 54)
    draw_rich(c, p["title"], ft, X0, 330, MAXW, p=clamp(t / 0.8), align="center")
    a = eo(t / 0.5)
    c.rrect((140, 450, 940, 1060), 40, fill=PANEL, outline=LINE, width=2, alpha=a)
    c.rrect((180, 490, 900, 860), 28, fill=(24, 48, 66), alpha=a)
    # stylised candle
    fl = math.sin(t * 13) * 3 + math.sin(t * 7.3) * 2
    c.ellipse((440 - 60, 520, 660 + 60, 600), fill=(60, 50, 30), alpha=a * 0.35)
    c.ellipse((530 - fl, 560, 550 + fl, 612), fill=(255, 190, 80), alpha=a)
    c.line([(540, 612), (540, 630)], (40, 30, 20), 4, a)
    c.rrect((440, 625, 640, 830), 24, fill=(232, 222, 204), alpha=a)
    c.rrect((440, 700, 640, 760), 0, fill=(20, 184, 166), alpha=a * 0.8)
    c.text(180, 888, p.get("product", "Hand-poured soy candle"), F("bodyb", 40), WHITE, a)
    c.text(180, 944, p.get("price", "A$34.00"), F("display", 50), TEAL, a)
    added = t > 2.2
    bx = (590, 950, 900, 1024)
    c.rrect(bx, 37, fill=TEAL if added else PANEL2, outline=TEAL, width=2, alpha=a)
    c.text((bx[0] + bx[2]) / 2, 987, "ADDED" if added else "ADD TO CART", F("mono", 26), NAVY if added else TEAL, a, anchor="mm")
    # checkout panel
    e = eo((t - 3.0) / 0.6)
    if e > 0:
        oy = (1 - e) * 300
        c.rrect((140, 1090 + oy, 940, 1450 + oy), 40, fill=PANEL, outline=TEAL, width=2, alpha=e)
        c.spaced(180, 1122 + oy, "CHECKOUT", F("mono", 24), TEAL, e, sp=5)
        for k, lab in enumerate(["Apple Pay", "Google Pay", "Card"]):
            x = 180 + k * 245
            sel = t > 4.3 and k == 0
            c.rrect((x, 1170 + oy, x + 225, 1240 + oy), 20, fill=(236, 242, 248) if sel else PANEL2,
                    outline=WHITE if sel else LINE, width=2, alpha=e)
            c.text(x + 112, 1205 + oy, lab, F("bodyb", 30), NAVY if sel else WHITE, e, anchor="mm")
        c.text(180, 1266 + oy, "Total, incl. GST", F("body", 32), MUTED, e)
        c.text(900, 1266 + oy, p.get("price", "A$34.00"), F("bodyb", 32), WHITE, e, anchor="ra")
        paid = t > 5.2
        c.rrect((180, 1330 + oy, 900, 1410 + oy), 40, fill=TEAL if not paid else (16, 120, 110), alpha=e)
        c.text(540, 1370 + oy, "PAID" if paid else "PAY " + p.get("price", "A$34.00"), F("mono", 30), NAVY, e, anchor="mm")
    # toast
    e = eob((t - 5.6) / 0.5)
    if e > 0:
        oy = (1 - e) * -80
        ae = clamp(e)
        c.rrect((150, 470 + oy, 930, 610 + oy), 30, fill=(10, 60, 56), outline=TEAL, width=3, alpha=ae)
        c.check(222, 540 + oy, 34, alpha=ae)
        c.text(280, 494 + oy, "Payment received · " + p.get("price", "A$34.00"), F("bodyb", 36), WHITE, ae)
        c.text(280, 546 + oy, "Order #1047 · alert sent to your phone", F("mono", 22), TEAL, ae)

_ICO = None

def icosa():
    global _ICO
    if _ICO is None:
        ph = (1 + 5 ** 0.5) / 2
        v = []
        for a in (-1, 1):
            for b in (-ph, ph):
                v += [(0, a, b), (a, b, 0), (b, 0, a)]
        v = np.array(v, float)
        v /= np.linalg.norm(v[0])
        e = []
        for i in range(12):
            for j in range(i + 1, 12):
                if abs(np.linalg.norm(v[i] - v[j]) - 1.0515) < 0.05:
                    e.append((i, j))
        _ICO = (v, e)
    return _ICO

def sc_cube(c, t, d, p):
    v, edges = icosa()
    s = 300 * eob(t / 0.9)
    a1, a2 = t * 0.55, t * 0.37 + 0.4
    ry = np.array([[math.cos(a1), 0, math.sin(a1)], [0, 1, 0], [-math.sin(a1), 0, math.cos(a1)]])
    rx = np.array([[1, 0, 0], [0, math.cos(a2), -math.sin(a2)], [0, math.sin(a2), math.cos(a2)]])
    r = v @ ry.T @ rx.T
    cx, cy = 540, 820
    pts = [(cx + x * s / (1 + z * 0.25), cy + y * s / (1 + z * 0.25), z) for x, y, z in r]
    # orbit ring
    rr = 420 * eo(t / 1.2)
    c.ellipse((cx - rr, cy - rr * 0.28, cx + rr, cy + rr * 0.28), outline=LINE, width=2)
    ang = t * 1.4
    c.ellipse((cx + rr * math.cos(ang) - 9, cy + rr * 0.28 * math.sin(ang) - 9,
               cx + rr * math.cos(ang) + 9, cy + rr * 0.28 * math.sin(ang) + 9), fill=SKY)
    order = sorted(edges, key=lambda e: pts[e[0]][2] + pts[e[1]][2], reverse=True)
    for i, j in order:
        z = (pts[i][2] + pts[j][2]) / 2
        k = clamp((1 - z) / 2)
        col = tuple(int(TEAL[n] * k + (SKY[n] * 0.4) * (1 - k)) for n in range(3))
        c.line([pts[i][:2], pts[j][:2]], (8, 52, 58), 12)
        c.line([pts[i][:2], pts[j][:2]], col, 4)
    for x, y, z in pts:
        rad = 7 + 4 * clamp((1 - z) / 2)
        c.ellipse((x - rad, y - rad, x + rad, y + rad), fill=WHITE)
    fh = F("display", 70)
    draw_rich(c, p["head"], fh, X0, 1240, MAXW, p=clamp((t - 0.6) / 1.0), align="center")
    a = eo((t - 1.8) / 0.5)
    c.text(540, 1440, p["sub"], F("body", 38), MUTED, a, anchor="ma")

def sc_aisearch(c, t, d, p):
    ft = F("display", 54)
    draw_rich(c, p["title"], ft, X0, 330, MAXW, p=clamp(t / 0.8), align="center")
    a = eo(t / 0.5)
    c.rrect((100, 450, 980, 1420), 44, fill=PANEL, outline=LINE, width=2, alpha=a)
    c.ellipse((140, 486, 176, 522), fill=SKY, alpha=a)
    c.spaced(196, 490, "AI ASSISTANT", F("mono", 24), SKY, a, sp=5)
    q = p["query"]
    fq = F("body", 36)
    t0 = 0.5
    n = int(clamp((t - t0) * 22, 0, len(q)))
    typed = q[:n]
    lines = wrap_plain(typed, fq, 740) if typed else [""]
    c.rrect((130, 550, 950, 700), 30, fill=PANEL2, outline=LINE, width=2, alpha=a)
    for k, ln in enumerate(lines[:2]):
        c.text(165, 578 + k * 48, ln, fq, WHITE, a)
    if (t * 2) % 1 < 0.6 and n < len(q):
        lx = 165 + fq.getlength(lines[-1])
        c.rrect((lx + 4, 580 + (len(lines) - 1) * 48, lx + 8, 622 + (len(lines) - 1) * 48), 1, fill=TEAL)
    t_done = t0 + len(q) / 22
    if t_done < t < t_done + 1.0:
        for k in range(3):
            ph = (t * 6 + k * 0.8) % 3
            c.ellipse((150 + k * 30, 740 - (6 if ph < 1 else 0), 166 + k * 30, 756 - (6 if ph < 1 else 0)), fill=MUTED)
    ta = t_done + 1.0
    if t > ta:
        e = eo((t - ta) / 0.4)
        c.text(140, 730, "Here are a few well-reviewed options:", F("body", 34), MUTED, e)
        for k in range(3):
            e = eob((t - ta - 0.3 - k * 0.35) / 0.4)
            if e <= 0:
                continue
            y = 800 + k * 128 + (1 - e) * 30
            ae = clamp(e)
            c.rrect((130, y, 950, y + 108), 24, fill=PANEL2, alpha=ae)
            c.ellipse((156, y + 30, 204, y + 78), fill=LINE, alpha=ae)
            c.text(180, y + 54, str(k + 1), F("bodyb", 28), WHITE, ae, anchor="mm")
            c.text(232, y + 20, "Competitor #%d" % (k + 1), F("bodyb", 36), WHITE, ae)
            c.text(232, y + 66, p["reviews"][k], F("mono", 22), MUTED, ae)
        e = eob((t - ta - 1.6) / 0.45)
        if e > 0:
            y = 1190 + (1 - e) * 30
            ae = clamp(e)
            c.rrect((130, y, 950, y + 120), 24, outline=RED, width=3, alpha=ae)
            c.text(170, y + 22, "Your business", F("bodyb", 38), DIM, ae)
            c.spaced(170, y + 74, "NOT MENTIONED", F("mono", 22), RED, ae, sp=5)
    if t > ta + 2.4:
        draw_rich(c, p["caption"], F("display", 64), X0, 1470, MAXW, p=clamp((t - ta - 2.4) / 0.8), align="center")

def sc_stat(c, t, d, p):
    fe = F("mono", 28)
    a = eo(t / 0.4)
    c.spaced(540, 620, p["eyebrow"], fe, TEAL, a, sp=5, center=True)
    fbig = F("display", 230)
    c.text(290, 900, str(p["before"]), fbig, DIM, eo((t - 0.2) / 0.5), anchor="mm")
    ea = eo((t - 0.7) / 0.5)
    c.line([(430, 900), (430 + 190 * ea, 900)], TEAL, 12, ea)
    if ea > 0.6:
        c.line([(600, 860), (640, 900), (600, 940)], TEAL, 12, ea)
    k = eo((t - 0.9) / 1.2)
    val = int(round(p["before"] + (p["after"] - p["before"]) * k))
    c.text(820, 900, str(val), fbig, TEAL, eo((t - 0.9) / 0.3), anchor="mm")
    fl = F("body", 42)
    for i, ln in enumerate(wrap_plain(p["label"], fl, MAXW)):
        c.text(540, 1080 + i * 58, ln, fl, MUTED, eo((t - 1.6) / 0.6), anchor="ma")

def sc_cta(c, t, d, p):
    cx, cy = 540, 560
    for k, (r, col) in enumerate([(110, TEAL), (64, SKY)]):
        e = eob((t - k * 0.12) / 0.6)
        c.ellipse((cx - r * e, cy - r * e, cx + r * e, cy + r * e), outline=col, width=6, alpha=clamp(e) * (0.6 if k == 0 else 1))
    e = eob((t - 0.3) / 0.5)
    c.ellipse((cx - 22 * e, cy - 22 * e, cx + 22 * e, cy + 22 * e), fill=TEAL)
    pr = 110 + ((t * 70) % 90)
    c.ellipse((cx - pr, cy - pr, cx + pr, cy + pr), outline=TEAL, width=3, alpha=0.5 * (1 - (pr - 110) / 90))
    fh = F("display", 76)
    h = draw_rich(c, p["head"], fh, X0, 740, MAXW, p=clamp((t - 0.4) / 1.0), align="center")
    y = 740 + h + 50
    a = eo((t - 1.4) / 0.5)
    c.spaced(540, y, p["price"], F("mono", 28), TEAL, a, sp=4, center=True)
    y += 80
    a = eo((t - 1.8) / 0.5)
    fu = F("display", 62)
    c.text(540, y, p.get("url", "practicalaico.ai"), fu, WHITE, a, anchor="ma")
    uw = fu.getlength(p.get("url", "practicalaico.ai"))
    c.rrect((540 - uw / 2 * a, y + 78, 540 + uw / 2 * a, y + 84), 3, fill=TEAL, alpha=a)
    y += 120
    a = eo((t - 2.2) / 0.5)
    c.text(540, y, "hello@practicalaico.ai", F("body", 36), MUTED, a, anchor="ma")
    y += 90
    a = eob((t - 2.6) / 0.5)
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    fpil = F("mono", 26)
    pw = fpil.getlength(p.get("pill", "FIXED PRICE · NO SALES CALL")) + 60
    c.rrect((540 - pw / 2, y, 540 + pw / 2, y + 74), 37, fill=TEAL, alpha=clamp(a))
    c.rrect((540 - pw / 2 - 8, y - 8, 540 + pw / 2 + 8, y + 82), 45, outline=TEAL, width=2, alpha=clamp(a) * pulse * 0.6)
    c.text(540, y + 37, p.get("pill", "FIXED PRICE · NO SALES CALL"), fpil, NAVY, clamp(a), anchor="mm")

SCENES = dict(hook=sc_hook, statement=sc_statement, ticks=sc_ticks, chat=sc_chat, checkout=sc_checkout,
              cube=sc_cube, aisearch=sc_aisearch, stat=sc_stat, cta=sc_cta)

# ---------------------------------------------------------------- background
def make_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    base[:] = NAVY
    g1 = np.exp(-(((x - W * .5) / (W * .9)) ** 2 + ((y + H * .05) / (H * .42)) ** 2))
    base += g1[..., None] * np.array([10, 70, 100], np.float32)
    g2 = np.exp(-(((x - W * .95) / (W * .6)) ** 2 + ((y - H * 1.0) / (H * .35)) ** 2))
    base += g2[..., None] * np.array([10, 80, 72], np.float32)
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")

GAP = 90

def make_grid():
    g = Image.new("RGBA", (W, H + GAP), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for x in range(0, W + 1, GAP):
        d.line([(x, 0), (x, H + GAP)], fill=(255, 255, 255, 9), width=1)
    for y in range(0, H + GAP + 1, GAP):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 9), width=1)
    return g

# ---------------------------------------------------------------- audio
def add(buf, sig, start):
    if start >= len(buf):
        return
    end = min(len(buf), start + len(sig))
    buf[start:end] += sig[: end - start]

def make_audio(dur, cuts, hook_end, path, seed, bpm):
    sr = 44100
    n = int(dur * sr) + sr
    rng = np.random.default_rng(seed)
    L = np.zeros(n, np.float32)
    R = np.zeros(n, np.float32)
    beat = 60 / bpm
    kt = np.arange(int(0.4 * sr)) / sr
    kick = np.sin(2 * np.pi * np.cumsum(45 + 80 * np.exp(-kt * 30)) / sr) * np.exp(-kt * 8)
    hl = int(0.06 * sr)
    hat = np.diff(rng.standard_normal(hl + 1)) * np.exp(-np.arange(hl) / sr * 70)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    nb = int(dur / beat) + 1
    for i in range(nb):
        s = int(i * beat * sr)
        tt = i * beat
        if tt >= hook_end - 0.01:
            add(L, kick * .5, s); add(R, kick * .5, s)
            h = int((i + .5) * beat * sr)
            add(L, hat * .10, h); add(R, hat * .07, h)
        # bass pluck on root
        ch = chords[(i // 8) % 4]
        bl = int(beat * .9 * sr)
        bt = np.arange(bl) / sr
        f0 = hz(ch[0] - 24)
        bass = (np.sin(2 * np.pi * f0 * bt) + .3 * np.sin(4 * np.pi * f0 * bt)) * np.exp(-bt * 5)
        g = .16 if tt >= hook_end else .08
        add(L, bass * g, s); add(R, bass * g, s)
    seg = beat * 8
    for k in range(int(dur / seg) + 1):
        ch = chords[k % 4]
        ln = int(seg * sr)
        st = np.arange(ln) / sr
        env = np.minimum(1, st / .6) * np.minimum(1, (seg - st) / .6)
        pad = sum(np.sin(2 * np.pi * hz(m) * st + j) + .25 * np.sin(4 * np.pi * hz(m) * st) for j, m in enumerate(ch))
        pad *= env * .035
        add(L, pad, int(k * seg * sr)); add(R, pad * .9, int(k * seg * sr))
    # impact at the open and whooshes into each cut
    it = np.arange(int(1.2 * sr)) / sr
    boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-it * 12)) / sr) * np.exp(-it * 3.5) * .8
    add(L, boom, 0); add(R, boom, 0)
    wl = int(.45 * sr)
    for cut in cuts:
        noise = np.convolve(rng.standard_normal(wl), np.ones(24) / 24, "same")
        env = (np.arange(wl) / wl) ** 2.2
        w = noise * env * .9
        add(L, w, max(0, int((cut - .45) * sr))); add(R, w * .8, max(0, int((cut - .45) * sr)))
    L, R = L[: int(dur * sr)], R[: int(dur * sr)]
    fade = np.ones_like(L)
    fl = int(1.8 * sr)
    fade[-fl:] = np.linspace(1, 0, fl)
    peak = max(np.abs(L).max(), np.abs(R).max()) + 1e-9
    L, R = L * fade / peak * .85, R * fade / peak * .85
    data = (np.stack([L, R], 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes(data.tobytes())

# ---------------------------------------------------------------- render
def timeline(ad):
    out, t = [], 0.0
    for sc in ad["scenes"]:
        out.append((t, sc))
        t += sc["dur"]
    return out, t

class Renderer:
    def __init__(self, ad):
        self.ad = ad
        self.tl, self.dur = timeline(ad)
        self.bg = make_bg()
        self.grid = make_grid()
        rng = np.random.default_rng(ad["id"])
        self.parts = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(8, 30), rng.uniform(1.5, 3.5)) for _ in range(46)]

    def frame(self, t):
        fr = self.bg.copy()
        off = int((t * 18) % GAP)
        fr.alpha_composite(self.grid.crop((0, off, W, off + H)))
        d = ImageDraw.Draw(fr)
        for x, y, sp, r in self.parts:
            yy = (y - t * sp) % H
            d.ellipse((x - r, yy - r, x + r, yy + r), fill=(60, 140, 160, 255))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for k, (st, sc) in enumerate(self.tl):
            if st <= t < st + sc["dur"] or (k == len(self.tl) - 1 and t >= st):
                lt = t - st
                SCENES[sc["kind"]](C(layer), lt, sc["dur"], sc)
                last = k == len(self.tl) - 1
                a = eo(lt / 0.3) * (1 if last else 1 - eo((lt - (sc["dur"] - 0.28)) / 0.28))
                if a < 0.999:
                    layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
                break
        fr.alpha_composite(layer)
        c = C(fr)
        # chrome: progress bar + brand
        c.rrect((0, 0, W * clamp(t / self.dur), 8), 0, fill=TEAL)
        fm = F("mono", 24)
        label = "THE PRACTICAL AI CO."
        tw = sum(fm.getlength(ch) for ch in label) + 4 * (len(label) - 1)
        x0 = 540 - (tw + 46) / 2
        c.ellipse((x0, 206, x0 + 30, 236), outline=TEAL, width=3, alpha=.8)
        c.ellipse((x0 + 10, 216, x0 + 20, 226), fill=TEAL)
        c.spaced(x0 + 46, 207, label, fm, MUTED, .85, sp=4)
        return fr.convert("RGB")

def render(ad, stills=False):
    os.makedirs(OUT, exist_ok=True)
    r = Renderer(ad)
    slug = "ad%d-%s" % (ad["id"], ad["slug"])
    if stills:
        for k, (st, sc) in enumerate(r.tl):
            for frac in (0.5, 0.95):
                r.frame(st + sc["dur"] * frac).save(os.path.join(OUT, "%s-s%02d-%d.png" % (slug, k, int(frac * 100))))
        return
    wav = os.path.join(OUT, slug + ".wav")
    cuts = [st for st, _ in r.tl[1:]]
    hook_end = sum(sc["dur"] for sc in ad["scenes"] if sc["kind"] == "hook") or r.tl[1][0]
    make_audio(r.dur, cuts, hook_end, wav, ad["id"], ad.get("bpm", 100))
    mp4 = os.path.join(OUT, slug + ".mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", mp4]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round(r.dur * FPS))
    for i in range(nf):
        pr.stdin.write(r.frame(i / FPS).tobytes())
    pr.stdin.close()
    pr.wait()
    os.remove(wav)
    # cover image = the hook frame
    r.frame(min(1.6, r.tl[0][1]["dur"] * .8)).save(os.path.join(OUT, slug + "-cover.jpg"), quality=90)
    print("wrote", mp4, "%.1fs" % r.dur)

if __name__ == "__main__":
    args = sys.argv[1:]
    stills = "--stills" in args
    ids = [int(a) for a in args if a.isdigit()]
    for ad in ADS:
        if not ids or ad["id"] in ids:
            render(ad, stills)
