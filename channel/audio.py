# -*- coding: utf-8 -*-
"""Voz (Kokoro TTS local), música synthwave original y efectos, todo generado aquí."""
import os, re
import numpy as np
import soundfile as sf

SR = 24000
KOKORO_DIR = os.environ.get("KOKORO_DIR", "/tmp/claude-0/kokoro")
VOICE = os.environ.get("VOICE", "em_alex")
SPEED = float(os.environ.get("VOICE_SPEED", "1.08"))

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
    (r"\bonline\b", "onláin"), (r"\bspoilers?\b", "espóiler"), (r"\bPro\b", "Pro"), (r"\bOceanía\b", "Oceanía"),
]

def pron(text):
    for a, b in PRON:
        text = re.sub(a, b, text)
    return text

_k = None
def tts(text, out_wav):
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(f"{KOKORO_DIR}/kokoro-v1.0.onnx", f"{KOKORO_DIR}/voices-v1.0.bin")
    samples, sr = _k.create(pron(text), voice=VOICE, speed=SPEED, lang="es")
    assert sr == SR
    samples = np.asarray(samples, dtype=np.float32)
    # recorta silencios de los extremos
    nz = np.where(np.abs(samples) > 0.01)[0]
    if len(nz):
        samples = samples[max(0, nz[0] - 600): nz[-1] + 1200]
    sf.write(out_wav, samples, SR)
    return samples

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
