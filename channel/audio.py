# -*- coding: utf-8 -*-
"""Voz (Kokoro TTS local), música synthwave original y efectos, todo generado aquí."""
import os, re
import numpy as np
import soundfile as sf

SR = 24000
KOKORO_DIR = os.environ.get("KOKORO_DIR", "/tmp/claude-0/kokoro")
VOICE = os.environ.get("VOICE", "em_alex")
SPEED = float(os.environ.get("VOICE_SPEED", "1.02"))

# Pronunciación: el TTS lee en español, así que adaptamos nombres en inglés.
PRON = [
    (r"\bGTA 6\b", "ge te a seis"), (r"\bGTA\b", "ge te a"),
    (r"\bPS5 Pro\b", "pe ese cinco Pro"), (r"\bPS5\b", "pe ese cinco"), (r"\bPS4\b", "pe ese cuatro"), (r"\bPS3\b", "pe ese tres"),
    (r"\bXbox Live\b", "Équis box Láiv"), (r"\bXbox\b", "Équis box"), (r"\bSeries\b", "Síries"),
    (r"\bPlayStation Network\b", "Pleistéishon Nétwork"), (r"\bPlayStation\b", "Pleistéishon"),
    (r"\bRed Dead Redemption\b", "Red Ded Ridémpshon"), (r"\bRockstar North\b", "Rócstar Norz"), (r"\bRockstar\b", "Rócstar"),
    (r"\bVice City\b", "Váis Síti"), (r"\bLiberty City\b", "Líberti Síti"), (r"\bLeonida Keys\b", "Leonida Kíis"),
    (r"\bGrassrivers\b", "Gras Ríbers"), (r"\bPort Gellhorn\b", "Port Guéljorn"), (r"\bMount Kalaga\b", "Máunt Kalága"),
    (r"\bEverglades\b", "Évergleids"), (r"\bJason\b", "Yéison"), (r"\bDuval\b", "Duvál"),
    (r"\bCal Hampton\b", "Cal Jámpton"), (r"\bBrian Heder\b", "Bráian Jéder"), (r"\bBoobie Ike\b", "Búbi Áik"),
    (r"\bDre Quan Priest\b", "Dre Kuán Prist"), (r"\bReal Dimez\b", "Rial Dáims"), (r"\bTommy Vercetti\b", "Tómi Verchéti"),
    (r"\bC J\b", "Si Yéi"), (r"\bDMA Design\b", "de eme a Disáin"), (r"\bHDR\b", "hache de erre"),
    (r"\bSSD\b", "ese ese de"), (r"\bUSB\b", "u ese be"), (r"\bAPK\b", "a pe ka"), (r"\bGPS\b", "ge pe ese"),
    (r"\bMetacritic\b", "Métacritic"), (r"\bOcarina of Time\b", "Ocarina of Táim"), (r"\bstreamer\b", "estrímer"),
    (r"\bapp\b", "ap"), (r"\bInstagram\b", "Ínstagram"), (r"\bSony\b", "Sóni"),
    (r"\bBigfoot\b", "Bigfut"), (r"\bGullet Marsh\b", "Gálet Marsh"), (r"\bWashington\b", "Uáshington"),
    (r"\bPipework\b", "Páipguork"), (r"\bMandy\b", "Mándi"), (r"\bSensor Tower\b", "Sénsor Táuer"), (r"\bTake-Two\b", "Teik Tu"),
    (r"\bPapa Audacity\b", "Papa Odásiti"),
    (r"\bWAiNK\b", "Uéink"), (r"\bBuck Me\b", "Bak Mi"), (r"\bThree Sheets\b", "Zri Shits"), (r"\bVice-Dale\b", "Váis Deil"),
    (r"\bMoses\b", "Móuses"), (r"\bKick\b", "Kik"), (r"\bTwitch\b", "Tuich"), (r"\bYouTube\b", "Yutub"),
    (r"\bLeague of Legends\b", "Lig of Léyends"), (r"\bFortnite\b", "Fórtnait"), (r"\bFlu\b", "Flu"),
    (r"\bRunning on Empty\b", "Ráning on Émpti"), (r"\bHot Together\b", "Jot Tuguéder"), (r"\bDazed\b", "Déizd"),
    (r"\bEdge\b", "Edch"), (r"\bAaron Garbut\b", "Éron Gárbut"), (r"\bArthur Morgan\b", "Ártur Mórgan"), (r"\bCERO Z\b", "Sero Zeta"),
    (r"\bTrue Fat\b", "Tru Fat"), (r"\bBrian\b", "Bráian"), (r"\bstrip club\b", "estríp club"), (r"\bgym\b", "yim"),
    (r"\bonline\b", "onláin"), (r"\bspoilers?\b", "espóiler"), (r"\bPro\b", "Pro"), (r"\bOceanía\b", "Oceanía"),
]

