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

# ================================================================== tanda 2: primeras impresiones (18/11)
FUENTES = ("Fuentes: reseñas de Kotaku, Forbes, GamesRadar, Vice, TheSixthAxis, Wccftech y Cultured Vultures; "
           "NZ Herald y Newsweek sobre los primeros jugadores en Nueva Zelanda.")
SHORTS += [
{"slug": "s4-ya-salio", "seed": 31,
 "title": "GTA 6 YA SALIÓ: esto dicen los primeros que lo juegan 🔥 #gta6 #shorts",
 "desc": "GTA 6 ya se está jugando en Nueva Zelanda. Esto dicen los primeros jugadores y las primeras reseñas.\n\n" + FUENTES,
 "tags": ["gta 6", "gta 6 ya salio", "gta 6 nueva zelanda", "gta 6 metacritic", "gta 6 primeras impresiones", "shorts"],
 "scenes": [
  {"img": "Vice_City_27", "fx": 0.5, "head": "GTA 6 YA SE ESTÁ JUGANDO",
   "say": "GTA 6 ya salió en Nueva Zelanda, y los primeros jugadores ya están en Leonida. Esto es lo que dicen."},
  {"img": "Jason_and_Lucia_16", "fx": 0.45, "head": "UN FESTÍN VISUAL",
   "say": "Lo primero que comentan son los gráficos. Un streamer neozelandés lo llamó un festín para los ojos."},
  {"img": "Jason_Duval_19", "fx": 0.84, "head": "CONDUCIR SE SIENTE BRUTAL",
   "say": "Lo segundo, la conducción. Dicen que los coches se sienten muy suaves, tanto en la carretera como en la arena de la playa."},
  {"img": "Vice_City_15", "fx": 0.5, "head": "LA CRÍTICA, RENDIDA", "big": "99", "label": "METACRITIC",
   "say": "Y la crítica está de acuerdo. En sus primeras horas, GTA 6 llegó a noventa y nueve en Metacritic, empatando el récord histórico de Zelda Ocarina of Time."},
  {"img": "Jason_and_Lucia_20", "fx": 0.45, "head": "OJO CON EL TRUCO", "chip": "CAMBIAR LA REGIÓN A NUEVA ZELANDA",
   "say": "Ojo: mucha gente está jugando antes cambiando su región a Nueva Zelanda. Las condiciones de PlayStation no lo permiten, y te arriesgas a una sanción."},
  {"img": "Jason_and_Lucia_18", "fx": 0.62, "head": "¿LO JUEGAS ESTA NOCHE?",
   "say": "En América se desbloquea esta noche, a tu medianoche. ¿Lo vas a jugar en cuanto salga? Sígueme para más."},
 ]},
{"slug": "s5-como-se-juega", "seed": 32,
 "title": "¿Cómo se SIENTE jugar GTA 6? Conducción y disparos 🎮 #gta6 #shorts",
 "desc": "Cómo se conduce y cómo se dispara en GTA 6, según las primeras reseñas y los que ya lo están jugando.\n\n" + FUENTES,
 "tags": ["gta 6", "gta 6 gameplay", "gta 6 conduccion", "gta 6 disparos", "como se juega gta 6", "shorts"],
 "scenes": [
  {"img": "Jason_Duval_17", "fx": 0.45, "head": "¿CÓMO SE JUEGA GTA 6?",
   "say": "¿Cómo se siente jugar GTA 6? Junté lo que dicen las primeras reseñas y los que ya lo están jugando."},
  {"img": "Jason_Duval_19", "fx": 0.84, "head": "CONDUCCIÓN", "chip": "ENTRE GTA IV Y GTA V",
   "say": "La conducción está entre GTA cuatro y GTA cinco. Los coches tienen más peso, más física y más daños, pero son menos difíciles que en GTA cuatro."},
  {"img": "Vice_City_24", "fx": 0.33, "head": "UNA APP PARA ROBAR COCHES",
   "say": "Y en el teléfono hay una app que escanea los coches, para saber cuáles son más fáciles de robar."},
  {"img": "Jason_Duval_16", "fx": 0.5, "head": "DISPAROS", "chip": "HAY QUE APUNTAR DE VERDAD",
   "say": "En los tiroteos, se acabó cubrirte y acertar casi sin apuntar. Aquí tienes que apuntar de verdad, y cada arma se siente distinta."},
  {"img": "Lucia_Caminos_13", "fx": 0.45, "head": "LO QUE CUESTA",
   "say": "Eso sí, varias reseñas dicen que las automáticas son más difíciles de controlar, y que el cuerpo a cuerpo se siente algo rígido."},
  {"img": "Jason_and_Lucia_17", "fx": 0.5, "head": "MÁS REALISTA QUE GTA 5",
   "say": "En resumen: más realista y con más peso que GTA cinco. Al principio cuesta un poco, pero luego engancha. Sígueme para más."},
 ]},
{"slug": "s6-policia", "seed": 33,
 "title": "La POLICÍA de GTA 6 es otro nivel 🚨 #gta6 #shorts",
 "desc": "Así funciona la policía en GTA 6: testigos, cámaras, tu descripción y hasta 6 estrellas. Y cómo evitar que te reconozcan.\n\n" + FUENTES,
 "tags": ["gta 6", "gta 6 policia", "gta 6 estrellas", "gta 6 wanted", "gta 6 trucos", "shorts"],
 "scenes": [
  {"img": "Jason_Duval_18", "fx": 0.55, "head": "LA POLICÍA YA NO ES TONTA",
   "say": "La policía de GTA 6 no funciona como en GTA cinco. Si no sabes esto, te van a atrapar enseguida."},
  {"img": "Lucia_Caminos_14", "fx": 0.55, "head": "NECESITAN TESTIGOS",
   "say": "Para empezar, un crimen solo se denuncia si alguien lo ve, si salta una alarma o si te graba una cámara de seguridad."},
  {"img": "Vice_City_22", "fx": 0.5, "head": "LLEGAN CON TU DESCRIPCIÓN", "chip": "CARA · ROPA · COCHE",
   "say": "Y los policías llegan con tu descripción: tu cara, tu ropa, tu coche, e incluso el aspecto de tu pareja."},
  {"img": "Jason_and_Lucia_15", "fx": 0.45, "head": "EL TRUCO: TÁPATE",
   "say": "El truco: tapa tu cara con máscaras, gorras o bandanas, y cambia de ropa y de coche. Y no lleves el arma a la vista, porque eso también levanta sospechas."},
  {"img": "Jason_Duval_11", "fx": 0.5, "head": "VUELVEN LAS", "big": "6", "label": "ESTRELLAS DE BÚSQUEDA",
   "say": "Y vuelven las seis estrellas. Algunas reseñas dicen que la presión policial puede llegar a agobiar."},
  {"img": "Vice_City_17", "fx": 0.5, "head": "¿YA TE ESCAPASTE?",
   "say": "¿Ya te escapaste de la policía en Leonida? Cuéntame cómo en los comentarios."},
 ]},
{"slug": "s7-novedades", "seed": 34,
 "title": "5 cosas NUEVAS de GTA 6 que no había en GTA 5 🆕 #gta6 #shorts",
 "desc": "Cinco novedades de GTA 6 confirmadas por las primeras reseñas: pareja, perfil criminal, robos, redes sociales y reintentos.\n\n" + FUENTES,
 "tags": ["gta 6", "gta 6 novedades", "gta 6 vs gta 5", "gta 6 perfil criminal", "gta 6 nuevo", "shorts"],
 "scenes": [
  {"img": "Jason_and_Lucia_16", "fx": 0.45, "head": "5 COSAS NUEVAS DE GTA 6",
   "say": "Cinco cosas nuevas de GTA 6 que no existían en GTA cinco."},
  {"img": "Jason_and_Lucia_20", "fx": 0.4, "head": "1. TU PAREJA",
   "say": "Una: tu pareja. Con el gatillo izquierdo ya no solo apuntas, también puedes tomarla de la mano. Y por el teléfono le puedes escribir y llamar."},
  {"img": "Jason_Duval_12", "fx": 0.55, "head": "2. PERFIL CRIMINAL",
   "say": "Dos: el perfil criminal. El juego registra si eres compasivo y dejas a la gente inconsciente, o si eres un asesino a sangre fría."},
  {"img": "Jason_and_Lucia_15", "fx": 0.45, "head": "3. ROBOS CON PLAN",
   "say": "Tres: robar una tienda es mucho más elaborado, y puedes hacer reconocimiento antes de entrar."},
  {"img": "Lucia_Caminos_11", "fx": 0.6, "head": "4. RED SOCIAL",
   "say": "Cuatro: en el teléfono hay una red social al estilo Instagram."},
  {"img": "Jason_Duval_13", "fx": 0.5, "head": "5. REINTENTAR", "chip": "DESDE EL ÚLTIMO PUNTO DE CONTROL",
   "say": "Y cinco: ahora puedes reiniciar una misión tú mismo desde el último punto de control. ¿Cuál te gusta más? Sígueme para más."},
 ]},
{"slug": "s8-lo-malo", "seed": 35,
 "title": "Lo MALO de GTA 6 (según las reseñas) 😬 #gta6 #shorts",
 "desc": "GTA 6 tiene un 99 en Metacritic, pero no es perfecto: 30 fps, un arranque lento, mucho realismo y un cuerpo a cuerpo rígido.\n\n" + FUENTES,
 "tags": ["gta 6", "gta 6 review", "gta 6 30 fps", "gta 6 malo", "gta 6 criticas", "shorts"],
 "scenes": [
  {"img": "Jason_Duval_14", "fx": 0.55, "head": "LO MALO DE GTA 6",
   "say": "GTA 6 tiene un noventa y nueve en Metacritic, pero no es perfecto. Esto es lo que critican las reseñas."},
  {"img": "Jason_Duval_11", "fx": 0.5, "head": "1. RENDIMIENTO", "big": "30 FPS", "label": "INCLUSO EN PS5 PRO",
   "say": "Uno: va a treinta cuadros por segundo, incluso en PS5 Pro, y no hay modo de sesenta. En la PS5 normal, algunas reseñas notan bajones en las persecuciones."},
  {"img": "Grassrivers_08", "fx": 0.5, "head": "2. EMPIEZA LENTO",
   "say": "Dos: el ritmo. Las primeras horas son lentas, y la historia se toma su tiempo para arrancar."},
  {"img": "Jason_Duval_15", "fx": 0.5, "head": "3. MUY REALISTA", "chip": "COCHES FRÁGILES · FACTURAS · RUTINAS",
   "say": "Tres: el realismo. Coches más frágiles, facturas de reparación y tareas diarias. Si vienes directo de GTA cinco, cuesta acostumbrarse."},
  {"img": "Jason_Duval_12", "fx": 0.55, "head": "4. CUERPO A CUERPO",
   "say": "Y cuatro: algunas reseñas dicen que las peleas cuerpo a cuerpo se sienten rígidas."},
  {"img": "Jason_and_Lucia_17", "fx": 0.5, "head": "¿IMPORTA?",
   "say": "¿Importa? Para la mayoría, no: aun así, es uno de los juegos mejor valorados de la historia. ¿A ti qué te molesta más? Te leo."},
 ]},
]

