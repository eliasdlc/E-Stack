#!/usr/bin/env bash
# export.sh FILE.drawio [png|pdf|svg] [OUT]
# Exports a draw.io file inside gamescope's headless Wayland session, so no
# window ever opens on Elias's screen (verified on the laptop, 15 Oct 2026).
# The output defaults to the input's name with the new extension.
set -euo pipefail
in=$(readlink -f "$1"); fmt=${2:-png}; out=${3:-${in%.*}.$fmt}
out=$(readlink -f "$(dirname "$out")")/$(basename "$out")
app=${DRAWIO:-$HOME/.local/bin/drawio.AppImage}
[[ -x $app ]] || { echo "export: draw.io AppImage not found at $app" >&2; exit 2; }
cmd=("$app" --no-sandbox -x -f "$fmt" -o "$out")
[[ $fmt == pdf ]] && cmd+=(--crop)
cmd+=("$in")
if command -v gamescope >/dev/null; then
  timeout 120 gamescope --backend headless --expose-wayland -W 1600 -H 1200 -- "${cmd[@]}" >/dev/null 2>&1 || true
else
  echo "export: gamescope missing; refusing to open a window on the real display" >&2; exit 2
fi
[[ -s $out ]] || { echo "export: no output written to $out" >&2; exit 1; }
echo "$out ($(stat -c %s "$out") bytes)"
