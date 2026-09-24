#!/usr/bin/env bash
# Installs every skill in this repo into ~/.claude/skills/ (personal, global
# across all repos/terminals). Safe to re-run - each skill is replaced fresh.
# Also installs agents/*.md and agents/hooks/ into ~/.claude/agents/.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
agents_target="${CLAUDE_AGENTS_DIR:-$HOME/.claude/agents}"

pybin=""
if command -v python3 >/dev/null 2>&1; then
  pybin="python3"
elif command -v python >/dev/null 2>&1; then
  pybin="python"
fi

if [[ -n "$pybin" ]]; then
  if ! "$pybin" "$repo_root/scripts/lint.py"; then
    echo "lint failed - aborting install" >&2
    exit 1
  fi
else
  echo "warning: python/python3 not found on PATH, skipping lint" >&2
fi

mkdir -p "$target"
mkdir -p "$agents_target"

installed=()
while IFS= read -r -d '' skill_md; do
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  dest="$target/$name"
  rm -rf "$dest"
  cp -r "$skill_dir" "$dest"
  installed+=("$name")
done < <(find "$repo_root" -mindepth 2 -maxdepth 3 -name "SKILL.md" -print0)

installed_agents=()
while IFS= read -r -d '' agent_md; do
  name="$(basename "$agent_md")"
  cp "$agent_md" "$agents_target/$name"
  installed_agents+=("${name%.md}")
done < <(find "$repo_root/agents" -maxdepth 1 -name "*.md" ! -name "README.md" -print0)

mkdir -p "$agents_target/hooks"
if [[ -d "$repo_root/agents/hooks" ]]; then
  cp -rf "$repo_root/agents/hooks/." "$agents_target/hooks/"
fi

printf 'Installed %d skill(s) to %s:\n' "${#installed[@]}" "$target"
printf '  - %s\n' "${installed[@]}"

printf 'Installed %d agent(s) to %s:\n' "${#installed_agents[@]}" "$agents_target"
printf '  - %s\n' "${installed_agents[@]}"
