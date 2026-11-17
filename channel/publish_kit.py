# -*- coding: utf-8 -*-
"""Genera descripciones, plan de subida y arte del canal a partir de los renders."""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import visuals as V
from visuals import font, fit, text_img, badge, PINK, CYAN, YEL, WHITE
from videos import VIDEOS, CHANNEL

OUT = os.path.join(V.ROOT, "output")

DESC = {
 "01-hora-lanzamiento": "¿A qué hora sale GTA 6? Te explico cuándo se desbloquea en tu país, cómo comprobar la precarga y qué hacer si el juego no te deja jugar el día de lanzamiento.",
 "02-plataformas": "¿GTA 6 funciona en PS4, Xbox One o PC? Aquí tienes, en menos de 3 minutos, en qué consolas puedes jugar GTA 6 y qué esperar de Xbox Series S y PS5 Pro.",
 "03-gta6-pc": "¿Cuándo sale GTA 6 en PC? No hay fecha oficial, pero la historia de Rockstar con GTA 5 y Red Dead Redemption 2 nos da pistas. Y cuidado con las 'descargas gratis'.",
 "04-cuanto-pesa": "¿Cuánto pesa GTA 6 y cabe en tu consola? Cómo liberar espacio en PS5 y Xbox Series en 5 minutos, y qué saber antes de usar un disco externo.",
 "05-fisico-o-digital": "¿Comprar GTA 6 en físico o en digital? Ventajas, errores comunes (PS5 Digital y Series S no tienen lector) y qué revisar antes de pagar.",
 "06-mapa-leonida": "El mapa de GTA 6 explicado: las 6 regiones de Leonida — Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia y Mount Kalaga.",
 "07-personajes": "¿Quién es quién en GTA 6? Jason Duval, Lucia Caminos y los personajes presentados por Rockstar, sin spoilers de la historia.",
 "08-primeras-horas": "10 cosas que debes hacer en tus primeras horas de GTA 6: ajustes, consejos para no perder progreso y cómo disfrutar Leonida desde el minuto uno.",
 "09-estafas": "Cuidado con las estafas de GTA 6: 'GTA 6 PC gratis', APK para móvil, claves baratísimas y generadores de dinero. Cómo proteger tu cuenta en 3 pasos.",
 "10-historia-gta": "La historia de GTA en 2 minutos: de Grand Theft Auto (1997) a Vice City, San Andreas, GTA V y el lanzamiento de GTA 6 en Leonida.",
}

DISCLAIMER = ("Canal de fans no oficial. No estamos afiliados a Rockstar Games ni a Take-Two Interactive. "
              "Grand Theft Auto y GTA son marcas de sus respectivos dueños. Todas las imágenes, animaciones y música "
              "de este video son originales.")

KEEP = {"gta": "GTA", "ps5": "PS5", "ps4": "PS4", "pc": "PC", "xbox": "Xbox", "usb": "USB", "ssd": "SSD", "gps": "GPS",
        "apk": "APK", "ee.uu.": "EE.UU.", "vice": "Vice", "city": "City", "leonida": "Leonida", "keys": "Keys", "mount": "Mount",
        "kalaga": "Kalaga", "port": "Port", "gellhorn": "Gellhorn", "grassrivers": "Grassrivers", "ambrosia": "Ambrosia",
        "jason": "Jason", "lucia": "Lucia", "duval": "Duval", "caminos": "Caminos", "series": "Series", "rockstar": "Rockstar",
        "pro": "Pro", "s": "S", "x": "X", "digital": "Digital", "vs": "vs"}
def sentence(t):
    out = []
    for i, w in enumerate(t.lower().split()):
        core = w.strip("¿?¡!:,()\"'")
        if core in KEEP: w = w.replace(core, KEEP[core])
        elif i == 0 or (out and out[-1].endswith(":")): w = w[:1].upper() + w[1:] if w[:1].isalpha() else w[:1] + w[1:2].upper() + w[2:]
        out.append(w)
    return " ".join(out)

def mmss(s): return f"{int(s)//60}:{int(s)%60:02}"

def descriptions():
    rows = []
    for i, v in enumerate(VIDEOS):
        d = os.path.join(OUT, v["slug"])
        mp = os.path.join(d, "meta.json")
        if not os.path.exists(mp):
            print("falta render:", v["slug"]); continue
        m = json.load(open(mp))
        caps = []
        for (t, _), sc in zip(m["capitulos"], v["scenes"]):
            lay = sc["layout"]
            if lay == "compare": name = f"{sentence(sc['left']['title'])} vs {sentence(sc['right']['title'])}"
            elif lay == "cta": name = "Final"
            elif lay == "quote": name = "Conclusión"
            elif lay == "big": name = f"{sc['big']} – {sc['label']}"
            else: name = sc.get("title") or sc.get("heading") or sc.get("highlight") or sc.get("name") or "..."
            name = name.replace('"', "")
            name = sentence(name) if name.isupper() else name
            if caps and t - caps[-1][0] < 10:   # YouTube exige capítulos de 10 s o más
                continue
            caps.append((t, name[:60]))
        caps[0] = (0, caps[0][1])
        caps = [f"{mmss(t)} {n}" for t, n in caps]
        txt = (f"{DESC[v['slug']]}\n\n"
               f"🔔 Suscríbete a {CHANNEL['name']} para guías diarias de GTA 6 en español.\n\n"
               f"CAPÍTULOS\n" + "\n".join(caps) + "\n\n"
               "Los datos de este video se basan en la información pública disponible antes del lanzamiento. "
               "Si algo cambió, te lo cuento en los comentarios fijados.\n\n"
               f"{DISCLAIMER}\n\n#GTA6 #GTAVI #Leonida")
        open(os.path.join(d, "descripcion.txt"), "w").write(txt)
        open(os.path.join(d, "titulo.txt"), "w").write(v["title"])
        open(os.path.join(d, "tags.txt"), "w").write(", ".join(v["tags"]))
        rows.append((i, v, m))
    return rows

