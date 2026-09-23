#!/usr/bin/env bash
# Installs dotfiles/CLAUDE.md as your global ~/.claude/CLAUDE.md.
#   merge   - appends it to your existing CLAUDE.md (creates one if you don't have one)
#   replace - overwrites/creates ~/.claude/CLAUDE.md from this repo's copy
set -euo pipefail

mode="${1:-}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$repo_root/dotfiles/CLAUDE.md"
dest="${CLAUDE_MD_DEST:-$HOME/.claude/CLAUDE.md}"

if [[ "$mode" != "merge" && "$mode" != "replace" ]]; then
  echo "Usage: $0 merge|replace" >&2
  exit 1
fi

mkdir -p "$(dirname "$dest")"

if [[ "$mode" == "replace" ]]; then
  cp "$src" "$dest"
  echo "Replaced $dest with $src"
elif [[ -f "$dest" ]]; then
  {
    cat "$dest"
    echo
    echo "<!-- appended from $src on $(date +%F) -->"
    echo
    cat "$src"
  } > "$dest.new"
  mv "$dest.new" "$dest"
  echo "Merged $src into $dest (appended - check for duplicate sections)"
else
  cp "$src" "$dest"
  echo "No existing $dest - created from $src"
fi
