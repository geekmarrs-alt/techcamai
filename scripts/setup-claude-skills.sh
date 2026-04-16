#!/usr/bin/env bash
# setup-claude-skills.sh — Install alirezarezvani/claude-skills into this project
#
# Usage:
#   ./scripts/setup-claude-skills.sh               # install engineering + commands
#   ./scripts/setup-claude-skills.sh --all         # install all domains
#   ./scripts/setup-claude-skills.sh --list        # list available domains

set -euo pipefail

REPO_URL="https://github.com/alirezarezvani/claude-skills.git"
SKILLS_DIR="$(mktemp -d)"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="$ROOT_DIR/.claude"

DOMAINS_DEFAULT=("engineering-team" "engineering")
DOMAINS_ALL=("engineering-team" "engineering" "product-team" "c-level-advisor" "project-management" "business-growth" "finance" "ra-qm-team" "marketing-skill")

cleanup() { rm -rf "$SKILLS_DIR"; }
trap cleanup EXIT

list_domains() {
  echo "Available domains:"
  for d in "${DOMAINS_ALL[@]}"; do echo "  • $d"; done
}

install_domain() {
  local domain="$1"
  local src="$SKILLS_DIR/$domain"
  local dst="$CLAUDE_DIR/skills/$domain"
  if [ -d "$src" ]; then
    mkdir -p "$dst"
    cp -r "$src/." "$dst/"
    echo "  ✓ $domain"
  else
    echo "  ✗ $domain (not found in repo)"
  fi
}

ARG="${1:-}"
if [ "$ARG" = "--list" ]; then list_domains; exit 0; fi

echo "=== TECHCAMAI × claude-skills Setup ==="
echo ""
echo "Cloning alirezarezvani/claude-skills (shallow)…"
git clone --depth 1 "$REPO_URL" "$SKILLS_DIR" -q

mkdir -p "$CLAUDE_DIR/skills"

if [ "$ARG" = "--all" ]; then
  echo "Installing all domains:"
  for d in "${DOMAINS_ALL[@]}"; do install_domain "$d"; done
else
  echo "Installing engineering skills:"
  for d in "${DOMAINS_DEFAULT[@]}"; do install_domain "$d"; done
fi

echo ""
echo "Done! Skills installed to .claude/skills/"
echo ""
echo "Available Claude Code slash commands (from .claude/commands/):"
echo "  /git/cm          Stage and commit (Conventional Commit)"
echo "  /git/cp          Commit and push with CI check"
echo "  /git/pr          Create pull request"
echo "  /review          Pre-push lint + syntax gate"
echo "  /security-scan   Secrets + dependency audit"
echo ""
echo "To install all domains: ./scripts/setup-claude-skills.sh --all"
