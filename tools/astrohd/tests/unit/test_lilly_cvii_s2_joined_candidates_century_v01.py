"""Invented seven-body classical longitudes only; no person/chart source."""
import json
from pathlib import Path
import sys
import unittest

import numpy as np

SRC=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SRC))
import lilly_cvii_s2_actual_joined_planet_candidates_century_v01 as s2

class OriginalJoinedSecondStage(unittest.TestCase):
    def sample(self):
        return np.array([[300.,100.,104.,110.,200.,240.,270.]],dtype=float)

    def test_original_smaller_orb_excludes_larger_venus_contact(self):
        p=self.sample()
        small=s2.candidates_joined_to_moon_or_mercury(p,s2.ORB_OPTIONS["1647_table_smaller_orbs"],s2.SCOPES[0])
        large=s2.candidates_joined_to_moon_or_mercury(p,s2.ORB_OPTIONS["1647_table_larger_orbs"],s2.SCOPES[0])
        # Venus to Moon 10°; small moiety 9.5, large 10.25.
        self.assertFalse(small["moon"][0,3])
        self.assertTrue(large["moon"][0,3])
        self.assertTrue(small["mercury"][0,3])
        self.assertTrue(large["mercury"][0,3])
        self.assertTrue(np.all(~small["union"]|large["union"]))

    def test_original_broad_scope_includes_moon_mercury_mutual(self):
        p=self.sample()
        small=s2.candidates_joined_to_moon_or_mercury(p,s2.ORB_OPTIONS["1647_table_smaller_orbs"],s2.SCOPES[0])
        broad=s2.candidates_joined_to_moon_or_mercury(p,s2.ORB_OPTIONS["1647_table_smaller_orbs"],s2.SCOPES[1])
        self.assertFalse(small["union"][0,1])
        self.assertFalse(small["union"][0,2])
        self.assertTrue(broad["union"][0,1])
        self.assertTrue(broad["union"][0,2])
        self.assertFalse(broad["both"][0,1])
        self.assertFalse(broad["both"][0,2])

    def test_one_external_planet_joins_both_moon_mercury(self):
        p=np.array([[250.,100.,106.,105.,220.,240.,270.]],float)
        v=s2.candidates_joined_to_moon_or_mercury(p,s2.ORB_OPTIONS["1647_table_smaller_orbs"],s2.SCOPES[0])
        self.assertTrue(v["both"][0,3])
        self.assertFalse(v["both"][0,0])
        self.assertEqual(v["both"].shape,(1,7))

    def test_original_conjunction_wraps_at_360(self):
        p=np.array([[5.,357.,1.,359.,200.,240.,270.]],float)
        v=s2.candidates_joined_to_moon_or_mercury(p,s2.ORB_OPTIONS["1647_table_smaller_orbs"],s2.SCOPES[0])
        self.assertTrue(v["moon"][0,3])
        self.assertTrue(v["mercury"][0,3])

    def test_bad_source_shape_or_orbs_refused(self):
        with self.assertRaises(ValueError):
            s2.candidates_joined_to_moon_or_mercury(np.ones((1,8)),np.ones(7),s2.SCOPES[0])
        with self.assertRaises(ValueError):
            s2.candidates_joined_to_moon_or_mercury(np.ones((1,7)),np.ones(7),"operator_picked")
        with self.assertRaises(ValueError):
            s2.candidates_joined_to_moon_or_mercury(np.ones((1,7))*361,np.ones(7),s2.SCOPES[0])

    def test_12_conditional_models_without_human_natal_input(self):
        self.assertEqual(s2.STAGES,12)
        import inspect
        self.assertEqual(set(inspect.signature(s2.run).parameters),
                         {"west","angles","hd_cache","hd_join","verify_sha"})

    def test_actual_complete_source_century_when_present(self):
        p=Path(__file__).resolve().parents[2]/"reference/research/lilly_cvii_s2_original_joining_full_century_public_v01.json"
        if not p.exists():self.skipTest("Full 3.5m immutable source-neutral S2 census not yet computed")
        j=json.loads(p.read_text());c=j["counts"]
        self.assertEqual(j["samples"],3506400)
        self.assertEqual(c["HD_root_uncertain"],125)
        self.assertEqual(c["ptolemy_conditional_four_mode_common"],4553)
        self.assertFalse(j["actual_Lilly_CVII_manners_ruler_computed"])
        self.assertFalse(j["independent_human_behavioral_validation"])
        for mode in s2.MODES:
            for orb in s2.ORB_OPTIONS:
                for scope in s2.SCOPES:
                    tag="|".join((mode,orb,scope))
                    self.assertEqual(c[tag+"|S2_any"],
                                     c[tag+"|S2_one_joined_planet"]+c[tag+"|S2_multiple_joined_planets"])
                    self.assertEqual(c[tag+"|S2_zero_proceed_to_S3"]+c[tag+"|S2_any"],
                                     c[mode+"|S1_empty"])
                    self.assertLessEqual(c[tag+"|S2_joined_to_both_Moon_and_Mercury"],c[tag+"|S2_any"])
        self.assertEqual(j["source_sensitive_S2_eligibility_method_count"],12)

if __name__=="__main__":unittest.main()
