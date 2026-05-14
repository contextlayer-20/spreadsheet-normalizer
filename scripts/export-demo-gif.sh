#!/usr/bin/env bash
# Re-export a screen recording as a GIF for README.
#
# Why single-pass often looks bad:
#   ffmpeg -i x.webm -vf "fps=10,scale=800:-1" … → one global palette, heavy banding, very choppy motion.
# This script uses palettegen + paletteuse (two-pass in one filter graph) and higher fps.
#
# Depends: ffmpeg
# Input: WebM, MP4, MOV, …
#
# Optional environment (tune quality vs file size):
#   DEMO_GIF_FPS=18          # default 18; lower = smaller + choppier
#   DEMO_GIF_WIDTH=960       # default 960 px wide; lower = smaller
#   DEMO_GIF_START=0         # seek into source (seconds)
#   DEMO_GIF_DURATION=       # if set, only encode this many seconds (shrinks huge recordings)
#   DEMO_GIF_DITHER=floyd_steinberg  # or bayer; default floyd_steinberg (often smoother gradients)
#
# Example (trim ~30s for a README-sized GIF):
#   DEMO_GIF_DURATION=30 DEMO_GIF_START=5 ./scripts/export-demo-gif.sh demo-1.webm assets/demo.gif

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT="${1:?Usage: $0 INPUT.webm|mp4|mov [OUTPUT.gif]}"
OUTPUT="${2:-"${ROOT}/assets/demo.gif"}"

FPS="${DEMO_GIF_FPS:-18}"
W="${DEMO_GIF_WIDTH:-960}"
SS="${DEMO_GIF_START:-0}"
DITHER="${DEMO_GIF_DITHER:-floyd_steinberg}"

mkdir -p "$(dirname "${OUTPUT}")"

IN_ARGS=()
if [[ -n "${DEMO_GIF_DURATION:-}" ]]; then
  IN_ARGS=(-ss "${SS}" -t "${DEMO_GIF_DURATION}" -i "${INPUT}")
else
  if [[ "${SS}" != "0" && -n "${SS}" ]]; then
    IN_ARGS=(-ss "${SS}" -i "${INPUT}")
  else
    IN_ARGS=(-i "${INPUT}")
  fi
fi

# rgb24 before palettegen avoids “not sRGB” color surprises on some VP8/WebM captures.
FILTER="fps=${FPS},scale=${W}:-1:flags=lanczos,format=rgb24,split[s0][s1];\
[s0]palettegen=max_colors=256:stats_mode=full[p];\
[s1][p]paletteuse=dither=${DITHER}"

ffmpeg -y "${IN_ARGS[@]}" -vf "${FILTER}" -loop 0 "${OUTPUT}"

echo "Wrote ${OUTPUT}"
