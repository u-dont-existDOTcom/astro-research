"""Synthetic cross-system/source check of Lilly CVII's first geometrical branch."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
S=ROOT/"scripts/lilly_cvii_initial_geom_grid_census_v01.py"
sp=importlib.util.spec_from_file_location("lillygeom",S)
lilly=importlib.util.module_from_spec(sp);sp.loader.exec_module(lilly)


class LillyFirstRungTests(unittest.TestCase):
    def test_categories_disjoint_and_development_scope(self):
        asc=np.array([0,0,0,0,0],dtype=float)
        p=np.array([
            [95,190,220,250,280,310,330], # none in Aries
            [95,190,5,250,280,310,330], # Mercury
            [95,190,5,15,280,310,330], # Mercury Venus
            [5,10,100,250,280,310,330], # Sun Moon
            [5,190,100,250,280,310,15] # Sun Saturn
        ],dtype=float)
        out=lilly.classifications(asc,p)
        for i,key in enumerate(("none_in_asc_sign","one_nonlum_only","multiple_nonlum_only","luminaries_only","nonlum_and_luminaries")):
            self.assertEqual(out[key].sum(),1,key)
            self.assertTrue(out[key][i],key)

    def test_normalized_angles_are_mandatory(self):
        for bad in (-0.1,360.0,float("nan")):
            with self.assertRaises(ValueError):
                lilly.classifications([bad],np.ones((1,7))*90.)

    def test_planet_shape_fails_closed(self):
        with self.assertRaises(ValueError):
            lilly.classifications([32.],np.ones((1,8)))

    def test_valid_reference_header(self):
        wp={"schema":"western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL",
            "record_order":list(lilly.PLANETS)+["Mercury_lon_speed"],
            "step_minutes":15,"record_bytes":64,"total_samples":2,
            "utc_start_inclusive":"2000-01-01T00:00:00Z",
            "utc_end_exclusive":"2000-01-01T00:30:00Z"}
        ap={"schema":"location-conditioned-western-angles-utc-grid-v1-NONCANONICAL",
            "cols":["asc"],"step_minutes":15,"record_bytes":136,
            "sample_count":2,"utc_start":"2000-01-01T00:00:00Z",
            "utc_end_exclusive":"2000-01-01T00:30:00Z"}
        wm={"total_samples":2,"chunks":[{"first_index":0,"count":2}]}
        am={"total_samples":2,"shards":[{"count":2}]}
        self.assertEqual(lilly.check_manifest(wp,wm,ap,am),2)
        ap["sample_count"]=3
        with self.assertRaisesRegex(RuntimeError,"Record count"):
            lilly.check_manifest(wp,wm,ap,am)

    def test_manifest_unaligned_shard_fails(self):
        wp={"schema":"western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL",
            "record_order":list(lilly.PLANETS)+["Mercury_lon_speed"],
            "step_minutes":15,"record_bytes":64,"total_samples":2,
            "utc_start_inclusive":"2000-01-01T00:00:00Z",
            "utc_end_exclusive":"2000-01-01T00:30:00Z"}
        ap={"schema":"location-conditioned-western-angles-utc-grid-v1-NONCANONICAL",
            "cols":["asc"],"step_minutes":15,"record_bytes":136,"sample_count":2,
            "utc_start":"2000-01-01T00:00:00Z","utc_end_exclusive":"2000-01-01T00:30:00Z"}
        with self.assertRaisesRegex(RuntimeError,"Missing or repeated"):
            lilly.check_manifest(wp,{"total_samples":2,"chunks":[{"first_index":1,"count":2}]},
                                 ap,{"total_samples":2,"shards":[{"count":2}]})

    def test_typed_source_policy_never_claims_personality(self):
        data=json.loads((ROOT/"reference/research/lilly_cvii_initial_manners_source_register_v01.json").read_text())
        self.assertEqual(data["status"],"SOURCE_INITIAL_BRANCH_PARTIALLY_CODED_NO_MANNERS_PERSONALITY_SCORE")
        self.assertFalse(data["rank_eligible"])
        self.assertFalse(data["human_behavior_validated"])

    def test_no_birth_or_personal_profile_constants(self):
        s=S.read_text()
        self.assertNotIn("1985",s)
        self.assertNotIn("/home/joel",s)
        self.assertIn("not continuous",s.lower())

    def test_rising_sign_membership_does_not_count_houses_as_source(self):
        out=lilly.classifications([359.9],[[0,30,60,90,120,150,359.8]])
        self.assertTrue(out["one_nonlum_only"][0])

if __name__=="__main__":unittest.main()
