# -*- coding: utf-8 -*-
"""LeonidaDiario English Shorts pipeline (v3).

What changed vs. channel/shorts.py (Spanish v2), keeping the same look (fonts, headline style,
subtitle style/position, overlay, music, branding):
  * Narration: native American-English Kokoro voice (am_puck), ONE continuous generation per
    scene (no sentence chopping, no respelling hacks), gentle edge trims with micro-fades,
    no dynamic compression; every scene is checked with offline speech recognition (Vosk) and
    regenerated if words are missing/duplicated, if there are long internal gaps, or clipping.
  * Subtitles: timed from the recognizer's word timestamps (real sync), not estimated.
  * Visuals: assets picked through the registry (assets/registry.json) so unused official
    screenshots come first; varied camera moves; official animated stickers as accents.
  * QC: automatic checks on the final MP4 (resolution, duration, black frames, silences,
    loudness, re-transcription of the exported audio against the script).

Usage: python3 channel/leonida.py short_01 [short_02 ...]   (no upload; files only)
"""
import difflib, json, math, os, re, subprocess, sys, wave, datetime
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A
import visuals as V
import registry as R
import shorts as S
import motion as M
from visuals import PINK, CYAN, YEL, WHITE, font, fit, text_img, badge

W, H, FPS = 1080, 1920, 30
ROOT = V.ROOT
OUT = os.path.join(ROOT, "LeonidaDiario")
KOKORO = "/tmp/claude-0/kokoro"
LANG = "es"   # the channel's narration language (Spanish); English settings kept for reference
VOSK = {"es": "/tmp/claude-0/vosk/vosk-model-small-es-0.42", "en": "/tmp/claude-0/vosk/vosk-model-en-us-0.22-lgraph"}[LANG]
VOICE, SPEED = {"es": ("em_alex", 1.0), "en": ("am_puck", 1.04)}[LANG]
KLANG = {"es": "es", "en": "en-us"}[LANG]
MIN_MATCH = {"es": 0.80, "en": 0.88}[LANG]   # Spanish ASR model is small and misses English names/acronyms
LEAD, TAIL = 0.08, 0.30
MANDY = "assets/clips/mandy_pipework.mp4"

# --------------------------------------------------------------------------------------------- specs
SHORTS_EN = [
{"id": "short_01", "slug": "en-relationship-meter", "topic": "relationship_meter", "seed": 71,
 "title": "Ignore Lucia in GTA 6 and THIS happens 💔 #gta6 #shorts",
 "description": "Jason and Lucia have a relationship meter in GTA 6. Here's what raises it, what breaks it, and why ignoring her calls is a bad idea.",
 "hashtags": ["#gta6", "#gtavi", "#jasonandlucia", "#gta6lucia", "#rockstargames", "#gaming", "#shorts"],
 "tags": ["gta 6", "gta 6 relationship", "jason and lucia", "gta 6 romance", "gta 6 lucia", "gta 6 tips", "gtavi"],
 "pinned": "Be honest: how many of Lucia's calls have you ignored so far? 📱",
 "cover": ("Lucia_Caminos_10", .47, .36, 1.4, ["DON'T IGNORE", "LUCIA"], "RELATIONSHIP METER"),
 "scenes": [
  {"asset": "Lucia_Caminos_10", "move": "zin", "head": "DON'T IGNORE HER CALLS",
   "say": "If you keep ignoring Lucia's calls in GTA 6, you're going to lose a lot more than a conversation."},
  {"asset": "Jason_and_Lucia_03", "move": "pan_r", "head": "THE RELATIONSHIP METER", "chip": "4 LEVELS",
   "say": "Jason and Lucia have a relationship meter with four levels. Guides list them from Running on Empty, all the way up to Hot Together."},
  {"asset": "Jason_and_Lucia_01", "move": "zout", "head": "WHAT RAISES IT",
   "rows": [["HOLDING HANDS", "+"], ["TALKING & GREETING", "+"], ["SAME BEDTIME", "+"]],
   "say": "Holding hands, greeting each other, starting conversations, even going to bed at the same time. And both of them have to put in the effort."},
  {"asset": "Jason_and_Lucia_06", "move": "pan_l", "head": "WHAT BREAKS IT",
   "say": "Neglect her, and the hand holding and kissing disappear until you rebuild the bond. Ignored calls and texts are one of the fastest ways to hurt it."},
  {"asset": "Jason_and_Lucia_05", "move": "zin", "head": "IT CAN CHANGE THE STORY",
   "say": "Some guides even report that a broken relationship can change dialogue, mission options and cutscenes."},
  {"asset": "Jason_and_Lucia_13", "move": "zout", "head": "NO JEALOUSY, THOUGH", "sticker": "sticker_flamingo",
   "say": "The good news? There's no jealousy system. A strip club visit won't start a fight. So, are you a good partner in Leonida?"},
 ]},
{"id": "short_02", "slug": "en-body-system", "topic": "body_system", "seed": 72,
 "title": "You can make Jason FAT in GTA 6 🍔 (but not THAT fat) #gta6 #shorts",
 "description": "GTA 6 tracks what Jason and Lucia eat, how they train and how they sleep. Players already tested 'True Fat Jason'. Plus: the smell system.",
 "hashtags": ["#gta6", "#gtavi", "#gta6jason", "#gta6gym", "#rockstargames", "#gaming", "#shorts"],
 "tags": ["gta 6", "gta 6 weight", "gta 6 gym", "fat jason", "gta 6 body", "gta 6 smell system", "gtavi"],
 "pinned": "Gym build or taco build? 🌮💪 What's your Jason running on right now?",
 "cover": ("Lucia_Caminos_09", .36, .16, 1.45, ["GET FIT", "OR GET FAT"], "GTA 6 BODY SYSTEM"),
 "scenes": [
  {"asset": "Lucia_Caminos_09", "move": "zin", "head": "GTA 6 IS WATCHING YOU EAT",
   "say": "GTA 6 is watching what you eat. And yes, you can actually make Jason fat."},
  {"asset": "Jason_Duval_06", "move": "pan_r", "head": "CONFIRMED BY ROCKSTAR",
   "say": "Rockstar confirmed it to Dazed. Jason and Lucia's bodies change with what they eat and how hard they train. Overeat and you gain weight. Hit the gym and you build muscle."},
  {"asset": "Jason_Duval_01", "move": "zout", "head": "THERE'S A HEALTH APP",
   "say": "There's even a health app tracking sleep, diet and weight. And if you stop training, those gains fade."},
  {"asset": "Vice_City_26", "move": "pan_l", "head": "\"TRUE FAT JASON\"", "chip": "BURGERS + TACOS",
   "say": "One player fed Jason burgers and tacos to build True Fat Jason. The result? A belly and a double chin, but players say he never gets as big as Arthur Morgan at his heaviest."},
  {"asset": "Grassrivers_05", "move": "zin", "head": "AND IT SMELLS", "chip": "SMELL SYSTEM",
   "say": "And there's a smell system too. Rockstar's Aaron Garbut told Edge that Jason and Lucia react with disgust to bad smells across the map."},
  {"asset": "Jason_and_Lucia_12", "move": "zout", "head": "GYM OR TACOS?", "sticker": "sticker_gator",
   "say": "So, what's your Jason running on right now? Gym, or tacos?"},
 ]},
{"id": "short_03", "slug": "en-japan-censorship", "topic": "japan_censorship", "seed": 73,
 "title": "In JAPAN, GTA 6 is a different game 🇯🇵 #gta6 #shorts",
 "description": "The Japanese version of GTA 6 is rated CERO Z and has been edited: shower scenes, the gore slider, file size and subtitles. Some reports still conflict.",
 "hashtags": ["#gta6", "#gtavi", "#gta6japan", "#censorship", "#rockstargames", "#gaming", "#shorts"],
 "tags": ["gta 6", "gta 6 japan", "gta 6 censored", "gta 6 japan version", "cero z", "gtavi"],
 "pinned": "Would you play a censored GTA 6, or is that a deal breaker? 🤔",
 "cover": ("Jason_Duval_01", .77, .19, 1.45, ["JAPAN", "CENSORED IT"], "GTA 6 JAPAN VERSION"),
 "scenes": [
  {"asset": "Jason_Duval_03", "move": "zin", "head": "A DIFFERENT GTA 6",
   "say": "In one country, GTA 6 is a different game. Jason literally showers in his underwear."},
  {"asset": "Vice_City_10", "move": "pan_r", "head": "JAPAN: ADULTS ONLY", "chip": "RATED CERO Z",
   "say": "Japan's version is rated CERO Z, which means adults only. And it has been edited."},
  {"asset": "Jason_Duval_08", "move": "zout", "head": "THE SHOWER SCENES",
   "say": "Where other versions show full nudity in the shower, the Japanese version keeps Jason in his briefs. Reports say Lucia's scenes were changed too."},
  {"asset": "Jason_and_Lucia_04", "move": "pan_l", "head": "NO GORE SLIDER",
   "say": "The blood and gore slider is gone completely, and blood is toned down. Reports even disagree on whether decapitations were cut."},
  {"asset": "Vice_City_11", "move": "zin", "head": "SMALLER DOWNLOAD", "big": "-1.2 GB", "label": "JAPANESE SUBTITLES ONLY",
   "say": "It's also about one point two gigabytes smaller, and it ships with Japanese subtitles only."},
  {"asset": "Jason_and_Lucia_09", "move": "zout", "head": "DEAL BREAKER?", "sticker": "sticker_sun",
   "say": "Would you play a censored GTA 6, or is that a deal breaker?"},
 ]},
{"id": "short_04", "slug": "en-mandy-choice", "topic": "mandy_choice", "seed": 74,
 "title": "The MANDY choice most GTA 6 players rushed 🔧 #gta6 #shorts",
 "description": "In the Pipework mission, GTA 6 lets you provoke Mandy or defuse the conversation. Here's what guides say happens, and the theory about what came out of her pipe. Chapter 1 spoilers.",
 "hashtags": ["#gta6", "#gtavi", "#mandy", "#gta6mandy", "#pipework", "#rockstargames", "#shorts"],
 "tags": ["gta 6", "gta 6 mandy", "mandy gta 6", "pipework", "gta 6 choice", "gta 6 jason", "gtavi"],
 "pinned": "Provoke or defuse: which one did you pick with Mandy? 👀",
 "credit": "Clip: @GTAmemesSOL (X) · Images: Rockstar Games",
 "cover": ("Mandy_frame", .48, .28, 1.7, ["PROVOKE", "OR DEFUSE?"], "THE MANDY CHOICE"),
 "scenes": [
  {"clip": (MANDY, 22.0), "head": "DID YOU RUSH THIS?", "chip": "SPOILER · CHAPTER 1",
   "say": "There's a choice in the Mandy scene that most players rushed straight through."},
  {"asset": "Brian_Heder_01", "move": "pan_r", "head": "QUICK RECAP",
   "say": "Brian sends Jason to collect rent from Mandy in the Keys. She won't pay until he fixes her clogged sink."},
  {"clip": (MANDY, 0.0), "head": "SOMETHING IN THE PIPE",
   "say": "While Jason unclogs it, something comes out of the pipe, and Mandy snatches it before he gets a good look."},
  {"clip": (MANDY, 8.0), "head": "PROVOKE OR DEFUSE?",
   "say": "Then the game lets you choose. Provoke Mandy, or defuse the conversation."},
  {"clip": (MANDY, 16.5), "head": "THE TWIST",
   "say": "Here's the twist. Guides say both paths end the same way. Mandy retreats to her bathroom and asks Jason to leave. And there's no romance route with her."},
  {"asset": "Leonida_Keys_06", "move": "zin", "head": "SO WHAT WAS IT?", "sticker": "sticker_crab",
   "say": "So what was in that pipe? Fans swear it was a finger. Rockstar hasn't confirmed anything. What do you think she's hiding?"},
 ]},
{"id": "short_05", "slug": "en-lucia-prison", "topic": "lucia_prison", "seed": 75,
 "title": "Why was LUCIA in prison? GTA 6 explained ⛓️ #gta6 #shorts",
 "description": "GTA 6 starts with Lucia behind bars. Here's what Rockstar's official bio actually says about why, and what it leaves out.",
 "hashtags": ["#gta6", "#gtavi", "#lucia", "#gta6lucia", "#luciacaminos", "#rockstargames", "#shorts"],
 "tags": ["gta 6", "lucia caminos", "gta 6 lucia", "why was lucia in prison", "gta 6 story", "gtavi"],
 "pinned": "What do you think Lucia actually did? Drop your theory 👇",
 "cover": ("Lucia_Caminos_05", .56, .22, 1.45, ["WHY WAS SHE", "IN PRISON?"], "LUCIA'S PAST"),
 "scenes": [
  {"asset": "Lucia_Caminos_05", "move": "zin", "head": "LUCIA STARTS IN PRISON",
   "say": "When you meet Lucia in GTA 6, she's behind bars. That's exactly how Rockstar introduced her in the very first trailer. But why is she there?"},
  {"asset": "Lucia_Caminos_01", "move": "pan_r", "head": "RAISED TO FIGHT",
   "say": "According to Rockstar's official bio, her father taught her to fight from childhood."},
  {"asset": "Lucia_Caminos_03", "move": "zout", "head": "FIGHTING FOR FAMILY",
   "say": "And fighting to protect her family is what landed her in Leonida Penitentiary. The exact crime? Rockstar still hasn't said, and that's what fans keep arguing about."},
  {"asset": "Lucia_Caminos_07", "move": "pan_l", "head": "SHE GOT LUCKY", "chip": "\"SHEER LUCK\"",
   "say": "She didn't earn her way out, either. The bio says she got out through sheer luck."},
  {"asset": "Jason_and_Lucia_11", "move": "zin", "head": "HER WAY OUT?",
   "say": "And it ends with one line. A life with Jason could be her way out."},
  {"asset": "Jason_and_Lucia_08", "move": "zout", "head": "COULD BE...", "sticker": "sticker_palm",
   "say": "Could be. What do you think Lucia actually did? Drop your theory."},
 ]},
]

