#!/usr/bin/env bash
set -euo pipefail

# TECHCAMAI Pi installer (MVP)
# Usage:
#   curl -fsSL http://<HOST>:<PORT>/install.sh | sudo bash -s -- \
#     --src http://<HOST>:<PORT>/techcamai.tgz \
#     --camera-urls "http://user:pass@cam/ISAPI/Streaming/channels/1/picture"

SRC_URL=""
CAMERA_URLS=""
API_PORT="8000"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --src) SRC_URL="$2"; shift 2;;
    --camera-urls) CAMERA_URLS="$2"; shift 2;;
    --api-port) API_PORT="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

if [[ -z "$SRC_URL" ]]; then
  echo "Missing --src <url-to-techcamai.tgz>" >&2
  exit 2
fi

echo "[+] Installing Docker (if missing)"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

systemctl enable --now docker || true

echo "[+] Installing Compose plugin (if missing)"
if ! docker compose version >/dev/null 2>&1; then
  apt-get update
  apt-get install -y docker-compose-plugin
fi

INSTALL_DIR="/opt/techcamai"
mkdir -p "$INSTALL_DIR"

echo "[+] Fetching TECHCAMAI bundle: $SRC_URL"
# wipe install dir contents (MVP)
rm -rf "$INSTALL_DIR"/*

curl -fsSL "$SRC_URL" | tar -xz -C "$INSTALL_DIR"

# Support both bundle layouts:
#  A) /opt/techcamai/techcamai/docker-compose.yml
#  B) /opt/techcamai/docker-compose.yml
if [[ -f "$INSTALL_DIR/techcamai/docker-compose.yml" ]]; then
  APP_DIR="$INSTALL_DIR/techcamai"
elif [[ -f "$INSTALL_DIR/docker-compose.yml" ]]; then
  APP_DIR="$INSTALL_DIR"
else
  echo "Bundle missing docker-compose.yml under $INSTALL_DIR" >&2
  find "$INSTALL_DIR" -maxdepth 2 -type f -name docker-compose.yml -print || true
  exit 1
fi

cd "$APP_DIR"

echo "[+] Writing .env"
cp -f .env.example .env

# set API_PORT only if present in example env
if grep -q '^API_PORT=' .env; then
  sed -i "s/^API_PORT=.*/API_PORT=${API_PORT}/" .env
fi

if [[ -n "$CAMERA_URLS" ]]; then
  sed -i "s|^CAMERA_SNAPSHOT_URLS=.*|CAMERA_SNAPSHOT_URLS=${CAMERA_URLS}|" .env
fi

echo "[+] Starting stack"
docker compose up -d --build

echo "[+] Done. Open: http://$(hostname -I | awk '{print $1}'):${API_PORT}/"
