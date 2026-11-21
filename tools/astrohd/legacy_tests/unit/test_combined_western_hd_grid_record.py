"""Generic source-neutral grid record assembly acceptance tests."""
from __future__ import annotations
import importlib.util
from datetime import UTC,datetime
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[2]/"scripts/lookup_combined_western_hd_grid_chart.py"
spec=importlib.util.spec_from_file_location("composite_natal_record",SOURCE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class CombinedSourceGridTests(unittest.TestCase):
    def setUp(self):
        self.plan={"utc_start_inclusive":"2000-01-01T00:00:00+00:00",
                   "utc_end_exclusive":"2000-01-02T00:00:00+00:00",
                   "step_minutes":15,"total_samples":96}

    def test_valid_grid_index_exact(self):
        self.assertEqual(mod.position_for_grid(mod.utc("2000-01-01T00:00:00Z"),self.plan),0)
        self.assertEqual(mod.position_for_grid(mod.utc("2000-01-01T12:00:00Z"),self.plan),48)
        self.assertEqual(mod.position_for_grid(mod.utc("2000-01-01T23:45:00Z"),self.plan),95)

    def test_reject_non_grid_minute(self):
        with self.assertRaisesRegex(ValueError,"not EXACTLY"):
            mod.position_for_grid(mod.utc("2000-01-01T00:07:00Z"),self.plan)

    def test_reject_outside_horizon(self):
        for dt in ("1999-12-31T23:45:00Z","2000-01-02T00:00:00Z"):
            with self.assertRaisesRegex(ValueError,"outside"):
                mod.position_for_grid(mod.utc(dt),self.plan)

    def test_source_shard_offsets(self):
        shards=[{"first_index":0,"count":4},{"first_index":4,"count":2}]
        self.assertEqual(mod.get_shard(shards,0,"first_index","count")[1],0)
        self.assertEqual(mod.get_shard(shards,5,"first_index","count")[1],1)
        with self.assertRaises(RuntimeError):
            mod.get_shard(shards,7,"first_index","count")

    def test_exaltation_and_debility_exact(self):
        self.assertTrue(mod.dignity("Moon",42.)["exaltation"])
        self.assertTrue(mod.dignity("Venus",357.)["exaltation"])
        self.assertTrue(mod.dignity("Jupiter",298.)["fall"])
        self.assertFalse(mod.dignity("Mercury",295.)["domicile"])

    def test_all_pair_relations_returned(self):
        data={n:{"longitude":(i*60)%360} for i,n in enumerate(mod.PLANETS)}
        a=mod.major_aspects(data)
        self.assertEqual(len(a),21)
        self.assertTrue(any(item["nearest_major_aspect"]=="conjunction" for item in a))

    def test_utc_offset_explicit(self):
        self.assertEqual(mod.utc("2000-01-01T00:00:00Z"),datetime(2000,1,1,tzinfo=UTC))
        with self.assertRaises(ValueError):
            mod.utc("2000-01-01T00:00:00")

if __name__=="__main__":unittest.main()
