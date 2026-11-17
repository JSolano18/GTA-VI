# -*- coding: utf-8 -*-
"""Arte original procedural (sin material de Rockstar): fondos, paneles, mapa, miniaturas."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 1920, 1080
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")

PINK = (255, 46, 136); CYAN = (0, 229, 255); YEL = (255, 214, 10); WHITE = (255, 255, 255)
ORANGE = (255, 140, 50); RED = (255, 59, 59); GREEN = (60, 230, 140)

_fc = {}
def font(kind, size):
    key = (kind, size)
    if key not in _fc:
        if kind == "head":
            f = ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), size)
        else:
            f = ImageFont.truetype(os.path.join(FONTS, "Montserrat.ttf"), size)
            f.set_variation_by_name({"black": "Black", "bold": "Bold", "semi": "SemiBold", "reg": "Medium"}[kind])
        _fc[key] = f
    return _fc[key]

def fit(text, kind, max_w, size, min_size=24):
    while size > min_size:
        f = font(kind, size)
        if f.getbbox(text)[2] <= max_w:
            return f
        size -= 4
    return font(kind, min_size)

def wrap(text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getbbox(t)[2] <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def text_img(text, f, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), glow=None, pad=30):
    bb = f.getbbox(text, stroke_width=stroke)
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pos = (pad - bb[0], pad - bb[1])
    if glow:
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).text(pos, text, font=f, fill=glow + (255,), stroke_width=stroke + 4, stroke_fill=glow + (255,))
        g = g.filter(ImageFilter.GaussianBlur(14))
        im = Image.alpha_composite(im, g); im = Image.alpha_composite(im, g)
        d = ImageDraw.Draw(im)
    d.text(pos, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def vgrad(w, h, stops):
    """stops: [(pos 0..1, (r,g,b)), ...]"""
    y = np.linspace(0, 1, h)[:, None]
    out = np.zeros((h, 1, 3), np.float32)
    for c in range(3):
        out[:, 0, c] = np.interp(y[:, 0], [s[0] for s in stops], [s[1][c] for s in stops])
    return Image.fromarray(np.repeat(out, w, axis=1).astype(np.uint8), "RGB")

def palm(h, color=(12, 4, 25), seed=0):
    rng = np.random.default_rng(seed)
    w = int(h * 0.9)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    base = (w // 2 + int(rng.integers(-20, 20)), h)
    lean = rng.uniform(-0.25, 0.25)
    top = (int(w / 2 + lean * h * 0.6), int(h * 0.3))
    pts = []
    for i in range(30):
        t = i / 29
        x = base[0] + (top[0] - base[0]) * t + math.sin(t * math.pi) * 25 * np.sign(lean or 1)
        y = base[1] + (top[1] - base[1]) * t
        pts.append((x, y, int(h * 0.028 * (1 - t * 0.45))))
    for x, y, r in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)
    tx, ty = pts[-1][0], pts[-1][1]
    for k in range(9):
        ang = -math.pi / 2 + (k - 4) * 0.42 + rng.uniform(-0.1, 0.1)
        L = h * rng.uniform(0.32, 0.42)
        poly_top, poly_bot = [], []
        for i in range(16):
            t = i / 15
            droop = (t ** 2) * L * 0.55
            x = tx + math.cos(ang) * L * t
            y = ty + math.sin(ang) * L * t + droop
            th = h * 0.04 * math.sin(t * math.pi) + 1
            nx, ny = -math.sin(ang), math.cos(ang)
            poly_top.append((x + nx * th, y + ny * th)); poly_bot.append((x - nx * th * 0.3, y - ny * th * 0.3))
        d.polygon(poly_top + poly_bot[::-1], fill=color)
    return im

def skyline(w, h, seed, color=(10, 6, 30), lit=True):
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 0
    while x < w:
        bw = int(rng.integers(40, 140)); bh = int(rng.integers(h * 0.2, h * 0.95))
        d.rectangle([x, h - bh, x + bw, h], fill=color)
        if rng.random() < 0.25:
            d.rectangle([x + bw // 2 - 3, h - bh - 40, x + bw // 2 + 3, h - bh], fill=color)
        if lit:
            for wy in range(h - bh + 12, h - 8, 18):
                for wx in range(x + 8, x + bw - 8, 16):
                    if rng.random() < 0.3:
                        c = [YEL, CYAN, PINK, (255, 240, 200)][int(rng.integers(0, 4))]
                        d.rectangle([wx, wy, wx + 6, wy + 9], fill=c + (int(rng.integers(120, 255)),))
        x += bw + int(rng.integers(0, 12))
    return im

def background(theme, seed=0):
    """Fondo grande (10% mayor que el cuadro) para movimiento de cámara."""
    BW, BH = int(W * 1.12), int(H * 1.12)
    rng = np.random.default_rng(seed)
    if theme == "sunset":
        sky = vgrad(BW, BH, [(0, (20, 6, 50)), (0.35, (110, 20, 120)), (0.58, (255, 70, 120)), (0.62, (255, 150, 80)), (1, (40, 8, 60))])
        im = sky.convert("RGBA"); d = ImageDraw.Draw(im)
        # sol con franjas
        R = 300; cx, cy = BW // 2, int(BH * 0.58)
        sun = vgrad(2 * R, 2 * R, [(0, (255, 230, 90)), (1, (255, 40, 140))]).convert("RGBA")
        m = Image.new("L", (2 * R, 2 * R), 0); md = ImageDraw.Draw(m); md.ellipse([0, 0, 2 * R, 2 * R], fill=255)
        for i in range(7):
            y0 = int(R * 1.05 + i * 26); md.rectangle([0, y0, 2 * R, y0 + 4 + i * 2], fill=0)
        glow = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([cx - R - 80, cy - R - 80, cx + R + 80, cy + R + 80], fill=(255, 80, 150, 120))
        im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(60)))
        im.paste(sun, (cx - R, cy - R), m)
        sk = skyline(BW, 260, seed, color=(30, 6, 50), lit=False)
        im.alpha_composite(sk, (0, int(BH * 0.62) - 260 + 40))
        floor = vgrad(BW, BH - int(BH * 0.64), [(0, (40, 6, 70)), (1, (10, 2, 25))]).convert("RGBA")
        im.alpha_composite(floor, (0, int(BH * 0.64)))
    elif theme == "night":
        im = vgrad(BW, BH, [(0, (4, 3, 18)), (0.55, (30, 12, 75)), (0.7, (80, 20, 110)), (1, (6, 4, 20))]).convert("RGBA")
        d = ImageDraw.Draw(im)
        for _ in range(260):
            x, y = rng.integers(0, BW), rng.integers(0, int(BH * 0.55)); r = rng.random() * 1.8
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(rng.integers(80, 255))))
        moon = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); mdd = ImageDraw.Draw(moon)
        mdd.ellipse([BW * 0.78, BH * 0.12, BW * 0.78 + 120, BH * 0.12 + 120], fill=(255, 230, 240, 255))
        im = Image.alpha_composite(im, moon.filter(ImageFilter.GaussianBlur(30)))
        im = Image.alpha_composite(im, moon)
        far = skyline(BW, 420, seed + 1, color=(25, 12, 60), lit=True)
        near = skyline(BW, 330, seed + 2, color=(8, 4, 22), lit=True)
        hz = int(BH * 0.7)
        im.alpha_composite(far, (0, hz - 420)); im.alpha_composite(near, (0, hz - 330))
        water = vgrad(BW, BH - hz, [(0, (40, 15, 80)), (1, (5, 3, 15))]).convert("RGBA")
        refl = im.crop((0, hz - 330, BW, hz)).transpose(Image.FLIP_TOP_BOTTOM).resize((BW, BH - hz))
        refl = refl.filter(ImageFilter.GaussianBlur(4)); refl.putalpha(90)
        water.alpha_composite(refl)
        wd = ImageDraw.Draw(water)
        for _ in range(140):
            x, y = rng.integers(0, BW), rng.integers(0, BH - hz); L = rng.integers(20, 120)
            wd.line([x, y, x + L, y], fill=(PINK if rng.random() < 0.5 else CYAN) + (int(rng.integers(30, 110)),), width=2)
        im.alpha_composite(water, (0, hz))
    else:  # beach
        im = vgrad(BW, BH, [(0, (12, 40, 110)), (0.45, (40, 170, 210)), (0.6, (255, 200, 150)), (1, (255, 180, 120))]).convert("RGBA")
        d = ImageDraw.Draw(im)
        sun = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(sun).ellipse([BW * 0.15, BH * 0.18, BW * 0.15 + 180, BH * 0.18 + 180], fill=(255, 250, 210, 255))
        im = Image.alpha_composite(im, sun.filter(ImageFilter.GaussianBlur(40))); im = Image.alpha_composite(im, sun)
        hz = int(BH * 0.6)
        sea = vgrad(BW, int(BH * 0.22), [(0, (10, 140, 170)), (1, (30, 200, 200))]).convert("RGBA")
        sd = ImageDraw.Draw(sea)
        for _ in range(200):
            x, y = rng.integers(0, BW), rng.integers(0, sea.size[1]); L = rng.integers(20, 90)
            sd.line([x, y, x + L, y], fill=(255, 255, 255, int(rng.integers(40, 140))), width=2)
        im.alpha_composite(sea, (0, hz))
        sand = vgrad(BW, BH - hz - sea.size[1], [(0, (250, 215, 160)), (1, (220, 170, 110))]).convert("RGBA")
        im.alpha_composite(sand, (0, hz + sea.size[1]))
        sk = skyline(int(BW * 0.5), 160, seed, color=(40, 80, 130), lit=False)
        im.alpha_composite(sk, (int(BW * 0.45), hz - 160))
    # palmeras en primer plano
    pc = (10, 3, 22) if theme != "beach" else (20, 40, 40)
    for i, (px, ph) in enumerate([(-120, 900), (BW - 520, 820), (BW - 760, 560), (160, 520)]):
        p = palm(ph, pc, seed + i)
        im.alpha_composite(p, (int(px), BH - ph + 40))
    return im.convert("RGB")

def vignette():
    y, x = np.ogrid[:H, :W]
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    a = np.clip((d - 0.55) * 255, 0, 200).astype(np.uint8)
    v = np.zeros((H, W, 4), np.uint8); v[..., 3] = a
    # oscurece un poco el centro para legibilidad
    v[..., 3] = np.maximum(v[..., 3], 70)
    return Image.fromarray(v, "RGBA")

def grid_frames(n=30):
    """Suelo de cuadrícula synthwave animado (loop)."""
    frames = []
    hz = int(H * 0.66)
    for k in range(n):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for i in range(-24, 25):
            x0 = W / 2 + i * 40; x1 = W / 2 + i * 260
            d.line([x0, hz, x1, H], fill=PINK + (110,), width=2)
        for j in range(14):
            t = ((j + k / n) / 14) ** 2.2
            y = hz + t * (H - hz)
            d.line([0, y, W, y], fill=PINK + (int(40 + 120 * t),), width=2)
        frames.append(im)
    return frames

def panel(w, h, accent=PINK, alpha=200):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle([16, 16, w - 16, h - 16], 28, outline=accent + (255,), width=10)
    g = g.filter(ImageFilter.GaussianBlur(12))
    im.alpha_composite(g)
    ImageDraw.Draw(im).rounded_rectangle([16, 16, w - 16, h - 16], 28, fill=(14, 6, 32, alpha), outline=accent + (255,), width=4)
    return im

def badge(text, f, bg=PINK, fg=WHITE, padx=28, pady=12, skew=True):
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + padx * 2, bb[3] - bb[1] + pady * 2
    im = Image.new("RGBA", (w + 20, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    s = 14 if skew else 0
    d.polygon([(s, 0), (w + 20, 0), (w + 20 - s, h), (0, h)], fill=bg)
    d.text((padx + 10 - bb[0], pady - bb[1]), text, font=f, fill=fg)
    return im

def silhouette(h, color, seed=0):
    """Busto genérico estilizado (no representa a ningún personaje real)."""
    w = int(h * 0.8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hr = int(h * 0.17)
    cx = w // 2
    d.ellipse([cx - hr, int(h * 0.12), cx + hr, int(h * 0.12) + int(hr * 2.3)], fill=(15, 8, 35, 255))
    d.rectangle([cx - hr * 0.45, int(h * 0.48), cx + hr * 0.45, int(h * 0.62)], fill=(15, 8, 35, 255))
    d.chord([cx - w * 0.48, int(h * 0.56), cx + w * 0.48, int(h * 1.5)], 180, 360, fill=(15, 8, 35, 255))
    edge = im.split()[3].filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    glow = Image.new("RGBA", im.size, color + (0,)); glow.putalpha(edge)
    g2 = glow.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g2); out.alpha_composite(g2); out.alpha_composite(im); out.alpha_composite(glow)
    q = font("head", int(h * 0.3))
    ImageDraw.Draw(out).text((cx, int(h * 0.29)), "?", font=q, fill=color + (230,), anchor="mm")
    return out

# ---------------------------------------------------------------- mapa estilizado de Leonida (original, no a escala)
REGIONS = {
    "MOUNT KALAGA": [(0.30, 0.08), (0.62, 0.06), (0.66, 0.26), (0.42, 0.30), (0.28, 0.22)],
    "PORT GELLHORN": [(0.06, 0.10), (0.30, 0.08), (0.28, 0.22), (0.30, 0.36), (0.10, 0.34), (0.03, 0.22)],
    "AMBROSIA": [(0.42, 0.30), (0.66, 0.26), (0.70, 0.46), (0.52, 0.56), (0.36, 0.48), (0.30, 0.36), (0.28, 0.22)],
    "GRASSRIVERS": [(0.36, 0.48), (0.52, 0.56), (0.58, 0.72), (0.48, 0.84), (0.36, 0.76), (0.32, 0.60)],
    "VICE CITY": [(0.52, 0.56), (0.70, 0.46), (0.76, 0.62), (0.70, 0.80), (0.58, 0.72)],
}
KEYS = [(0.50, 0.90), (0.42, 0.93), (0.33, 0.95), (0.24, 0.96), (0.15, 0.955)]
LABEL_POS = {"MOUNT KALAGA": (0.47, 0.17), "PORT GELLHORN": (0.16, 0.22), "AMBROSIA": (0.50, 0.40),
             "GRASSRIVERS": (0.44, 0.67), "VICE CITY": (0.66, 0.62), "LEONIDA KEYS": (0.32, 0.88)}

def leonida_map(w, h, highlight=None):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    P = lambda p: (p[0] * w, p[1] * h)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    d = ImageDraw.Draw(im)
    for name, poly in REGIONS.items():
        hl = name == highlight
        pts = [P(p) for p in poly]
        d.polygon(pts, fill=(PINK + (210,)) if hl else (40, 25, 80, 200), outline=CYAN + (255,), width=3)
        if hl: gd.polygon(pts, fill=PINK + (255,))
    for i, k in enumerate(KEYS):
        x, y = P(k); r = 16 - i * 1.5
        hl = highlight == "LEONIDA KEYS"
        d.ellipse([x - r * 1.8, y - r, x + r * 1.8, y + r], fill=(PINK + (230,)) if hl else (40, 25, 80, 220), outline=CYAN + (255,), width=3)
        if hl: gd.ellipse([x - r * 2, y - r * 1.2, x + r * 2, y + r * 1.2], fill=PINK + (255,))
    # puente de los cayos
    d.line([P((0.56, 0.84)), P((0.50, 0.90)), P((0.15, 0.955))], fill=CYAN + (140,), width=2)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(glow.filter(ImageFilter.GaussianBlur(25))); out.alpha_composite(im)
    od = ImageDraw.Draw(out)
    for name, (lx, ly) in LABEL_POS.items():
        hl = name == highlight
        f = font("black", 30 if hl else 22)
        od.text((lx * w, ly * h), name, font=f, fill=(WHITE if hl else (190, 180, 230)) + (255,), anchor="mm",
                stroke_width=4, stroke_fill=(10, 5, 25))
    return out

# ---------------------------------------------------------------- miniaturas
def thumbnail(v, path):
    TW, TH = 1280, 720
    bg = background(v["theme"], seed=hash(v["slug"]) % 1000).resize((TW, TH))
    im = bg.convert("RGBA")
    dark = Image.new("RGBA", (TW, TH), (0, 0, 0, 0)); dd = ImageDraw.Draw(dark)
    for x in range(TW):
        a = int(max(0, 210 - x * 0.25))
        dd.line([x, 0, x, TH], fill=(10, 0, 25, a))
    im = Image.alpha_composite(im, dark)
    th = v["thumb"]
    # gran "6" de neón de fondo (tipografía libre, no logotipo oficial)
    six = text_img("6", font("head", 620), fill=(255, 255, 255, 0), stroke=10, stroke_fill=PINK + (255,), glow=PINK)
    im.alpha_composite(six, (TW - six.size[0] + 40, TH - six.size[1] + 90))
    t1 = text_img(th["top"], fit(th["top"], "head", 760, 120), fill=WHITE, stroke=8, stroke_fill=(0, 0, 0))
    im.alpha_composite(t1, (30, 40))
    t2 = text_img(th["big"], fit(th["big"], "head", 820, 260), fill=YEL, stroke=12, stroke_fill=(0, 0, 0), glow=PINK)
    im.alpha_composite(t2, (20, 40 + t1.size[1] - 50))
    b = badge(th["badge"], font("black", 54), bg=PINK)
    b = b.rotate(4, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(b, (50, TH - b.size[1] - 50))
    tag = text_img("GTA 6", font("head", 70), fill=WHITE, stroke=6, stroke_fill=PINK, glow=CYAN)
    im.alpha_composite(tag, (TW - tag.size[0] - 20, 10))
    im.convert("RGB").save(path, quality=92)
