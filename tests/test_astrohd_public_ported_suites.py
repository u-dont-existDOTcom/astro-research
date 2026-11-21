"""Public AstroHD subset: synthetic tests only; never score real private births."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PortedAstroResearchTests(unittest.TestCase):
    def _run(self, *command: str) -> None:
        result = subprocess.run(
            [sys.executable, *command],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(
            result.returncode, 0,
            f"Failed public AstroHD test command: {command}\n"
            + result.stdout[-3500:]
            + result.stderr[-3500:],
        )

    def test_ported_self_contained_contracts(self):
        self._run(
            "-m", "unittest", "discover", "-s", "tools/astrohd/tests/unit",
            "-p", "test_*.py", "-q",
        )

    def test_ported_grid_and_interview_synthetic(self):
        self._run("tools/astrohd/tests/test_century_grid_query_and_interview.py", "-q")

    def test_ported_utc_grid_synthetic(self):
        self._run("tools/astrohd/tests/test_western_utc_grid_cache_pilot.py", "-q")

if __name__ == "__main__":
    unittest.main()