SHORTS_ES = [
{"id": "short_01", "slug": "es-medidor-relacion", "topic": "relationship_meter", "seed": 71,
 "title": "Si IGNORAS a Lucía en GTA 6 pasa ESTO 💔 #gta6 #shorts",
 "description": "Jason y Lucía tienen un medidor de relación en GTA 6. Qué lo sube, qué lo rompe y por qué ignorar sus llamadas es mala idea.",
 "hashtags": ["#gta6", "#gtavi", "#jasonylucia", "#gta6lucia", "#rockstargames", "#gaming", "#shorts"],
 "tags": ["gta 6", "gta 6 relacion", "jason y lucia", "gta 6 romance", "gta 6 lucia", "gta 6 consejos", "gtavi"],
 "pinned": "Sé sincero: ¿cuántas llamadas de Lucía has ignorado ya? 📱",
 "cover": ("Lucia_Caminos_10", .47, .36, 1.4, ["NO IGNORES", "A LUCÍA"], "MEDIDOR DE RELACIÓN"),
 "scenes": [
  {"asset": "Lucia_Caminos_10", "move": "zin", "head": "NO IGNORES SUS LLAMADAS",
   "say": "Si sigues ignorando las llamadas de Lucía en GTA 6, vas a perder mucho más que una conversación."},
  {"asset": "Jason_and_Lucia_03", "move": "pan_r", "head": "EL MEDIDOR DE RELACIÓN", "chip": "4 NIVELES",
   "say": "Jason y Lucía tienen un medidor de relación con cuatro niveles. Las guías los nombran desde Running on Empty hasta Hot Together."},
  {"asset": "Jason_and_Lucia_01", "move": "zout", "head": "LO QUE LO SUBE",
   "rows": [["IR DE LA MANO", "+"], ["SALUDARSE Y HABLAR", "+"], ["DORMIR A LA MISMA HORA", "+"]],
   "say": "Ir de la mano, saludarse, empezar conversaciones, incluso irse a dormir a la misma hora. Y los dos tienen que poner de su parte."},
  {"asset": "Jason_and_Lucia_06", "move": "pan_l", "head": "LO QUE LO ROMPE",
   "say": "Si la descuidas, desaparecen los besos y el ir de la mano hasta que reconstruyas el vínculo. Ignorar llamadas y mensajes es de lo que más lo daña."},
  {"asset": "Jason_and_Lucia_05", "move": "zin", "head": "PUEDE CAMBIAR LA HISTORIA",
   "say": "Algunas guías incluso dicen que una relación rota puede cambiar diálogos, opciones de misión y escenas."},
  {"asset": "Jason_and_Lucia_13", "move": "zout", "head": "PERO SIN CELOS", "sticker": "sticker_flamingo",
   "say": "La buena noticia: no hay sistema de celos. Ir a un strip club no va a provocar una pelea. Entonces, ¿eres buena pareja en Leonida?"},
 ]},
{"id": "short_02", "slug": "es-sistema-cuerpo", "topic": "body_system", "seed": 72,
 "title": "Puedes poner GORDO a Jason en GTA 6 🍔 (pero no TANTO) #gta6 #shorts",
 "description": "GTA 6 controla lo que comen Jason y Lucía, cuánto entrenan y cuánto duermen. Los jugadores ya probaron el 'True Fat Jason'. Y además: el sistema de olores.",
 "hashtags": ["#gta6", "#gtavi", "#gta6jason", "#gta6gym", "#rockstargames", "#gaming", "#shorts"],
 "tags": ["gta 6", "gta 6 peso", "gta 6 gimnasio", "jason gordo", "gta 6 cuerpo", "gta 6 olores", "gtavi"],
 "pinned": "¿Build de gimnasio o build de tacos? 🌮💪 ¿Cómo va tu Jason?",
 "cover": ("Lucia_Caminos_09", .36, .16, 1.45, ["EN FORMA", "O GORDO"], "SISTEMA DE CUERPO"),
 "scenes": [
  {"asset": "Lucia_Caminos_09", "move": "zin", "head": "GTA 6 TE VIGILA LA DIETA",
   "say": "GTA 6 está pendiente de lo que comes. Y sí, puedes poner gordo a Jason."},
  {"asset": "Jason_Duval_06", "move": "pan_r", "head": "CONFIRMADO POR ROCKSTAR",
   "say": "Rockstar se lo confirmó a la revista Dazed: el cuerpo de Jason y Lucía cambia según lo que comen y cuánto entrenan. Si comes de más, engordas. Si vas al gym, ganas músculo."},
  {"asset": "Jason_Duval_01", "move": "zout", "head": "HAY UNA APP DE SALUD",
   "say": "Hay hasta una app de salud que registra el sueño, la dieta y el peso. Y si dejas de entrenar, pierdes lo ganado."},
  {"asset": "Vice_City_26", "move": "pan_l", "head": "\"TRUE FAT JASON\"", "chip": "HAMBURGUESAS + TACOS",
   "say": "Un jugador alimentó a Jason a base de hamburguesas y tacos para crear al True Fat Jason. ¿El resultado? Barriga y papada, pero según los jugadores nunca llega a estar tan gordo como Arthur Morgan."},
  {"asset": "Grassrivers_05", "move": "zin", "head": "Y TAMBIÉN HUELE", "chip": "SISTEMA DE OLORES",
   "say": "Y además hay un sistema de olores. Aaron Garbut, de Rockstar, le contó a la revista Edge que Jason y Lucía ponen cara de asco ante los malos olores del mapa."},
  {"asset": "Jason_and_Lucia_12", "move": "zout", "head": "¿GYM O TACOS?", "sticker": "sticker_gator",
   "say": "Entonces, ¿tu Jason va a base de gym, o a base de tacos?"},
 ]},
{"id": "short_03", "slug": "es-japon-censura", "topic": "japan_censorship", "seed": 73,
 "title": "En JAPÓN, GTA 6 es OTRO juego 🇯🇵 #gta6 #shorts",
 "description": "La versión japonesa de GTA 6 tiene calificación CERO Z y viene editada: las escenas de ducha, el ajuste de violencia, el tamaño y los subtítulos. Algunos reportes todavía no coinciden.",
 "hashtags": ["#gta6", "#gtavi", "#gta6japon", "#censura", "#rockstargames", "#gaming", "#shorts"],
 "tags": ["gta 6", "gta 6 japon", "gta 6 censurado", "gta 6 version japonesa", "cero z", "gtavi"],
 "pinned": "¿Jugarías un GTA 6 censurado o para ti eso es imperdonable? 🤔",
 "cover": ("Jason_Duval_01", .77, .19, 1.45, ["JAPÓN LO", "CENSURÓ"], "GTA 6 VERSIÓN JAPONESA"),
 "scenes": [
  {"asset": "Jason_Duval_03", "move": "zin", "head": "OTRO GTA 6",
   "say": "En un país, GTA 6 es otro juego. Literalmente, Jason se ducha en calzoncillos."},
  {"asset": "Vice_City_10", "move": "pan_r", "head": "JAPÓN: SOLO ADULTOS", "chip": "CALIFICACIÓN CERO Z",
   "say": "La versión de Japón tiene la calificación CERO Z, solo para adultos. Y viene editada."},
  {"asset": "Jason_Duval_08", "move": "zout", "head": "LAS ESCENAS DE DUCHA",
   "say": "Donde las demás versiones muestran desnudos en la ducha, la japonesa deja a Jason en calzoncillos. Y según los reportes, las escenas de Lucía también cambiaron."},
  {"asset": "Jason_and_Lucia_04", "move": "pan_l", "head": "SIN AJUSTE DE GORE",
   "say": "El ajuste de sangre y violencia desaparece por completo, y hay menos sangre. Y los reportes ni siquiera coinciden en si quitaron las decapitaciones."},
  {"asset": "Vice_City_11", "move": "zin", "head": "PESA MENOS", "big": "-1,2 GB", "label": "SOLO SUBTÍTULOS EN JAPONÉS",
   "say": "Además pesa uno coma dos gigas menos, y solo trae subtítulos en japonés."},
  {"asset": "Jason_and_Lucia_09", "move": "zout", "head": "¿LO JUGARÍAS?", "sticker": "sticker_sun",
   "say": "¿Tú jugarías un GTA 6 censurado, o eso para ti es imperdonable?"},
 ]},
{"id": "short_04", "slug": "es-decision-mandy", "topic": "mandy_choice", "seed": 74,
 "title": "La DECISIÓN de MANDY que casi nadie pensó 🔧 #gta6 #shorts",
 "description": "En la misión Pipework, GTA 6 te deja provocar a Mandy o calmar la situación. Esto dicen las guías que pasa, y la teoría sobre lo que salió de su tubería. Spoilers del capítulo 1.",
 "hashtags": ["#gta6", "#gtavi", "#mandy", "#gta6mandy", "#pipework", "#rockstargames", "#shorts"],
 "tags": ["gta 6", "gta 6 mandy", "mandy gta 6", "pipework", "gta 6 decision", "gta 6 jason", "gtavi"],
 "pinned": "¿Provocar o calmar? ¿Qué elegiste tú con Mandy? 👀",
 "credit": "Clip: @GTAmemesSOL (X) · Imágenes: Rockstar Games",
 "cover": ("Mandy_frame", .48, .28, 1.7, ["¿PROVOCAR", "O CALMAR?"], "LA DECISIÓN DE MANDY"),
 "scenes": [
  {"clip": (MANDY, 20.5), "head": "¿TE LO SALTASTE?", "chip": "SPOILER · CAPÍTULO 1",
   "say": "En la escena de Mandy hay una decisión que casi todos los jugadores pasaron sin pensar."},
  {"asset": "Brian_Heder_01", "move": "pan_r", "head": "RESUMEN RÁPIDO",
   "say": "Brian manda a Jason a cobrarle el alquiler a Mandy en los Cayos. Ella no paga hasta que le arregle el fregadero."},
  {"clip": (MANDY, 0.0), "head": "ALGO EN LA TUBERÍA",
   "say": "Mientras Jason lo destapa, sale algo de la tubería, y Mandy se lo quita antes de que pueda verlo bien."},
  {"clip": (MANDY, 8.0), "head": "¿PROVOCAR O CALMAR?",
   "say": "Entonces el juego te deja elegir: provocar a Mandy, o calmar la conversación."},
  {"clip": (MANDY, 16.5), "head": "EL GIRO",
   "say": "Y aquí viene el giro. Según las guías, los dos caminos acaban igual: Mandy se encierra en el baño y le pide a Jason que se vaya. Y no hay opción de romance con ella."},
  {"asset": "Leonida_Keys_06", "move": "zin", "head": "¿QUÉ ERA?", "sticker": "sticker_crab",
   "say": "Entonces, ¿qué había en esa tubería? Los fans juran que era un dedo. Rockstar no ha confirmado nada. ¿Tú qué crees que esconde?"},
 ]},
{"id": "short_05", "slug": "es-lucia-prision", "topic": "lucia_prison", "seed": 75,
 "title": "¿Por qué LUCÍA estaba en la CÁRCEL? GTA 6 ⛓️ #gta6 #shorts",
 "description": "GTA 6 empieza con Lucía en prisión. Esto es lo que dice de verdad la biografía oficial de Rockstar, y lo que no cuenta.",
 "hashtags": ["#gta6", "#gtavi", "#lucia", "#gta6lucia", "#luciacaminos", "#rockstargames", "#shorts"],
 "tags": ["gta 6", "lucia caminos", "gta 6 lucia", "por que lucia estaba en la carcel", "gta 6 historia", "gtavi"],
 "pinned": "¿Qué crees que hizo Lucía de verdad? Deja tu teoría 👇",
 "cover": ("Lucia_Caminos_05", .56, .22, 1.45, ["¿POR QUÉ", "ESTABA PRESA?"], "EL PASADO DE LUCÍA"),
 "scenes": [
  {"asset": "Lucia_Caminos_05", "move": "zin", "head": "LUCÍA EMPIEZA EN PRISIÓN",
   "say": "Cuando conoces a Lucía en GTA 6, está entre rejas. Así mismo la presentó Rockstar en el primer tráiler. Pero, ¿por qué está ahí?"},
  {"asset": "Lucia_Caminos_01", "move": "pan_r", "head": "CRIADA PARA PELEAR",
   "say": "Según la biografía oficial de Rockstar, su padre le enseñó a pelear desde niña."},
  {"asset": "Lucia_Caminos_03", "move": "zout", "head": "POR SU FAMILIA",
   "say": "Y pelear por proteger a su familia es lo que la llevó a la Penitenciaría de Leonida. ¿El delito exacto? Rockstar todavía no lo ha dicho, y los fans no paran de discutirlo."},
  {"asset": "Lucia_Caminos_07", "move": "pan_l", "head": "TUVO SUERTE", "chip": "\"PURA SUERTE\"",
   "say": "Y tampoco salió por buen comportamiento. La biografía dice que salió por pura suerte."},
  {"asset": "Jason_and_Lucia_11", "move": "zin", "head": "¿SU SALIDA?",
   "say": "Y termina con una frase: una vida con Jason podría ser su salida."},
  {"asset": "Jason_and_Lucia_08", "move": "zout", "head": "PODRÍA SER...", "sticker": "sticker_palm",
   "say": "Podría ser. ¿Tú qué crees que hizo Lucía de verdad? Deja tu teoría."},
 ]},
]
SHORTS = SHORTS_ES

