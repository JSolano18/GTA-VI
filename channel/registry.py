# -*- coding: utf-8 -*-
"""Asset registry: tracks every image/clip, its source, rights and where it has been used.

The registry lives in assets/registry.json. `python3 channel/registry.py` rebuilds it from the
assets on disk plus the usage recorded in channel/shorts.py (Spanish shorts) and in
LeonidaDiario/metadata/*.json (English shorts).
"""
import glob, json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "assets", "registry.json")
IMG_DIR = os.path.join(ROOT, "assets", "oficial", "shorts")

CHARS = {"Jason": "jason", "Lucia": "lucia", "Brian": "brian", "Boobie": "boobie", "Cal": "cal", "DreQuan": "drequan",
         "Raul": "raul", "Real_Dimez": "real_dimez", "Mandy": "mandy"}
PLACES = {"Vice_City": "vice_city", "Leonida_Keys": "leonida_keys", "Grassrivers": "grassrivers", "Port_Gellhorn": "port_gellhorn",
          "Ambrosia": "ambrosia", "Mount_Kalaga": "mount_kalaga"}

# Hand-written descriptions for assets whose official alt text we don't have (from visual review).
DESC = {
    "Jason_Duval_01": "Jason in a tank top next to a green sport bike, palm trees", "Jason_Duval_03": "Jason fishing from a boat in the Keys",
    "Jason_Duval_04": "Jason checking his phone under a palm tree at night, neon street",
    "Jason_Duval_05": "Jason aiming a rifle at night, city lights", "Jason_Duval_06": "Jason at a Keys bar with a beer, friends around",
    "Jason_Duval_07": "Jason behind a chain fence, police lights", "Jason_Duval_08": "Jason with a pistol by a seaplane",
    "Jason_Duval_09": "Jason loading a pistol, bullets on table", "Jason_Duval_10": "Jason in a hoodie with a pistol, dark",
    "Jason_and_Lucia_01": "Jason and Lucia close together, skyline behind", "Jason_and_Lucia_02": "Jason and Lucia geared up in a vault",
    "Jason_and_Lucia_03": "Lucia smiling in a car, Jason driving", "Jason_and_Lucia_04": "Jason and Lucia in a shootout, glass breaking",
    "Jason_and_Lucia_05": "Jason and Lucia facing a group in a doorway", "Jason_and_Lucia_06": "Jason and Lucia in a car at night with guns",
    "Jason_and_Lucia_07": "Jason and Lucia low-angle, teal light", "Jason_and_Lucia_08": "Jason and Lucia walking toward a fire",
    "Jason_and_Lucia_09": "Jason and Lucia on a motorbike chased by police", "Jason_and_Lucia_10": "Lucia sitting on a rooftop party, city night",
    "Jason_and_Lucia_11": "Jason and Lucia in a convertible, daylight", "Jason_and_Lucia_12": "Jason and Lucia armed in a dark corridor",
    "Jason_and_Lucia_13": "Jason and Lucia embracing at sunset, helicopter", "Lucia_Caminos_01": "Lucia boxing in a prison gym",
    "Lucia_Caminos_03": "Lucia on a motorbike outside a liquor bar", "Lucia_Caminos_04": "Lucia with a pistol, man in the dark",
    "Lucia_Caminos_05": "Lucia in an orange prison uniform, handcuffed", "Lucia_Caminos_06": "Lucia dancing in a nightclub",
    "Lucia_Caminos_07": "Lucia in a car, police lights", "Lucia_Caminos_08": "Lucia walking to a check-cashing store",
    "Lucia_Caminos_09": "Lucia working out at an outdoor gym", "Lucia_Caminos_10": "Lucia in a car, neon light on her face",
    "Leonida_Keys_06": "Iguana on a rock, Keys beach", "Vice_City_10": "Vice City twin towers and bay, daytime",
    "Vice_City_11": "Vice City tower at sunset", "Vice_City_12": "Man with gold rifle, close-up",
    "Mandy_frame": "Mandy in her kitchen (frame from third-party clip)",
}


def _tags(name):
    t = set()
    for k, v in CHARS.items():
        if k in name: t.add(v)
    for k, v in PLACES.items():
        if name.startswith(k): t.add(v)
    return sorted(t)


def _usage_spanish():
    """Usage from the Spanish shorts in channel/shorts.py (images per scene + Extended Look segments)."""
    sys.path.insert(0, os.path.join(ROOT, "channel"))
    import shorts as S
    out = []
    for i, sh in enumerate(S.SHORTS):
        clips = S.GAMEPLAY.get(sh["slug"]) or []
        for j, sc in enumerate(sh["scenes"]):
            c = clips[j] if j < len(clips) else None
            if c and isinstance(c[0], str):
                out.append((sh["slug"], i, "clip:" + os.path.basename(c[0]) + f"@{c[1]}"))
            elif c:
                out.append((sh["slug"], i, f"extended_look@{c[0]}"))
            else:
                out.append((sh["slug"], i, sc["img"]))
    return out


