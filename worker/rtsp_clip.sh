#!/usr/bin/env sh
set -eu

# Capture a short browser-playable MP4 clip from RTSP.
# Usage: rtsp_clip.sh "rtsp://user:pass@ip:554/Streaming/Channels/101" /data/clips/1/alert-1.mp4 12

URL="$1"
OUT="$2"
DURATION="${3:-12}"
RTSP_TIMEOUT_US="${RTSP_TIMEOUT_US:-5000000}"
CONNECT_TIMEOUT_SEC="${RTSP_CONNECT_TIMEOUT_SEC:-5}"
LIMIT="${RTSP_CLIP_TIMEOUT_SEC:-$((DURATION + CONNECT_TIMEOUT_SEC + 10))}"

mkdir -p "$(dirname "$OUT")"

exec timeout "$LIMIT" ffmpeg -nostdin -hide_banner -loglevel error -y \
  -rtsp_transport tcp \
  -rw_timeout "$RTSP_TIMEOUT_US" \
  -i "$URL" \
  -t "$DURATION" \
  -an \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p \
  -movflags +faststart \
  "$OUT"
