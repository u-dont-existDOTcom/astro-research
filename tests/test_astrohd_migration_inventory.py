"""Private-to-public astrology migration integrity and disclosure boundaries.

This tests only the public ledger and files. The exact historical private
branch remains in an owner-only offline recovery archive, never in public CI.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/astrohd/MIGRATION_INVENTORY_20261121.json"

class MigrationInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta = json.loads(LEDGER.read_text())
        cls.rows = cls.meta["files"]

    def test_all_source_changed_files_are_accounted_for(self):
        self.assertEqual(self.meta["source_changed_file_count"], 123)
        self.assertEqual(self.meta["public_ported_file_count"], 86)
        self.assertEqual(self.meta["retained_private_file_count"], 37)
        self.assertEqual(len(self.rows), 123)
        self.assertEqual(len({r["historical_path"] for r in self.rows}), 123)

    def test_public_paths_exist_and_are_reproducibly_hashed(self):
        for record in self.rows:
            with self.subTest(record=record["historical_path"]):
                dest = record["public_path"]
                if dest is None:
                    self.assertEqual(
                        record["status"], "PRIVATE_RECOVERY_EXACT_PUBLIC_METHOD_SUMMARY_ONLY"
                    )
                    continue
                path = (ROOT / dest).resolve()
                self.assertTrue(path.is_relative_to(ROOT.resolve()))
                self.assertTrue(path.is_file(), dest)
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if record.get("public_sha256"):
                    self.assertEqual(digest, record["public_sha256"])
                else:
                    self.assertEqual(digest, record["sha256"])

    def test_private_source_never_hidden_in_public_directory(self):
        self.assertEqual(
            sum(row["public_path"] is None for row in self.rows), 37
        )
        for r in self.rows:
            if r["public_path"] is None:
                self.assertNotIn("tools/astrohd/", r["historical_path"])

    def test_public_astrohd_has_no_private_personal_locators(self):
        roots = [ROOT / "tools/astrohd", ROOT / "docs/astrohd"]
        all_files = [
            p for base in roots for p in base.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix in (".md",".json",".py")
        ]
        patterns = [
            re.compile(r"/home/[^/\s]+/(?:Documents|Downloads|\.config)/"),
            re.compile(r"\b(?:private_birth_data|private_interview_verbatim|third_party_medical_record)\b", re.IGNORECASE),
            re.compile(r"[\w.%+-]+@(?:gmail|yahoo|outlook)\.com", re.IGNORECASE),
            re.compile(r"\b(?:Jan(?:uary)?\s+29,?\s*1985)\b", re.IGNORECASE),
        ]
        for f in all_files:
            s = f.read_text(errors="replace")
            for exp in patterns:
                self.assertIsNone(exp.search(s), f"{f}: {exp.pattern}")

    def test_public_repo_not_replaced_with_private_engine(self):
        self.assertTrue((ROOT / "engine/astro_engine.py").exists())
        self.assertTrue((ROOT / "engine/hdmatch/chart/calculator.py").exists())
        self.assertIn("ASTRO_RESEARCH_CANONICAL", (ROOT / "AGENTS.md").read_text())
        self.assertIn("verify_active_astrology_repository.py", (ROOT / "README.md").read_text())

    def test_only_one_canonical_new_home(self):
        expected = "u-dont-existDOTcom/astro-research"
        self.assertEqual(self.meta["target_public_repository"], expected)
        self.assertNotIn(
            "humandesign.git", (ROOT / "AGENTS.md").read_text()
        )


if __name__ == "__main__":
    unittest.main()
