#!/usr/bin/env bash
# Installs every skill in this repo into ~/.claude/skills/ (personal, global
# across all repos/terminals). Safe to re-run - each of our own skill dirs is
# replaced fresh; a same-named dir NOT installed by this repo (no marker
# file) is left alone unless --force. Also copies agents/*.md and
# agents/hooks/ over ~/.claude/agents/; agents there that aren't in this
# repo are warned about, never deleted.
#
# Flags:
#   --no-lint  proceed even if no working python 3 is found (skips lint)
#   --force    replace foreign skill dirs (no marker file) instead of
#              skipping them
set -euo pipefail

MARKER=".from-krishp147-skills"

no_lint=0
force=0
for arg in "$@"; do
  case "$arg" in
    --no-lint) no_lint=1 ;;
    --force) force=1 ;;
    *)
      echo "Usage: $0 [--no-lint] [--force]" >&2
      exit 1
      ;;
  esac
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
agents_target="${CLAUDE_AGENTS_DIR:-$HOME/.claude/agents}"

# first candidate that actually runs Python 3 (skips e.g. the Windows Store
# python/python3 stub, which exists on PATH but refuses to run code)
pybin=""
pyargs=()
try_py() {
  local cmd="$1"; shift
  command -v "$cmd" >/dev/null 2>&1 || return 1
  "$cmd" "$@" -c 'import sys; sys.exit(sys.version_info[0] != 3)' >/dev/null 2>&1
}
if try_py python3; then
  pybin="python3"
elif try_py python; then
  pybin="python"
elif try_py py -3; then
  pybin="py"
  pyargs=(-3)
fi

if [[ -n "$pybin" ]]; then
  # ${arr[@]+...}: empty-array expansion under set -u breaks bash < 4.4 (macOS)
  if ! "$pybin" ${pyargs[@]+"${pyargs[@]}"} "$repo_root/scripts/lint.py"; then
    echo "lint failed - aborting install" >&2
    exit 1
  fi
elif (( no_lint )); then
  echo "warning: no working python 3 found, skipping lint (--no-lint)" >&2
else
  echo "error: no working python 3 found on PATH (checked python3, python, py -3)." >&2
  echo "Install Python 3, or pass --no-lint to skip the lint step." >&2
  exit 1
fi

mkdir -p "$target"
mkdir -p "$agents_target"

installed=()
skipped_foreign=()
while IFS= read -r -d '' skill_md; do
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  dest="$target/$name"
  if [[ -e "$dest" && ! -f "$dest/$MARKER" && $force -eq 0 ]]; then
    echo "warning: $dest exists and wasn't installed by this repo, skipping (use --force to replace)" >&2
    skipped_foreign+=("$name")
    continue
  fi
  rm -rf "$dest"
  cp -r "$skill_dir" "$dest"
  find "$dest" -depth -name "__pycache__" -type d -exec rm -rf {} +
  : > "$dest/$MARKER"
  installed+=("$name")
done < <(find "$repo_root" -mindepth 2 -maxdepth 3 -name "SKILL.md" -not -path "$repo_root/templates/*" -print0)

installed_agents=()
while IFS= read -r -d '' agent_md; do
  name="$(basename "$agent_md")"
  cp "$agent_md" "$agents_target/$name"
  installed_agents+=("${name%.md}")
done < <(find "$repo_root/agents" -maxdepth 1 -name "*.md" ! -name "README.md" -print0)

mkdir -p "$agents_target/hooks"
if [[ -d "$repo_root/agents/hooks" ]]; then
  cp -rf "$repo_root/agents/hooks/." "$agents_target/hooks/"
  find "$agents_target/hooks" -depth -name "__pycache__" -type d -exec rm -rf {} +
fi

printf 'Installed %d skill(s) to %s:\n' "${#installed[@]}" "$target"
printf '  - %s\n' "${installed[@]}"

if (( ${#skipped_foreign[@]} )); then
  printf 'warning: skipped %d foreign skill dir(s) without marker (use --force): %s\n' \
    "${#skipped_foreign[@]}" "${skipped_foreign[*]}" >&2
fi

printf 'Installed %d agent(s) to %s:\n' "${#installed_agents[@]}" "$agents_target"
printf '  - %s\n' "${installed_agents[@]}"

stale=()
while IFS= read -r -d '' existing; do
  name="$(basename "$existing")"
  [[ -f "$repo_root/agents/$name" ]] || stale+=("$name")
done < <(find "$agents_target" -maxdepth 1 -type f -name "*.md" ! -name "README.md" -print0)
if (( ${#stale[@]} )); then
  printf 'warning: stale agent(s) not in repo, remove manually: %s\n' "${stale[*]}" >&2
fi

if (( ${#skipped_foreign[@]} )); then
  exit 1
fi