def pron(text):
    for a, b in PRON:
        text = re.sub(a, b, text)
    return text

_k = None
def _kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(f"{KOKORO_DIR}/kokoro-v1.0.onnx", f"{KOKORO_DIR}/voices-v1.0.bin")
    return _k

def _trim(x, thr=0.008):
    nz = np.where(np.abs(x) > thr)[0]
    if not len(nz): return x
    return x[max(0, nz[0] - 480): nz[-1] + 960]

def _fade(x, ms=12):
    n = min(len(x) // 2, int(SR * ms / 1000))
    if n > 0:
        x = x.copy(); x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    return x

def _sentences(text):
    parts = re.split(r'(?<=[.!?;:])\s+', text.strip())
    out = []
    for p in parts:  # frases muy largas: se parten en comas para que el modelo no las corte por dentro
        if len(p) > 170 and "," in p:
            bits = p.split(","); cur = ""
            for b in bits:
                if len(cur) + len(b) > 120 and cur:
                    out.append(cur.strip() + ","); cur = b
                else:
                    cur = (cur + "," + b) if cur else b
            if cur.strip(): out.append(cur.strip())
        elif p:
            out.append(p)
    return out

def _polish(x):
    """Ecualización suave + compresión ligera para una voz más limpia y estable."""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as d:
        a, b = f"{d}/a.wav", f"{d}/b.wav"
        sf.write(a, x, SR)
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", a, "-af",
                        "highpass=f=75,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=1.5,"
                        "deesser=i=0.35,acompressor=threshold=-20dB:ratio=2.2:attack=10:release=160:makeup=1.5",
                        "-ar", str(SR), b], check=True)
        y, _ = sf.read(b, dtype="float32")
    return y

def tts(text, out_wav, speed=None):
    k = _kokoro()
    spd = speed or SPEED
    pieces, pieces_end = [], [""]
    for i, sent in enumerate(_sentences(text)):
        samples, sr = k.create(pron(sent), voice=VOICE, speed=spd, lang="es")
        seg = _fade(_trim(np.asarray(samples, dtype=np.float32)))
        if pieces:
            gap = 0.16 if pieces_end[-1] == "," else 0.26
            pieces.append(np.zeros(int(SR * gap), np.float32))
        pieces.append(seg); pieces_end = [sent[-1]]
    samples = np.concatenate(pieces) if pieces else np.zeros(1, np.float32)
    samples = _polish(samples)
    samples = samples / (np.abs(samples).max() + 1e-6) * 0.89
    sf.write(out_wav, samples, SR)
    return samples

def master(in_wav, out_wav, target=-14.0, ceiling=0.84):
    """Sonoridad -14 LUFS con ganancia fija (medida con loudnorm) + limitador suave: sin bombeo."""
    import subprocess, json as _j
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", in_wav, "-af", f"loudnorm=I={target}:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300)
    m = _j.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    x, sr = sf.read(in_wav, dtype="float32")
    x = x * (10 ** ((target - float(m["input_i"])) / 20))
    # limitador con anticipación de 5 ms y liberación de 80 ms
    from scipy.ndimage import maximum_filter1d
    from scipy.signal import lfilter
    peak = maximum_filter1d(np.abs(x), size=int(sr * 0.010))
    g = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
    a = np.exp(-1.0 / (sr * 0.08))
    g = np.minimum(g, lfilter([1 - a], [1, -a], g))
    look = int(sr * 0.005)
    y = np.concatenate([x[look:], np.zeros(look, np.float32)]) * g
    y = np.clip(y, -0.98, 0.98).astype(np.float32)
    sf.write(out_wav + ".24k.wav", y, sr)
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", out_wav + ".24k.wav", "-af",
                    "aresample=48000:resampler=soxr,alimiter=limit=0.82:attack=5:release=60:level=false", out_wav], check=True, stdin=subprocess.DEVNULL, timeout=300)
    os.remove(out_wav + ".24k.wav")

# ---------------------------------------------------------------- música
def _note(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def _env(n, a, r):
    e = np.ones(n, np.float32)
    a = min(a, n); r = min(r, n - a)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] = np.linspace(1, 0, r)
    return e