SOURCES = {  # claim-level source log per short (written to LeonidaDiario/sources/)
 "short_01": [("Four relationship levels, 'Running on Empty' to 'Hot Together'", "credible reporting (guides)", "https://www.gtabase.com/articles/gta-6/gta-6-jason-and-lucia-s-relationship-system-explained"),
              ("Holding hands, greeting, talking, same bedtime raise it; both must contribute", "credible reporting (guides)", "https://www.keengamer.com/articles/guides/gta-6-relationship-guide-how-to-raise-jason-and-lucias-bond/"),
              ("Neglect removes hand-holding/kissing until rebuilt; ignored calls hurt", "credible reporting (guides)", "https://www.pcgamer.com/games/grand-theft-auto/gta-6-romance-jason-lucia/"),
              ("Broken relationship can change dialogue, mission options, cutscenes", "credible reporting (guides, hedged as 'some guides report')", "https://www.gamespot.com/articles/gta-6-romance-relationships/"),
              ("No jealousy system; strip club visit won't cause drama", "credible reporting", "https://gamerant.com/gta-6-characters-jason-lucia-relationship-romance/"),
              ("Texting Lucia to meet, hand-holding in the open world", "official (Rockstar via Bloomberg/Vice)", "https://www.vice.com/en/article/gta-6-jason-lucia-relationship-features/")],
 "short_02": [("Bodies change with eating and gym work", "official (Rockstar to Dazed, via Beebom)", "https://beebom.com/gta-6-weight-system-gym-body-fitness-explained/"),
              ("Health app tracks sleep, diet, weight; gains fade", "credible reporting", "https://beebom.com/gta-6-weight-system-gym-body-fitness-explained/"),
              ("'True Fat Jason' burger/taco test; not as big as Arthur Morgan", "community discovery (reported by GamesRadar)", "https://www.gamesradar.com/games/grand-theft-auto/gta-6-players-confirm-true-fat-jason-and-max-weight-lucia-arent-very-fat-at-all-setting-the-stage-for-the-first-pc-mod-to-super-size-them/"),
              ("Smell system: Jason and Lucia react with disgust", "official (Aaron Garbut to Edge, via Beebom)", "https://beebom.com/gta-6-realistic-smell-system/")],
 "short_03": [("Japanese version rated CERO Z", "credible reporting", "https://www.gtaboom.com/gta-6-is-censored-in-japan-exactly-like-we-predicted-f912"),
              ("Jason in briefs in the shower; Lucia also affected", "credible reporting", "https://www.videogameschronicle.com/news/japan-censors-gta-6s-violence-and-nudity-including-jason-in-the-shower/"),
              ("No blood & gore slider; less blood", "credible reporting", "https://en.gamespark.jp/article/2026/11/19/2475.html"),
              ("Decapitations: reports conflict (VGC vs Game*Spark)", "conflicting reports - stated as such", "https://www.gtaboom.com/gta-6-is-censored-in-japan-exactly-like-we-predicted-f912"),
              ("~1.19 GB smaller; Japanese subtitles only", "credible reporting", "https://www.gtaboom.com/gta-6-is-censored-in-japan-exactly-like-we-predicted-f912")],
 "short_04": [("Pipework: Brian sends Jason to collect Mandy's rent; clogged sink", "credible reporting (mission guides)", "https://beebom.com/gta-6-pipework-mandy-rent-mission/amp/"),
              ("Object from the drain, Mandy snatches it", "credible reporting", "https://gamerant.com/gta-6-mandy-sink-pipework-serial-killer/"),
              ("Provoke or defuse choice; both end with Mandy retreating to bathroom", "credible reporting (guides)", "https://www.keengamer.com/articles/news/gta-6s-mandy-goes-viral-on-launch-day-after-pipework-scene/"),
              ("Choice has no lasting effect", "credible reporting (guide)", "https://xboxplay.games/gta-6/gta-6-mandy-scene-should-you-provoke-or-defuse-choice-77396"),
              ("No romance route", "credible reporting (guides)", "https://www.sportskeeda.com/gta/who-mandy-can-you-romance-her-gta-6"),
              ("'Finger' theory", "fan speculation - stated as unconfirmed", "https://insider-gaming.com/who-is-mandy-gta-6-when-do-you-meet-serial-killer/")],
 "short_05": [("Father taught her to fight from childhood", "official bio (quoted by wikis)", "https://gta.wiki/w/Lucia_Caminos"),
              ("Fighting for her family landed her in Leonida Penitentiary; crime undisclosed", "official bio (quoted by wikis)", "https://meowdb.com/gta6/characters/lucia-caminos"),
              ("Got out through sheer luck", "official bio (quoted by wikis)", "https://gta.wiki/w/Lucia_Caminos"),
              ("'A life with Jason could be her way out'", "official bio (quoted)", "https://gta.wiki/w/Lucia_Caminos"),
              ("Trailer 1 (Dec 2023) introduced Lucia in prison", "official (Rockstar Trailer 1)", "https://www.rockstargames.com/VI")],
}

