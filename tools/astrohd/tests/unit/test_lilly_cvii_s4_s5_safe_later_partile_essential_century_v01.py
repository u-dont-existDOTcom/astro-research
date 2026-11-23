"""Invented zodiac examples and original source-admission counters only."""
import json
import sys
from pathlib import Path
import unittest
from collections import Counter
import numpy as np
import swisseph as swe
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import lilly_cvii_s4_s5_partile_essential_genuine_later_century_v01 as m

class SourcePartileAndEssentialPlace(unittest.TestCase):
    def test_original_p106_same_numbered_degree_not_modern_one_degree(self):
        # Moon 10° Leo, Mercury 10° Libra, Venus 10° Aries => both rays.
        p=np.array([[5,130.2,190.4,10.9,230,280,330],
                    [5,131.1,190.4,10.9,230,280,330]],dtype=float)
        w=m.partile_body_candidates(p)
        self.assertTrue(w["moon"][0,3])
        self.assertTrue(w["mercury"][0,3])
        self.assertTrue(w["both"][0,3])
        self.assertFalse(w["moon"][1,3])
        self.assertTrue(w["mercury"][1,3])
        self.assertEqual(w[m.PARTILES[0]].shape,(2,7))
        self.assertEqual(w[m.PARTILES[1]].shape,(2,7))
        self.assertFalse(w[m.PARTILES[1]][1,3])
    def test_original_source_three_aspect_vs_nontraditional_same_sign(self):
        p=np.array([[5,130,190,130.5,230,280,330]],dtype=float)
        w=m.partile_body_candidates(p)
        self.assertFalse(w["moon"][0,3])
        self.assertFalse(w["both"][0,3])
        with self.assertRaises(ValueError):
            m.partile_body_candidates(np.ones((2,8)))
        with self.assertRaises(ValueError):
            m.partile_body_candidates(np.ones((2,7))*361)
    def test_restrict_S4_S5_to_genuine_later_not_ambiguous_own_dispositor(self):
        f=np.array([1,0,0,0,0,0],bool)
        j=np.array([0,1,0,0,0,0],bool)
        d=np.array([0,0,1,0,0,0],bool)
        a=np.array([0,0,1,1,1,0],bool)
        own=np.array([0,0,0,0,1,0],bool)
        stage=m.s3.source_s3_later_partitions(f,j,d,a,own)
        join=np.zeros((6,7),bool);join[0,3]=True;join[1,3]=True;join[3,3]=True;join[4,3]=True;join[5,3]=True
        s4,s5=m.source_eligible_S4_S5(stage,join)
        self.assertEqual(s4.tolist(),[False,False,False,False,False,True])
        self.assertFalse(s5.any())
        join[5,3]=False
        s4,s5=m.source_eligible_S4_S5(stage,join)
        self.assertEqual(s5.tolist(),[False,False,False,False,False,True])
        self.assertFalse(s4.any())
        self.assertTrue(stage["SY"][4]);self.assertTrue(stage["SX"][3])
    def test_source_method_count(self):
        self.assertEqual(m.STAGE_METHODS,48)
        self.assertEqual(m.S4_S5_METHODS,96)
        self.assertEqual(m.ALL_S5_SOURCE_POLICIES,576)
        self.assertEqual(len(m.S5_TERMS),3)
        self.assertEqual(len(m.S5_AGGREGATES),2)
    def test_finite_source_UTC_full_century_output_if_available(self):
        p=ROOT/"reference/research/lilly_cvii_s4_s5_genuine_later_full_century_public_v01.json"
        if not p.exists():self.skipTest("Original complete century source scan not yet executed")
        j=json.loads(p.read_text());c=j["counts"]
        self.assertEqual(j["samples"],3506400)
        self.assertEqual(j["HD_structural_interval_total"],288908)
        self.assertEqual(c["HD_root_margin_unknown"],125)
        self.assertEqual(c["conditional_Ptolemy_4mode_possible_common_lord"],4553)
        self.assertTrue(j["old_96_source_S4_S5_and_new_48_S3_LATER_exactly_reconciled"])
        self.assertFalse(j["S4_forcible_aspect_historical_rule_adjudicated"])
        self.assertFalse(j["original_1647_CVII_S5_full_manners_ruler_selected"])
        self.assertTrue(j["no_real_human_personality_prediction"])
        self.assertTrue(j["no_private_natal_birth_interview_or_person_source_evidence_used"])
        for mode in m.MODES:
            for orb in m.ORBS:
                for join in m.JOINS:
                    for behold in m.BEHOLDS:
                        for contact in m.CONTACTS:
                            base="|".join((mode,orb,join,behold,"all="+contact))
                            for part in m.PARTILES:
                                tag=base+"|"+part
                                self.assertEqual(
                                    c[tag+"|S4_GEOMETRIC_possible_forcible_unverified"]+
                                    c[tag+"|S5_NO_geometric_partile"],
                                    c[base+"|genuine_LATER"])
                                self.assertEqual(c[tag+"|S4_GEOMETRIC_possible_forcible_unverified"],
                                    c[tag+"|S4_exactly_one_body"]+c[tag+"|S4_multiple_bodies"])
                                self.assertEqual(c[tag+"|S5_NO_geometric_partile"],
                                    c[tag+"|S5_six_source_same_unique_five_positive_lord"]+
                                    c[tag+"|S5_six_source_tied_or_sect_unknown"])
if __name__=="__main__":unittest.main()
