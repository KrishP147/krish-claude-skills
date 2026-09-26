"""Tests for scripts/build_site.py. Run: python -m unittest discover -s scripts -p "test_*.py" """
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site  # noqa: E402
import lint  # noqa: E402

ROOT = lint.repo_root()


class BuildSiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = tempfile.mkdtemp(prefix="site-dist-")
        cls.entries = build_site.build(ROOT, cls.out)
        with open(os.path.join(cls.out, "skills.json"), encoding="utf-8") as f:
            cls.data = json.load(f)
        with open(os.path.join(cls.out, "index.html"), encoding="utf-8") as f:
            cls.index = f.read()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def test_counts_match_lint(self):
        skills, agents = build_site.counts(self.entries)
        self.assertEqual(skills, len(lint.find_skill_files(ROOT)))
        self.assertEqual(agents, len(lint.find_agent_files(ROOT)))
        self.assertIn(build_site.esc(build_site.count_line(self.entries)), self.index)

    def test_groups(self):
        by = {e["name"]: e["group"] for e in self.data}
        self.assertEqual(by["pair"], "core")
        self.assertEqual(by["next"], "kanban")
        self.assertEqual(by["implementer"], "agents")
        self.assertNotIn("README", by)
        self.assertTrue(set(by.values()) <= set(build_site.GROUPS))
        order = [build_site.GROUPS.index(e["group"]) for e in self.data]
        self.assertEqual(order, sorted(order))

    def test_json_fields(self):
        for e in self.data:
            self.assertEqual(set(e), {"name", "description", "summary", "group", "source", "readme"})
            self.assertTrue(e["name"] and e["description"] and e["summary"])
            self.assertNotIn("\\", e["source"])
            self.assertNotIn("\r", e["readme"])
            self.assertTrue(e["description"].startswith(e["summary"].rstrip(".!?")[:20]))
        pair = next(e for e in self.data if e["name"] == "pair")
        self.assertEqual(pair["source"], "pair")
        self.assertTrue(pair["readme"])
        impl = next(e for e in self.data if e["name"] == "implementer")
        self.assertEqual(impl["source"], "agents/implementer.md")
        self.assertNotIn("name: implementer", impl["readme"])

    def test_placeholder_pages(self):
        for e in self.data:
            path = os.path.join(self.out, e["name"], "index.html")
            self.assertTrue(os.path.isfile(path), path)
        with open(os.path.join(self.out, "pair", "index.html"), encoding="utf-8") as f:
            self.assertIn("/pair", f.read())
        for fn in ("404.html", "style.css", "filter.js", "app.js"):
            self.assertTrue(os.path.isfile(os.path.join(self.out, fn)), fn)

    def test_list_links_server_rendered(self):
        for e in self.data:
            self.assertIn('href="/%s"' % e["name"], self.index)
        self.assertNotIn("{{", self.index)

    def test_first_sentence(self):
        fs = build_site.first_sentence
        self.assertEqual(fs("One thing. Two things."), "One thing.")
        self.assertEqual(fs("Use e.g. this. Then that."), "Use e.g. this.")
        self.assertEqual(fs("No period"), "No period")
        self.assertEqual(fs("Line\r\nwrap. Next."), "Line wrap.")
        self.assertEqual(fs("v1.2 is out. Yes."), "v1.2 is out.")

    def test_escaping(self):
        e = {"name": "x", "summary": '<b>"a" & b</b>', "group": "core"}
        html = build_site.render_list([e])
        self.assertIn("&lt;b&gt;&quot;a&quot; &amp; b&lt;/b&gt;", html)
        self.assertNotIn("<b>", html)
        embedded = build_site.embed_json([{"summary": "</script><!--"}])
        self.assertNotIn("<", embedded)
        self.assertEqual(json.loads(embedded)[0]["summary"], "</script><!--")

    def test_deterministic_and_wipes(self):
        stale = os.path.join(self.out, "stale.txt")
        with open(stale, "w") as f:
            f.write("x")
        out2 = tempfile.mkdtemp(prefix="site-dist2-")
        try:
            build_site.build(ROOT, self.out)
            build_site.build(ROOT, out2)
            self.assertFalse(os.path.exists(stale))
            for rel in ("index.html", "skills.json", os.path.join("pair", "index.html")):
                with open(os.path.join(self.out, rel), "rb") as a, open(os.path.join(out2, rel), "rb") as b:
                    self.assertEqual(a.read(), b.read(), rel)
        finally:
            shutil.rmtree(out2, ignore_errors=True)

    def test_no_skill_md_under_site(self):
        # lint globs */SKILL.md and */*/SKILL.md; the site must not add any.
        for dirpath, _dirs, files in os.walk(os.path.join(ROOT, "site")):
            self.assertNotIn("SKILL.md", files, dirpath)


if __name__ == "__main__":
    unittest.main()
