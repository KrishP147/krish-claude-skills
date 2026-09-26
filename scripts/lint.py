#!/usr/bin/env python3
"""Lints SKILL.md and agents/*.md files in this repo. Stdlib only.

Checks: frontmatter present; name matches parent dir (skills) or file stem
(agents); description present and <=1024 chars; body non-empty; no
"praxic" (case-insensitive) anywhere in a linted file; every skill an
agent preloads exists as a skill dir in the repo; no agent preloads a
skill marked disable-model-invocation: true.

Also warns (to stderr, non-fatal) when a skill's README.md is missing one
of the required "## " section headings from templates/skill/README.md.
"templates/" itself is excluded from every check and from install.

Usage: python scripts/lint.py
Exit 0 + "OK: N skills, M agents" on success (last stdout line). Exit 1
with one line per failure otherwise. WARN lines never affect exit code.
"""
import glob
import os
import sys

SKIP_DIRS = {".git", "node_modules", "templates"}

REQUIRED_README_SECTIONS = [
    "What it does",
    "When to use",
    "How to invoke",
    "How it works",
    "Design principles",
    "Use cases",
    "Tips",
    "Example",
    "Related",
    "Prereqs",
]


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def find_skill_files(root):
    found = set()
    for pattern in ("*/SKILL.md", "*/*/SKILL.md"):
        for path in glob.glob(os.path.join(root, pattern)):
            rel = os.path.relpath(path, root)
            parts = rel.split(os.sep)
            if any(p in SKIP_DIRS for p in parts):
                continue
            found.add(os.path.normpath(path))
    return sorted(found)


def find_agent_files(root):
    # README.md is human docs, not an agent definition.
    return sorted(
        p for p in glob.glob(os.path.join(root, "agents", "*.md"))
        if os.path.basename(p).lower() != "readme.md"
    )


def parse_frontmatter(text):
    """Minimal '---' delimited frontmatter parser. Top-level `key: value`
    lines are captured. A key with an empty value followed by indented
    `- item` lines becomes a list. Deeper nested blocks are skipped."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, text
    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])

    data = {}
    current_key = None
    for line in fm_lines:
        if not line.strip():
            continue
        if not line[0].isspace():
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                if val == "":
                    data[key] = []
                    current_key = key
                else:
                    data[key] = val
                    current_key = None
            else:
                current_key = None
        else:
            stripped = line.strip()
            if stripped.startswith("- ") and isinstance(data.get(current_key), list):
                data[current_key].append(stripped[2:].strip())
            # else: nested block content - not needed for these checks, skip.
    return data, body


def lint_common(path, text, fm, body, expected_name, failures):
    if fm is None:
        failures.append("%s: missing frontmatter" % path)
        return
    name = fm.get("name")
    if not name:
        failures.append("%s: missing 'name' in frontmatter" % path)
    elif name != expected_name:
        failures.append("%s: name '%s' != expected '%s'" % (path, name, expected_name))

    description = fm.get("description")
    if not description:
        failures.append("%s: missing 'description' in frontmatter" % path)
    elif len(description) > 1024:
        failures.append("%s: description exceeds 1024 chars (%d)" % (path, len(description)))

    if not body.strip():
        failures.append("%s: empty body" % path)

    if "praxic" in text.lower():
        failures.append("%s: contains forbidden word 'praxic'" % path)


def readme_headings(text):
    headings = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            headings.add(stripped[3:].strip())
    return headings


def warn_missing_readme_sections(skill_md_path):
    """If a README.md sits next to this SKILL.md, print one WARN line to
    stderr naming any required section headings it's missing. "## Invoke"
    counts as "## How to invoke". Never affects the exit code."""
    readme_path = os.path.join(os.path.dirname(skill_md_path), "README.md")
    if not os.path.isfile(readme_path):
        return
    with open(readme_path, "r", encoding="utf-8") as f:
        headings = readme_headings(f.read())
    if "Invoke" in headings:
        headings.add("How to invoke")
    missing = [h for h in REQUIRED_README_SECTIONS if h not in headings]
    if missing:
        sys.stderr.write(
            "WARN: %s: missing sections: %s\n" % (readme_path, ", ".join(missing))
        )


def main():
    root = repo_root()
    failures = []

    skill_files = find_skill_files(root)
    agent_files = find_agent_files(root)

    skill_names = set()
    disabled_skills = set()

    for path in skill_files:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        fm, body = parse_frontmatter(text)
        parent_dir = os.path.basename(os.path.dirname(path))
        skill_names.add(parent_dir)
        lint_common(path, text, fm, body, parent_dir, failures)
        if fm and str(fm.get("disable-model-invocation", "")).strip().lower() == "true":
            disabled_skills.add(parent_dir)
        warn_missing_readme_sections(path)

    agent_skill_lists = {}
    for path in agent_files:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        fm, body = parse_frontmatter(text)
        stem = os.path.splitext(os.path.basename(path))[0]
        lint_common(path, text, fm, body, stem, failures)
        if fm:
            skills_list = fm.get("skills")
            if isinstance(skills_list, list):
                agent_skill_lists[path] = skills_list

    for path, skills_list in agent_skill_lists.items():
        for entry in skills_list:
            if entry not in skill_names:
                failures.append("%s: preloads unknown skill '%s' (no such skill dir)" % (path, entry))
            if entry in disabled_skills:
                failures.append(
                    "%s: preloads '%s', which has disable-model-invocation: true (unsupported)" % (path, entry)
                )

    if failures:
        for f in failures:
            print(f)
        sys.exit(1)

    print("OK: %d skills, %d agents" % (len(skill_files), len(agent_files)))


if __name__ == "__main__":
    main()