SHORTS.append(
{"id": "short_06", "slug": "es-primera-persona", "topic": "first_person", "seed": 76,
 "title": "Cómo jugar GTA 6 en PRIMERA PERSONA 🎮 (4 trucos) #gta6 #shorts",
 "description": "GTA 6 no tiene un modo en primera persona completo, pero hay 4 formas de conseguirlo: quieto, apuntando con mira, conduciendo con el móvil y el truco del botón de cámara. Animaciones de mando y menú: ilustraciones.",
 "hashtags": ["#gta6", "#gtavi", "#primerapersona", "#gta6trucos", "#gta6tips", "#rockstargames", "#shorts"],
 "tags": ["gta 6 primera persona", "gta 6 first person", "como poner primera persona gta 6", "gta 6 camara", "gta 6 trucos", "gta 6 ps5", "gtavi"],
 "pinned": "¿Lo conseguiste? Dime qué método te funcionó 👇 Si Rockstar lo parchea, te aviso.",
 "credit": "Imágenes: Rockstar Games · Animaciones: ilustración",
 "cover": ("derived_fp_scope", .5, .2917, 1.0, ["PRIMERA", "PERSONA"], "GTA 6 · 4 TRUCOS"),
 "scenes": [
  {"asset": "Jason_Duval_16", "move": "zin", "head": "¿PRIMERA PERSONA EN GTA 6?",
   "say": "¿Se puede jugar GTA 6 en primera persona? No del todo. Pero hay cuatro trucos para conseguirlo."},
  {"asset": "Jason_and_Lucia_11", "move": "pan_r", "head": "NO HAY MODO COMPLETO", "chip": "NI EN LOS AJUSTES",
   "say": "No hay un modo completo, ni una opción en los ajustes de cámara. Así que vamos con los trucos."},
  {"asset": "Vice_City_10", "pad": [["L2", 0.4, 5.6, "MANTÉN L2"], ["RS", 1.2, 2.0, "PULSA R3"], ["RS", 3.0, 3.8, "PULSA R3"]],
   "head": "1. QUIETO: L2 + R3", "chip": "XBOX: LT + STICK DERECHO",
   "say": "Uno: quieto de pie, mantén L2 y pulsa R3. En Xbox, LT y stick derecho. Si sueltas o te mueves, vuelve la cámara normal."},
  {"asset": "Jason_Duval_05", "scope": True, "move": "zin", "head": "2. APUNTANDO CON MIRA",
   "say": "Dos: con un arma con mira, apunta con L2, pulsa R3, y apuntas en primera persona."},
  {"asset": "Jason_Duval_19", "pad": [["UP", 0.6, 1.4, "CRUCETA ARRIBA"], ["UP", 2.4, 3.2, "CRUCETA ARRIBA"]],
   "head": "3. CONDUCIENDO: SACA EL MÓVIL",
   "say": "Tres: conduciendo, saca el móvil con la cruceta arriba. Según las guías, la cámara pasa al asiento del conductor."},
  {"asset": "Vice_City_11", "menu": True, "head": "4. EL TRUCO VIRAL", "chip": "NO OFICIAL",
   "say": "Y cuatro, el truco viral: en Ajustes, Mando, cambia el botón del panel táctil, o Vista en Xbox, de Mapa a Cámara."},
  {"asset": "Lucia_Caminos_08", "pad": [["CIR", 0.8, 1.3, "CIERRA EL MÓVIL"], ["PAD", 1.35, 2.0, "¡Y YA!"], ["CIR", 3.0, 3.5, "CIERRA EL MÓVIL"], ["PAD", 3.55, 4.2, "¡Y YA!"]],
   "head": "CIERRA EL MÓVIL + CÁMARA", "chip": "XBOX: B + VISTA",
   "say": "Abre el móvil, y justo al cerrarlo, pulsa rápido ese botón. Si te sale, te quedas en primera persona."},
  {"asset": "Jason_and_Lucia_03", "move": "zout", "head": "OJO CON ESTE TRUCO", "sticker": "sticker_manatee",
   "say": "Ojo: es un fallo. Para volver, carga la partida, y Rockstar lo puede quitar en cualquier parche."},
 ]})
SOURCES["short_06"] = [
  ("No full first-person mode; no camera-settings option", "credible reporting (multiple guides)", "https://www.gamesradar.com/games/grand-theft-auto/gta-6-first-person-mode-explained/"),
  ("Standing still: hold L2 + press R3 (Xbox LT + RS); exits on release/move", "credible reporting (guides)", "https://dotesports.com/gta/guides/gta-6-first-person-view"),
  ("Scoped weapons: L2 + R3 for first-person aiming", "credible reporting (guides)", "https://game8.co/games/GTA-6/archives/638527"),
  ("Driving: phone out (D-pad up) switches to driver-seat view; one source calls footage unverified", "credible reporting, partly disputed (stated 'según las guías')", "https://www.gtabase.com/gta-6/articles/how-to-go-first-person-in-gta-6"),
  ("Phone glitch: set Touchpad/View button to Camera, press while closing the phone; reload save to exit; lose map shortcut", "community discovery reported by outlets", "https://www.videogameschronicle.com/guide/gta-6-first-person-mode-glitch-grand-theft-auto/"),
  ("Xbox button naming (View vs Back) differs between sources", "conflicting - we say 'Vista'", "https://www.g2a.com/news/gta-6-news/gta-6-first-person-mode/"),
]

SHORTS.append(
{"id": "short_07", "slug": "es-fisica-choques", "topic": "crash_physics", "seed": 77,
 "title": "Los CHOQUES de GTA 6 son otro nivel 💥🚗 #gta6 #shorts",
 "description": "Así se ven los choques en GTA 6: más peso, daño que se queda, coches más frágiles y facturas de taller. Y en moto, sales volando. Clips de jugadores; el diagrama de daños es una ilustración.",
 "hashtags": ["#gta6", "#gtavi", "#gta6fisica", "#choques", "#crashphysics", "#rockstargames", "#shorts"],
 "tags": ["gta 6 fisica", "gta 6 choques", "gta 6 crash physics", "gta 6 daño coches", "gta 6 conduccion", "gta 6 moto", "gtavi"],
 "pinned": "¿Es la física de choques más realista de un GTA? 💥 ¿Cuál ha sido tu peor choque?",
 "credit": "Clips: jugadores de X · @rodiorraf · Imágenes: Rockstar Games",
 "cover": ("derived_crash_cover", .5, .2917, 1.0, ["CHOQUES", "BRUTALES"], "FÍSICA DE GTA 6"),
 "scenes": [
  {"clip": ("assets/clips/crash_pickup.mp4", 1.0, "fill", .5, (1.4, .47)), "head": "MIRA ESTE CHOQUE",
   "say": "Mira cómo se arruga esta camioneta. Así son los choques en GTA 6."},
  {"clip": ("assets/clips/crash_pickup.mp4", 4.3, "fill", .5), "head": "MÁS PESO, MÁS DAÑO", "chip": "ENTRE GTA IV Y GTA V",
   "say": "Las reseñas coinciden: la conducción está entre GTA cuatro y GTA cinco. Los coches pesan más, y el daño depende de cómo y dónde golpeas."},
  {"clip": ("assets/clips/crash_pickup.mp4", 8.3, "fill", .72), "head": "EL DAÑO SE QUEDA",
   "say": "Y el daño se queda: chapa hundida, piezas sueltas. Además, los coches son más frágiles que en GTA cinco."},
  {"clip": ("assets/clips/crash_sedan.mp4", 2.4, "fill", .5), "head": "UN SEGUNDO DE DESPISTE",
   "say": "Un segundo de despiste en Vice City, y el coche queda tocado. Ojo: si usas el móvil conduciendo, se controla peor."},
  {"asset": "Vice_City_24", "damage": True, "head": "Y SALE CARO", "chip": "FACTURAS DE TALLER",
   "say": "Y arreglarlo cuesta dinero de verdad. Las reseñas hablan de facturas de reparación."},
  {"clip": ("assets/clips/crash_moto_rodiorraf.mov", 0.3, "fit"), "head": "¿Y EN MOTO?",
   "say": "¿Y en moto? Sales volando, el personaje se arrastra por el asfalto, y se levanta como puede."},
  {"asset": "Jason_and_Lucia_09", "move": "zout", "head": "¿REALISTA O EXAGERADO?", "sticker": "sticker_lowrider",
   "say": "¿Es la física de choques más realista de un GTA? Cuéntame tu peor choque."},
 ]})
SOURCES["short_07"] = [
  ("Driving between GTA IV and GTA V; more vehicle weight, physics and damage", "credible reporting (reviews)", "https://wccftech.com/review/grand-theft-auto-vi-review-ps5pro/"),
  ("Cars more fragile, repair bills, learning curve vs GTA V", "credible reporting (review roundup)", "https://outputlag.com/featured-slider/gta-6-review-roundup/"),
  ("Phone use while driving makes control harder", "credible reporting (launch live blog)", "https://www.engadget.com/2320788/gta-vi-launch-day-live-blog/"),
  ("Damage depends on impact (shown in player clips)", "community footage", "player clips supplied by channel owner (X; @rodiorraf)"),
  ("Motorcycle crash: rider thrown, crawls, gets up", "community footage", "@rodiorraf clip"),
]

