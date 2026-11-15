#!/usr/bin/env bash
# One-time setup in a fresh session: Python packages (including Playwright for Python if missing), the preinstalled
# Chromium, the free Kokoro voice (from GitHub), and the orchestral soundfont. Creates studio/py = the Python to use.
set -e
cd "$(dirname "$0")"
PY=""
for p in /usr/bin/python3 python3 /usr/local/bin/python3; do
  if command -v "$p" >/dev/null 2>&1 && "$p" -c "import playwright" 2>/dev/null; then PY=$(command -v "$p"); break; fi
done
if [ -z "$PY" ]; then   # no Python Playwright yet: install the library only (the browser is already on the machine)
  for p in /usr/bin/python3 python3 /usr/local/bin/python3; do
    if command -v "$p" >/dev/null 2>&1 && "$p" -m pip --version >/dev/null 2>&1; then PY=$(command -v "$p"); break; fi
  done
  [ -n "$PY" ] || { echo "No Python with pip found"; exit 1; }
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 "$PY" -m pip install -q --break-system-packages playwright >/dev/null 2>&1 || PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 "$PY" -m pip install -q playwright
fi
printf '#!/usr/bin/env bash\nexec %s "$@"\n' "$PY" > py && chmod +x py
# the preinstalled Chromium (newest build), used if Playwright's own browser version isn't present
CH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux*/chrome /opt/pw-browsers/chromium/chrome-linux*/chrome "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux*/chrome 2>/dev/null | sort -V | tail -1 || true)
[ -n "$CH" ] && echo "$CH" > .chromium
"$PY" -m pip install -q --break-system-packages kokoro-onnx soundfile numpy >/dev/null 2>&1 || "$PY" -m pip install -q kokoro-onnx soundfile numpy
mkdir -p tts
[ -s tts/kokoro.onnx ] || curl -sSL -o tts/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s tts/voices.bin ] || curl -sSL -o tts/voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
command -v ffmpeg >/dev/null || (apt-get install -y -q ffmpeg >/dev/null 2>&1 || true)

"$PY" -c "import kokoro_onnx, soundfile; print('setup ok with', '$PY')"
# Smoke & Borders orchestral score: FluidSynth + the FluidR3 GM soundfont (MIT, Frank Wen), 148 MB, kept out of git
"$PY" -m pip install -q --break-system-packages pyfluidsynth 2>/dev/null || "$PY" -m pip install -q pyfluidsynth
"$PY" -m pip install -q --break-system-packages scrapetube pillow 2>/dev/null || "$PY" -m pip install -q scrapetube pillow   # smoke/scout.py fallback + contact sheets
python3 -c "import ctypes.util,sys; sys.exit(0 if ctypes.util.find_library('fluidsynth') else 1)" || (apt-get install -y -q libfluidsynth3 >/dev/null 2>&1 || (apt-get update -qq >/dev/null 2>&1 && apt-get install -y -q libfluidsynth3 >/dev/null 2>&1) || true)
mkdir -p music && [ -s music/FluidR3_GM.sf2 ] && head -c 4 music/FluidR3_GM.sf2 | grep -q RIFF || curl -sL -o music/FluidR3_GM.sf2 https://media.githubusercontent.com/media/Jacalz/fluid-soundfont/master/original-files/FluidR3_GM.sf2
"$PY" -c "import fluidsynth; print('score ok')"
# film-style episodes: archival photos cut into layers (smoke/photo.py, smoke/portrait.py)
"$PY" -m pip install -q --break-system-packages rembg onnxruntime opencv-python-headless scipy 2>/dev/null || "$PY" -m pip install -q rembg onnxruntime opencv-python-headless scipy
