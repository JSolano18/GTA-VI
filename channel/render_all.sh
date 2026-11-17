#!/bin/bash
# Renderiza los 10 videos (3 en paralelo). Uso: bash channel/render_all.sh
cd "$(dirname "$0")/.."
ls -1 output 2>/dev/null >/dev/null
python3 -c "import sys; sys.path.insert(0,'channel'); from videos import VIDEOS; print('\n'.join(v['slug'] for v in VIDEOS))" \
 | xargs -P 3 -I{} sh -c 'python3 channel/render.py {} > output/log-{}.txt 2>&1 && echo OK {} || echo FAIL {}'