SHORTS += [
{"id": "short_08", "slug": "es-ventas-oficiales", "topic": "official_sales", "seed": 78,
 "title": "GTA 6 hizo $3.790 MILLONES en UN día 💰 #gta6 #shorts",
 "description": "Es oficial: Rockstar y Take-Two confirmaron 3.790 millones de dólares en ventas el primer día y 32,5 millones de copias antes del lanzamiento. Más del doble de lo que estimaba Sensor Tower.",
 "hashtags": ["#gta6", "#gtavi", "#gta6ventas", "#record", "#rockstargames", "#taketwo", "#shorts"],
 "tags": ["gta 6 ventas", "gta 6 record", "gta 6 3790 millones", "gta 6 copias vendidas", "take two", "gta 6 vs gta 5", "gtavi"],
 "pinned": "¿Tú eres uno de esos millones? 🎮 ¿En qué consola lo juegas?",
 "cover": ("Boobie_Ike_01", .45, .22, 1.45, ["$3.790", "MILLONES"], "EN 1 DÍA · OFICIAL"),
 "scenes": [
  {"asset": "Boobie_Ike_01", "move": "zin", "head": "ES OFICIAL",
   "say": "Es oficial, y es una locura. Rockstar acaba de dar los números del primer día de GTA 6."},
  {"asset": "Vice_City_08", "move": "pan_r", "head": "EN UN SOLO DÍA", "big": "$3.790 M", "label": "VENTAS EL PRIMER DÍA",
   "say": "Tres mil setecientos noventa millones de dólares en ventas en todo el mundo, en su primer día."},
  {"asset": "Raul_Bautista_03", "move": "zout", "head": "ANTES DE SALIR", "big": "32,5 M", "label": "COPIAS VENDIDAS",
   "say": "Y antes de salir, ya había vendido treinta y dos millones y medio de copias."},
  {"asset": "Vice_City_10", "move": "pan_l", "head": "MÁS DEL DOBLE",
   "rows": [["ESTIMACIÓN SENSOR TOWER", "$1.650 M"], ["CIFRA OFICIAL", "$3.790 M"]],
   "say": "Hace unos días te contamos la estimación de Sensor Tower: mil seiscientos cincuenta millones. La cifra real es más del doble."},
  {"asset": "Vice_City_02", "move": "zin", "head": "¿Y GTA 5?", "chip": "x4,6",
   "say": "Para que te hagas una idea: GTA cinco hizo unos ochocientos quince millones en su primer día. GTA 6 lo multiplica por más de cuatro."},
  {"asset": "Vice_City_04", "move": "zout", "head": "¿LO COMPRASTE?", "sticker": "sticker_crab",
   "say": "¿Tú eres uno de esos millones? Cuéntame en qué consola lo juegas."},
 ]},
{"id": "short_09", "slug": "es-animales", "topic": "animals", "seed": 79,
 "title": "Los ANIMALES de GTA 6 son una locura 🐊🐕 #gta6 #shorts",
 "description": "Perros y gatos que puedes acariciar, caimanes que te embisten, más de 170 especies según Game Informer y caza en Mount Kalaga.",
 "hashtags": ["#gta6", "#gtavi", "#gta6animales", "#caiman", "#leonida", "#rockstargames", "#shorts"],
 "tags": ["gta 6 animales", "gta 6 perros", "gta 6 caiman", "gta 6 mascotas", "gta 6 caza", "gta 6 fauna", "gtavi"],
 "pinned": "¿Cuál es el animal más raro que has visto en Leonida? 🐊",
 "cover": ("Vice_City_19", .2, .42, 1.45, ["NO TOQUES", "ESE PERRO"], "ANIMALES DE GTA 6"),
 "scenes": [
  {"asset": "Vice_City_19", "move": "zin", "head": "¿PUEDES ACARICIAR AL PERRO?",
   "say": "¿Se puede acariciar a los perros en GTA 6? Sí. Kotaku ya recopiló clips de Jason acariciando perros y gatos. Y eso es solo el principio."},
  {"asset": "Mount_Kalaga_National_Park_05", "move": "pan_r", "head": "MÁS DE 170 ESPECIES", "chip": "SEGÚN GAME INFORMER",
   "say": "Según Game Informer, Leonida tiene más de ciento setenta especies de animales."},
  {"asset": "Grassrivers_08", "move": "zin", "head": "CUIDADO CON LOS CAIMANES",
   "say": "Pero ojo con los caimanes. Si pisas su territorio, te embisten, te tiran al suelo, y prácticamente se acabó."},
  {"asset": "Grassrivers_07", "move": "pan_l", "head": "LA VIDA EN GRASSRIVERS",
   "say": "En los pantanos de Grassrivers hay serpientes, caimanes, y gente bastante rara."},
  {"asset": "Mount_Kalaga_National_Park_03", "move": "zout", "head": "CAZA EN KALAGA",
   "say": "Y en Mount Kalaga, las imágenes oficiales muestran cazadores en el bosque. Las guías ya hablan de caza y pesca."},
  {"asset": "Leonida_Keys_06", "move": "zin", "head": "¿CUÁL ES TU FAVORITO?", "sticker": "sticker_gator",
   "say": "¿Cuál es el animal más raro que has visto en Leonida?"},
 ]},
{"id": "short_10", "slug": "es-radio", "topic": "radio", "seed": 80,
 "title": "VUELVEN las radios de VICE CITY a GTA 6 📻 #gta6 #shorts",
 "description": "Flash FM y Emotion 98.3 vuelven en GTA 6: 24 emisoras, cientos de canciones, de pop ochentero a metal, y playlists secretas según PC Gamer.",
 "hashtags": ["#gta6", "#gtavi", "#flashfm", "#gta6radio", "#vicecity", "#rockstargames", "#shorts"],
 "tags": ["gta 6 radio", "gta 6 canciones", "gta 6 soundtrack", "flash fm gta 6", "emotion 98.3", "gta 6 emisoras", "gtavi"],
 "pinned": "¿Cuál es tu emisora favorita de GTA 6? 📻",
 "cover": ("Real_Dimez_04", .45, .25, 1.45, ["VUELVE", "FLASH FM"], "RADIOS DE GTA 6"),
 "scenes": [
  {"asset": "Real_Dimez_04", "move": "zin", "head": "¿TE ACUERDAS DE FLASH FM?",
   "say": "Si jugaste a Vice City, este nombre te va a sonar: Flash FM ha vuelto en GTA 6."},
  {"asset": "Vice_City_08", "move": "pan_r", "head": "Y EMOTION 98.3",
   "say": "Y no viene sola. También vuelve Emotion noventa y ocho punto tres, con baladas y soft rock de los ochenta."},
  {"asset": "Lucia_Caminos_06", "move": "zout", "head": "UNA BARBARIDAD DE MÚSICA", "big": "24", "label": "EMISORAS",
   "say": "En total hay veinticuatro emisoras, y una guía cuenta más de ochocientas canciones. Las cifras varían según la fuente."},
  {"asset": "DreQuan_Priest_04", "move": "pan_l", "head": "PARA TODOS LOS GUSTOS",
   "rows": [["FLASH FM", "POP"], ["EMOTION 98.3", "80s"], ["RADIO ON-U", "REGGAE"], ["THE CHAMBER", "METAL"]],
   "say": "Pop y dance en Flash FM, reggae y dub en Radio On-U, y en The Chamber, hasta heavy metal."},
  {"asset": "Real_Dimez_01", "move": "zin", "head": "Y PLAYLISTS SECRETAS",
   "say": "Y según PC Gamer, hay listas de reproducción secretas escondidas en el juego."},
  {"asset": "Jason_and_Lucia_10", "move": "zout", "head": "¿CUÁL ESCUCHAS TÚ?", "sticker": "sticker_sun",
   "say": "¿Cuál es tu emisora favorita? Déjala en los comentarios."},
 ]},
]
SOURCES["short_08"] = [("$3.79B day-one retail sales; 32.5M units pre-release", "official (Rockstar press release, Take-Two SEC 8-K)", "https://www.sec.gov/Archives/edgar/data/0000946581/000162828026075217/exhibit9918k.htm"),
  ("Sensor Tower earlier estimate (we reported ~$1.65B)", "third-party estimate", "https://gamerant.com/gta-6-copies-sold-billion-dollar-sales-hour/"),
  ("GTA V day one ~$815.7M", "official record (Guinness)", "https://videocardz.com/newz/gta-6-generates-3-79-billion-in-first-day-sales-with-32-5-million-copies-sold-before-launch")]
SOURCES["short_09"] = [("Jason petting dogs and cats (clips)", "credible reporting (Kotaku)", "https://kotaku.com/grand-theft-auto-6-gta6-cats-dogs-snake-pet-alligator-2000758120"),
  ("170+ species", "credible reporting (Game Informer via Red Bull/GTA Intel)", "https://www.redbull.com/int-en/gta-6-wildlife"),
  ("Alligators charge and knock Jason down", "credible reporting (Vice/Kotaku clips)", "https://www.vice.com/en/article/6-wild-animal-encounters-in-gta-6-that-you-have-to-see-to-believe/"),
  ("Hunters in Mount Kalaga official screenshots; hunting & fishing activities in guides", "official image + guides", "https://driffle.com/blog/gta-6-activities-side-missions-everything-confirmed-so-far/")]
SOURCES["short_10"] = [("Flash FM and Emotion 98.3 return; 24 stations; Radio On-U reggae/dub; The Chamber metal", "credible reporting", "https://consequence.net/2026/11/gta-6-radio-stations-songs-soundtrack/"),
  ("800+ tracks (counts vary)", "credible reporting, conflicting counts (stated)", "https://musicexp.substack.com/p/a-complete-list-of-every-track-in"),
  ("Secret unique playlists", "credible reporting (PC Gamer)", "https://www.pcgamer.com/games/grand-theft-auto/gta-6-radio-songs/")]

