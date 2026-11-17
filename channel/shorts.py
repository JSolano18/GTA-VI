# -*- coding: utf-8 -*-
"""Shorts verticales (1080x1920, < 60 s) con imágenes oficiales de Rockstar.

Uso: python3 channel/shorts.py s1-hora-por-pais
"""
import json, math, os, subprocess, sys
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A
import visuals as V
from visuals import PINK, CYAN, YEL, WHITE, font, fit, wrap, text_img, badge, panel

W, H, FPS = 1080, 1920, 30
IMG = os.path.join(V.ROOT, "assets", "oficial", "shorts")
OUT = os.path.join(V.ROOT, "output", "shorts")
LEAD, TAIL = 0.12, 0.28
CREDIT = "Imágenes: Rockstar Games"

SHORTS = [
# ------------------------------------------------------------------ 1
{"slug": "s1-hora-por-pais", "seed": 21,
 "title": "¿A qué hora sale GTA 6 en tu país? 🕛 #gta6 #shorts",
 "desc": "GTA 6 se desbloquea a medianoche por país, y Nueva Zelanda es la primera. Esta es la hora a la que empiezan allí, convertida a tu país.",
 "tags": ["gta 6", "a que hora sale gta 6", "gta 6 hora", "gta 6 nueva zelanda", "gta 6 lanzamiento", "shorts"],
 "scenes": [
  {"img": "Lucia_Caminos_02", "fx": 0.46, "head": "¿A QUÉ HORA SALE GTA 6?",
   "say": "Hay gente que va a jugar GTA 6 casi un día antes que tú. Te explico por qué."},
  {"img": "Vice_City_01", "fx": 0.55, "head": "MEDIANOCHE POR PAÍS",
   "say": "El lanzamiento va por zonas horarias: el juego se desbloquea a la medianoche de cada país, empezando por Oceanía."},
  {"img": "Leonida_Keys_02", "fx": 0.6, "head": "NUEVA ZELANDA, PRIMERO", "big": "00:00", "label": "NUEVA ZELANDA · JUEVES 19",
   "say": "Los primeros son Nueva Zelanda. Allí la medianoche del jueves llega cuando en México todavía es miércoles."},
  {"img": "Vice_City_03", "fx": 0.5, "head": "ESA HORA EN TU PAÍS",
   "rows": [["MÉXICO", "05:00"], ["COLOMBIA · PERÚ", "06:00"], ["ARGENTINA · CHILE", "08:00"], ["ESPAÑA", "12:00"]], "rows_note": "Miércoles 18",
   "say": "En ese momento, en México serán las cinco de la mañana del miércoles dieciocho. En Colombia y Perú, las seis. En Argentina y Chile, las ocho. Y en España, el mediodía."},
  {"img": "Vice_City_05", "fx": 0.55, "head": "¿Y TÚ CUÁNDO JUEGAS?", "big": "00:00", "label": "TU MEDIANOCHE",
   "say": "¿Y tú? A tu medianoche, en la noche del miércoles al jueves. Confirma la hora exacta en la ficha de tu tienda."},
  {"img": "Jason_Duval_02", "fx": 0.3, "head": "PRECARGA ABIERTA",
   "say": "Y la precarga está abierta desde el diez de noviembre. Si no la tienes al cien por cien, déjala descargando ya. Sígueme para más de GTA 6."},
 ]},
# ------------------------------------------------------------------ 2
{"slug": "s2-bonus-reserva", "seed": 22,
 "title": "Esto te dan GRATIS por reservar GTA 6 🚗 #gta6 #shorts",
 "desc": "El Vintage Vice City Pack: lo que te llevas gratis por reservar GTA 6 antes del lanzamiento, en cualquiera de sus ediciones.",
 "tags": ["gta 6", "gta 6 reserva", "gta 6 bonus", "vintage vice city pack", "gta 6 preorder", "shorts"],
 "scenes": [
  {"img": "VINTAGE_VICE_CITY_PACK_01", "fx": 0.45, "head": "GRATIS POR RESERVAR",
   "say": "Si reservas GTA 6 antes del lanzamiento, te llevas un coche, un garaje y mucho más. Gratis."},
  {"img": "VINTAGE_VICE_CITY_PACK_02", "fx": 0.42, "head": "VINTAGE VICE CITY PACK", "chip": "EDICIÓN NORMAL Y ULTIMATE",
   "say": "Se llama Vintage Vice City Pack, y viene con las dos ediciones: la normal y la Ultimate."},
  {"img": "VINTAGE_VICE_CITY_PACK_VAPID_STANIER_01", "fx": 0.45, "head": "1. VAPID STANIER '55", "chip": "+ GARAJE EN OCEAN BEACH",
   "say": "Uno: un Vapid Stanier del cincuenta y cinco, con su propio garaje junto a Ocean Beach. Trae armero y un sitio para guardar lo robado."},
  {"img": "VINTAGE_VICE_CITY_PACK_EXCLUSIVE_LOOKS_01", "fx": 0.6, "head": "2. LOOKS DE LOS 80",
   "say": "Dos: ropa y peinados de los ochenta. Jason, con traje de lino pastel. Lucía, con un mini vestido rojo de lentejuelas y rizos."},
  {"img": "VINTAGE_VICE_CITY_PACK_EXCLUSIVE_LOOKS_03", "fx": 0.45, "head": "3. PATRÓN TROPICAL",
   "say": "Tres: un patrón tropical para casi todas las armas, inspirado en la camisa de palmeras de Tommy Vercetti."},
  {"img": "VINTAGE_VICE_CITY_PACK_EXCLUSIVE_LOOKS_02", "fx": 0.5, "head": "+ 1 MES DE GTA+", "chip": "SOLO RESERVA DIGITAL",
   "say": "Y si reservas en digital, también un mes gratis de GTA plus. Ojo: la oferta termina con el lanzamiento. Sígueme para más."},
 ]},
# ------------------------------------------------------------------ 3
{"slug": "s3-ultimate-edition", "seed": 23,
 "title": "¿Vale la pena la ULTIMATE de GTA 6? 💎 #gta6 #shorts",
 "desc": "Todo lo que trae la Ultimate Edition de GTA 6 en menos de un minuto: vehículos, tiendas exclusivas, talleres y más. ¿Vale los 20 dólares extra?",
 "tags": ["gta 6", "gta 6 ultimate edition", "gta 6 ediciones", "gta 6 vale la pena", "gta 6 precio", "shorts"],
 "scenes": [
  {"img": "ULTIMATE_EDITION_01", "fx": 0.55, "head": "¿VALE LA PENA LA ULTIMATE?", "chip": "+20 USD (EE.UU.)",
   "say": "La Ultimate Edition de GTA 6 cuesta veinte dólares más en Estados Unidos. Esto es todo lo que trae."},
  {"img": "ULTIMATE_EDITION_GROTTI_CHEETAH_01", "fx": 0.3, "head": "VEHÍCULOS",
   "say": "Vehículos: un Grotti Cheetah del noventa y cinco, una lancha Squalo con caja de explosivos, y una moto y un kayak para Jason."},
  {"img": "ULTIMATE_EDITION_ELECTRIC_FANG_01", "fx": 0.3, "head": "TIENDAS EXCLUSIVAS",
   "say": "Tiendas exclusivas: el tatuador Electric Fang, con más de cincuenta tatuajes, el salón de Sara y la tienda de ropa Stock 305."},
  {"img": "ULTIMATE_EDITION_RIDEOUT_CUSTOMS_01", "fx": 0.3, "head": "TALLERES",
   "say": "Dos talleres: Rideout Customs, para llantas y estilo donk, y One Eyed Willie's, para todoterrenos."},
  {"img": "ULTIMATE_EDITION_WYMAN_CAR_COLLECTION_01", "fx": 0.5, "head": "Y ADEMÁS...",
   "say": "Y además: revólveres grabados, un encargo para restaurar coches clásicos, y una banda a la que puedes asaltar para sacar contrabando."},
  {"img": "ULTIMATE_EDITION_SARAS_SALON_01", "fx": 0.35, "head": "MI VEREDICTO",
   "rows": [["SOLO HISTORIA", "NORMAL"], ["CIENTOS DE HORAS", "ULTIMATE"]],
   "say": "¿Vale la pena? No cambia la historia, son extras. Si vas a jugar cientos de horas, sí. Si solo quieres la historia, con la normal te basta. ¿Tú cuál compraste?"},
 ]},
]

