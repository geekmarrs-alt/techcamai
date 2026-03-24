#!/usr/bin/env bash
# setup-ruflo.sh — Initialize Ruflo AI orchestration for TECHCAMAI
#
# Usage:
#   ./scripts/setup-ruflo.sh          # guided wizard
#   ./scripts/setup-ruflo.sh --full   # wizard + MCP server + diagnostics
#   ./scripts/setup-ruflo.sh --mcp    # start MCP server only (Claude Code integration)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# ── Prerequisites ────────────────────────────────────────────────────────────

check_node() {
  if ! command -v node &>/dev/null; then
    echo "ERROR: Node.js is required (v20+). Install from https://nodejs.org/"
    exit 1
  fi
  NODE_VER=$(node -e "process.stdout.write(process.versions.node.split('.')[0])")
  if [ "$NODE_VER" -lt 20 ]; then
    echo "ERROR: Node.js v20+ required (found v${NODE_VER}). Please upgrade."
    exit 1
  fi
  echo "  Node.js v$(node --version) — OK"
}

check_api_key() {
  if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo ""
    echo "WARNING: ANTHROPIC_API_KEY is not set."
    echo "  Set it in your .env file or export it before running Ruflo:"
    echo "    export ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
  else
    echo "  ANTHROPIC_API_KEY — OK"
  fi
}

# ── Modes ────────────────────────────────────────────────────────────────────

mode_wizard() {
  echo ""
  echo "Running Ruflo setup wizard..."
  cd "$ROOT_DIR"
  npx ruflo@latest init --wizard
}

mode_full() {
  echo ""
  echo "Running full Ruflo setup (wizard + MCP + diagnostics)..."
  curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/claude-flow@main/scripts/install.sh | bash -s -- --full
}

mode_mcp() {
  echo ""
  echo "Starting Ruflo MCP server for Claude Code integration..."
  echo "Add the following to your Claude Code MCP config, or use:"
  echo "  claude mcp add ruflo -- npx -y ruflo@latest mcp start"
  echo ""
  cd "$ROOT_DIR"
  npx ruflo@latest mcp start
}

# ── Main ─────────────────────────────────────────────────────────────────────

echo "=== TECHCAMAI × Ruflo Setup ==="
echo ""
echo "Checking prerequisites..."
check_node
check_api_key

ARG="${1:-}"

case "$ARG" in
  --full)
    mode_full
    ;;
  --mcp)
    mode_mcp
    ;;
  *)
    mode_wizard
    ;;
esac

echo ""
echo "Done! Ruflo is ready."
echo ""
echo "Useful commands:"
echo "  npm run ruflo:status   — check agent/swarm status"
echo "  npm run ruflo:start    — start the MCP server"
echo "  npm run ruflo:swarm    — initialize a swarm"
echo ""
echo "Claude Code integration:"
echo "  claude mcp add ruflo -- npx -y ruflo@latest mcp start"
echo "  claude mcp list"
