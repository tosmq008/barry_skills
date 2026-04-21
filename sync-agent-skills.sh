#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILLS_DIR="$SCRIPT_DIR/skills"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"

MODE="${1:-link}"

declare -a TARGETS=(
  "claude:$HOME/.claude/skills"
  "codex:$HOME/.codex/skills"
  "opencode:$HOME/.opencode/skills"
  "antigravity:$SCRIPT_DIR/.agent/skills"
)

usage() {
  cat <<'EOF'
Usage:
  ./sync-agent-skills.sh [link|copy|status|help]

Modes:
  link    Create/update symlinks so each agent points to this project's skills directory
  copy    Mirror this project's skills directory into each agent target directory
  status  Show current target status without modifying anything
  help    Show this help message

Notes:
  - Claude Code target: ~/.claude/skills
  - Codex target: ~/.codex/skills
  - OpenCode target: ~/.opencode/skills
  - Antigravity target: ./.agent/skills
    Antigravity's Agent Skills Manager uses the workspace-local .agent/skills path.
EOF
}

ensure_source_exists() {
  if [[ ! -d "$SOURCE_SKILLS_DIR" ]]; then
    echo "[ERROR] Source skills directory not found: $SOURCE_SKILLS_DIR" >&2
    exit 1
  fi
}

backup_path() {
  local target="$1"
  local backup="${target}.bak_${TIMESTAMP}"
  mv "$target" "$backup"
  echo "  backed up existing target to: $backup"
}

status_line() {
  local name="$1"
  local target="$2"

  if [[ -L "$target" ]]; then
    local resolved
    resolved="$(readlink "$target")"
    echo "[$name] symlink -> $resolved"
  elif [[ -d "$target" ]]; then
    echo "[$name] directory exists: $target"
  elif [[ -e "$target" ]]; then
    echo "[$name] file exists: $target"
  else
    echo "[$name] missing: $target"
  fi
}

ensure_parent_dir() {
  local target="$1"
  mkdir -p "$(dirname "$target")"
}

link_target() {
  local name="$1"
  local target="$2"

  ensure_parent_dir "$target"

  if [[ -L "$target" ]]; then
    local resolved
    resolved="$(readlink "$target")"
    if [[ "$resolved" == "$SOURCE_SKILLS_DIR" ]]; then
      echo "[$name] already linked: $target -> $resolved"
      return 0
    fi
    rm "$target"
  elif [[ -e "$target" ]]; then
    backup_path "$target"
  fi

  ln -s "$SOURCE_SKILLS_DIR" "$target"
  echo "[$name] linked: $target -> $SOURCE_SKILLS_DIR"
}

copy_with_rsync() {
  local source="$1/"
  local target="$2/"
  rsync -a --delete "$source" "$target"
}

copy_with_cp() {
  local source="$1"
  local target="$2"

  find "$target" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  cp -R "$source"/. "$target"/
}

copy_target() {
  local name="$1"
  local target="$2"

  ensure_parent_dir "$target"

  if [[ -L "$target" ]]; then
    rm "$target"
  elif [[ -e "$target" && ! -d "$target" ]]; then
    backup_path "$target"
  fi

  mkdir -p "$target"

  if command -v rsync >/dev/null 2>&1; then
    copy_with_rsync "$SOURCE_SKILLS_DIR" "$target"
  else
    copy_with_cp "$SOURCE_SKILLS_DIR" "$target"
  fi

  echo "[$name] copied: $SOURCE_SKILLS_DIR -> $target"
}

run_status() {
  echo "Source: $SOURCE_SKILLS_DIR"
  for item in "${TARGETS[@]}"; do
    local name="${item%%:*}"
    local target="${item#*:}"
    status_line "$name" "$target"
  done
}

run_link() {
  echo "Sync mode: link"
  echo "Source: $SOURCE_SKILLS_DIR"
  for item in "${TARGETS[@]}"; do
    local name="${item%%:*}"
    local target="${item#*:}"
    link_target "$name" "$target"
  done
}

run_copy() {
  echo "Sync mode: copy"
  echo "Source: $SOURCE_SKILLS_DIR"
  for item in "${TARGETS[@]}"; do
    local name="${item%%:*}"
    local target="${item#*:}"
    copy_target "$name" "$target"
  done
}

ensure_source_exists

case "$MODE" in
  help|-h|--help)
    usage
    ;;
  status)
    run_status
    ;;
  link)
    run_link
    ;;
  copy)
    run_copy
    ;;
  *)
    echo "[ERROR] Unknown mode: $MODE" >&2
    echo >&2
    usage >&2
    exit 1
    ;;
esac
