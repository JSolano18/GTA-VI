# -*- coding: utf-8 -*-
"""Renderiza un video completo: voz + música + animación + subtítulos + montaje.

Uso: python3 channel/render.py 01-hora-lanzamiento [--preview]
"""
import json, math, os, subprocess, sys
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A
import visuals as V
from visuals import W, H, PINK, CYAN, YEL, WHITE, RED, font, fit, wrap, text_img, panel, badge
from videos import VIDEOS, CHANNEL

FPS = 30
OUT = os.path.join(V.ROOT, "output")
LEAD, TAIL = 0.35, 0.55

def ease(p):
    p = max(0.0, min(1.0, p)); return 1 - (1 - p) ** 3

def ease_back(p):
    p = max(0.0, min(1.0, p)); c = 1.70158
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2

def E(img, x, y, t0, anim="fade", d=0.45, sfx=None):
    return {"img": img, "x": int(x), "y": int(y), "t0": t0, "anim": anim, "d": d, "sfx": sfx}

def center_x(img): return (W - img.size[0]) // 2

# ---------------------------------------------------------------- layouts
def L_title(s, dur):
    els = []
    k = badge(s["kicker"], font("black", 44), bg=PINK)
    els.append(E(k, center_x(k), 170, 0.05, "pop", sfx="pop"))
    f = font("head", 150)
    lines = wrap(s["title"], f, 1650)
    y = 290
    for i, ln in enumerate(lines):
        t = text_img(ln, fit(ln, "head", 1700, 150), fill=YEL, stroke=8, stroke_fill=(0, 0, 0), glow=PINK)
        els.append(E(t, center_x(t), y, 0.25 + i * 0.15, "up")); y += t.size[1] - 55
    sub = text_img(s["sub"], font("bold", 54), stroke=4)
    els.append(E(sub, center_x(sub), y + 20, 0.8, "fade"))
    return els

def L_big(s, dur):
    els = []
    b = text_img(s["big"], fit(s["big"], "head", 1600, 330), fill=WHITE, stroke=10, stroke_fill=(0, 0, 0), glow=PINK)
    els.append(E(b, center_x(b), 140, 0.1, "pop", d=0.55, sfx="pop"))
    l = badge(s["label"], font("black", 56), bg=PINK)
    ly = 140 + b.size[1] - 40
    els.append(E(l, center_x(l), ly, 0.55, "up"))
    if s.get("sub"):
        sb = text_img(s["sub"], fit(s["sub"], "semi", 1600, 44), stroke=3)
        els.append(E(sb, center_x(sb), ly + l.size[1] + 25, 1.0, "fade"))
    return els

def L_list(s, dur):
    els = []
    h = text_img(s["heading"], fit(s["heading"], "head", 1600, 100), fill=YEL, stroke=6, glow=PINK)
    els.append(E(h, 120, 90, 0.05, "left"))
    n = len(s["items"]); span = max(1.0, dur * 0.72 - 0.6)
    y = 300
    step = min(150, int(560 / max(n, 1)))
    for i, it in enumerate(s["items"]):
        f = fit(it, "bold", 1440, 56, 34)
        row = panel(1560, 120, accent=CYAN if i % 2 else PINK, alpha=215)
        d = ImageDraw.Draw(row)
        d.polygon([(60, 60), (80, 40), (100, 60), (80, 80)], fill=YEL)
        d.text((130, 60), it, font=f, fill=WHITE, anchor="lm")
        els.append(E(row, 170, y, 0.6 + span * i / n, "left", sfx="pop")); y += step
    return els

def L_compare(s, dur):
    els = []
    for side, (data, acc, x) in enumerate([(s["left"], CYAN, 130), (s["right"], PINK, 990)]):
        p = panel(800, 700, accent=acc, alpha=225)
        d = ImageDraw.Draw(p)
        d.text((400, 95), data["title"], font=fit(data["title"], "head", 700, 96), fill=acc, anchor="mm")
        d.line([60, 160, 740, 160], fill=acc + (160,), width=3)
        els.append(E(p, x, 120, 0.1 + side * 0.25, "up", sfx="pop" if side == 0 else None))
        n = len(data["items"])
        for i, it in enumerate(data["items"]):
            body = text_img(it, fit(it, "bold", 620, 50, 30))
            t = Image.new("RGBA", (body.size[0] + 60, body.size[1]), (0, 0, 0, 0))
            md = ImageDraw.Draw(t); cy = body.size[1] // 2
            if side == 0:
                md.line([(30, cy), (42, cy + 14), (64, cy - 14)], fill=acc, width=9)
            else:
                md.line([(32, cy - 14), (60, cy + 14)], fill=acc, width=9); md.line([(32, cy + 14), (60, cy - 14)], fill=acc, width=9)
            t.alpha_composite(body, (50, 0))
            t0 = 0.8 + (side * n + i) * max(0.35, (dur * 0.7) / (2 * n + 1))
            els.append(E(t, x + 50, 300 + i * 115, t0, "left", sfx="pop"))
    return els

