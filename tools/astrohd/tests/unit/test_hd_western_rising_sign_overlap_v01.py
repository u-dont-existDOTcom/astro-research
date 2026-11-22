"""A cross-system structural astronomical test is NOT an HD personality test."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
p=ROOT/"scripts/audit_hd_western_rising_sign_overlap_v01.py"
sp=importlib.util.spec_from_file_location("overlap",p)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)


class CrossSystemStructuralTests(unittest.TestCase):
    def test_valid_multiple_rising_signs_with_same_hd_state(self):
        ids,sgn,unknown=m.classify_ids_and_rising(
            np.array([0,0,0,1,-1],dtype=np.int32),
            np.array([1.,31.,61.,25.,90.]),3)
        self.assertEqual(list(ids),[0,0,0,1])
        self.assertEqual(list(sgn),[0,1,2,0])
        self.assertEqual(unknown,1)

    def test_out_of_range_hd_state_fails(self):
        with self.assertRaisesRegex(ValueError,"outside"):
            m.classify_ids_and_rising([3],[15.],3)

    def test_out_of_range_asc_fails(self):
        for value in (-1,360,float("nan")):
            with self.assertRaisesRegex(ValueError,"Invalid ASC"):
                m.classify_ids_and_rising([0],[value],2)

    def test_mismatched_length_fails(self):
        with self.assertRaisesRegex(ValueError,"Shape"):
            m.classify_ids_and_rising([0,1],[18.],2)

    def test_valid_identical_manifest_sample_census(self):
        j={"schema":m.HD_SCHEMA,"total_utc_grid_samples":3,
           "total_hd_structural_intervals":10,"step_minutes":15,
           "shards":[{"count":3,"index_first":0}]}
        a={"schema":m.ANGLE_SCHEMA,"total_samples":3,
           "shards":[{"count":3,"first_index":0}]}
        self.assertEqual(m.validate(j,a),(3,10))

    def test_manifest_dropped_shard_fails(self):
        j={"schema":m.HD_SCHEMA,"total_utc_grid_samples":3,
           "total_hd_structural_intervals":10,"step_minutes":15,
           "shards":[{"count":2,"index_first":0}]}
        a={"schema":m.ANGLE_SCHEMA,"total_samples":3,
           "shards":[{"count":2,"first_index":0}]}
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            m.validate(j,a)

    def test_manifest_bad_first_index_fails(self):
        j={"schema":m.HD_SCHEMA,"total_utc_grid_samples":3,
           "total_hd_structural_intervals":10,"step_minutes":15,
           "shards":[{"count":3,"index_first":1}]}
        a={"schema":m.ANGLE_SCHEMA,"total_samples":3,
           "shards":[{"count":3,"first_index":1}]}
        with self.assertRaisesRegex(ValueError,"Noncontiguous"):
            m.validate(j,a)

    def test_no_private_natal_or_personal_scoring_in_source(self):
        text=p.read_text()
        self.assertIn("NOT a personality score",text)
        self.assertNotIn("1985",text)
        self.assertNotIn("/home/joel",text)
        self.assertIn("source_location_policy",text)

if __name__=="__main__":
    unittest.main()
