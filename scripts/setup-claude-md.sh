#!/usr/bin/env bash
# Installs dotfiles/CLAUDE.md as your global ~/.claude/CLAUDE.md.
#   merge   - appends it to your existing CLAUDE.md (creates one if you don't have one)
#   replace - overwrites/creates ~/.claude/CLAUDE.md from this repo's copy
# --prefix <p> substitutes the <your-prefix> branch-prefix placeholder with <p>.
# Without --prefix, the placeholder is left in place and a hint is printed.
set -euo pipefail

mode=""
prefix=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix)
      if [[ $# -lt 2 || -z "$2" ]]; then
        echo "--prefix needs a value" >&2
        exit 1
      fi
      prefix="$2"
      shift 2
      ;;
    merge|replace)
      mode="$1"
      shift
      ;;
    *)
      echo "Usage: $0 merge|replace [--prefix <p>]" >&2
      exit 1
      ;;
  esac
done

if [[ "$mode" != "merge" && "$mode" != "replace" ]]; then
  echo "Usage: $0 merge|replace [--prefix <p>]" >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$repo_root/dotfiles/CLAUDE.md"
dest="${CLAUDE_MD_DEST:-$HOME/.claude/CLAUDE.md}"

incoming="$(cat "$src")"$'\n'
if [[ -n "$prefix" ]]; then
  incoming="${incoming//<your-prefix>/$prefix}"
else
  echo "hint: branch prefix left as <your-prefix> placeholder - pass --prefix <p> to fill it in" >&2
fi

mkdir -p "$(dirname "$dest")"

if [[ "$mode" == "replace" ]]; then
  printf '%s' "$incoming" > "$dest"
  echo "Replaced $dest with $src"
elif [[ -f "$dest" ]]; then
  {
    cat "$dest"
    echo
    echo "<!-- appended from $src on $(date +%F) -->"
    echo
    printf '%s' "$incoming"
  } > "$dest.new"
  mv "$dest.new" "$dest"
  echo "Merged $src into $dest (appended - check for duplicate sections)"
else
  printf '%s' "$incoming" > "$dest"
  echo "No existing $dest - created from $src"
fi
