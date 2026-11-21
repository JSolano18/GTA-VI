# -*- coding: utf-8 -*-
"""Programmatic tutorial animations (labelled as illustrations, never presented as gameplay):
generic gamepad with animated button presses, settings-menu mockup, and a scope view effect."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import visuals as V
from visuals import PINK, CYAN, YEL, WHITE, font, text_img

W, H = 1080, 1920
BODY = (28, 24, 44); EDGE = (90, 80, 130); BTN = (60, 54, 88)

# button positions on a 960x560 pad canvas
POS = {"L2": (215, 40), "R2": (745, 40), "L1": (215, 95), "R1": (745, 95),
       "LS": (330, 330), "RS": (630, 400), "UP": (215, 245), "DOWN": (215, 335), "LEFT": (170, 290), "RIGHT": (260, 290),
       "TRI": (745, 225), "CIR": (805, 285), "CRO": (745, 345), "SQU": (685, 285), "PAD": (480, 215)}

def _pad_base():
    im = Image.new("RGBA", (960, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # triggers / bumpers
    for x in (215, 745):
        d.rounded_rectangle([x - 90, 10, x + 90, 70], 26, fill=BTN, outline=EDGE, width=4)
        d.rounded_rectangle([x - 100, 75, x + 100, 115], 18, fill=BTN, outline=EDGE, width=4)
    # body with grips
    d.rounded_rectangle([80, 110, 880, 420], 120, fill=BODY, outline=EDGE, width=6)
    d.ellipse([60, 250, 360, 550], fill=BODY, outline=EDGE, width=6)
    d.ellipse([600, 250, 900, 550], fill=BODY, outline=EDGE, width=6)
    d.rounded_rectangle([90, 120, 870, 410], 110, fill=BODY)
    d.rectangle([200, 260, 760, 420], fill=BODY)
    # touchpad / center
    d.rounded_rectangle([370, 150, 590, 285], 22, fill=(40, 36, 64), outline=EDGE, width=4)
    # d-pad
    cx, cy = 215, 290
    for dx, dy in ((0, -45), (0, 45), (-45, 0), (45, 0)):
        d.rounded_rectangle([cx + dx - 26, cy + dy - 26, cx + dx + 26, cy + dy + 26], 8, fill=BTN, outline=EDGE, width=3)
    # sticks
    for k in ("LS", "RS"):
        x, y = POS[k]; d.ellipse([x - 62, y - 62, x + 62, y + 62], fill=(18, 16, 30), outline=EDGE, width=5)
        d.ellipse([x - 42, y - 42, x + 42, y + 42], fill=BTN, outline=EDGE, width=4)
    # face buttons with generic symbols
    for k in ("TRI", "CIR", "CRO", "SQU"):
        x, y = POS[k]; d.ellipse([x - 32, y - 32, x + 32, y + 32], fill=BTN, outline=EDGE, width=4)
    _sym(d, "TRI", (220, 220, 230)); _sym(d, "CIR", (220, 220, 230)); _sym(d, "CRO", (220, 220, 230)); _sym(d, "SQU", (220, 220, 230))
    for k, lab in (("L2", "L2"), ("R2", "R2"), ("L1", "L1"), ("R1", "R1")):
        x, y = POS[k]; d.text((x, y), lab, font=font("black", 30), fill=(200, 200, 215), anchor="mm")
    return im

def _sym(d, k, col):
    x, y = POS[k]
    if k == "TRI": d.polygon([(x, y - 16), (x - 16, y + 12), (x + 16, y + 12)], outline=col, width=4)
    if k == "CIR": d.ellipse([x - 15, y - 15, x + 15, y + 15], outline=col, width=4)
    if k == "CRO": d.line([(x - 14, y - 14), (x + 14, y + 14)], fill=col, width=4); d.line([(x - 14, y + 14), (x + 14, y - 14)], fill=col, width=4)
    if k == "SQU": d.rectangle([x - 13, y - 13, x + 13, y + 13], outline=col, width=4)

_BASE = None
def pad_frame(lt, seq, caption=None):
    """seq: list of (button, t_start, t_end, label). Returns RGBA 960x700 with pad + press highlights."""
    global _BASE
    if _BASE is None: _BASE = _pad_base()
    im = Image.new("RGBA", (960, 700), (0, 0, 0, 0))
    im.alpha_composite(_BASE, (0, 0))
    glow = Image.new("RGBA", (960, 700), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    d = ImageDraw.Draw(im)
    for (b, t0, t1, lab) in seq:
        if not (t0 <= lt <= t1): continue
        x, y = POS[b]
        hold = (t1 - t0) > 0.9
        pulse = 0.5 + 0.5 * math.sin((lt - t0) * (6 if hold else 14))
        r = 52 + 10 * pulse if b not in ("L2", "R2", "L1", "R1", "PAD") else 0
        col = YEL if hold else PINK
        if b in ("L2", "R2", "L1", "R1"):
            yy = 40 if b in ("L2", "R2") else 95; hh = 32 if b in ("L2", "R2") else 22
            g.rounded_rectangle([x - 100, yy - hh - 6, x + 100, yy + hh + 6], 26, fill=col + (255,))
            d.rounded_rectangle([x - 90, yy - hh + (6 if hold else 0), x + 90, yy + hh], 22, fill=col + (255,))
            d.text((x, yy + 3), b, font=font("black", 32), fill=(20, 10, 30), anchor="mm")
        elif b == "PAD":
            g.rounded_rectangle([360, 140, 600, 295], 26, fill=col + (255,))
            d.rounded_rectangle([370, 150, 590, 285], 22, fill=col + (230,))
        else:
            g.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
            rr = 40 if b in ("LS", "RS") else 30
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (255,))
            if b in ("TRI", "CIR", "CRO", "SQU"): _sym(d, b, (20, 10, 30))
        if lab:
            t = text_img(lab, font("black", 40), fill=WHITE, stroke=5, stroke_fill=(0, 0, 0), pad=10)
            lx = min(max(10, x - t.size[0] // 2), 950 - t.size[0])
            im.alpha_composite(t, (lx, 575))
            d.line([(x, y + 40 if b not in ("L2", "R2") else y + 40), (x, 580)], fill=col + (200,), width=4)
    out = Image.new("RGBA", (960, 700), (0, 0, 0, 0))
    out.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18))); out.alpha_composite(im)
    return out

def menu_frame(lt):
    """Mockup of Settings > Controller: highlight moves to the shortcut and its value flips Map -> Camera."""
    pw, ph = 940, 640
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], 26, fill=(12, 8, 26, 235), outline=CYAN + (255,), width=4)
    d.text((40, 40), "AJUSTES  ›  MANDO", font=font("black", 40), fill=CYAN)
    items = ["Vibración", "Sensibilidad de la cámara", "Botón del panel táctil", "Invertir eje Y"]
    sel = 0 if lt < 0.8 else (1 if lt < 1.4 else 2)
    val = "Mapa" if lt < 2.6 else "Cámara"
    for i, it in enumerate(items):
        y = 140 + i * 115
        if i == sel:
            d.rounded_rectangle([24, y - 12, pw - 24, y + 82], 16, fill=PINK + (230,))
        d.text((54, y + 35), it, font=font("bold", 38), fill=WHITE, anchor="lm")
        v = {0: "Sí", 1: "5", 2: val, 3: "No"}[i]
        if i == 2:
            d.text((pw - 54, y + 35), f"‹  {v}  ›", font=font("black", 40), fill=YEL if lt >= 2.6 else WHITE, anchor="rm")
        else:
            d.text((pw - 54, y + 35), v, font=font("bold", 36), fill=(200, 200, 215), anchor="rm")
    if 2.6 <= lt < 3.0:
        fl = Image.new("RGBA", im.size, (255, 255, 255, int(160 * (1 - (lt - 2.6) / 0.4))))
        m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([24, 140 + 2 * 115 - 12, pw - 24, 140 + 2 * 115 + 82], 16, fill=255)
        im.paste(fl, (0, 0), m)
    tag = text_img("ILUSTRACIÓN · menú simplificado", font("semi", 24), fill=(220, 220, 230), stroke=2, pad=6)
    im.alpha_composite(tag, (pw - tag.size[0] - 20, ph - tag.size[1] - 14))
    return im

def scope_overlay(frame, lt, cx=W // 2, cy=820):
    """Animated scope vignette: circle closes in, crosshair fades in."""
    p = min(1.0, max(0.0, (lt - 0.6) / 0.6)); e = p * p * (3 - 2 * p)
    r = int(1300 - e * 880)
    mask = Image.new("L", (W, H), 255); ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 235)); dark.putalpha(mask.point(lambda v: int(v * 0.92)))
    frame.alpha_composite(dark)
    if e > 0.3:
        a = int(255 * min(1, (e - 0.3) / 0.5)); d = ImageDraw.Draw(frame)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 0, 0, a), width=10)
        d.line([(cx - r, cy), (cx - 30, cy)], fill=(0, 0, 0, a), width=4); d.line([(cx + 30, cy), (cx + r, cy)], fill=(0, 0, 0, a), width=4)
        d.line([(cx, cy - r), (cx, cy - 30)], fill=(0, 0, 0, a), width=4); d.line([(cx, cy + 30), (cx, cy + r)], fill=(0, 0, 0, a), width=4)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 40, 40, a))