def _usage_english():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "LeonidaDiario", "metadata", "*.json"))):
        m = json.load(open(p))
        for a in m.get("assets_used", []):
            out.append((m["slug"], 1000 + m.get("order", 0), a))
    return out


def build():
    reg = {}
    for f in sorted(glob.glob(os.path.join(IMG_DIR, "*.jpg")) + glob.glob(os.path.join(IMG_DIR, "*.png"))):
        n = os.path.splitext(os.path.basename(f))[0]
        third = n.startswith("Mandy_frame")
        reg[n] = {"id": n, "file": os.path.relpath(f, ROOT), "kind": "image",
                  "origin": "third-party" if third else "official",
                  "source": "X post by @GTAmemesSOL, supplied by channel owner" if third else
                            "Rockstar Games official site / press screenshot pack (rockstargames.com/VI)",
                  "license": "unclear - not licensed; use with credit at owner's risk" if third else
                             "Official promotional material offered for download and sharing; not a formal license. Credit 'Rockstar Games'.",
                  "description": DESC.get(n, n.replace("_", " ")), "tags": _tags(n),
                  "used_in": [], "times_used": 0, "last_used": None}
    reg["clip:mandy_pipework.mp4"] = {"id": "clip:mandy_pipework.mp4", "file": "assets/clips/mandy_pipework.mp4", "kind": "video",
        "origin": "third-party", "source": "X post by @GTAmemesSOL (gameplay capture), supplied by channel owner",
        "license": "unclear - not licensed; credit @GTAmemesSOL", "description": "GTA VI Pipework mission: Jason under Mandy's sink, then their conversation",
        "tags": ["jason", "mandy", "leonida_keys", "pipework"], "used_in": [], "times_used": 0, "last_used": None}
    reg["extended_look"] = {"id": "extended_look", "file": "remote", "kind": "video", "origin": "official",
        "source": "Rockstar 'Grand Theft Auto VI: An Extended Look' (official download)", "license": "official promo; BANNED by channel owner from 2026-11-19",
        "description": "Official 27-min gameplay reveal", "tags": ["banned"], "used_in": [], "times_used": 0, "last_used": None}
    for n in ["sticker_lowrider", "sticker_sun", "sticker_flamingo", "sticker_gator", "sticker_palm", "sticker_manatee", "sticker_crab"]:
        reg[n] = {"id": n, "file": f"assets/stickers/{n}.mp4", "kind": "animated-sticker", "origin": "official",
                  "source": "Rockstar Games official GTA VI website animation (alpha-matted)", "license": "official promo graphic",
                  "description": n.replace("sticker_", "animated ") + " sticker", "tags": ["sticker"], "used_in": [], "times_used": 0, "last_used": None}
    for slug, order, a in _usage_spanish() + _usage_english():
        key = a.split("@")[0] if a.startswith(("clip:", "extended_look")) else a
        if key not in reg: continue
        r = reg[key]
        if slug not in r["used_in"]: r["used_in"].append(slug)
        r["times_used"] += 1
        r["last_order"] = max(r.get("last_order", -1), order)
        r["last_used"] = slug
    json.dump(reg, open(REG, "w"), indent=1, ensure_ascii=False)
    return reg


def load():
    return json.load(open(REG)) if os.path.exists(REG) else build()


def pick(reg, want_tags=(), avoid=(), recent_slugs=(), k=1, kind="image", allow_third_party=False):
    """Least-used assets matching ALL want_tags, never one used in `recent_slugs`, never in `avoid`."""
    c = [r for r in reg.values() if r["kind"] == kind and r["id"] not in avoid
         and set(want_tags) <= set(r["tags"]) and (allow_third_party or r["origin"] == "official")
         and not (set(r["used_in"]) & set(recent_slugs))]
    c.sort(key=lambda r: (r["times_used"], r.get("last_order", -1), r["id"]))
    return [r["id"] for r in c[:k]]


if __name__ == "__main__":
    reg = build()
    fresh = sum(1 for r in reg.values() if r["times_used"] == 0 and r["kind"] == "image")
    print(f"{len(reg)} assets, {fresh} never-used images -> {REG}")
    for r in sorted(reg.values(), key=lambda r: -r["times_used"])[:8]:
        print(f"  {r['times_used']:2}x {r['id']}")
