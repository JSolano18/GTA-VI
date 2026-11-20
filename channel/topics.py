# -*- coding: utf-8 -*-
"""Topic discovery scoring. Scores are judgements (1-5) backed by the evidence notes and source
URLs below; no search volumes are invented. Similarity to already-published shorts is computed.

Run: python3 channel/topics.py  -> writes LeonidaDiario/sources/topic_scores.md
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "channel"))

WEIGHTS = {"search": 0.18, "discussion": 0.16, "visual": 0.14, "hook": 0.16, "fresh": 0.10,
           "footage": 0.10, "credibility": 0.16}   # minus similarity penalty

CANDIDATES = [
 {"id": "mandy_choice", "title": "The Mandy choice: provoke or defuse?",
  "s": {"search": 4, "discussion": 5, "visual": 5, "hook": 5, "fresh": 4, "footage": 4, "credibility": 4},
  "evidence": "Pipework/Mandy went viral on launch day (KeenGamer, Game Rant, Insider Gaming); our own Mandy short did ~4.5k views vs ~20 normal, 56% stayed. Choice mechanic documented in guides. Only real gameplay we hold is the owner-supplied Mandy clip.",
  "sources": ["https://www.keengamer.com/articles/news/gta-6s-mandy-goes-viral-on-launch-day-after-pipework-scene/",
              "https://beebom.com/gta-6-pipework-mandy-rent-mission/amp/", "https://xboxplay.games/gta-6/gta-6-mandy-scene-should-you-provoke-or-defuse-choice-77396",
              "https://gamerant.com/gta-6-mandy-sink-pipework-serial-killer/", "https://insider-gaming.com/who-is-mandy-gta-6-when-do-you-meet-serial-killer/"]},
 {"id": "relationship_meter", "title": "Ignore Lucia and you lose more than a conversation",
  "s": {"search": 4, "discussion": 5, "visual": 4, "hook": 5, "fresh": 5, "footage": 4, "credibility": 4},
  "evidence": "Fresh relationship guides from PC Gamer, GameSpot, GTABase, KeenGamer (Nov 19-20); Vice/Bloomberg interview on hand-holding; TikTok 'microcheating' debate (Yahoo). Character interaction = closest to the benchmark short.",
  "sources": ["https://www.pcgamer.com/games/grand-theft-auto/gta-6-romance-jason-lucia/", "https://www.gamespot.com/articles/gta-6-romance-relationships/",
              "https://www.gtabase.com/articles/gta-6/gta-6-jason-and-lucia-s-relationship-system-explained",
              "https://www.keengamer.com/articles/guides/gta-6-relationship-guide-how-to-raise-jason-and-lucias-bond/",
              "https://www.vice.com/en/article/gta-6-jason-lucia-relationship-features/", "https://gamerant.com/gta-6-characters-jason-lucia-relationship-romance/",
              "https://www.yahoo.com/entertainment/articles/gta-6s-lucia-jason-already-195950601.html"]},
 {"id": "body_system", "title": "You can make Jason fat (but not that fat)",
  "s": {"search": 4, "discussion": 4, "visual": 4, "hook": 5, "fresh": 5, "footage": 3, "credibility": 4},
  "evidence": "Rockstar confirmed weight/muscle system to Dazed; 'True Fat Jason' player test covered by GamesRadar/Yahoo/Notebookcheck post-launch; smell system confirmed by Aaron Garbut (Edge) via Beebom.",
  "sources": ["https://www.gamesradar.com/games/grand-theft-auto/gta-6-players-confirm-true-fat-jason-and-max-weight-lucia-arent-very-fat-at-all-setting-the-stage-for-the-first-pc-mod-to-super-size-them/",
              "https://www.notebookcheck.net/GTA-6-gym-diaries-This-is-what-Jason-looks-like-at-max-weight.1454757.0.html",
              "https://beebom.com/gta-6-weight-system-gym-body-fitness-explained/", "https://beebom.com/gta-6-realistic-smell-system/"]},
 {"id": "japan_censorship", "title": "In Japan, Jason showers in his underwear",
  "s": {"search": 4, "discussion": 4, "visual": 3, "hook": 5, "fresh": 5, "footage": 3, "credibility": 4},
  "evidence": "VGC, Game Rant, Game*Spark, Cybernews report the Japanese version's changes (Nov 19). Suggestive-but-safe curiosity angle; partly conflicting on decapitations (we say so).",
  "sources": ["https://www.videogameschronicle.com/news/japan-censors-gta-6s-violence-and-nudity-including-jason-in-the-shower/",
              "https://en.gamespark.jp/article/2026/11/19/2475.html", "https://gamerant.com/gta-6-censored-japan/",
              "https://www.gtaboom.com/gta-6-is-censored-in-japan-exactly-like-we-predicted-f912", "https://cybernews.com/news/gta6-japan-censorship/"]},
 {"id": "lucia_prison", "title": "Why was Lucia in prison?",
  "s": {"search": 4, "discussion": 3, "visual": 5, "hook": 4, "fresh": 3, "footage": 5, "credibility": 4},
  "evidence": "Evergreen character question; answer comes from Rockstar's official bio (quoted by wikis). Many unused official Lucia screenshots (prison, boxing, bar, police).",
  "sources": ["https://gta.wiki/w/Lucia_Caminos", "https://www.gtabase.com/de/gta-6/charaktere/lucia", "https://meowdb.com/gta6/characters/lucia-caminos"]},
 {"id": "miami_clip", "title": "GTA 6 or real life? Rockstar's Miami clip",
  "s": {"search": 3, "discussion": 4, "visual": 3, "hook": 4, "fresh": 2, "footage": 1, "credibility": 3},
  "evidence": "Viral Nov 11 (NBC Miami, Push Square, Kotaku) but pre-launch and the clip itself isn't ours to use; origin unconfirmed.",
  "sources": ["https://www.nbcmiami.com/news/local/this-viral-miami-beach-video-looks-straight-out-of-gta-6-and-it-might-be/3887284/"]},
 {"id": "adult_searches", "title": "Adult GTA 6 searches up 5,000%",
  "s": {"search": 5, "discussion": 3, "visual": 1, "hook": 4, "fresh": 5, "footage": 1, "credibility": 3},
  "evidence": "OpenCritic/TheGamer citing Google Trends; risky for platform suitability and hard to illustrate appropriately.",
  "sources": ["https://opencritic.com/news/39998/searches-for-gta-6-adult-terms-have-skyrocketed-by-5-000-since-the-game-launched"]},
 {"id": "mount_kalaga", "title": "The side of Leonida nobody talks about",
  "s": {"search": 2, "discussion": 2, "visual": 5, "hook": 3, "fresh": 3, "footage": 5, "credibility": 4},
  "evidence": "Six never-used official Mount Kalaga screenshots, but little new verifiable information.",
  "sources": ["https://www.rockstargames.com/VI"]},
]

PUBLISHED = ["mandy asesina mision viral pipework", "record ventas doble gta 5", "secretos easter eggs bigfoot dexter",
             "cosas raras trucos calcetines movil", "consejos primer dia", "misiones secundarias strangers freaks clima",
             "dinero perder banco", "robar coches lujo wainK", "twitch horas gta flu", "policia estrellas testigos",
             "novedades pareja perfil criminal", "lo malo 30 fps", "como se juega conduccion disparos", "ya salio nueva zelanda",
             "personajes jason lucia quien es quien", "mapa leonida regiones", "historia gta"]
KEYWORDS = {"mandy_choice": "mandy pipework", "relationship_meter": "pareja relationship lucia", "body_system": "weight gym fat",
            "japan_censorship": "japan censored", "lucia_prison": "lucia prison bio personajes", "miami_clip": "miami real life",
            "adult_searches": "searches adult", "mount_kalaga": "mapa leonida regiones kalaga"}


def similarity(cid):
    kw = set(KEYWORDS[cid].split())
    best = 0.0
    for p in PUBLISHED:
        pw = set(p.split())
        best = max(best, len(kw & pw) / max(1, len(kw)))
    return round(best, 2)


def rank():
    rows = []
    for c in CANDIDATES:
        base = sum(WEIGHTS[k] * v for k, v in c["s"].items())
        sim = similarity(c["id"])
        rows.append((round(base - 0.8 * sim, 2), base, sim, c))
    return sorted(rows, key=lambda r: -r[0])


if __name__ == "__main__":
    out = os.path.join(ROOT, "LeonidaDiario", "sources"); os.makedirs(out, exist_ok=True)
    L = ["# Topic scoring (2026-11-20)", "",
         "Scores 1-5 are editorial judgements backed by the evidence column. No search volumes are invented: YouTube, TikTok, Reddit and Google Trends are not reachable from the production server, so 'search' and 'discussion' are inferred from how widely credible outlets covered each topic in the last 48 h. Similarity = overlap with topics already published by the channel (penalised).", "",
         "| Rank | Topic | Score | Base | Similarity | Evidence |", "|---|---|---|---|---|---|"]
    for i, (score, base, sim, c) in enumerate(rank(), 1):
        L.append(f"| {i} | {c['title']} | {score} | {base:.2f} | {sim} | {c['evidence']} |")
    L += ["", "## Sources per topic", ""]
    for _, _, _, c in rank():
        L.append(f"**{c['title']}**"); L += [f"- {u}" for u in c["sources"]]; L.append("")
    open(os.path.join(out, "topic_scores.md"), "w").write("\n".join(L))
    for i, (score, base, sim, c) in enumerate(rank(), 1):
        print(f"{i}. {score:5}  (base {base:.2f}, sim {sim})  {c['title']}")