def L_warn(s, dur):
    els = []
    tri = Image.new("RGBA", (300, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(tri)
    d.polygon([(150, 10), (290, 260), (10, 260)], fill=RED + (255,))
    d.text((150, 165), "!", font=font("head", 170), fill=WHITE, anchor="mm")
    g = tri.filter(ImageFilter.GaussianBlur(20)); g2 = Image.new("RGBA", tri.size); g2.alpha_composite(g); g2.alpha_composite(tri)
    els.append(E(g2, center_x(g2), 70, 0.05, "pop", d=0.5, sfx="pop"))
    h = text_img(s["heading"], fit(s["heading"], "head", 1700, 130), fill=WHITE, stroke=8, stroke_fill=RED, glow=RED)
    els.append(E(h, center_x(h), 330, 0.35, "up"))
    f = font("bold", 54)
    y = 330 + h.size[1] - 20
    for i, ln in enumerate(wrap(s["text"], f, 1500)):
        t = text_img(ln, f, fill=YEL, stroke=4)
        els.append(E(t, center_x(t), y, 0.8 + i * 0.15, "fade")); y += t.size[1] - 30
    return els

def L_quote(s, dur):
    els = []
    q = text_img("“", font("head", 360), fill=PINK, glow=PINK)
    els.append(E(q, 120, 20, 0.05, "pop"))
    f = font("head", 104)
    lines = wrap(s["text"], f, 1500)
    y = 540 - (len(lines) * 120) // 2 - 60
    for i, ln in enumerate(lines):
        t = text_img(ln, f, fill=WHITE, stroke=6, glow=(120, 30, 160))
        els.append(E(t, center_x(t), y, 0.3 + i * 0.35, "up")); y += 120
    return els

def L_timeline(s, dur):
    els = []
    h = text_img(s["heading"], fit(s["heading"], "head", 1600, 100), fill=YEL, stroke=6, glow=PINK)
    els.append(E(h, center_x(h), 80, 0.05, "up"))
    line = Image.new("RGBA", (1640, 20), (0, 0, 0, 0))
    ImageDraw.Draw(line).rounded_rectangle([0, 4, 1640, 14], 6, fill=CYAN + (255,))
    els.append(E(line, 140, 530, 0.3, "wipe", d=0.9))
    ev = s["events"]; n = len(ev)
    span = max(1.0, dur * 0.7 - 0.8)
    for i, (yr, lab) in enumerate(ev):
        cx = 140 + 1640 * (i + 0.5) / n
        t0 = 0.8 + span * i / n
        dot = Image.new("RGBA", (80, 80), (0, 0, 0, 0)); dd = ImageDraw.Draw(dot)
        dd.ellipse([10, 10, 70, 70], fill=PINK, outline=WHITE, width=6)
        els.append(E(dot, cx - 40, 500, t0, "pop", sfx="pop"))
        yt = text_img(yr, fit(yr, "head", 1640 / n - 20, 110), fill=WHITE, stroke=6, glow=PINK)
        els.append(E(yt, cx - yt.size[0] / 2, 470 - yt.size[1] + 20, t0 + 0.1, "up"))
        f = font("bold", 44)
        yy = 610
        for ln in wrap(lab, f, 1640 / n - 40):
            lt = text_img(ln, f, fill=YEL, stroke=3)
            els.append(E(lt, cx - lt.size[0] / 2, yy, t0 + 0.25, "fade")); yy += lt.size[1] - 30
    return els

_map_cache = {}
def L_map(s, dur):
    els = []
    hl = s["highlight"]
    if hl not in _map_cache:
        _map_cache[hl] = V.leonida_map(860, 820, hl)
    m = _map_cache[hl]
    p = panel(920, 880, accent=CYAN, alpha=190)
    p.alpha_composite(m, (30, 30))
    els.append(E(p, 950, 60, 0.0, "fade", d=0.35))
    k = badge("LEONIDA", font("black", 40), bg=CYAN, fg=(10, 5, 25))
    els.append(E(k, 110, 210, 0.15, "left"))
    words = hl.split()
    y = 290
    for i, wd in enumerate(words):
        t = text_img(wd, fit(wd, "head", 780, 170), fill=YEL, stroke=8, glow=PINK)
        els.append(E(t, 100, y, 0.3 + i * 0.15, "left", sfx="pop" if i == 0 else None)); y += t.size[1] - 60
    # pin
    lx, ly = V.LABEL_POS[hl]
    pin = Image.new("RGBA", (70, 90), (0, 0, 0, 0)); pd = ImageDraw.Draw(pin)
    pd.ellipse([5, 0, 65, 60], fill=YEL); pd.polygon([(10, 42), (60, 42), (35, 88)], fill=YEL); pd.ellipse([22, 17, 48, 43], fill=(20, 10, 40))
    els.append(E(pin, 950 + 30 + lx * 860 - 35, 60 + 30 + ly * 820 - 130, 0.6, "drop", d=0.6))
    return els

def L_chars(s, dur):
    els = []
    sil = V.silhouette(760, PINK if "LUCIA" in s["name"] else CYAN)
    els.append(E(sil, 120, 1080 - 760 - 120, 0.0, "up", d=0.6))
    r = badge(s["role"].upper(), font("black", 42), bg=PINK)
    els.append(E(r, 820, 190, 0.2, "left", sfx="pop"))
    y = 260
    for i, wd in enumerate(s["name"].split()):
        t = text_img(wd, fit(wd, "head", 1000, 190), fill=YEL if i == 0 else WHITE, stroke=8, glow=PINK)
        els.append(E(t, 800, y, 0.35 + i * 0.15, "left")); y += t.size[1] - 70
    f = font("semi", 46)
    for ln in wrap(s["note"], f, 980):
        t = text_img(ln, f, stroke=3)
        els.append(E(t, 815, y + 30, 0.9, "fade")); y += t.size[1] - 30
    return els

def L_cta(s, dur):
    els = []
    btn = Image.new("RGBA", (760, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(btn)
    d.rounded_rectangle([0, 0, 760, 170], 30, fill=(230, 20, 40))
    d.polygon([(60, 50), (60, 120), (120, 85)], fill=WHITE)
    d.text((440, 85), "SUSCRÍBETE", font=font("head", 100), fill=WHITE, anchor="mm")
    els.append(E(btn, 120, 260, 0.2, "pop", d=0.6, sfx="pop"))
    t = text_img("+ activa la campanita", font("bold", 52), stroke=4)
    els.append(E(t, 140, 460, 0.8, "fade"))
    ch = text_img(CHANNEL["name"].upper(), font("head", 90), fill=YEL, stroke=6, glow=PINK)
    els.append(E(ch, 120, 100, 0.0, "left"))
    # huecos para las pantallas finales de YouTube (vídeo recomendado + lista)
    for i, lab in enumerate(["SIGUIENTE VIDEO", "LISTA GTA 6"]):
        box = Image.new("RGBA", (760, 428), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, 759, 427], 20, fill=(0, 0, 0, 120), outline=CYAN if i else PINK, width=6)
        bd.text((380, 214), lab, font=font("black", 44), fill=(255, 255, 255, 140), anchor="mm")
        els.append(E(box, 1060, 60 + i * 470, 0.4 + i * 0.2, "left"))
    return els

LAYOUTS = {"title": L_title, "big": L_big, "list": L_list, "compare": L_compare, "warn": L_warn,
           "quote": L_quote, "timeline": L_timeline, "map": L_map, "chars": L_chars, "cta": L_cta}

# ---------------------------------------------------------------- subtítulos
def chunks(text, maxc=34):
    words, out, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) > maxc and cur:
            out.append(cur); cur = w
        else:
            cur = t
        if cur.endswith((".", "?", ":", "!")) and len(cur) > 12:
            out.append(cur); cur = ""
    if cur: out.append(cur)
    return out

def caption_img(txt):
    f = font("black", 50)
    t = text_img(txt, f, fill=WHITE, stroke=5, stroke_fill=(0, 0, 0), pad=18)
    bg = Image.new("RGBA", (t.size[0] + 30, t.size[1] + 6), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle([0, 0, bg.size[0] - 1, bg.size[1] - 1], 18, fill=(10, 4, 25, 170))
    bg.alpha_composite(t, (15, 3))
    return bg

def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# ---------------------------------------------------------------- render
def fade_alpha(img, f):
    if f >= 0.999: return img
    im = img.copy()
    a = im.getchannel("A").point(lambda v: int(v * f))
    im.putalpha(a); return im

def draw_el(frame, e, t, scene_end):
    lt = t - e["t0"]
    if lt < 0: return
    p = min(1.0, lt / e["d"])
    out_f = min(1.0, max(0.0, (scene_end - t) / 0.22))
    img, x, y = e["img"], e["x"], e["y"]
    a = ease(p)
    if e["anim"] == "up":
        y += int((1 - a) * 60)
    elif e["anim"] == "left":
        x += int((1 - a) * 120)
    elif e["anim"] == "drop":
        y -= int((1 - ease_back(p)) * 200)
    elif e["anim"] == "pop" and p < 1:
        s = max(0.05, ease_back(p))
        nw, nh = max(1, int(img.size[0] * s)), max(1, int(img.size[1] * s))
        x += (img.size[0] - nw) // 2; y += (img.size[1] - nh) // 2
        img = img.resize((nw, nh), Image.BILINEAR)
    elif e["anim"] == "wipe" and p < 1:
        img = img.crop((0, 0, max(1, int(img.size[0] * a)), img.size[1]))
    alpha = (min(1.0, p * 2.5) if e["anim"] != "pop" else 1.0) * out_f
    if alpha <= 0.01: return
    im = fade_alpha(img, alpha)
    if x < 0 or y < 0:
        im = im.crop((max(0, -x), max(0, -y), im.size[0], im.size[1])); x, y = max(0, x), max(0, y)
    if x >= W or y >= H: return
    im = im.crop((0, 0, min(im.size[0], W - x), min(im.size[1], H - y)))
    frame.alpha_composite(im, (x, y))

def build(slug, preview=False):
    v = next(x for x in VIDEOS if x["slug"] == slug)
    vi = VIDEOS.index(v)
    work = os.path.join(OUT, slug, "_work"); os.makedirs(work, exist_ok=True)
    outdir = os.path.join(OUT, slug)
    scenes = v["scenes"][:2] if preview else v["scenes"]

    # 1) voz por escena
    timeline, voice_parts, t = [], [], 0.0
    for i, s in enumerate(scenes):
        wav = os.path.join(work, f"vo_{i:02}.wav")
        if not os.path.exists(wav) or os.path.getmtime(wav) < os.path.getmtime(os.path.join(V.ROOT, "channel", "videos.py")):
            A.tts(s["say"], wav)
        vo, _ = sf.read(wav, dtype="float32")
        vd = len(vo) / A.SR
        dur = LEAD + vd + TAIL
        if s["layout"] == "cta": dur = max(dur, 15.0)
        timeline.append({"start": t, "dur": dur, "vo_start": t + LEAD, "vo_dur": vd, "scene": s})
        voice_parts.append((t + LEAD, vo)); t += dur
    total = t
    N = int(math.ceil(total * FPS))

    # 2) elementos visuales + subtítulos
    caps, srt = [], []
    for tl in timeline:
        s = tl["scene"]
        tl["els"] = LAYOUTS[s["layout"]](s, tl["dur"])
        cs = chunks(s["say"]); tot = sum(len(c) + 4 for c in cs); cur = tl["vo_start"]
        for c in cs:
            d = tl["vo_dur"] * (len(c) + 4) / tot
            caps.append((cur, cur + d, caption_img(c))); srt.append((cur, cur + d, c)); cur += d
    with open(os.path.join(outdir, f"{slug}.srt"), "w") as fh:
        for i, (a, b, c) in enumerate(srt, 1):
            fh.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{c}\n\n")

    # 3) audio: voz + música con ducking + efectos
    n = int(total * A.SR) + A.SR
    voice = np.zeros(n, np.float32)
    for st, vo in voice_parts:
        a = int(st * A.SR); voice[a:a + len(vo)] += vo
    env = np.convolve(np.abs(voice), np.ones(int(0.3 * A.SR)) / (0.3 * A.SR), mode="same")
    env = np.clip(env / (env.max() + 1e-6) * 4, 0, 1)
    mus = A.music(n / A.SR, seed=vi)
    mus = mus[:n] * (0.20 - 0.13 * env[:len(mus)])
    sfx = np.zeros(n, np.float32)
    wh, pp = A.whoosh(vi), A.pop()
    for i, tl in enumerate(timeline):
        a = int(max(0, tl["start"] - 0.15) * A.SR); sfx[a:a + len(wh)] += wh[: n - a]
        for e in tl["els"]:
            if e.get("sfx") == "pop":
                b = int((tl["start"] + e["t0"]) * A.SR); sfx[b:b + len(pp)] += pp[: n - b]
    mix = voice + mus + sfx * 0.7
    mix = mix[: int(total * A.SR)]
    mix_wav = os.path.join(work, "mix.wav"); sf.write(mix_wav, np.clip(mix, -1, 1), A.SR)

    # 4) imagen
    bg = V.background(v["theme"], seed=vi * 7 + 3)
    bw, bh = bg.size
    grid = V.grid_frames() if v["theme"] == "sunset" else None
    vig = V.vignette()
    rng = np.random.default_rng(vi)
    parts = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(-8, 8), rng.uniform(-30, -8), rng.uniform(4, 12)) for _ in range(28)]
    spr = {}
    def sprite(r):
        r = int(r)
        if r not in spr:
            im = Image.new("RGBA", (r * 6, r * 6), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([r * 2, r * 2, r * 4, r * 4], fill=(255, 180, 230, 150))
            spr[r] = im.filter(ImageFilter.GaussianBlur(r * 0.8))
        return spr[r]
    logo = badge(CHANNEL["name"].upper(), font("black", 30), bg=PINK)
    logo = fade_alpha(logo, 0.85)

    out_mp4 = os.path.join(outdir, f"{slug}{'-preview' if preview else ''}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", mix_wav, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-threads", "2",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", "-shortest", out_mp4]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    si = 0; ci = 0
    for fi in range(N):
        t = fi / FPS
        while si + 1 < len(timeline) and t >= timeline[si + 1]["start"]:
            si += 1
        tl = timeline[si]; lt = t - tl["start"]; sp = lt / tl["dur"]
        # cámara: paneo lento alternando dirección por escena
        dirx = 1 if si % 2 == 0 else -1
        ox = (bw - W) / 2 + dirx * (sp - 0.5) * (bw - W) * 0.9
        oy = (bh - H) * (0.3 + 0.4 * sp)
        frame = bg.transform((W, H), Image.AFFINE, (1, 0, ox, 0, 1, oy), resample=Image.BILINEAR).convert("RGBA")
        if grid: frame.alpha_composite(grid[fi % len(grid)])
        for (px, py, vx, vy, r) in parts:
            x = (px + vx * t) % W; y = (py + vy * t) % H
            frame.alpha_composite(sprite(r), (int(x), int(y)))
        frame.alpha_composite(vig)
        end = tl["start"] + tl["dur"] if si + 1 < len(timeline) else 1e9
        for e in tl["els"]:
            draw_el(frame, e, lt, tl["dur"] if si + 1 < len(timeline) else 1e9)
        # subtítulo activo
        while ci + 1 < len(caps) and t >= caps[ci + 1][0]:
            ci += 1
        a, b, cimg = caps[ci]
        if a <= t < b + 0.15 and tl["scene"]["layout"] != "cta":
            pp_ = min(1.0, (t - a) / 0.12)
            cy = 945 + int((1 - ease(pp_)) * 18)
            frame.alpha_composite(cimg, ((W - cimg.size[0]) // 2, cy))
        # flash de transición
        if lt < 0.12 and si > 0:
            fl = Image.new("RGBA", (W, H), (255, 120, 200, int(150 * (1 - lt / 0.12))))
            frame.alpha_composite(fl)
        frame.alpha_composite(logo, (36, 30))
        # barra de progreso
        d = ImageDraw.Draw(frame)
        d.rectangle([0, H - 8, int(W * fi / N), H], fill=PINK)
        ff.stdin.write(frame.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    if not preview:
        V.thumbnail(v, os.path.join(outdir, f"{slug}-miniatura.jpg"))
        meta = {"titulo": v["title"], "duracion_seg": round(total, 1), "tags": v["tags"],
                "capitulos": [(round(tl["start"]), tl["scene"].get("title") or tl["scene"].get("heading") or tl["scene"].get("highlight") or tl["scene"].get("name") or tl["scene"].get("big") or tl["scene"].get("text") or "Final") for tl in timeline]}
        json.dump(meta, open(os.path.join(outdir, "meta.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{slug}: {total:.1f}s -> {out_mp4}")

if __name__ == "__main__":
    build(sys.argv[1], preview="--preview" in sys.argv)