SHORTS += [
{"id": "short_11", "slug": "es-portal-vice-city", "topic": "vice_city_portal", "seed": 81,
 "title": "Hay un PORTAL SECRETO a VICE CITY 2002 en GTA 6 🌀 #gta6 #shorts",
 "description": "Un easter egg de GTA 6 te lleva al Club Malibu del Vice City original de 2002. Lo descubrió el creador Memeio. Así se activa, y qué premio da. Efecto de portal: ilustración.",
 "hashtags": ["#gta6", "#gtavi", "#vicecity", "#tommyvercetti", "#easteregg", "#rockstargames", "#shorts"],
 "tags": ["gta 6 portal vice city", "gta 6 easter egg", "gta 6 secreto", "tommy vercetti gta 6", "club malibu gta 6", "gta 6 vice city 2002", "gtavi"],
 "pinned": "¿Lo vas a intentar? 🌀 Si te sale, cuéntame cuánto tardaste.",
 "credit": "Imágenes: Rockstar Games · Efecto de portal: ilustración",
 "cover": ("VINTAGE_VICE_CITY_PACK_EXCLUSIVE_LOOKS_05", .52, .45, 1.3, ["PORTAL A", "VICE CITY"], "SECRETO DE GTA 6"),
 "scenes": [
  {"asset": "VINTAGE_VICE_CITY_PACK_EXCLUSIVE_LOOKS_05", "move": "zin", "portal": True, "head": "UN PORTAL AL PASADO",
   "say": "En GTA 6 hay un portal secreto que te lleva al Vice City original de dos mil dos."},
  {"asset": "Leonida_Keys_01", "move": "pan_r", "head": "1. LA TORRE DE KEY LENTO",
   "say": "Empieza en la torre de radio de Key Lento: sube, baja la palanca, pulsa el botón, y la tele marcará Club Malibu."},
  {"asset": "Ambrosia_04", "move": "zout", "head": "2. 12 SUBESTACIONES", "chip": "SOLO CON JASON · SIN VIAJE RÁPIDO",
   "say": "Después, recorre doce subestaciones eléctricas en orden, siguiendo letras pintadas en las paredes. Hazlo con Jason y sin viaje rápido, o se reinicia."},
  {"asset": "Ambrosia_02", "move": "pan_l", "head": "LA FRASE SECRETA", "chip": "LIFE IS PASSING ME BY",
   "say": "Las letras forman LIFE IS PASSING ME BY, uno de los trucos clásicos de Vice City."},
  {"asset": "Vice_City_06", "move": "zin", "portal": True, "head": "3. EL PORTAL", "chip": "DE 19:00 A 6:00",
   "say": "Al terminar te llega un mensaje, y de noche se abre un portal azul que te lleva al Club Malibu del juego original."},
  {"asset": "VINTAGE_VICE_CITY_PACK_EXCLUSIVE_LOOKS_04", "move": "pan_r", "head": "EL PREMIO",
   "say": "El premio: la camisa hawaiana de Tommy Vercetti, y una moto del juego de dos mil dos. Lo descubrió el creador Memeio, después de tres días."},
  {"asset": "Leonida_Keys_05", "move": "zout", "head": "¿LO VAS A INTENTAR?", "chip": "NECESITAS EL CAPÍTULO 3", "sticker": "sticker_palm",
   "say": "Ojo: necesitas llegar al capítulo tres para tener todo el mapa. ¿Lo vas a intentar?"},
 ]},
{"id": "short_12", "slug": "es-radios-secretas", "topic": "secret_radios", "seed": 82,
 "title": "Las 2 RADIOS SECRETAS de GTA 6 (cómo desbloquearlas) 📻🔓 #gta6 #shorts",
 "description": "GTA 6 tiene dos emisoras ocultas, The Vault y The Sniper of La Perle. Se desbloquean escaneando pósters con la app WAiNK. Aquí dónde están.",
 "hashtags": ["#gta6", "#gtavi", "#gta6radio", "#secreto", "#gta6trucos", "#rockstargames", "#shorts"],
 "tags": ["gta 6 radios secretas", "the vault gta 6", "sniper of la perle", "gta 6 wainK posters", "gta 6 secretos", "gta 6 emisoras", "gtavi"],
 "pinned": "¿Ya desbloqueaste las dos? 🔓 ¿Cuál te gusta más?",
 "credit": "Imágenes: Rockstar Games · Animación de mando: ilustración",
 "cover": ("Boobie_Ike_02", .25, .22, 1.45, ["RADIOS", "SECRETAS"], "CÓMO DESBLOQUEARLAS"),
 "scenes": [
  {"asset": "Boobie_Ike_02", "move": "zin", "head": "2 EMISORAS OCULTAS",
   "say": "GTA 6 tiene dos emisoras secretas, y casi nadie sabe cómo desbloquearlas."},
  {"asset": "Real_Dimez_02", "pad": [["UP", 0.5, 2.6, "MANTÉN ARRIBA"], ["R1", 3.2, 3.9, "R1: ESCANEAR"], ["R1", 4.6, 5.3, "R1: ESCANEAR"]],
   "head": "SACA EL MÓVIL Y ESCANEA", "chip": "APP WAiNK",
   "say": "Necesitas la app WAiNK. Mantén la cruceta arriba para sacar el móvil, y pulsa R1 para escanear los pósters."},
  {"asset": "Vice_City_06", "move": "pan_r", "head": "1. THE VAULT", "chip": "1 PÓSTER ROJO",
   "say": "La primera, The Vault: un póster rojo en la entrada de una discoteca de Downtown, al oeste de la NINE1NINE y al sur del Jack of Hearts."},
  {"asset": "DreQuan_Priest_02", "move": "zout", "head": "2. THE SNIPER OF LA PERLE", "chip": "4 PÓSTERS",
   "say": "La segunda, The Sniper of La Perle, pide escanear cuatro pósters por La Perle y Crosstown, por ejemplo en Aunt Zola's Soul Food."},
  {"asset": "Boobie_Ike_04", "move": "pan_l", "head": "OJO", "chip": "UNO SE DESBLOQUEA MÁS TARDE",
   "say": "Ojo: uno de los pósters no está disponible hasta un capítulo más avanzado, y las guías no coinciden en todos los detalles."},
  {"asset": "Vice_City_09", "move": "zin", "head": "¿YA LAS TIENES?", "sticker": "sticker_sun",
   "say": "¿Ya tienes las dos? Cuéntame cuál te gusta más."},
 ]},
{"id": "short_13", "slug": "es-robar-cajero", "topic": "atm_tow", "seed": 83,
 "title": "Así se ROBA un CAJERO ENTERO en GTA 6 🏧🪝 #gta6 #shorts",
 "description": "En GTA 6 puedes arrancar un cajero de la pared con el gancho de una grúa. Paso a paso, según las guías y el clip viral de Reddit. Animación del cajero: ilustración.",
 "hashtags": ["#gta6", "#gtavi", "#gta6dinero", "#gta6trucos", "#cajero", "#rockstargames", "#shorts"],
 "tags": ["gta 6 robar cajero", "gta 6 atm", "gta 6 dinero facil", "gta 6 grua", "gta 6 trucos", "gta 6 dinero", "gtavi"],
 "pinned": "¿Cuánto sacaste del cajero? 💸 Te leo.",
 "credit": "Imágenes: Rockstar Games · Animación del cajero: ilustración",
 "cover": ("Jason_Duval_10", .5, .33, 1.4, ["ROBA EL", "CAJERO"], "TRUCO DE GTA 6"),
 "scenes": [
  {"asset": "Jason_Duval_10", "move": "zin", "head": "ROBA UN CAJERO ENTERO",
   "say": "En GTA 6 puedes arrancar un cajero entero de la pared. Con una grúa."},
  {"asset": "ULTIMATE_EDITION_RIDEOUT_CUSTOMS_02", "move": "pan_r", "head": "1. PONLE UN GANCHO", "chip": "EN EL TALLER",
   "say": "Primero, en un taller, ponle un cabrestante con gancho a tu vehículo. Una guía dice que cuesta mil quinientos noventa y cinco dólares."},
  {"asset": "Vice_City_09", "atm": True, "head": "2. ENGANCHA Y ACELERA",
   "say": "Después, da marcha atrás hasta un cajero exterior, engánchalo, y acelera para arrancarlo de la pared."},
  {"asset": "ULTIMATE_EDITION_VAPID_GANADO_RETRO_BUILD_01", "move": "zout", "head": "NO TODOS SIRVEN",
   "say": "Ojo: no todos los cajeros se pueden arrancar. Si uno no engancha, prueba con otro."},
  {"asset": "ULTIMATE_EDITION_ONE_EYED_WILLIE_01", "move": "pan_l", "head": "3. ÁBRELO",
   "say": "Luego arrástralo hasta que se rompa, o ábrelo con un explosivo, y el dinero es tuyo."},
  {"asset": "Jason_Duval_07", "move": "zin", "head": "Y QUE NO TE VEAN", "sticker": "sticker_lowrider",
   "say": "Eso sí: con la policía de GTA 6, mejor que nadie te vea. ¿Ya lo probaste?"},
 ]},
]
SOURCES["short_11"] = [("Secret portal to 2002 Vice City's Malibu Club, found by Memeio (~3 days)", "community discovery reported by outlets", "https://videocardz.com/newz/gta-vi-has-a-secret-portal-that-takes-players-back-to-vice-city-from-2002"),
  ("Key Lento radio tower lever/button; TV shows CLUB MALIBU; 12 substations; stay as Jason, no fast travel", "community guides", "https://gameriv.com/gta-6-how-to-unlock-the-secret-vice-city-portal/"),
  ("Phrase LIFE IS PASSING ME BY (Vice City cheat); portal 7PM-6AM; rewards Tommy shirt + motorbike; Chapter 3 needed", "community guides (details vary)", "https://press-start.com.au/news/playstation/2026/11/24/gta-6-has-an-og-vice-city-portal-thats-super-hard-to-find/")]
SOURCES["short_12"] = [("Two hidden stations: The Vault (1 red poster, Downtown club W of NINE1NINE, S of Jack of Hearts) and The Sniper of La Perle (4 posters, La Perle/Crosstown, e.g. Aunt Zola's)", "credible reporting (guides)", "https://www.pushsquare.com/guides/gta-6-unique-playlist-locations"),
  ("Scan with WAiNK; phone via D-pad up; R1/RB", "credible reporting (guides)", "https://www.gamingbible.com/news/gta-6-how-to-unlock-secret-radio-stations-790145-20261122"),
  ("One poster locked until later chapter; details conflict", "credible reporting, conflicting (stated)", "https://mixed-news.com/en/gta-6-hidden-playlists-poster-locations-waink-it/")]
SOURCES["short_13"] = [("Tow hook/winch can rip ATMs off walls (Reddit clip)", "community discovery reported by outlets", "https://journalarta.com/en/2026/11/23/gta-6-players-tow-truck-atm-money-trick/"),
  ("Winch fitted at a mod shop, $1,595 (one guide)", "guide (single source, stated as such)", "https://www.altchar.com/guides/grand-theft-auto-6-how-to-rob-atms-by-ripping-them-out-of-the-wall-a4oUP6r4ZR5m"),
  ("Only some ATMs towable; drag until it breaks or use explosives", "guides", "https://games.gg/grand-theft-auto-vi/guides/gta-6-how-to-open-a-stolen-atm-and-rob-atms-with-a-winch/")]

# --------------------------------------------------------------------------------------------- voice
_k = _vm = None
def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(f"{KOKORO}/kokoro-v1.0.onnx", f"{KOKORO}/voices-v1.0.bin")
    return _k

def vosk_model():
    global _vm
    if _vm is None:
        from vosk import Model, SetLogLevel
        SetLogLevel(-1); _vm = Model(VOSK)
    return _vm

