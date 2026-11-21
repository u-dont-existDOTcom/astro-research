"""Regression: legacy HD repo may never be silently selected as the write target."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "canonical", ROOT / "scripts" / "verify_active_astrology_repository.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RepositoryRoutingTests(unittest.TestCase):
    def make_repo(self, remote: str, sentinel: bool = True) -> Path:
        self.addCleanup(self.cleanup_temp)
        temp = tempfile.TemporaryDirectory()
        if not hasattr(self, "_temps"):
            self._temps = []
        self._temps.append(temp)
        root = Path(temp.name)
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(root), "remote", "add", "origin", remote],
            check=True, capture_output=True,
        )
        (root / "AGENTS.md").write_text(module.SENTINEL if sentinel else "Old guidance")
        (root / "state").mkdir()
        (root / "state" / "CURRENT-STATE.md").write_text("# Current\n")
        return root

    def cleanup_temp(self) -> None:
        # Each registered cleanup may be called more than once; context owns it.
        for temp in getattr(self, "_temps", []):
            temp.cleanup()
        self._temps = []

    def test_active_https_remote_accepted(self):
        r = self.make_repo("https://github.com/u-dont-existDOTcom/astro-research.git")
        self.assertEqual(module.verify(r)["status"], "CANONICAL_PUBLIC_ASTRO_RESEARCH_CHECKOUT")

    def test_active_ssh_remote_accepted(self):
        r = self.make_repo("git@github.com:u-dont-existDOTcom/astro-research.git")
        self.assertTrue(module.verify(r)["repository_sentinel_present"])

    def test_stale_private_legacy_remote_rejected(self):
        r = self.make_repo("https://github.com/u-dont-existDOTcom/humandesign.git")
        with self.assertRaisesRegex(ValueError, "Wrong canonical"):
            module.verify(r)

    def test_random_repo_rejected(self):
        r = self.make_repo("https://github.com/other/astro-research.git")
        with self.assertRaisesRegex(ValueError, "Wrong canonical"):
            module.verify(r)

    def test_missing_live_owner_instruction_rejected(self):
        r = self.make_repo("https://github.com/u-dont-existDOTcom/astro-research.git", sentinel=False)
        with self.assertRaisesRegex(ValueError, "Missing current"):
            module.verify(r)

    def test_ambiguous_non_github_remote_rejected(self):
        r = self.make_repo("file:///tmp/other-repo.git")
        with self.assertRaisesRegex(ValueError, "Unrecognized GitHub origin"):
            module.verify(r)


if __name__ == "__main__":
    unittest.main()
