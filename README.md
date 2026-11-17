# Leonida Diario — canal de GTA 6

10 videos listos para subir el jueves 19 de noviembre de 2026, día de lanzamiento de GTA 6.

- **Videos, miniaturas, subtítulos, títulos, descripciones y tags:** `output/<video>/`
- **Orden y horas de subida:** [`PLAN_DE_SUBIDA.md`](PLAN_DE_SUBIDA.md)
- **Datos que revisar antes de publicar:** [`FACT_CHECK.md`](FACT_CHECK.md)
- **Arte del canal (avatar y banner):** `output/canal/`

## Cómo se hacen

Todo se genera desde los guiones en `channel/videos.py`:

| Pieza | Herramienta |
|---|---|
| Voz | Kokoro TTS (local, voz `em_alex`) |
| Música y efectos | Synthwave original generado con numpy (`channel/audio.py`) |
| Imágenes y animación | Arte procedural con Pillow (`channel/visuals.py`, `channel/render.py`) |
| Montaje | ffmpeg (H.264 1080p30, AAC, -14 LUFS) |

Para regenerar un video tras editar su guion: `python3 channel/render.py 06-mapa-leonida`.
Para todos: `bash channel/render_all.sh`, y luego `python3 channel/publish_kit.py`.

Los videos (.mp4, menos de 35 MB cada uno) van en el propio repositorio.
