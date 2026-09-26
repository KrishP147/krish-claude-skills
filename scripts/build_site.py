#!/usr/bin/env python3
"""Builds the static skills site into site/dist/. Stdlib only.

Reuses scripts/lint.py discovery + frontmatter parsing so the site lists
exactly what lint counts. Output (wiped + recreated every run):

  site/dist/index.html          terminal home + server-rendered skill list
  site/dist/skills.json         full data (name, description, summary,
                                group, source, readme)
  site/dist/<name>/index.html   placeholder detail page per skill/agent
  site/dist/404.html
  site/dist/*.css|*.js          copied from site/src/

Usage: python scripts/build_site.py [--out DIR]
"""
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint  # noqa: E402

REPO_URL = "https://github.com/KrishP147/skills"
GROUPS = ("core", "kanban", "agents")
STATIC_EXTS = (".css", ".js")
# Abbreviations that end in '.' but don't end a sentence.
_ABBREV = ("e.g.", "i.e.", "etc.", "vs.")


def read_text(path):
    # utf-8-sig drops a BOM; text mode normalises CRLF to LF.
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def first_sentence(text):
    text = " ".join(text.split())
    for m in re.finditer(r"[.!?](?=\s|$)", text):
        end = m.end()
        if any(text[:end].lower().endswith(a) for a in _ABBREV):
            continue
        return text[:end]
    return text


def posix_rel(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")


def collect(root):
    """Return entries sorted by group order then name."""
    entries = []
    for path in lint.find_skill_files(root):
        fm, _body = lint.parse_frontmatter(read_text(path))
        fm = fm or {}
        skill_dir = os.path.dirname(path)
        rel_dir = posix_rel(skill_dir, root)
        group = "kanban" if rel_dir.startswith("kanban/") else "core"
        readme_path = os.path.join(skill_dir, "README.md")
        readme = read_text(readme_path) if os.path.isfile(readme_path) else ""
        entries.append(_entry(fm, os.path.basename(skill_dir), group, rel_dir, readme))
    for path in lint.find_agent_files(root):
        fm, body = lint.parse_frontmatter(read_text(path))
        fm = fm or {}
        stem = os.path.splitext(os.path.basename(path))[0]
        entries.append(_entry(fm, stem, "agents", posix_rel(path, root), body.strip("\n") + "\n"))
    entries.sort(key=lambda e: (GROUPS.index(e["group"]), e["name"]))
    return entries


def _entry(fm, fallback_name, group, source, readme):
    description = fm.get("description") or ""
    if not isinstance(description, str):
        description = ""
    return {
        "name": fm.get("name") or fallback_name,
        "description": description,
        "summary": first_sentence(description),
        "group": group,
        "source": source,
        "readme": readme,
    }


def counts(entries):
    agents = sum(1 for e in entries if e["group"] == "agents")
    return len(entries) - agents, agents


def count_line(entries):
    skills, agents = counts(entries)
    return "%d skill%s · %d agent%s" % (
        skills, "" if skills == 1 else "s", agents, "" if agents == 1 else "s")


def esc(s):
    return html.escape(s, quote=True)


def render_list(entries):
    out = []
    for group in GROUPS:
        items = [e for e in entries if e["group"] == group]
        if not items:
            continue
        out.append('<section class="group" aria-labelledby="g-%s">' % group)
        out.append('<h2 id="g-%s">%s <span class="n">(%d)</span></h2>' % (group, group, len(items)))
        out.append('<ul class="skill-list">')
        for e in items:
            out.append(
                '<li><a href="/%s"><span class="nm">/%s</span>'
                '<span class="ds">%s</span></a></li>'
                % (esc(e["name"]), esc(e["name"]), esc(e["summary"])))
        out.append("</ul>")
        out.append("</section>")
    return "\n".join(out)


def embed_json(obj):
    # Safe inside <script type="application/json">: no '</script>' or '<!--'.
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def render_index(template, entries):
    data = [{"name": e["name"], "summary": e["summary"], "group": e["group"]} for e in entries]
    return (template
            .replace("{{COUNT}}", esc(count_line(entries)))
            .replace("{{LIST}}", render_list(entries))
            .replace("{{DATA}}", embed_json(data)))


def render_detail(template, e):
    source_url = "%s/%s/%s" % (REPO_URL, "blob/master" if e["source"].endswith(".md") else "tree/master", e["source"])
    return (template
            .replace("{{NAME}}", esc(e["name"]))
            .replace("{{GROUP}}", esc(e["group"]))
            .replace("{{DESCRIPTION}}", esc(e["description"]))
            .replace("{{SOURCE_URL}}", esc(source_url))
            .replace("{{SOURCE}}", esc(e["source"])))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def build(root, out):
    src = os.path.join(root, "site", "src")
    entries = collect(root)
    names = [e["name"] for e in entries]
    if len(set(names)) != len(names):
        raise SystemExit("duplicate skill/agent names: %s" % sorted(n for n in names if names.count(n) > 1))

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    write(os.path.join(out, "index.html"), render_index(read_text(os.path.join(src, "index.html")), entries))
    detail_tpl = read_text(os.path.join(src, "detail.html"))
    for e in entries:
        write(os.path.join(out, e["name"], "index.html"), render_detail(detail_tpl, e))
    write(os.path.join(out, "404.html"), read_text(os.path.join(src, "404.html")))
    write(os.path.join(out, "skills.json"),
          json.dumps(entries, ensure_ascii=False, indent=2) + "\n")
    for fn in sorted(os.listdir(src)):
        if fn.endswith(STATIC_EXTS):
            write(os.path.join(out, fn), read_text(os.path.join(src, fn)))
    return entries


def main(argv):
    root = lint.repo_root()
    out = os.path.join(root, "site", "dist")
    if len(argv) >= 2 and argv[0] == "--out":
        out = os.path.abspath(argv[1])
    entries = build(root, out)
    skills, agents = counts(entries)
    print("Built %s: %d skills, %d agents" % (posix_rel(out, root), skills, agents))


if __name__ == "__main__":
    main(sys.argv[1:])
