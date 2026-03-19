#!/usr/bin/env sh
set -eu

# Capture a short browser-playable MP4 clip from RTSP.
# Usage: rtsp_clip.sh "rtsp://user:pass@ip:554/Streaming/Channels/101" /data/clips/1/alert-1.mp4 12

URL="$1"
OUT="$2"
DURATION="${3:-12}"

mkdir -p "$(dirname "$OUT")"

ffmpeg -nostdin -hide_banner -loglevel error -y \
  -rtsp_transport tcp \
  -i "$URL" \
  -t "$DURATION" \
  -an \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p \
  -movflags +faststart \
  "$OUT"