# ================================================================== tanda 3: lanzamiento mundial (19/11)
FUENTES3 = ("Fuentes: Insider Gaming, Game Rant, Beebom (misión Pipework); Sensor Tower vía Game Rant y Yahoo Finance (ventas, "
            "estimaciones no oficiales); GameSpot, Engadget y Kotaku (secretos y curiosidades del día de lanzamiento).")
SHORTS += [
{"slug": "s9-mandy", "seed": 41,
 "title": "¿MANDY es una ASESINA? La misión viral de GTA 6 🔪 #gta6 #shorts",
 "desc": "Pipework, la misión de Jason y Mandy que se hizo viral el día de lanzamiento de GTA 6, y la teoría que tiene a todos hablando. Contiene spoilers del capítulo 1.\n\n" + FUENTES3,
 "tags": ["gta 6", "gta 6 mandy", "mandy gta 6", "pipework gta 6", "gta 6 teoria", "gta 6 jason", "gta 6 mision", "gtavi", "shorts"],
 "scenes": [
  {"img": "Leonida_Keys_03", "fx": 0.5, "head": "¿MANDY ES UNA ASESINA?", "chip": "SPOILER · CAPÍTULO 1",
   "say": "La misión de GTA 6 de la que todo el mundo habla se llama Pipework. Y la protagonista no es Jason: es Mandy."},
  {"img": "Brian_Heder_03", "fx": 0.55, "head": "BRIAN TE MANDA A COBRAR",
   "say": "Brian manda a Jason a cobrarle el alquiler a Mandy, una de sus inquilinas en los Cayos. Pero ella no paga hasta que alguien le arregle el fregadero."},
  {"img": "Leonida_Keys_04", "fx": 0.5, "head": "JASON DESTAPA EL FREGADERO",
   "say": "Así que Jason se pone a destaparlo. Y dentro de la tubería aparece algo."},
  {"img": "Leonida_Keys_05", "fx": 0.5, "head": "¿UN DEDO HUMANO?",
   "say": "Mandy se lo quita de las manos y lo esconde sin dar explicaciones. Muchos jugadores juran que era un dedo humano."},
  {"img": "Vice_City_22", "fx": 0.5, "head": "Y SU COCHE...", "chip": "CUCHILLO · LEJÍA · CINTA",
   "say": "Y en su coche hay un cuchillo de carnicero, lejía y cinta americana. Demasiada casualidad, ¿no?"},
  {"img": "Leonida_Keys_02", "fx": 0.6, "head": "¿TEORÍA O VERDAD?",
   "say": "Ojo: Rockstar no lo ha confirmado, y la historia no lo aclara. ¿Tú qué crees? ¿Mandy es una asesina? Te leo."},
 ]},
{"slug": "s10-ventas", "seed": 42,
 "title": "GTA 6 ROMPIÓ el récord: el DOBLE que GTA 5 💰 #gta6 #shorts",
 "desc": "Las primeras estimaciones de ventas de GTA 6 en su día de lanzamiento, comparadas con GTA V. Cifras de Sensor Tower, todavía no oficiales.\n\n" + FUENTES3,
 "tags": ["gta 6", "gta 6 ventas", "gta 6 record", "gta 6 vs gta 5", "rockstar", "take two", "gtavi", "shorts"],
 "scenes": [
  {"img": "Vice_City_27", "fx": 0.5, "head": "GTA 6 ROMPIÓ EL RÉCORD",
   "say": "GTA 6 acaba de salir y ya es historia. Mira estos números."},
  {"img": "Vice_City_13", "fx": 0.5, "head": "SU PRIMER DÍA", "big": "$1.650 M", "label": "ESTIMACIÓN DE SENSOR TOWER",
   "say": "Según la firma Sensor Tower, GTA 6 generó unos mil seiscientos cincuenta millones de dólares en su día de lanzamiento."},
  {"img": "Vice_City_15", "fx": 0.5, "head": "EN UN SOLO DÍA", "big": "17 M", "label": "COPIAS (ESTIMACIÓN)",
   "say": "Eso serían más de diecisiete millones de copias en un solo día."},
  {"img": "Vice_City_24", "fx": 0.4, "head": "EL DOBLE QUE GTA V",
   "rows": [["GTA V · 2013", "$815 M"], ["GTA 6 · 2026", "$1.650 M"]],
   "say": "Para comparar: GTA cinco hizo ochocientos quince millones en su primer día, en dos mil trece. GTA 6 casi lo duplica."},
  {"img": "Vice_City_26", "fx": 0.5, "head": "LA BOLSA, DE FIESTA",
   "say": "Y las acciones de Take-Two, la empresa dueña de Rockstar, subieron con el lanzamiento."},
  {"img": "Jason_and_Lucia_16", "fx": 0.45, "head": "FALTA EL DATO OFICIAL",
   "say": "Ojo: son estimaciones. Take-Two todavía no ha dado cifras oficiales. Sígueme y te aviso en cuanto salgan."},
 ]},
{"slug": "s11-secretos", "seed": 43,
 "title": "5 SECRETOS que ya encontraron en GTA 6 🥚 #gta6 #shorts",
 "desc": "Los primeros easter eggs y secretos que los jugadores encontraron en GTA 6 el día de su lanzamiento.\n\n" + FUENTES3,
 "tags": ["gta 6", "gta 6 secretos", "gta 6 easter eggs", "gta 6 bigfoot", "gta 6 curiosidades", "gtavi", "shorts"],
 "scenes": [
  {"img": "Vice_City_27", "fx": 0.5, "head": "5 SECRETOS DE GTA 6",
   "say": "GTA 6 lleva solo unas horas a la venta y los jugadores ya encontraron estos secretos."},
  {"img": "Vice_City_15", "fx": 0.5, "head": "1. EL HUEVO DE PASCUA",
   "say": "Uno: sube a la torre más alta de Vice City, unos siete minutos escalando, y en un nido hay un huevo de Pascua pintado. Lo puedes lanzar a la gente de abajo."},
  {"img": "Grassrivers_08", "fx": 0.5, "head": "2. BIGFOOT EXISTE",
   "say": "Dos: Bigfoot existe, y tiene hasta una misión. Lo encuentras en Gullet Marsh."},
  {"img": "Leonida_Keys_07", "fx": 0.5, "head": "3. EL PERRO EN MOTO DE AGUA",
   "say": "Tres: si nadas demasiado lejos mar adentro, aparece un perro en moto acuática."},
  {"img": "Vice_City_26", "fx": 0.5, "head": "4. EL PISO DE DEXTER",
   "say": "Cuatro: en Washington Island hay un guiño al apartamento de Dexter Morgan, el asesino de la serie Dexter."},
  {"img": "Vice_City_22", "fx": 0.5, "head": "5. LA CASA CONSPIRANOICA",
   "say": "Y cinco: en Belville hay una casa llena de notas de un conspiranoico, con guiños a San Andreas. ¿Cuál vas a buscar primero?"},
 ]},
{"slug": "s12-cosas-raras", "seed": 44,
 "title": "Cosas RARAS que descubrieron en GTA 6 🤨 #gta6 #shorts",
 "desc": "Detalles curiosos que los jugadores están descubriendo en GTA 6: trucos, calcetines, el móvil al volante y más.\n\n" + FUENTES3,
 "tags": ["gta 6", "gta 6 trucos", "gta 6 curiosidades", "gta 6 detalles", "gta 6 cheats", "gtavi", "shorts"],
 "scenes": [
  {"img": "Jason_Duval_19", "fx": 0.84, "head": "COSAS RARAS DE GTA 6",
   "say": "Cosas raras de GTA 6 que la gente está descubriendo hoy."},
  {"img": "Jason_Duval_15", "fx": 0.5, "head": "1. NO HAY TRUCOS... AÚN", "chip": "HASTA TERMINAR LA HISTORIA",
   "say": "Una: no puedes usar trucos hasta terminar la historia. Nada de vida infinita en tu primera partida."},
  {"img": "Jason_Duval_17", "fx": 0.45, "head": "2. CALCETINES CON CHANCLAS", "chip": "PROHIBIDO",
   "say": "Dos: Jason no puede ponerse calcetines con chanclas. Rockstar tiene sus límites."},
  {"img": "Lucia_Caminos_12", "fx": 0.45, "head": "3. EL MÓVIL TE DISTRAE",
   "say": "Tres: si usas el teléfono mientras conduces, el coche se vuelve más difícil de controlar."},
  {"img": "Jason_Duval_14", "fx": 0.55, "head": "4. FACTURAS DEL TALLER",
   "say": "Y cuatro: los coches son más frágiles, y repararlos cuesta dinero de verdad."},
  {"img": "Jason_and_Lucia_17", "fx": 0.5, "head": "¿Y TÚ QUÉ ENCONTRASTE?",
   "say": "¿Qué otra cosa rara encontraste tú? Cuéntamelo en los comentarios."},
 ]},
{"slug": "s13-consejos", "seed": 45,
 "title": "5 consejos para tu PRIMER DÍA en GTA 6 ✅ #gta6 #shorts",
 "desc": "Cinco consejos para empezar GTA 6 sin que te atrape la policía ni pierdas el progreso.\n\n" + FUENTES + "\n" + FUENTES3,
 "tags": ["gta 6", "gta 6 consejos", "gta 6 tips", "gta 6 principiantes", "gta 6 guia", "gtavi", "shorts"],
 "scenes": [
  {"img": "Jason_and_Lucia_20", "fx": 0.45, "head": "TU PRIMER DÍA EN GTA 6",
   "say": "¿Vas a empezar GTA 6 hoy? Cinco consejos que te van a ahorrar disgustos."},
  {"img": "Jason_and_Lucia_15", "fx": 0.45, "head": "1. TÁPATE LA CARA",
   "say": "Uno: antes de un delito, ponte máscara, gorra o bandana. La policía busca tu cara, tu ropa y tu coche."},
  {"img": "Jason_Duval_18", "fx": 0.55, "head": "2. ARMA GUARDADA",
   "say": "Dos: no lleves el arma a la vista por la calle, porque levanta sospechas."},
  {"img": "Vice_City_24", "fx": 0.33, "head": "3. ESCANEA LOS COCHES",
   "say": "Tres: usa la app del teléfono que escanea coches, para saber cuáles son fáciles de robar."},
  {"img": "Jason_Duval_13", "fx": 0.5, "head": "4. REINTENTA LA MISIÓN",
   "say": "Cuatro: si una misión sale mal, puedes reiniciarla tú mismo desde el último punto de control."},
  {"img": "Jason_Duval_19", "fx": 0.84, "head": "5. SUELTA EL MÓVIL",
   "say": "Y cinco: no uses el móvil mientras conduces. Y recuerda: los trucos llegan al terminar la historia. Sígueme para más."},
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

EXTENDED_LOOK = "https://media-rockstargames-com.akamaized.net/VI/downloads/videos/GTAVI_An_Extended_Look/GTAVI_An_Extended_Look.mp4"
GAMEPLAY = {  # slug -> [(segundo de inicio en "An Extended Look", foco horizontal 0..1)] una por escena
    "s4-ya-salio": [(745, .5), (460, .55), (765, .5), (1045, .45), (805, .6), (1265, .5)],
    "s5-como-se-juega": [(925, .45), (505, .5), (1090, .5), (285, .55), (865, .35), (1065, .5)],
    "s6-policia": [(945, .45), (731, .5), (1105, .5), (245, .5), (930, .45), (1225, .5)],
    "s7-novedades": [(685, .5), (825, .5), (565, .4), (705, .5), (222, .55), (1325, .5)],
    "s8-lo-malo": [(705, .5), (1225, .5), (165, .5), (545, .4), (565, .45), (1045, .5)],
    # None = esa escena usa la imagen fija de "img"
}

def extract_clip(t0, fx, dur, out):
    """Recorta un tramo del gameplay oficial (4K) a vertical 1080x1920, 30 fps, sin audio."""
    if os.path.exists(out) and os.path.getsize(out) > 10000: return
    px = os.environ.get("HTTPS_PROXY", "")
    vf = (f"crop=ih*9/16:ih:max(0\\,min(iw-ih*9/16\\,iw*{fx}-ih*9/32)):0,scale={W}:{H}:flags=lanczos,fps={FPS},"
          "eq=saturation=1.08:contrast=1.03")
    cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error"] + (["-http_proxy", px, "-ca_file", "/root/.ccr/ca-bundle.crt"] if px else []) + \
          ["-ss", str(t0), "-i", EXTENDED_LOOK, "-t", f"{dur + 0.3:.2f}", "-an", "-vf", vf, "-c:v", "libx264", "-crf", "16", "-preset", "fast", out]
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL, timeout=900)

class ClipReader:
    def __init__(self, path):
        self.p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
        self.last = None
    def next(self):
        buf = self.p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = Image.frombytes("RGB", (W, H), buf)
        return self.last
    def close(self):
        try: self.p.kill()
        except Exception: pass

def build(slug):
    sh = next(x for x in SHORTS if x["slug"] == slug)
    od = os.path.join(OUT, slug); wk = os.path.join(od, "_work"); os.makedirs(wk, exist_ok=True)
    A.SPEED = 1.06
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
    raw = os.path.join(wk, "mix_raw.wav"); sf.write(raw, mix, A.SR)
    mw = os.path.join(wk, "mix.wav"); A.master(raw, mw)
    # imagen
    clips = GAMEPLAY.get(slug)
    for i, e in enumerate(tl):
        e["L"] = scene_layers(e["s"])
        if clips and clips[i]:
            cp = os.path.join(wk, f"clip_{i:02}.mp4")
            extract_clip(clips[i][0], clips[i][1], e["dur"], cp)
            e["clip"] = cp; e["reader"] = None
        else:
            e["bg"] = load_bg(e["s"]["img"])
    ov = overlay()
    cred = text_img("Gameplay e imágenes: Rockstar Games" if clips else CREDIT, font("semi", 26), stroke=3, pad=8)
    handle = text_img("@LeonidaDiario", font("black", 34), fill=WHITE, stroke=4, pad=8)
    out = os.path.join(od, slug + ".mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", mw, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
           "-shortest", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    N = int(math.ceil(total * FPS)); si = 0; ci = 0
    for fi in range(N):
        t = fi / FPS
        while si + 1 < len(tl) and t >= tl[si + 1]["start"]: si += 1
        e = tl[si]; lt = t - e["start"]; sp = lt / e["dur"]
        if "clip" in e:
            if e["reader"] is None:
                if si > 0 and tl[si - 1].get("reader"): tl[si - 1]["reader"].close()
                e["reader"] = ClipReader(e["clip"])
            frame = e["reader"].next().convert("RGBA")
        else:
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
    for e in tl:
        if e.get("reader"): e["reader"].close()
    with open(os.path.join(od, "titulo.txt"), "w") as f: f.write(sh["title"])
    with open(os.path.join(od, "descripcion.txt"), "w") as f:
        src = ("Gameplay: \"Grand Theft Auto VI: An Extended Look\" (Rockstar Games, descarga oficial)." if clips
               else "Imágenes: Rockstar Games (web oficial de GTA VI).")
        f.write(sh["desc"] + "\n\n" + src + " Canal de fans no oficial, sin afiliación con "
                "Rockstar Games ni Take-Two. Voz sintética.\n\n#GTA6 #GTAVI #Shorts")
    with open(os.path.join(od, "tags.txt"), "w") as f: f.write(", ".join(sh["tags"]))
    print(f"{slug}: {total:.1f}s -> {out}")

if __name__ == "__main__":
    build(sys.argv[1])
