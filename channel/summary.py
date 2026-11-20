# -*- coding: utf-8 -*-
"""Builds LeonidaDiario/README.md (production summary) from metadata + production reports."""
import json, os, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "channel"))
import leonida as LD, topics as T

OUT = os.path.join(ROOT, "LeonidaDiario")
why = {c["id"]: c["evidence"] for c in T.CANDIDATES}
L = ["# LeonidaDiario — 5 Shorts en español (2026-11-20)", "",
     "No se ha subido nada. Todo está listo para YouTube Shorts, TikTok e Instagram Reels (1080×1920, H.264/AAC, −15 LUFS aprox.). Narración en español (em_alex), validada escena por escena con reconocimiento de voz (Vosk es).", "",
     "| # | Title | Duration | QC | Voice check (ASR match) | Visuals | Video |", "|---|---|---|---|---|---|---|"]
details = []
for spec in LD.SHORTS:
    sid = spec["id"]
    rp = os.path.join(OUT, "production_reports", f"{sid}.json")
    if not os.path.exists(rp):
        L.append(f"| {sid} | {spec['title']} | – | NOT RENDERED | – | – | – |"); continue
    r = json.load(open(rp)); m = json.load(open(os.path.join(OUT, "metadata", f"{sid}.json")))
    vis = sorted(set(a.split("@")[0] for a in m["assets_used"]))
    third = any(a.startswith("clip:") or a.startswith("Mandy") for a in vis)
    vdesc = f"{sum(1 for a in vis if not a.startswith(('clip:','sticker')))} official stills" + (", third-party gameplay clip" if third else "") + \
            (", official animated sticker" if any(a.startswith("sticker") for a in vis) else "")
    L.append(f"| {sid[-1]} | {spec['title']} | {r['duration']} s | {r['qc']['verdict']} | {r['qc']['asr_match_full_voice']} | {vdesc} | `shorts/{sid}/{sid}.mp4` |")
    details += [f"## {sid}: {spec['title']}", "",
                f"**Why this topic:** {why[spec['topic']]}", "",
                f"**Description:**\n```\n{m['description']}\n```", f"**Pinned comment:** {spec['pinned']}", "",
                f"**Files:** `shorts/{sid}/` (mp4, cover jpg, srt, title/description/tags), script `scripts/{sid}.txt`, voice `voiceovers/{sid}_voice.wav`, sources `sources/{sid}.md`, report `production_reports/{sid}.json`.", "",
                f"**Visual assets:** {', '.join(vis)}", "",
                "**Narration per scene:** " + "; ".join(f"{i+1}: {s['voice']} ×{s['speed']} match {s['asr_match']}" + (f" gaps {s['long_gaps']}" if s['long_gaps'] else "") for i, s in enumerate(r["scenes"])), "",
                f"**QC:** {json.dumps(r['qc'])}", ""]
L += ["", "Folders: `shorts/` finished videos · `scripts/` narration · `voiceovers/` clean voice stems · `sources/` claim-by-claim sources and topic scoring · `metadata/` titles, descriptions, hashtags, pinned comments, assets used · `production_reports/` QC + benchmark analysis.", ""]
L += details
open(os.path.join(OUT, "README.md"), "w").write("\n".join(L))
print("\n".join(L[:12]))
