import importlib.machinery
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parents[1] / "bin" / "wintermute"
_loader = importlib.machinery.SourceFileLoader("wintermute", str(BIN))
_spec = importlib.util.spec_from_loader("wintermute", _loader)
wm = importlib.util.module_from_spec(_spec)
_loader.exec_module(wm)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._old_dist = wm.DIST
        wm.DIST = self.root / "dist"
        self.skills = wm.DIST / "harness" / "skills"
        (self.skills / "a").mkdir(parents=True)
        self.dest = self.root / "dest"
        self.dest.mkdir()

    def tearDown(self):
        wm.DIST = self._old_dist
        self.tmp.cleanup()

    def test_links_source(self):
        self.assertTrue(wm.link(self.skills / "a", self.dest / "a"))
        self.assertEqual((self.dest / "a").resolve(), (self.skills / "a").resolve())

    def test_replaces_own_link(self):
        (self.skills / "old").mkdir()
        (self.dest / "a").symlink_to(self.skills / "old")
        self.assertTrue(wm.link(self.skills / "a", self.dest / "a"))
        self.assertEqual((self.dest / "a").resolve(), (self.skills / "a").resolve())

    def test_skips_foreign_symlink(self):
        foreign = self.root / "foreign"
        foreign.mkdir()
        (self.dest / "a").symlink_to(foreign)
        self.assertFalse(wm.link(self.skills / "a", self.dest / "a"))
        self.assertEqual((self.dest / "a").readlink(), foreign)

    def test_skips_other_harness_link(self):
        other = wm.DIST / "other" / "skills" / "a"
        other.mkdir(parents=True)
        (self.dest / "a").symlink_to(other)
        self.assertFalse(wm.link(self.skills / "a", self.dest / "a"))
        self.assertEqual((self.dest / "a").readlink(), other)

    def test_skips_real_entry(self):
        (self.dest / "a").mkdir()
        self.assertFalse(wm.link(self.skills / "a", self.dest / "a"))
        self.assertFalse((self.dest / "a").is_symlink())

    def test_points_within_relative_link(self):
        (self.dest / "a").symlink_to(os.path.relpath(self.skills / "a", self.dest))
        self.assertTrue(wm.symlink_points_within(self.dest / "a", self.skills))

    def test_points_within_rejects_foreign(self):
        foreign = self.root / "foreign"
        foreign.mkdir()
        (self.dest / "a").symlink_to(foreign)
        self.assertFalse(wm.symlink_points_within(self.dest / "a", self.skills))

    def test_prunes_dangling_managed_link(self):
        (self.dest / "gone").symlink_to(self.skills / "gone")
        wm.link_all(self.skills, self.dest)
        self.assertFalse((self.dest / "gone").is_symlink())

    def test_prunes_dangling_link_from_other_subdir(self):
        agents = wm.DIST / "harness" / "agents"
        agents.mkdir()
        (self.dest / "gone").symlink_to(agents / "gone")
        wm.link_all(self.skills, self.dest)
        self.assertFalse((self.dest / "gone").is_symlink())

    def test_keeps_dangling_foreign_link(self):
        (self.dest / "gone").symlink_to(self.root / "elsewhere" / "gone")
        wm.link_all(self.skills, self.dest)
        self.assertTrue((self.dest / "gone").is_symlink())

    def test_keeps_live_link(self):
        (self.dest / "a").symlink_to(self.skills / "a")
        wm.link_all(self.skills, self.dest)
        self.assertEqual((self.dest / "a").resolve(), (self.skills / "a").resolve())


class AdoptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._old_dist = wm.DIST
        wm.DIST = self.root / "dist"
        self.claude = self.root / "claude"
        self.agents = self.root / "agents"
        self.dest = self.root / "opencode"
        for d in (self.claude, self.agents):
            d.mkdir()
        (self.claude / "user-skill").mkdir()
        (self.claude / "user-skill" / "SKILL.md").write_text("x")
        managed = wm.DIST / "claude-code" / "skills" / "wt-review"
        managed.mkdir(parents=True)
        (self.claude / "wt-review").symlink_to(managed)

    def tearDown(self):
        wm.DIST = self._old_dist
        self.tmp.cleanup()

    def test_adopts_external_skill(self):
        wm.adopt_external_skills([self.claude, self.agents], self.dest)
        link = self.dest / "user-skill"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), (self.claude / "user-skill").resolve())

    def test_skips_wintermute_managed(self):
        wm.adopt_external_skills([self.claude, self.agents], self.dest)
        self.assertFalse((self.dest / "wt-review").is_symlink())

    def test_skips_existing_entry(self):
        self.dest.mkdir()
        (self.dest / "user-skill").mkdir()
        wm.adopt_external_skills([self.claude, self.agents], self.dest)
        self.assertFalse((self.dest / "user-skill").is_symlink())

    def test_adopts_from_agents_too(self):
        (self.agents / "other-skill").mkdir()
        wm.adopt_external_skills([self.claude, self.agents], self.dest)
        self.assertTrue((self.dest / "other-skill").is_symlink())


class OpencodeCommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._old = (wm.DIST, wm.RULES)
        wm.DIST = self.root / "dist"
        wm.RULES = self.root / "rules.md"
        wm.RULES.write_text("# rules\n")
        self.out = self.root / "out"
        router = self.root / "skills" / "wintermute"
        router.mkdir(parents=True)
        (router / "SKILL.md.tmpl").write_text("x")
        review = self.root / "skills" / "review"
        review.mkdir(parents=True)
        (review / "SKILL.md").write_text("x")
        self.skills = {
            "wintermute": (router, {"name": "wintermute", "description": "R", "tier": "fast"}, "{{table}}\n"),
            "review": (review, {"name": "review", "description": "Rev", "tier": "deep",
                                "agents": ["review-quick"]}, "body\n"),
        }
        self.models = {
            "tiers": {"fast": {"opencode": "m/fast"}, "deep": {"opencode": "m/deep"}},
            "agents": {"review-quick": {"opencode": "m/quick"}},
        }

    def tearDown(self):
        wm.DIST, wm.RULES = self._old
        self.tmp.cleanup()

    def test_command_per_skill(self):
        wm.build_opencode(self.skills, self.models, set(), "wt-", self.out)
        self.assertTrue((self.out / "command" / "wintermute.md").exists())
        self.assertTrue((self.out / "command" / "wt-review.md").exists())

    def test_subskill_command_targets_its_agent(self):
        wm.build_opencode(self.skills, self.models, set(), "wt-", self.out)
        text = (self.out / "command" / "wt-review.md").read_text()
        self.assertIn('agent: "wt-review"', text)

    def test_router_command_runs_in_current_agent(self):
        wm.build_opencode(self.skills, self.models, set(), "wt-", self.out)
        text = (self.out / "command" / "wintermute.md").read_text()
        self.assertNotIn("agent:", text)
        self.assertIn("$ARGUMENTS", text)


if __name__ == "__main__":
    unittest.main()
