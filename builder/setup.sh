#!/bin/bash
# one-time setup for a fresh session
set -e
B=$(cd "$(dirname "$0")" && pwd)
mkdir -p ~/.fonts && cp "$B/Anton-Regular.ttf" ~/.fonts/ && fc-cache -f >/dev/null 2>&1 || true
pip install -q --break-system-packages rembg onnxruntime opencv-python-headless pillow numpy playwright 2>&1 | tail -1
python3 -m playwright install --with-deps chromium >/dev/null 2>&1 || python3 -m playwright install chromium
which ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg >/dev/null)
echo setup-ok