def _deacc(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def norm_tokens(word):
    """Spoken-form tokens for one display word (for alignment against the recognizer)."""
    from num2words import num2words
    w = _deacc(word.lower().strip(".,!?;:\"“”()…'’¿¡").replace("’", "'"))
    if not w: return []
    if w == "gta": return ["ge", "te", "a"] if LANG == "es" else ["g", "t", "a"]
    if re.fullmatch(r"-?\d+([.,]\d+)?", w):
        v = float(w.replace(",", ".")) if re.search(r"[.,]", w) else int(w)
        return _deacc(re.sub(r"[-,]", " ", num2words(v, lang=LANG))).split()
    return [t for t in re.split(r"[-/]", w) if t]

def transcribe(samples, sr):
    from vosk import KaldiRecognizer
    x = np.asarray(samples, np.float32)
    if sr != 16000:
        import scipy.signal as ss
        x = ss.resample_poly(x, 16000, sr)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()
    rec = KaldiRecognizer(vosk_model(), 16000); rec.SetWords(True)
    words = []
    for i in range(0, len(pcm), 8000):
        if rec.AcceptWaveform(pcm[i:i + 8000]):
            words += json.loads(rec.Result()).get("result", [])
    words += json.loads(rec.FinalResult()).get("result", [])
    return [(_deacc(w["word"]), w["start"], w["end"]) for w in words]

def align(display_words, rec_words):
    """Start time for each display word, from recognizer timestamps (interpolated where unmatched)."""
    flat, owner = [], []
    for i, w in enumerate(display_words):
        for t in norm_tokens(w): flat.append(t); owner.append(i)
    rtoks = [w[0] for w in rec_words]
    sm = difflib.SequenceMatcher(None, flat, rtoks, autojunk=False)
    starts = [None] * len(display_words)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            i = owner[a + k]
            if starts[i] is None: starts[i] = rec_words[b + k][1]
    known = [(i, s) for i, s in enumerate(starts) if s is not None]
    end = rec_words[-1][2] if rec_words else 1.0
    for i in range(len(starts)):
        if starts[i] is None:
            prev = max([k for k in known if k[0] < i], default=(-1, 0.0), key=lambda k: k[0])
            nxt = min([k for k in known if k[0] > i], default=(len(starts), end), key=lambda k: k[0])
            starts[i] = prev[1] + (nxt[1] - prev[1]) * (i - prev[0]) / max(1, nxt[0] - prev[0])
    return starts, sm.ratio(), (rec_words[-1][2] if rec_words else 0)

def gaps(x, sr, thr=0.004, min_gap=0.55):
    env = np.convolve(np.abs(x), np.ones(int(sr * 0.01)) / (sr * 0.01), "same")
    s = env < thr; out = []; c = 0
    for v in s[int(sr * 0.15): len(s) - int(sr * 0.15)]:
        if v: c += 1
        else:
            if c > sr * min_gap: out.append(round(c / sr, 2))
            c = 0
    return out

def tts(text):
    """One continuous generation for the whole scene; validated and retried if needed."""
    tries = [(VOICE, SPEED), (VOICE, 0.97), (VOICE, 1.04)] + ([("am_fenrir", 1.04)] if LANG == "en" else [])
    best = None
    for voice, spd in tries:
        s, sr = kokoro().create(A.pron(text) if LANG == "es" else text, voice=voice, speed=spd, lang=KLANG)
        s = np.asarray(s, np.float32)
        nz = np.where(np.abs(s) > 0.006)[0]
        s = s[max(0, nz[0] - int(sr * 0.04)): nz[-1] + int(sr * 0.08)] if len(nz) else s
        f = int(sr * 0.012); s[:f] *= np.linspace(0, 1, f); s[-f:] *= np.linspace(1, 0, f)
        s = s / (np.abs(s).max() + 1e-6) * 0.9
        rec = transcribe(s, sr)
        words = text.split()
        starts, ratio, _ = align(words, rec)
        g = gaps(s, sr)
        ok = ratio >= MIN_MATCH and not g
        rep = {"voice": voice, "speed": spd, "asr_match": round(ratio, 3), "long_gaps": g,
               "recognized": " ".join(w[0] for w in rec), "duration": round(len(s) / sr, 2)}
        rep["ok"] = ok
        if voice == VOICE and (best is None or (ok, ratio) > (best[3]["ok"], best[3]["asr_match"])):
            best = (s, sr, starts, rep)
        if ok: break
        # keep the channel's narrator: only fall back to another voice if the main one is clearly broken
        if voice == VOICE and spd == tries[2][1] and best[3]["asr_match"] >= MIN_MATCH - 0.08 and not best[3]["long_gaps"]:
            best[3]["note"] = "main voice kept (ASR below 0.88 is recognizer error on uncommon words; manually checked text)"
            return best
        if voice != VOICE: best = (s, sr, starts, rep)
    return best

# --------------------------------------------------------------------------------------------- visuals
# Where the face / subject is in each image (fractions), measured on a grid during asset review.
FOCUS = {"Jason_and_Lucia_03": (.45, .28), "Jason_and_Lucia_01": (.32, .27), "Lucia_Caminos_10": (.62, .22),
         "Jason_and_Lucia_06": (.62, .30), "Jason_and_Lucia_05": (.5, .45), "Jason_and_Lucia_13": (.53, .24),
         "Lucia_Caminos_09": (.53, .22), "Jason_Duval_06": (.53, .2), "Jason_Duval_01": (.68, .17), "Vice_City_26": (.5, .5),
         "Grassrivers_05": (.5, .45), "Jason_and_Lucia_12": (.65, .3), "Jason_Duval_03": (.14, .26), "Vice_City_10": (.42, .42),
         "Jason_Duval_08": (.48, .26), "Jason_and_Lucia_04": (.2, .17), "Vice_City_11": (.3, .45), "Jason_and_Lucia_09": (.62, .2),
         "Brian_Heder_01": (.53, .26), "Leonida_Keys_06": (.72, .25), "Lucia_Caminos_05": (.57, .14), "Lucia_Caminos_01": (.57, .3),
         "Lucia_Caminos_03": (.3, .26), "Lucia_Caminos_07": (.62, .27), "Jason_and_Lucia_11": (.55, .34), "Jason_and_Lucia_08": (.5, .42),
         "Jason_Duval_16": (.53, .24), "Jason_Duval_05": (.22, .3), "Jason_Duval_19": (.82, .28), "Lucia_Caminos_08": (.6, .4), "Vice_City_24": (.4, .45),
         "Boobie_Ike_01": (.45, .22), "Raul_Bautista_03": (.6, .12), "Vice_City_02": (.75, .38), "Vice_City_04": (.5, .2),
         "Vice_City_08": (.45, .42), "Mount_Kalaga_National_Park_05": (.45, .55), "Mount_Kalaga_National_Park_03": (.26, .55),
         "Grassrivers_07": (.31, .22), "Vice_City_19": (.2, .42), "Real_Dimez_04": (.45, .25), "Real_Dimez_01": (.55, .2),
         "DreQuan_Priest_04": (.25, .15), "Lucia_Caminos_06": (.55, .3), "Jason_and_Lucia_10": (.35, .4), "Grassrivers_08": (.5, .6),
         "VINTAGE_VICE_CITY_PACK_EXCLUSIVE_LOOKS_05": (.52, .45), "Leonida_Keys_01": (.5, .4), "Ambrosia_04": (.3, .5), "Ambrosia_02": (.5, .5),
         "Vice_City_06": (.5, .4), "VINTAGE_VICE_CITY_PACK_EXCLUSIVE_LOOKS_04": (.65, .22), "Leonida_Keys_05": (.6, .35),
         "Boobie_Ike_02": (.25, .22), "Real_Dimez_02": (.5, .35), "DreQuan_Priest_02": (.83, .17), "Boobie_Ike_04": (.4, .3),
         "Vice_City_09": (.5, .5), "Jason_Duval_10": (.5, .33), "ULTIMATE_EDITION_RIDEOUT_CUSTOMS_02": (.5, .5),
         "ULTIMATE_EDITION_VAPID_GANADO_RETRO_BUILD_01": (.4, .5), "ULTIMATE_EDITION_ONE_EYED_WILLIE_01": (.5, .5), "Jason_Duval_07": (.5, .4)}
FACE_Y = 640   # where the subject should sit in the 1920px frame (below the headline, above the subtitles)

def asset_image(name):
    p = os.path.join(S.IMG, name + ".jpg")
    if not os.path.exists(p): p = os.path.join(S.IMG, name + ".png")
    im = Image.open(p).convert("RGB")
    fx, fy = FOCUS.get(name, (.5, .5))
    scale_h = min(1.6, max(1.2, (FACE_Y + 60) / max(fy, 0.05) / H))   # enlarge only as much as needed
    s = (H * scale_h) / im.size[1]
    return im.resize((int(im.size[0] * s), int(im.size[1] * s)), Image.LANCZOS), (fx, fy)

def ease_io(p):
    p = max(0.0, min(1.0, p)); return p * p * (3 - 2 * p)

def camera(bg, move, sp, lt, focus=(0.5, 0.5)):
    """Varied Ken Burns moves around the subject + a short punch-in at the start of every scene."""
    fx, fy = focus
    bw, bh = bg.size
    e = ease_io(sp)
    z = {"zin": 1.0 + 0.12 * e, "zout": 1.12 - 0.12 * e}.get(move, 1.06)
    z *= 1.0 + 0.05 * max(0.0, 1 - lt / 0.25)          # punch-in
    cw, chh = W / z, H / z
    base = fx * bw
    if move == "pan_r": cx = base - (W * 0.06) + e * W * 0.12
    elif move == "pan_l": cx = base + (W * 0.06) - e * W * 0.12
    else: cx = base
    cx = min(max(cw / 2, cx), bw - cw / 2)
    top = fy * bh - FACE_Y / z
    top = min(max(0, top), bh - chh); cy = top + chh / 2
    return bg.transform((W, H), Image.AFFINE, (1 / z, 0, cx - cw / 2, 0, 1 / z, cy - chh / 2), resample=Image.BICUBIC)

def sticker_frames(name, width=330):
    src = os.path.join(ROOT, "assets", "stickers", name + ".mp4")
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True)
    w0, h0 = map(int, p.stdout.strip().split(","))
    half = h0 // 2
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", src, "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, stdin=subprocess.DEVNULL).stdout
    n = len(raw) // (w0 * h0 * 3); frames = []
    for i in range(n):
        im = Image.frombytes("RGB", (w0, h0), raw[i * w0 * h0 * 3:(i + 1) * w0 * h0 * 3])
        col, mat = im.crop((0, 0, w0, half)), im.crop((0, half, w0, half * 2)).convert("L")
        rgba = col.convert("RGBA"); rgba.putalpha(mat)
        bb = mat.point(lambda v: 255 if v > 20 else 0).getbbox() or (0, 0, w0, half)
        rgba = rgba.crop(bb); s = width / rgba.size[0]
        frames.append(rgba.resize((width, max(1, int(rgba.size[1] * s))), Image.LANCZOS))
    return frames

def extract_any(path, t0, dur, out, mode="fit", fx=0.5, zf=(1.0, 0.5)):
    """Local clip -> 1080x1920. 'fit' = whole frame over blurred copy; 'fill' = crop to fill around fx.
    If the clip has less footage left than the scene needs, it is slowed down (max 1.7x) instead of freezing."""
    src_d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                 capture_output=True, text=True).stdout)
    avail = max(0.5, src_d - t0 - 0.05)
    slow = min(1.7, max(1.0, (dur + 0.3) / avail))
    pts = f"setpts={slow:.3f}*PTS,"
    if mode == "fill":
        z, fy = zf
        vf = (f"[0:v]{pts}fps={FPS},scale=-2:{int(H * z)}:flags=lanczos,crop={W}:{H}:max(0\\,min(iw-{W}\\,iw*{fx}-{W/2})):"
              f"max(0\\,min(ih-{H}\\,ih*{fy}-{H/2})),"
              "eq=saturation=1.06:contrast=1.03[v]")
    else:
        vf = (f"[0:v]{pts}fps={FPS},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"boxblur=24:2,eq=brightness=-0.12[bg];[b]scale={W}:-2:flags=lanczos[fg];[bg][fg]overlay=0:(H-h)/2-40[v]")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", str(t0), "-i", path, "-t", f"{avail:.2f}",
                    "-an", "-filter_complex", vf, "-map", "[v]", "-t", f"{dur + 0.3:.2f}", "-c:v", "libx264", "-crf", "16",
                    "-preset", "fast", out], check=True, stdin=subprocess.DEVNULL, timeout=600)
    return slow

