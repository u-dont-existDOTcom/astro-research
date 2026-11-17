"""Invented-data test of the forecast-curve rule counter."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "mastro" / "forecast_rule_test.py"


class ForecastRuleTest(unittest.TestCase):
    def run_tool(self, maximums, events):
        with tempfile.TemporaryDirectory() as d:
            m, e, o = Path(d) / "maximums.json", Path(d) / "events.json", Path(d) / "out.json"
            m.write_text(json.dumps(maximums)); e.write_text(json.dumps(events))
            subprocess.run([sys.executable, str(TOOL), str(m), str(e), str(o)], check=True, capture_output=True)
            return json.loads(o.read_text())

    def test_windows_hits_and_chance(self):
        # one invented theme with five well separated points in an ordinary year
        maximums = {"themes": ["alpha", "beta"], "years": {"2021": {
            "alpha": [[2, 10, 9.0], [4, 10, 8.0], [6, 10, 7.0], [8, 10, 6.0], [10, 10, 5.0], [12, 10, 4.0], [12, 20, 3.0]],
            "beta": [[1, 15, 9.0], [1, 15, 8.5], [1, 16, 8.0], [3, 3, 7.0], [5, 5, 6.0], [7, 7, 5.0], [9, 9, 4.0]]}}}
        events = [{"date": "2021-02-06", "theme": "alpha"},   # 4 days before the first point: inside
                  {"date": "2021-02-05", "theme": "alpha"},   # 5 days before: outside
                  {"date": "2021-04-13", "theme": "alpha"},   # 3 days after the second point: inside
                  {"date": "2021-04-14", "theme": "alpha"},   # 4 days after: outside
                  {"date": "2021-12-10", "theme": "alpha"}]   # the sixth point: outside the five highest
        out = self.run_tool(maximums, events)
        self.assertEqual(out["primary"]["hits"], 2)
        self.assertAlmostEqual(out["primary"]["chance_rate"], 5 * 8 / 365, places=3)   # five windows of eight days
        self.assertEqual(out["primary_7"]["hits"], 3)

    def test_repeated_points_share_a_window(self):
        maximums = {"themes": ["beta"], "years": {"2021": {
            "beta": [[1, 15, 9.0], [1, 15, 8.5], [1, 16, 8.0], [3, 3, 7.0], [5, 5, 6.0], [7, 7, 5.0], [9, 9, 4.0]]}}}
        out = self.run_tool(maximums, [{"date": "2021-07-07", "theme": "beta"}])
        self.assertEqual(out["primary"]["hits"], 0)            # 7 July is the sixth listed point
        self.assertEqual(out["primary_distinct"]["hits"], 1)   # but the fourth separate peak
        self.assertLess(out["primary"]["chance_rate"], 5 * 8 / 365)


if __name__ == "__main__":
    unittest.main()
