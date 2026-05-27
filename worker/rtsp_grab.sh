#!/usr/bin/env sh
set -eu

# Grab a single JPEG frame from RTSP.
# Usage: rtsp_grab.sh "rtsp://user:pass@ip:554/Streaming/Channels/101" /tmp/out.jpg

URL="$1"
OUT="$2"
RTSP_TIMEOUT_US="${RTSP_TIMEOUT_US:-5000000}"
LIMIT="${RTSP_GRAB_TIMEOUT_SEC:-15}"

# -nostdin prevents ffmpeg hanging on stdin in containers
# -rtsp_transport tcp is more reliable on crappy networks
# -rw_timeout bounds socket reads while Python also enforces a process timeout
# -frames:v 1 writes a single frame
# -q:v controls jpeg quality
exec timeout "$LIMIT" ffmpeg -nostdin -hide_banner -loglevel error \
  -rtsp_transport tcp \
  -rw_timeout "$RTSP_TIMEOUT_US" \
  -i "$URL" \
  -frames:v 1 -q:v 3 \
  -update 1 "$OUT"
