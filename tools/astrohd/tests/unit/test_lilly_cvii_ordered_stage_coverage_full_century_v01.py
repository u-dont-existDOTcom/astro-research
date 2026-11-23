"""Lilly CVII 1647 invented-data ordered stages; no personal natal evidence."""
import json
import inspect
import sys
from pathlib import Path
import unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import lilly_cvii_ordered_stage_coverage_full_century_v01 as m

class LillyFullOrderFirstEditionSource(unittest.TestCase):
    def test_exhaustive_source_stage_labels_and_methods(self):
        self.assertEqual(m.STAGES,96)
        self.assertEqual(len(m.CODES),11)
        self.assertEqual(m.PROVISIONAL_SINGLE,{1,3,5,10})
        self.assertEqual(set(inspect.signature(m.run).parameters),
                         {"west","site","hd_cache","hd_join","verify_sha"})
    def test_synthetic_all_11_states_and_no_strength_laundering(self):
        n=11
        f=np.zeros((n,7),bool)
        j=np.zeros((n,7),bool)
        part=np.zeros((n,7),bool)
        f[0,2]=1;f[1,0]=1;f[1,1]=1
        j[2,3]=1;j[3,3]=1;j[3,4]=1
        part[7,5]=1;part[8,5]=1;part[8,6]=1
        stage={key:np.zeros(n,bool) for key in ("S1","S2","S3","SY","SX","LATER")}
        stage["S1"][:2]=True
        stage["S2"][2:4]=True
        stage["S3"][4]=True
        stage["SY"][5]=True
        stage["SX"][6]=True
        stage["LATER"][7:]=True
        s5=np.full(n,-1,np.int8);s5[9]=6
        lord=np.full(n,4,np.int8)
        status,who=m.stage_status(f,j,stage,part,s5,lord)
        self.assertEqual(status.tolist(),list(range(1,12)))
        self.assertEqual(who.tolist(),[2,-1,3,-1,4,-1,-1,-1,-1,6,-1])
        self.assertTrue(np.all(who[np.isin(status,[2,4,6,7,8,9,11])]==-1))
    def test_fail_closed_if_missing_original_source_stage_or_inconsistent_input(self):
        f=np.zeros((1,7),bool);j=f.copy();p=f.copy()
        stage={name:np.zeros(1,bool) for name in ("S1","S2","S3","SY","SX","LATER")}
        s5=np.full(1,-1,np.int8)
        with self.assertRaisesRegex(RuntimeError,"dropped"):
            m.stage_status(f,j,stage,p,s5,np.array([4]))
        stage["S1"][0]=True
        with self.assertRaisesRegex(RuntimeError,"S1"):
            m.stage_status(f,j,stage,p,s5,np.array([4]))
        stage["S1"][0]=False
        stage["LATER"][0]=True
        with self.assertRaises(ValueError):
            m.stage_status(np.zeros((1,8),bool),j,stage,p,s5,np.array([4]))
    def test_actual_source_complete_frozen_census_when_published(self):
        p=ROOT/"reference/research/lilly_cvii_ordered_stage_coverage_full_century_public_v01.json"
        if not p.exists():self.skipTest("Full source-complete finite UTC clock not yet executed")
        j=json.loads(p.read_text());c=j["counts"]
        self.assertEqual(j["samples"],3506400)
        self.assertEqual(j["original_96_stage_path_scenarios"],96)
        self.assertEqual(j["HD_structural_intervals"],288908)
        self.assertEqual(c["HD_root_margin_unassigned"],125)
        self.assertEqual(c["Ptolemy_conditional_fourmode_common"],4553)
        self.assertTrue(j["old_source_S3_S4_S5_counts_all96_reproduced_exactly"])
        self.assertTrue(j["forcible_partile_1647_original_still_unadjudicated"])
        self.assertTrue(j["source_unknown_SX_SY_states_retained"])
        self.assertFalse(j["historically_selected_single_final_manners_ruler"])
        self.assertFalse(j["independent_human_personality_accuracy"])
        self.assertFalse(j["private_natal_interview_ratings_used"])
        for mode in m.MODES:
            for orb in m.ORBS:
                for join in m.JOINS:
                    for behold in m.BEHOLDS:
                        for other in m.CONTACTS:
                            for part in m.PARTILES:
                                key="|".join((mode,orb,join,behold,"all="+other,part))
                                self.assertEqual(sum(c[key+"|"+stage] for stage in m.CODES),3506400)
                                self.assertEqual(c[key+"|source_primary_conditional_candidate"]+
                                                 c[key+"|historical_strength_or_rule_not_unique"],3506400)
        self.assertEqual(
            c["cross96_same_provisional_primary_candidate"]+
            c["cross96_stage_agrees_but_no_single_provisional_body"]+
            c["cross96_stages_disagree"],3506400)
        self.assertEqual(sum(c["cross96_same_stage_"+m.LABELS[x]+"|same_primary_body"] for x in m.PROVISIONAL_SINGLE),
                         c["cross96_same_provisional_primary_candidate"])
        for x in m.PROVISIONAL_SINGLE:
            key="cross96_same_stage_"+m.LABELS[x]
            self.assertEqual(c[key+"|same_primary_body"]+c[key+"|different_primary_body"],c[key])
        for name in ("S3_asc_lord","S5_positive_place_same_unique_six_models"):
            self.assertEqual(c["cross96_same_stage_"+name+"|different_primary_body"],0)
if __name__=="__main__":unittest.main()