SCHEDULE = ["00:05", "00:10", "07:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
ORDER = ["01-hora-lanzamiento", "09-estafas", "02-plataformas", "04-cuanto-pesa", "05-fisico-o-digital",
         "08-primeras-horas", "06-mapa-leonida", "07-personajes", "03-gta6-pc", "10-historia-gta"]

def plan(rows):
    by = {v["slug"]: (v, m) for _, v, m in rows}
    L = ["# Plan de subida — jueves 19 de noviembre de 2026", "",
         "Programa los videos en YouTube Studio como **Programado** (no Público) el miércoles por la noche. "
         "Horas en tu hora local. El orden sigue la intención de búsqueda del día: primero lo urgente (hora, estafas, "
         "plataformas, espacio), después lo que se busca jugando (consejos, mapa, personajes) y al final lo evergreen.", "",
         "| # | Hora | Video | Duración |", "|---|---|---|---|"]
    for k, slug in enumerate(ORDER):
        if slug in by:
            v, m = by[slug]
            L.append(f"| {k+1} | {SCHEDULE[k]} | {v['title']} | {mmss(m['duracion_seg'])} |")
    L += ["", "## Por cada video", "",
          "1. Sube `output/<video>/<video>.mp4`.",
          "2. Título: `titulo.txt`. Descripción: `descripcion.txt` (ya trae capítulos). Etiquetas: `tags.txt`.",
          "3. Miniatura: `<video>-miniatura.jpg` (1280×720).",
          "4. Subtítulos: sube `<video>.srt` en *Subtítulos → Subir archivo → Con sincronización*. Idioma: español.",
          "5. Pantalla final: los últimos ~15 s tienen dos huecos a la derecha (\"SIGUIENTE VIDEO\" y \"LISTA GTA 6\"). "
          "Pon ahí *Video → Mejor para el espectador* y *Lista de reproducción → GTA 6*. El botón de suscribirse va sobre el botón rojo.",
          "6. Lista de reproducción: añade los 10 a una lista llamada **GTA 6 — Todo lo que necesitas saber**.",
          "7. Divulgación: en *Contenido alterado o sintético* marca **Sí**, porque la voz es sintética (generada por IA).",
          "8. Categoría: Videojuegos. Audiencia: no es contenido para niños.", "",
          "## Antes de programar (miércoles por la noche)", "",
          "Revisa `FACT_CHECK.md`. Si Rockstar cambió algo (hora, precio, tamaño), dime qué y regenero el video afectado "
          "en unos minutos (`python3 channel/render.py <video>`).", "",
          "## Arte del canal", "",
          "- Foto de perfil: `output/canal/avatar.png` (800×800)",
          "- Banner: `output/canal/banner.png` (2560×1440, zona segura centrada 1546×423)",
          f"- Nombre sugerido: **{CHANNEL['name']}** ({CHANNEL['handle']}) — comprueba que el identificador esté libre.",
          f"- Descripción del canal: \"{CHANNEL['tagline']}. Lo que tienes que saber de GTA 6 cada día, sin relleno y sin spoilers. {DISCLAIMER}\""]
    open(os.path.join(V.ROOT, "PLAN_DE_SUBIDA.md"), "w").write("\n".join(L) + "\n")

def channel_art():
    d = os.path.join(OUT, "canal"); os.makedirs(d, exist_ok=True)
    bg = V.background("sunset", seed=42).resize((2560, 1440)).convert("RGBA")
    shade = Image.new("RGBA", bg.size, (10, 0, 25, 110)); bg.alpha_composite(shade)
    t = text_img(CHANNEL["name"].upper(), font("head", 230), fill=YEL, stroke=10, stroke_fill=(0, 0, 0), glow=PINK)
    bg.alpha_composite(t, ((2560 - t.size[0]) // 2, 520))
    s = text_img("GUÍAS Y NOTICIAS DE GTA 6 EN ESPAÑOL", font("black", 60), stroke=5)
    bg.alpha_composite(s, ((2560 - s.size[0]) // 2, 520 + t.size[1] - 70))
    bg.convert("RGB").save(os.path.join(d, "banner.png"))
    av = V.background("night", seed=7).crop((600, 100, 1700, 1200)).resize((800, 800)).convert("RGBA")
    ImageDraw.Draw(av).rectangle([0, 0, 800, 800], fill=(10, 0, 25, 120))
    six = text_img("6", font("head", 560), fill=YEL, stroke=12, stroke_fill=(0, 0, 0), glow=PINK)
    av.alpha_composite(six, ((800 - six.size[0]) // 2, (800 - six.size[1]) // 2 + 10))
    av.convert("RGB").save(os.path.join(d, "avatar.png"))

if __name__ == "__main__":
    rows = descriptions(); plan(rows); channel_art(); print("ok", len(rows))
