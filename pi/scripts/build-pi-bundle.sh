#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_NAME="${1:-techcamai-pi-ready-$(date +%F).tgz}"

if [[ "$OUT_NAME" = /* ]]; then
  OUT_PATH="$OUT_NAME"
else
  OUT_PATH="$ROOT_DIR/$OUT_NAME"
fi

mkdir -p "$(dirname "$OUT_PATH")"

TMP_PARENT="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_PARENT"
}
trap cleanup EXIT

STAGE_DIR="$TMP_PARENT/techcamai"
mkdir -p "$STAGE_DIR"

( cd "$ROOT_DIR" && tar \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='techcamai.tgz' \
    --exclude='node_modules' \
    -cf - . ) | ( cd "$STAGE_DIR" && tar -xf - )

tar -czf "$OUT_PATH" -C "$TMP_PARENT" techcamai

sha256="$(sha256sum "$OUT_PATH" | awk '{print $1}')"
size="$(du -h "$OUT_PATH" | awk '{print $1}')"

echo "[OK] Bundle created: $OUT_PATH"
echo "[OK] Size: $size"
echo "[OK] SHA256: $sha256"

echo
cat <<EOF
Serve these two files to the Pi for a clean install/update:
  - $OUT_PATH
  - $ROOT_DIR/pi/install.sh
EOF
