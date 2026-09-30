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


if __name__ == "__main__":
    unittest.main()
