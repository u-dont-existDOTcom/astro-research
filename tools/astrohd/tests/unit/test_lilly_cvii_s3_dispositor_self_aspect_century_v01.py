"""Original 1647 Lilly CVII S3, SX and self-dispositor ambiguous source states.

No personal natal, interviews or actual person names; invented zodiac only.
"""
from pathlib import Path
from collections import Counter
import inspect
import json
import sys
import unittest
import numpy as np
import swisseph as swe

SCRIPTS=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import lilly_cvii_s3_dispositor_other_aspect_self_gap_century_v01 as s


class OriginalThirdStage(unittest.TestCase):
    def test_48_declared_original_source_alternatives(self):
        self.assertEqual(s.STAGE_COUNT,48)
        self.assertEqual(set(s.MODES),set(s.s1.MODES))
        self.assertEqual(len(s.ORBS),2)
        self.assertEqual(len(s.JOIN_SCOPES),2)
        self.assertEqual(len(s.BEHOLDS),2)
        self.assertEqual(len(s.CONTACTS),2)
        self.assertEqual(set(inspect.signature(s.run).parameters),
                         {"west","angles","hd_cache","hd_join","verify_sha"})

    def test_asc_lord_and_true_domicile_dispositor_own_or_distinct(self):
        # ASC Aries => Mars always lord, Mars natal Leo => Sun dispositor
        p=np.array([[20.,110.,130.,150.,145.,180.,200.],
                    [20.,110.,130.,150.,12.,180.,200.]],float)
        lord,disp=s.asc_lord_dispositor_indices(p,np.array([10.,10.]))
        self.assertEqual(lord.tolist(),[4,4])
        self.assertEqual(disp.tolist(),[0,4])
        with self.assertRaises(ValueError):
            s.asc_lord_dispositor_indices(np.ones((1,8)),np.ones(1))

    def test_six_disjoint_source_states_including_new_self_dispositor_abstention(self):
        f=np.array([1,0,0,0,0,0],bool)
        j=np.array([0,1,0,0,0,0],bool)
        d=np.array([0,0,1,0,0,0],bool)
        any_other=np.array([0,0,1,1,1,0],bool)
        self_same=np.array([0,0,0,0,1,0],bool)
        stages=s.source_s3_later_partitions(f,j,d,any_other,self_same)
        expected={"S1":0,"S2":1,"S3":2,"SX":3,"SY":4,"LATER":5}
        self.assertEqual(set(stages),set(expected))
        for key,i in expected.items():
            self.assertTrue(stages[key][i])
            self.assertEqual(int(stages[key].sum()),1)
        with self.assertRaisesRegex(RuntimeError,"Dispositor aspect"):
            s.source_s3_later_partitions(f,j,d,np.zeros(6,bool),self_same)
        with self.assertRaisesRegex(RuntimeError,"Self as own dispositor"):
            s.source_s3_later_partitions(f,j,d,any_other,
                                         np.array([0,0,1,0,1,0],bool))

    def test_source_other_planet_aspect_person_id_and_self_exclusion(self):
        # ASC Aries lord Mars at 5 Leo. Jupiter 5 Sagittarius trine.
        p=np.array([[270.,100.,220.,320.,125.,245.,195.]],float)
        lord,disp,out=s.individual_other_aspector_masks(
           p,np.array([5.]),s.ORBS["1647_table_smaller_orbs"])
        self.assertEqual(lord.tolist(),[4])
        self.assertEqual(disp.tolist(),[0]) # Sun rules Leo
        self.assertFalse(out["dispositor_sign_ray"]["rays_only"][0,4])
        self.assertTrue(out["dispositor_sign_ray"]["rays_only"][0,5])

    def test_reconciled_prior_original_source_full_3p5m_when_published(self):
        p=Path(__file__).resolve().parents[2]/"reference/research/lilly_cvii_s3_original_dispositor_self_other_aspect_full_century_public_v01.json"
        if not p.exists():self.skipTest("Full original source 3.5m sample scan not yet completed")
        j=json.loads(p.read_text());c=j["counts"]
        self.assertEqual(j["samples"],3506400)
        self.assertEqual(j["number_source_S3_SX_self_interpretations"],48)
        self.assertEqual(j["HD_structural_intervals"],288908)
        self.assertEqual(c["HD_root_margin_unknown"],125)
        self.assertEqual(c["conditional_Ptolemy_fourmode_common"],4553)
        self.assertTrue(j["original_96_variant_S1_S2_S3_SX_S4_S5_count_reconciliation"])
        self.assertFalse(j["historically_actual_complete_Lilly_manners_ruler"])
        self.assertFalse(j["independently_validated_human_personality_accuracy"])
        self.assertFalse(j["private_owner_or_thirdparty_natal_case_source_used"])
        for mode in s.MODES:
            for orb in s.ORBS:
                for scope in s.JOIN_SCOPES:
                    for behold in s.BEHOLDS:
                        for aspect in s.CONTACTS:
                            k="|".join((mode,orb,scope,behold,"all="+aspect))
                            self.assertEqual(sum(c[k+"|"+name] for name in
                                ("S1","S2","S3","SY","SX","LATER")),3506400)
                            self.assertEqual(c[k+"|SY"],
                                c[k+"|SY_with_other_aspecting"]+
                                c[k+"|SY_without_other_aspecting"])
                            self.assertEqual(c["Ptolemy_"+k+"|SY"],
                                c["Ptolemy_"+k+"|SY_with_other_aspecting"]+
                                c["Ptolemy_"+k+"|SY_without_other_aspecting"])
                            self.assertEqual(c[k+"|SX"],
                                c[k+"|SX_exactly_one_other_aspector"]+
                                c[k+"|SX_multiple_other_aspectors"])

if __name__=="__main__":unittest.main()
