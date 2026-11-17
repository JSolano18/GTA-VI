# -*- coding: utf-8 -*-
"""Portadas 9:16 de los Shorts (imagen oficial + texto grande en la zona central segura)."""
import os, sys, subprocess
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import visuals as V
from visuals import PINK, CYAN, YEL, WHITE, font, fit, text_img, badge
from shorts import IMG, OUT, W, H, overlay

COVERS = {
    "s1-hora-por-pais": ("Lucia_Caminos_02", 0.46, ["¿A QUÉ HORA", "SALE?"], "EN TU PAÍS", "GTA 6"),
    "s2-bonus-reserva": ("VINTAGE_VICE_CITY_PACK_01", 0.45, ["GRATIS", "POR RESERVAR"], "COCHE + GARAJE + LOOKS", "GTA 6"),
    "s3-ultimate-edition": ("ULTIMATE_EDITION_01", 0.55, ["¿VALE LA", "PENA?"], "ULTIMATE EDITION", "GTA 6"),
}

def cover(slug):
    img, fx, lines, chip, tag = COVERS[slug]
    src = Image.open(os.path.join(IMG, img + ".jpg")).convert("RGB")
    s = H / src.size[1]; src = src.resize((int(src.size[0] * s), H), Image.LANCZOS)
    x0 = int(min(max(0, fx * src.size[0] - W / 2), src.size[0] - W))
    im = src.crop((x0, 0, x0 + W, H)).convert("RGBA")
    im.alpha_composite(overlay())
    # texto en el centro (zona que se ve también al recortar a cuadrado)
    y = 560
    t = text_img(tag, font("head", 110), fill=WHITE, stroke=7, stroke_fill=PINK, glow=CYAN)
    im.alpha_composite(t, ((W - t.size[0]) // 2, y - 150))
    for i, ln in enumerate(lines):
        f = fit(ln, "head", 1000, 230 if i == 0 else 250)
        tt = text_img(ln, f, fill=YEL if i == 1 else WHITE, stroke=12, stroke_fill=(0, 0, 0), glow=PINK)
        im.alpha_composite(tt, ((W - tt.size[0]) // 2, y)); y += tt.size[1] - 80
    b = badge(chip, fit(chip, "black", 900, 62), bg=PINK).rotate(3, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(b, ((W - b.size[0]) // 2, y + 30))
    cr = text_img("Imágenes: Rockstar Games", font("semi", 26), stroke=3, pad=8)
    im.alpha_composite(cr, (30, 120))
    out = os.path.join(OUT, slug, slug + "-cover.jpg")
    im.convert("RGB").save(out, quality=93)
    # incrustar como portada del archivo mp4
    mp4 = os.path.join(OUT, slug, slug + ".mp4"); tmp = mp4 + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-i", out, "-map", "0", "-map", "1", "-c", "copy",
                    "-disposition:v:1", "attached_pic", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, mp4)
    return out

if __name__ == "__main__":
    for k in COVERS: print(cover(k))
