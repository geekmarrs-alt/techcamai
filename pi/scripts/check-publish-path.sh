#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

warn() {
  echo "[WARN] $*" >&2
}

info() {
  echo "[INFO] $*"
}

if [[ ! -d .git ]]; then
  fail "This recovered copy is not a real git checkout. Shortest fix: either work from the real source-of-truth repo, or clone the GitHub repo fresh and copy these files into it before publishing."
fi

remote_url="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$remote_url" ]]; then
  fail "No git origin remote is configured. Reconnect this repo to the real GitHub source-of-truth before trying to publish."
fi

owner_repo="$(printf '%s\n' "$remote_url" | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')"
owner="${owner_repo%%/*}"
repo="${owner_repo##*/}"
[[ -n "$owner" && -n "$repo" && "$owner" != "$repo" ]] || fail "Could not parse GitHub owner/repo from origin: $remote_url"

api_expected="ghcr.io/${owner}/techcamai-api:stable"
worker_expected="ghcr.io/${owner}/techcamai-worker:stable"
workflow=".github/workflows/docker.yml"
compose_file="pi/docker-compose.pi.yml"

[[ -f "$workflow" ]] || fail "Missing $workflow"
[[ -f "$compose_file" ]] || fail "Missing $compose_file"

info "GitHub remote: $owner_repo"
info "Expected stable images:"
info "  - $api_expected"
info "  - $worker_expected"

if ! grep -q "branches: \[ \"master\" \]" "$workflow"; then
  warn "Workflow trigger is not the expected master push. Check $workflow manually."
else
  info "Workflow trigger: push to master"
fi

if ! grep -q "ghcr.io/\${{ github.repository_owner }}/techcamai-api:stable" "$workflow"; then
  warn "Workflow API tag does not use github.repository_owner as expected."
else
  info "Workflow API tag looks correct"
fi

if ! grep -q "ghcr.io/\${{ github.repository_owner }}/techcamai-worker:stable" "$workflow"; then
  warn "Workflow worker tag does not use github.repository_owner as expected."
else
  info "Workflow worker tag looks correct"
fi

if ! grep -q "$api_expected" "$compose_file"; then
  warn "Pi compose API image does not match origin owner ($api_expected)"
else
  info "Pi compose API image matches origin owner"
fi

if ! grep -q "$worker_expected" "$compose_file"; then
  warn "Pi compose worker image does not match origin owner ($worker_expected)"
else
  info "Pi compose worker image matches origin owner"
fi

if git diff --quiet && git diff --cached --quiet; then
  info "Working tree is clean"
else
  warn "Working tree has uncommitted changes. Commit before publishing or bundle from a dirty tree on purpose."
fi

cat <<EOF

Next clean publish flow:
  1. Commit the playback/dashboard changes in this repo.
  2. Push to origin master.
  3. Wait for GitHub Actions workflow 'build-and-push' to go green.
  4. On the Pi, either wait for Watchtower or run:
       docker compose -f /opt/techcamai/techcamai/pi/docker-compose.pi.yml pull
       docker compose -f /opt/techcamai/techcamai/pi/docker-compose.pi.yml up -d

Thumbs-up moment:
  The 'build-and-push' action for the commit containing the playback/dashboard work finishes successfully,
  and ghcr.io/${owner}/techcamai-{api,worker}:stable has been updated.
EOF
