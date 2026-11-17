# Plan de subida — jueves 19 de noviembre de 2026

Programa los videos en YouTube Studio como **Programado** (no Público) el miércoles por la noche. Horas en tu hora local. El orden sigue la intención de búsqueda del día: primero lo urgente (hora, estafas, plataformas, espacio), después lo que se busca jugando (consejos, mapa, personajes) y al final lo evergreen.

| # | Hora | Video | Duración |
|---|---|---|---|
| 1 | 00:05 | GTA 6: HORA EXACTA de lanzamiento, precarga y qué hacer si NO te deja jugar | 2:18 |
| 2 | 00:10 | CUIDADO: las ESTAFAS de GTA 6 (descargas gratis, APK y claves falsas) | 1:36 |
| 3 | 07:00 | ¿GTA 6 en PS4, Xbox One o PC? Las PLATAFORMAS explicadas | 1:32 |
| 4 | 08:00 | ¿Cuánto pesa GTA 6? Cómo liberar ESPACIO en PS5 y Xbox Series | 1:43 |
| 5 | 10:00 | GTA 6: ¿Físico o DIGITAL? Guía para comprarlo sin errores | 1:36 |
| 6 | 12:00 | GTA 6: 10 cosas que DEBES hacer en tus primeras horas | 1:38 |
| 7 | 14:00 | Mapa de GTA 6: las 6 REGIONES de Leonida explicadas | 1:49 |
| 8 | 16:00 | Personajes de GTA 6: QUIÉN ES QUIÉN (Jason, Lucia y compañía) | 1:33 |
| 9 | 18:00 | ¿Cuándo sale GTA 6 en PC? Lo que nos dice la HISTORIA de Rockstar | 1:42 |
| 10 | 20:00 | La historia de GTA en 2 minutos: de 1997 a LEONIDA | 1:50 |

## Por cada video

1. Sube `output/<video>/<video>.mp4`.
2. Título: `titulo.txt`. Descripción: `descripcion.txt` (ya trae capítulos). Etiquetas: `tags.txt`.
3. Miniatura: `<video>-miniatura.jpg` (1280×720).
4. Subtítulos: sube `<video>.srt` en *Subtítulos → Subir archivo → Con sincronización*. Idioma: español.
5. Pantalla final: los últimos ~15 s tienen dos huecos a la derecha ("SIGUIENTE VIDEO" y "LISTA GTA 6"). Pon ahí *Video → Mejor para el espectador* y *Lista de reproducción → GTA 6*. El botón de suscribirse va sobre el botón rojo.
6. Lista de reproducción: añade los 10 a una lista llamada **GTA 6 — Todo lo que necesitas saber**.
7. Divulgación: en *Contenido alterado o sintético* marca **Sí**, porque la voz es sintética (generada por IA).
8. Categoría: Videojuegos. Audiencia: no es contenido para niños.

## Antes de programar (miércoles por la noche)

Revisa `FACT_CHECK.md`. Si Rockstar cambió algo (hora, precio, tamaño), dime qué y regenero el video afectado en unos minutos (`python3 channel/render.py <video>`).

## Arte del canal

- Foto de perfil: `output/canal/avatar.png` (800×800)
- Banner: `output/canal/banner.png` (2560×1440, zona segura centrada 1546×423)
- Nombre sugerido: **Leonida Diario** (@LeonidaDiario) — comprueba que el identificador esté libre.
- Descripción del canal: "Guías, noticias y secretos de GTA 6 en español. Lo que tienes que saber de GTA 6 cada día, sin relleno y sin spoilers. Canal de fans no oficial. No estamos afiliados a Rockstar Games ni a Take-Two Interactive. Grand Theft Auto y GTA son marcas de sus respectivos dueños. Todas las imágenes, animaciones y música de este video son originales."
