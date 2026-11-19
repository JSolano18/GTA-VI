# -*- coding: utf-8 -*-
"""Portadas v2 pensadas para el clic: primer plano grande, 2-3 palabras gigantes, flecha y sello rojos.

Uso: python3 channel/covers_v2.py [slug ...]
"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import visuals as V
from visuals import PINK, YEL, WHITE, font, fit, text_img, badge
from shorts import IMG, OUT, W, H

RED = (235, 20, 35)
# slug: (imagen, foco x, foco y, zoom, [línea blanca, línea amarilla], sello, flecha (x, y, ángulo) o None)
# foco = posición de la cara en la imagen original (0..1); se coloca en (W/2, FACE_Y)
FACE_Y = 560
C = {
    "s9-mandy":        ("Mandy_frame", .48, .28, 1.7, ["¿ES UNA", "ASESINA?"], "MANDY · GTA 6", True),
    "s10-ventas":      ("Jason_and_Lucia_17", .58, .2, 1.45, ["$1.650", "MILLONES"], "EN 1 DÍA", False),
    "s11-secretos":    ("Grassrivers_07", .5, .3, 1.4, ["BIGFOOT", "EXISTE"], "5 SECRETOS", True),
    "s12-cosas-raras": ("Jason_Duval_15", .44, .19, 1.45, ["ESTO ES", "RARO..."], "GTA 6", True),
    "s13-consejos":    ("Jason_and_Lucia_15", .31, .22, 1.45, ["NO HAGAS", "ESTO"], "PRIMER DÍA", True),
    "s14-misiones-secundarias": ("Vice_City_16", .53, .36, 1.35, ["NADIE TE", "LO CUENTA"], "MISIONES SECRETAS", True),
}

def arrow(length=330, width=70):
    im = Image.new("RGBA", (length + 40, width * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cy = width * 1.5
    pts = [(20, cy - width / 3), (length - width * 1.2, cy - width / 3), (length - width * 1.2, cy - width),
           (length + 20, cy), (length - width * 1.2, cy + width), (length - width * 1.2, cy + width / 3), (20, cy + width / 3)]
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon(pts, fill=(0, 0, 0, 200))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(out).polygon(pts, fill=RED + (255,), outline=WHITE + (255,), width=8)
    return out

def cover(slug):
    img, fx, fy, zoom, lines, seal, arr = C[slug]
    pth = os.path.join(IMG, img + ".jpg")
    src = Image.open(pth if os.path.exists(pth) else os.path.join(IMG, img + ".png")).convert("RGB")
    s = H * zoom / src.size[1]; src = src.resize((int(src.size[0] * s), int(src.size[1] * s)), Image.LANCZOS)
    x0 = int(min(max(0, fx * src.size[0] - W / 2), src.size[0] - W)); y0 = int(min(max(0, fy * src.size[1] - FACE_Y), src.size[1] - H))
    im = src.crop((x0, y0, x0 + W, y0 + H))
    im = ImageEnhance.Color(im).enhance(1.35); im = ImageEnhance.Contrast(im).enhance(1.15); im = ImageEnhance.Sharpness(im).enhance(1.3)
    im = im.convert("RGBA")
    # viñeta y degradado superior para que el texto destaque
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    a = np.clip(np.maximum((y - 780) / 700 * 190, 0) + np.hypot((x - W / 2) / W, (y - H / 2) / H) * 150 - 40, 0, 220)
    ov = np.zeros((H, W, 4), np.uint8); ov[..., 3] = a.astype(np.uint8); im.alpha_composite(Image.fromarray(ov, "RGBA"))
    # texto gigante (mitad inferior; la cara queda arriba)
    yy = 1010
    for i, ln in enumerate(lines):
        f = fit(ln, "head", 1020, 300)
        t = text_img(ln, f, fill=YEL if i == 1 else WHITE, stroke=16, stroke_fill=(0, 0, 0), pad=40)
        sh = Image.new("RGBA", t.size, (0, 0, 0, 0)); sh.putalpha(t.getchannel("A").filter(ImageFilter.GaussianBlur(10)))
        im.alpha_composite(sh, ((W - t.size[0]) // 2 + 10, yy + 14)); im.alpha_composite(t, ((W - t.size[0]) // 2, yy))
        yy += t.size[1] - 90
    b = badge(seal, fit(seal, "black", 820, 70), bg=RED, padx=34, pady=16).rotate(-4, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(b, ((W - b.size[0]) // 2, 905))
    if arr:
        ar = arrow(280, 62).rotate(135, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(ar, (W // 2 + 150, 620))
    # marco fino de color para destacar en el feed
    d = ImageDraw.Draw(im); d.rectangle([0, 0, W - 1, H - 1], outline=YEL, width=14)
    cr = text_img("Imágenes: Rockstar Games", font("semi", 24), stroke=3, pad=8); im.alpha_composite(cr, (30, H - 70))
    out = os.path.join(OUT, slug, slug + "-cover.jpg"); im.convert("RGB").save(out, quality=94)
    mp4 = os.path.join(OUT, slug, slug + ".mp4")
    if os.path.exists(mp4):
        tmp = mp4 + ".tmp.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", mp4, "-i", out, "-map", "0:v:0", "-map", "0:a", "-map", "1",
                        "-c", "copy", "-disposition:v:1", "attached_pic", "-movflags", "+faststart", tmp], check=True, stdin=subprocess.DEVNULL)
        os.replace(tmp, mp4)
    return out

if __name__ == "__main__":
    for k in (sys.argv[1:] or C): print(cover(k))