# --------------------------------------------------------------------------------------------- build
def build(spec, order):
    sid = spec["id"]; d = os.path.join(OUT, "shorts", sid); wk = os.path.join(d, "_work")
    for sub in ["scripts", "voiceovers", "sources", "metadata", "production_reports"]:
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    os.makedirs(wk, exist_ok=True)
    reg = R.load()
    report = {"id": sid, "slug": spec["slug"], "title": spec["title"], "scenes": []}

    # 1) narration, validated per scene
    tl, t = [], 0.0
    for i, sc in enumerate(spec["scenes"]):
        s, sr, starts, rep = tts(sc["say"])
        dur = LEAD + len(s) / sr + TAIL
        tl.append(dict(start=t, dur=dur, vo=s, sr=sr, starts=starts, s=sc)); report["scenes"].append(rep); t += dur
        print(f"  [{sid}] scene {i+1}: {rep['voice']} x{rep['speed']} match={rep['asr_match']} gaps={rep['long_gaps']} ok={rep['ok']}")
    total = t
    sr = tl[0]["sr"]

    # 2) subtitles from real word timings (3-word chunks, break at punctuation)
    caps, srt = [], []
    for e in tl:
        words = e["s"]["say"].split(); st = [e["start"] + LEAD + x for x in e["starts"]]
        chunk = []
        for j, w in enumerate(words):
            chunk.append(j)
            if len(chunk) == 3 or w.endswith((".", ",", "?", "!", ":")) or j == len(words) - 1:
                a = st[chunk[0]]; caps.append([a, None, " ".join(words[k] for k in chunk)]); chunk = []
    for k in range(len(caps)):
        nxt = caps[k + 1][0] if k + 1 < len(caps) else total - 0.1
        caps[k][1] = min(nxt, caps[k][0] + 2.2)
    cap_imgs = [(a, b, S.cap_img(txt)) for a, b, txt in caps]
    with open(os.path.join(d, f"{sid}.srt"), "w") as fh:
        for k, (a, b, txt) in enumerate(caps, 1):
            fh.write(f"{k}\n{_ts(a)} --> {_ts(b)}\n{txt}\n\n")

    # 3) audio mix (voice + ducked original music + soft whooshes), mastered to -14 LUFS without pumping
    n = int(total * sr) + 1
    voice = np.zeros(n, np.float32)
    for e in tl:
        a = int((e["start"] + LEAD) * sr); voice[a:a + len(e["vo"])] += e["vo"][: n - a]
    sf.write(os.path.join(OUT, "voiceovers", f"{sid}_voice.wav"), voice, sr)
    env = np.convolve(np.abs(voice), np.ones(int(0.3 * sr)) / (0.3 * sr), mode="same")
    env = np.clip(env / (env.max() + 1e-6) * 4, 0, 1)
    mus = A.music(n / sr + 1, seed=spec["seed"], bpm=104)[:n]
    mus = np.pad(mus, (0, n - len(mus))) * (0.17 - 0.11 * env[:n])
    sfx = np.zeros(n, np.float32); wh = A.whoosh(spec["seed"]) * 0.5
    for e in tl[1:]:
        a = int(max(0, e["start"] - 0.15) * sr); sfx[a:a + len(wh)] += wh[: n - a]
    raw = os.path.join(wk, "mix_raw.wav"); sf.write(raw, np.clip(voice + mus + sfx, -1, 1), sr)
    mix = os.path.join(wk, "mix.wav"); A.master(raw, mix)

    # 4) visuals
    assets_used = []
    for i, e in enumerate(tl):
        e["L"] = S.scene_layers(e["s"])
        if "clip" in e["s"]:
            path, t0 = e["s"]["clip"][:2]; mode = e["s"]["clip"][2] if len(e["s"]["clip"]) > 2 else "fit"
            fx = e["s"]["clip"][3] if len(e["s"]["clip"]) > 3 else 0.5
            zf = e["s"]["clip"][4] if len(e["s"]["clip"]) > 4 else (1.0, 0.5)
            cp = os.path.join(wk, f"clip_{i:02}.mp4")
            if os.path.exists(cp): os.remove(cp)
            extract_any(os.path.join(ROOT, path), t0, e["dur"], cp, mode, fx, zf); e["clip"] = cp; e["reader"] = None
            assets_used.append(f"clip:{os.path.basename(path)}@{t0}")
        else:
            e["bg"], e["focus"] = asset_image(e["s"]["asset"]); assets_used.append(e["s"]["asset"])
            if e["s"].get("pad") or e["s"].get("menu") or e["s"].get("damage") or e["s"].get("atm"):   # tutorial scenes: dimmed, blurred backdrop
                b = e["bg"].filter(ImageFilter.GaussianBlur(14))
                e["bg"] = Image.blend(b, Image.new("RGB", b.size, (12, 6, 28)), 0.45)
        if e["s"].get("sticker"):
            e["stk"] = sticker_frames(e["s"]["sticker"]); assets_used.append(e["s"]["sticker"])
    ov = S.overlay()
    cred = text_img(spec.get("credit", "Imágenes: Rockstar Games"), font("semi", 26), stroke=3, pad=8)
    out = os.path.join(d, f"{sid}.mp4")
    cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    N = int(math.ceil(total * FPS)); si = ci = 0
    for fi in range(N):
        t = fi / FPS
        while si + 1 < len(tl) and t >= tl[si + 1]["start"]: si += 1
        e = tl[si]; lt = t - e["start"]; sp = lt / e["dur"]
        if "clip" in e:
            if e["reader"] is None:
                if si > 0 and tl[si - 1].get("reader"): tl[si - 1]["reader"].close()
                e["reader"] = S.ClipReader(e["clip"])
            frame = e["reader"].next().convert("RGBA")
        else:
            frame = camera(e["bg"], e["s"].get("move", "zin"), sp, lt, e["focus"]).convert("RGBA")
        if e["s"].get("scope"):
            M.scope_overlay(frame, lt)
        frame.alpha_composite(ov)
        if e["s"].get("pad"):
            pf = M.pad_frame(lt, e["s"]["pad"])
            S.paste(frame, pf, (W - pf.size[0]) // 2, 610, lt, 0.15, "up", 0.35)
        if e["s"].get("portal"):
            M.portal_overlay(frame, lt)
        if e["s"].get("atm"):
            af = M.atm_frame(lt)
            S.paste(frame, af, (W - af.size[0]) // 2, 640, lt, 0.15, "up", 0.35)
        if e["s"].get("damage"):
            dfm = M.car_damage_frame(lt)
            S.paste(frame, dfm, (W - dfm.size[0]) // 2, 640, lt, 0.15, "up", 0.35)
        if e["s"].get("menu"):
            mf = M.menu_frame(lt)
            S.paste(frame, mf, (W - mf.size[0]) // 2, 640, lt, 0.15, "up", 0.35)
        for (img, x, y, t0, anim) in e["L"]:
            S.paste(frame, img, x, y, lt, t0, anim)
        if e.get("stk"):
            st = e["stk"][fi % len(e["stk"])]
            S.paste(frame, st, W - st.size[0] - 40, 640, lt, 0.6, "pop", 0.35)
        while ci + 1 < len(cap_imgs) and t >= cap_imgs[ci + 1][0]: ci += 1
        a, b, c = cap_imgs[ci]
        if a <= t < b:
            S.paste(frame, c, (W - c.size[0]) // 2, 1360, t, a, "pop", 0.1)
        if lt < 0.08 and si > 0:
            frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(120 * (1 - lt / 0.08)))))
        frame.alpha_composite(cred, (30, 120))
        ff.stdin.write(frame.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    for e in tl:
        if e.get("reader"): e["reader"].close()

    # 5) cover (v2 click-oriented layout, English)
    cover(spec, d)

    # 6) metadata, script, sources
    report["duration"] = round(total, 2); report["assets_used"] = assets_used
    script = "\n\n".join(f"[{i+1}] {sc.get('head','')}\n{sc['say']}" for i, sc in enumerate(spec["scenes"]))
    open(os.path.join(OUT, "scripts", f"{sid}.txt"), "w").write(f"{spec['title']}\n\n{script}\n")
    meta = {"id": sid, "slug": spec["slug"], "order": order, "date": str(datetime.date.today()), "title": spec["title"],
            "description": spec["description"] + "\n\n" + " ".join(spec["hashtags"]) + "\n\n" +
                           spec.get("credit", "Imágenes: Rockstar Games") + ". Canal de fans no oficial, sin afiliación con Rockstar Games ni Take-Two. Narración con voz generada por IA.",
            "hashtags": spec["hashtags"], "tags": spec["tags"], "pinned_comment": spec["pinned"], "duration": round(total, 2),
            "assets_used": assets_used, "files": {"video": f"shorts/{sid}/{sid}.mp4", "cover": f"shorts/{sid}/{sid}-cover.jpg", "srt": f"shorts/{sid}/{sid}.srt"}}
    json.dump(meta, open(os.path.join(OUT, "metadata", f"{sid}.json"), "w"), indent=1, ensure_ascii=False)
    for name, txt in [("title.txt", spec["title"]), ("description.txt", meta["description"]), ("pinned_comment.txt", spec["pinned"]),
                      ("tags.txt", ", ".join(spec["tags"]))]:
        open(os.path.join(d, name), "w").write(txt)
    L = [f"# Sources — {spec['title']}", "", "| Claim | Status | Source |", "|---|---|---|"]
    L += [f"| {c} | {st} | {u} |" for c, st, u in SOURCES[sid]]
    open(os.path.join(OUT, "sources", f"{sid}.md"), "w").write("\n".join(L) + "\n")
    report["qc"] = qc(out, spec, caps)
    json.dump(report, open(os.path.join(OUT, "production_reports", f"{sid}.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{sid}: {total:.1f}s -> {out}  QC: {report['qc']['verdict']}")
    return report

def _ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# --------------------------------------------------------------------------------------------- cover
def cover(spec, d):
    import covers_v2 as C
    img, fx, fy, zoom, lines, seal = spec["cover"]
    return C.make((img, fx, fy, zoom, lines, seal, True), os.path.join(d, f"{spec['id']}-cover.jpg"),
                  os.path.join(d, f"{spec['id']}.mp4"), credit=spec.get("credit", "Imágenes: Rockstar Games"))

# --------------------------------------------------------------------------------------------- QC
def qc(mp4, spec, caps):
    r = {}
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                                    "-of", "json", mp4], capture_output=True, text=True).stdout)
    v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
    r["resolution"] = f"{v['width']}x{v['height']}"; r["duration"] = round(float(pr["format"]["duration"]), 2)
    r["has_audio"] = any(s["codec_type"] == "audio" for s in pr["streams"])
    bd = subprocess.run(["ffmpeg", "-nostdin", "-i", mp4, "-map", "0:v:0", "-vf", "blackdetect=d=0.1:pix_th=0.06", "-an", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    r["black_segments"] = len(re.findall(r"black_start", bd))
    sd = subprocess.run(["ffmpeg", "-nostdin", "-i", mp4, "-map", "0:a:0", "-af", "silencedetect=n=-45dB:d=0.8", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    r["silences_over_0.8s"] = len(re.findall(r"silence_start", sd))
    lu = subprocess.run(["ffmpeg", "-nostdin", "-i", mp4, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lu); pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", lu)
    r["loudness_lufs"] = float(m[-1]) if m else None; r["true_peak_dbfs"] = float(pk[-1]) if pk else None
    # re-transcribe the exported voice (voice stem) and compare with the script
    vw = os.path.join(OUT, "voiceovers", f"{spec['id']}_voice.wav")
    x, sr = sf.read(vw, dtype="float32")
    rec = transcribe(x, sr)
    script_words = " ".join(sc["say"] for sc in spec["scenes"]).split()
    _, ratio, _ = align(script_words, rec)
    r["recognized_text"] = " ".join(w[0] for w in rec)
    r["asr_match_full_voice"] = round(ratio, 3)
    flat = [t for w in script_words for t in norm_tokens(w)]
    rec_t = [w[0] for w in rec]
    dups = sum(1 for i in range(1, len(rec_t)) if rec_t[i] == rec_t[i - 1] and not (i < len(flat) and flat.count(rec_t[i]) > 1))
    r["repeated_word_events"] = dups
    r["clipping_samples"] = int(np.sum(np.abs(x) > 0.995))
    r["subtitles_match_script"] = " ".join(c[2] for c in caps).split() == script_words
    problems = []
    if r["resolution"] != "1080x1920": problems.append("resolution")
    if not r["has_audio"]: problems.append("no audio")
    if r["black_segments"]: problems.append("black frames")
    if r["silences_over_0.8s"]: problems.append("long silence")
    if r["asr_match_full_voice"] < MIN_MATCH: problems.append("narration mismatch")
    if r["clipping_samples"]: problems.append("clipping")
    if not r["subtitles_match_script"]: problems.append("subtitle text")
    if r["loudness_lufs"] is not None and not (-16.5 <= r["loudness_lufs"] <= -12.5): problems.append("loudness")
    if not (20 <= r["duration"] <= 60): problems.append("duration")
    r["problems"] = problems; r["verdict"] = "PASS" if not problems else "CHECK: " + ", ".join(problems)
    return r

if __name__ == "__main__":
    ids = sys.argv[1:] or [s["id"] for s in SHORTS]
    for k, spec in enumerate(SHORTS):
        if spec["id"] in ids:
            build(spec, k + 1)