def ease(p):
    p = max(0.0, min(1.0, p)); return 1 - (1 - p) ** 3

def ease_back(p):
    p = max(0.0, min(1.0, p)); c = 1.9
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2

def load_bg(name):
    im = Image.open(os.path.join(IMG, name + ".jpg")).convert("RGB")
    s = (H * 1.12) / im.size[1]
    return im.resize((int(im.size[0] * s), int(im.size[1] * s)), Image.LANCZOS)

def overlay():
    g = np.zeros((H, W, 4), np.uint8)
    y = np.arange(H)
    a = np.clip(np.maximum((620 - y) / 620 * 215, (y - 1000) / 920 * 235), 0, 235)
    g[..., 0] = 12; g[..., 1] = 4; g[..., 2] = 28; g[..., 3] = a[:, None]
    return Image.fromarray(g, "RGBA")

def scale_alpha(img, f):
    if f >= 0.999: return img
    im = img.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * f))); return im

def paste(frame, img, x, y, t, t0, anim="pop", d=0.35):
    lt = t - t0
    if lt < 0: return
    p = min(1.0, lt / d)
    if anim == "pop" and p < 1:
        s = max(0.05, ease_back(p))
        nw, nh = max(1, int(img.size[0] * s)), max(1, int(img.size[1] * s))
        x += (img.size[0] - nw) // 2; y += (img.size[1] - nh) // 2
        img = img.resize((nw, nh), Image.BILINEAR)
    elif anim == "up":
        y += int((1 - ease(p)) * 70); img = scale_alpha(img, min(1, p * 2))
    elif anim == "left":
        x += int((1 - ease(p)) * 140); img = scale_alpha(img, min(1, p * 2))
    frame.alpha_composite(img, (int(x), int(y)))