def _lowpass(x, alpha):
    # filtro de un polo (simple y rápido con lfilter si está disponible)
    try:
        from scipy.signal import lfilter
        return lfilter([alpha], [1, alpha - 1], x).astype(np.float32)
    except Exception:
        y = np.empty_like(x); acc = 0.0
        for i, v in enumerate(x):
            acc += alpha * (v - acc); y[i] = acc
        return y

def music(seconds, seed=0, bpm=96):
    """Loop synthwave original: pad + bajo + batería. Progresiones distintas por seed."""
    rng = np.random.default_rng(seed)
    progs = [[57, 53, 48, 55], [52, 48, 55, 50], [50, 46, 53, 48], [55, 51, 46, 53]]
    prog = progs[seed % len(progs)]
    beat = 60.0 / bpm
    bar = beat * 4
    total = int(seconds * SR) + SR
    out = np.zeros(total, np.float32)
    t_bar = int(bar * SR)
    nb = total // t_bar + 1
    tt = np.arange(t_bar) / SR
    kick_n = int(0.25 * SR); tk = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 9)
    sn_n = int(0.2 * SR)
    snare = rng.standard_normal(sn_n).astype(np.float32) * np.exp(-np.arange(sn_n) / SR * 18)
    snare = snare - _lowpass(snare, 0.15)
    hat_n = int(0.05 * SR)
    hat = rng.standard_normal(hat_n).astype(np.float32) * np.exp(-np.arange(hat_n) / SR * 80)
    hat = hat - _lowpass(hat, 0.5)
    for b in range(nb):
        root = prog[b % 4]
        s = b * t_bar
        if s >= total: break
        seg = np.zeros(t_bar, np.float32)
        # pad: acorde menor/mayor con sierras desafinadas
        chord = [root, root + (3 if b % 4 in (0, 3) and seed % 2 == 0 else 4), root + 7, root + 12]
        for n in chord:
            f = _note(n + 12)
            for d in (-0.15, 0.15):
                ph = (f * (1 + d / 100) * tt) % 1.0
                seg += (2 * ph - 1) * 0.035
        seg = _lowpass(seg, 0.06) * _env(t_bar, int(0.3 * SR), int(0.3 * SR))
        # bajo en corcheas
        en = int(beat / 2 * SR)
        for i in range(8):
            f = _note(root - 12 + (12 if i % 2 else 0))
            te = np.arange(en) / SR
            ph = (f * te) % 1.0
            v = (2 * ph - 1) * 0.16 * np.exp(-te * 6)
            seg[i * en:(i + 1) * en] += _lowpass(v.astype(np.float32), 0.12)[: len(seg[i * en:(i + 1) * en])]
        # arpegio suave
        an = int(beat / 4 * SR)
        arp = [chord[0] + 24, chord[1] + 24, chord[2] + 24, chord[1] + 24]
        for i in range(16):
            f = _note(arp[i % 4]); te = np.arange(an) / SR
            v = np.sin(2 * np.pi * f * te) * 0.03 * np.exp(-te * 10)
            seg[i * an:(i + 1) * an] += v[: len(seg[i * an:(i + 1) * an])].astype(np.float32)
        # batería
        bt = int(beat * SR)
        for i in range(4):
            p = i * bt
            seg[p:p + kick_n] += kick[: len(seg[p:p + kick_n])].astype(np.float32) * 0.5
            if i in (1, 3):
                seg[p:p + sn_n] += snare[: len(seg[p:p + sn_n])] * 0.18
            for h in (0, bt // 2):
                q = p + h
                seg[q:q + hat_n] += hat[: len(seg[q:q + hat_n])] * 0.06
        e = min(t_bar, total - s)
        out[s:s + e] += seg[:e]
    out = out[: int(seconds * SR)]
    fade = int(2.5 * SR)
    out[:int(0.5 * SR)] *= np.linspace(0, 1, int(0.5 * SR))
    out[-fade:] *= np.linspace(1, 0, fade)
    return out / (np.abs(out).max() + 1e-6) * 0.8

def whoosh(seed=1):
    rng = np.random.default_rng(seed)
    n = int(0.45 * SR)
    x = rng.standard_normal(n).astype(np.float32)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    y = _lowpass(x, 0.08) * 0.6 + (x - _lowpass(x, 0.3)) * 0.15
    return (y * env * 0.35).astype(np.float32)

def pop():
    n = int(0.08 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (900 - 4000 * t) * t) * np.exp(-t * 45) * 0.15).astype(np.float32)
