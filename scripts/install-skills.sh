#!/usr/bin/env bash
# Installs every skill in this repo into ~/.claude/skills/ (personal, global
# across all repos/terminals). Safe to re-run - each skill is replaced fresh.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$target"

installed=()
while IFS= read -r -d '' skill_md; do
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  dest="$target/$name"
  rm -rf "$dest"
  cp -r "$skill_dir" "$dest"
  installed+=("$name")
done < <(find "$repo_root" -mindepth 2 -maxdepth 3 -name "SKILL.md" -print0)

printf 'Installed %d skill(s) to %s:\n' "${#installed[@]}" "$target"
printf '  - %s\n' "${installed[@]}"