def chunks(text, maxw=3):
    words = text.split(); out = []; cur = []
    for w in words:
        cur.append(w)
        if len(cur) >= maxw or w.endswith((".", ",", "?", ":", "!")):
            out.append(" ".join(cur)); cur = []
    if cur: out.append(" ".join(cur))
    return out

def cap_img(t):
    f = fit(t.upper(), "black", 960, 84, 50)
    return text_img(t.upper(), f, fill=WHITE, stroke=9, stroke_fill=(0, 0, 0), pad=24)

def scene_layers(s):
    L = []  # (img, x, y, t0, anim)
    hf = font("head", 120)
    y = 250
    for i, ln in enumerate(wrap(s["head"], hf, 960)):
        t = text_img(ln, fit(ln, "head", 980, 120), fill=YEL, stroke=8, stroke_fill=(0, 0, 0), glow=PINK)
        L.append((t, (W - t.size[0]) // 2, y, 0.05 + i * 0.1, "pop")); y += t.size[1] - 55
    if s.get("chip"):
        c = badge(s["chip"], font("black", 44), bg=PINK)
        L.append((c, (W - c.size[0]) // 2, y + 45, 0.35, "pop")); y += c.size[1] + 45
    top = max(640, y + 60)
    if s.get("big"):
        b = text_img(s["big"], font("head", 300), fill=WHITE, stroke=10, stroke_fill=(0, 0, 0), glow=CYAN)
        L.append((b, (W - b.size[0]) // 2, top, 0.3, "pop"))
        l = badge(s["label"], font("black", 46), bg=CYAN, fg=(10, 5, 25))
        L.append((l, (W - l.size[0]) // 2, top + b.size[1] - 40, 0.55, "up"))
    if s.get("rows"):
        n = len(s["rows"]); ry = top + (90 if s.get("rows_note") else 0)
        if s.get("rows_note"):
            nb = badge(s["rows_note"].upper(), font("black", 40), bg=CYAN, fg=(10, 5, 25))
            L.append((nb, (W - nb.size[0]) // 2, ry - 90, 0.2, "pop"))
        for i, (a, b) in enumerate(s["rows"]):
            p = panel(960, 124, accent=PINK if i % 2 == 0 else CYAN, alpha=225)
            d = ImageDraw.Draw(p)
            d.text((50, 62), a, font=fit(a, "black", 560, 50, 30), fill=WHITE, anchor="lm")
            d.text((910, 62), b, font=font("head", 84), fill=YEL, anchor="rm")
            L.append((p, 60, ry + i * 132, 0.5 + i * 0.9, "left"))
    return L

def build(slug):
    sh = next(x for x in SHORTS if x["slug"] == slug)
    od = os.path.join(OUT, slug); wk = os.path.join(od, "_work"); os.makedirs(wk, exist_ok=True)
    A.SPEED = 1.14
    tl, t = [], 0.0
    for i, s in enumerate(sh["scenes"]):
        wav = os.path.join(wk, f"vo_{i:02}.wav")
        vo = A.tts(s["say"], wav)
        dur = LEAD + len(vo) / A.SR + TAIL
        tl.append(dict(start=t, dur=dur, vo=vo, s=s)); t += dur
    total = t
    # captions (palabras agrupadas de 3 en 3, repartidas por longitud)
    caps = []
    for e in tl:
        cs = chunks(e["s"]["say"]); tot = sum(len(c) + 3 for c in cs); cur = e["start"] + LEAD
        vd = len(e["vo"]) / A.SR
        for c in cs:
            d = vd * (len(c) + 3) / tot; caps.append((cur, cur + d, cap_img(c))); cur += d
    # audio
    n = int(total * A.SR) + 1
    voice = np.zeros(n, np.float32)
    for e in tl:
        a = int((e["start"] + LEAD) * A.SR); voice[a:a + len(e["vo"])] += e["vo"][: n - a]
    env = np.convolve(np.abs(voice), np.ones(int(0.25 * A.SR)) / (0.25 * A.SR), mode="same")
    env = np.clip(env / (env.max() + 1e-6) * 4, 0, 1)
    mus = A.music(n / A.SR, seed=sh["seed"], bpm=110)[:n]
    mus = mus * (0.28 - 0.17 * env[: len(mus)])
    sfx = np.zeros(n, np.float32); wh = A.whoosh(sh["seed"])
    for e in tl[1:]:
        a = int(max(0, e["start"] - 0.18) * A.SR); sfx[a:a + len(wh)] += wh[: n - a]
    mix = np.clip(voice + mus + sfx * 0.8, -1, 1)
    mw = os.path.join(wk, "mix.wav"); sf.write(mw, mix, A.SR)
    # imagen
    for e in tl:
        e["bg"] = load_bg(e["s"]["img"]); e["L"] = scene_layers(e["s"])
    ov = overlay()
    cred = text_img(CREDIT, font("semi", 26), stroke=3, pad=8)
    handle = text_img("@LeonidaDiario", font("black", 34), fill=WHITE, stroke=4, pad=8)
    out = os.path.join(od, slug + ".mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", mw, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
           "-shortest", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    N = int(math.ceil(total * FPS)); si = 0; ci = 0
    for fi in range(N):
        t = fi / FPS
        while si + 1 < len(tl) and t >= tl[si + 1]["start"]: si += 1
        e = tl[si]; lt = t - e["start"]; sp = lt / e["dur"]
        bg = e["bg"]; bw, bh = bg.size
        z = 1.0 + 0.07 * sp                      # zoom lento
        cw, chh = W / z, H / z
        cx = min(max(cw / 2, e["s"]["fx"] * bw + (sp - 0.5) * 60 * (1 if si % 2 else -1)), bw - cw / 2)
        cy = bh / 2
        frame = bg.transform((W, H), Image.AFFINE, (1 / z, 0, cx - cw / 2, 0, 1 / z, cy - chh / 2), resample=Image.BILINEAR).convert("RGBA")
        frame.alpha_composite(ov)
        for (img, x, y, t0, anim) in e["L"]:
            paste(frame, img, x, y, lt, t0, anim)
        while ci + 1 < len(caps) and t >= caps[ci + 1][0]: ci += 1
        a, b, c = caps[ci]
        if a <= t < b + 0.1:
            paste(frame, c, (W - c.size[0]) // 2, 1360, t, a, "pop", 0.12)
        if lt < 0.1 and si > 0:
            frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - lt / 0.1)))))
        frame.alpha_composite(cred, (30, 120))
        ff.stdin.write(frame.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    with open(os.path.join(od, "titulo.txt"), "w") as f: f.write(sh["title"])
    with open(os.path.join(od, "descripcion.txt"), "w") as f:
        f.write(sh["desc"] + "\n\n" + "Imágenes: Rockstar Games (web oficial de GTA VI). Canal de fans no oficial, sin afiliación con "
                "Rockstar Games ni Take-Two. Voz sintética.\n\n#GTA6 #GTAVI #Shorts")
    with open(os.path.join(od, "tags.txt"), "w") as f: f.write(", ".join(sh["tags"]))
    print(f"{slug}: {total:.1f}s -> {out}")

if __name__ == "__main__":
    build(sys.argv[1])
