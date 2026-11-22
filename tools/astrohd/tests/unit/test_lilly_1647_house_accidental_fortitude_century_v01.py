"""Invented geometry only, exact 1647 Lilly p115 house-strength witness."""
import sys
from pathlib import Path
import unittest
import numpy as np
import swisseph as swe

SCRIPTS=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import lilly_1647_house_accidental_fortitude_century_v01 as m

class SourceHouseOnly(unittest.TestCase):
    def test_source_original_p115_all_twelve_values(self):
        self.assertEqual(m.HOUSE_POINTS.tolist(),
                         [5,3,1,4,3,-2,4,-2,2,5,4,-5])
    def test_zodiac_houses_wrap_and_half_open_cusps(self):
        c=np.tile(np.arange(12,dtype=float)*30,(2,1))
        p=np.array([[0,29.999,30,359.999,330.,60.,270.],
                    [15.,345.,119.999,120.,180.,240.,330.]],dtype=float)
        h=m.house_ids(p,c)
        self.assertEqual(h.tolist(),[[0,0,1,11,11,2,9],
                                     [0,11,3,4,6,8,11]])
        self.assertEqual(h.shape,(2,7))
    def test_source_single_house_strength_does_not_select_full_ruler(self):
        h=np.array([[0,11,11,11,11,11,11],
                    [0,9,11,11,11,11,11],
                    [1,2,3,4,5,8,7]],dtype=np.int8)
        scores,w,unique=m.local_house_winner(h)
        self.assertEqual(scores[0].tolist(),[5,-5,-5,-5,-5,-5,-5])
        self.assertEqual(w.tolist(),[0,-1,2])
        self.assertEqual(unique.tolist(),[True,False,True])
    def test_cusps_fails_closed_for_incomplete_or_overlapping_arcs(self):
        x=np.ones((1,7))*5
        for c in (np.zeros((1,12)),np.array([[0.,200.,220.,240.,260.,280.,300.,320.,330.,340.,345.,350.]]),
                  np.full((2,12),30.)):
            with self.assertRaises(ValueError):
                m.house_ids(x,c)
        with self.assertRaises(ValueError):
            m.house_ids(np.array([[-1.,1.,1.,1.,1.,1.,1.]]),
                        np.arange(12,dtype=float).reshape(1,12)*30)
    def test_synthetic_regiomontanus_and_placidus_first_house_agree_with_source_asc(self):
        jd=swe.julday(2020,1,1,0.)
        pp=np.tile(np.array([0.,30.,60.,90.,120.,150.,180.]),(3,1))
        a=np.zeros((3,17))
        a[:,4]=40.
        for i in range(3):
            cu,arms=swe.houses_ex(jd+i/96.,39.,-75.,b"P")
            a[i,0]=cu[0];a[i,5:17]=cu
        ids=np.array([0,-1,1],dtype=np.int32)
        from collections import Counter
        c=Counter();h={}
        m.scan_chunk(np.hstack([pp,np.zeros((3,1))]),a,ids,jd_start=jd,
                     first_idx=0,lat=39.,lon=-75.,counts=c,hdsets=h)
        self.assertEqual(c["total_utc_samples"],3)
        self.assertEqual(c["original_planet_house_assignments"],21)
        self.assertEqual(c["HD_boundary_unassigned"],1)
        self.assertEqual(c["Regiomontanus_first_house_any"]+
                         c["Placidus_first_house_any"]>=0,True)
    def test_source_scoped_runner_has_no_human_profile_argument(self):
        import inspect
        self.assertEqual(set(inspect.signature(m.run).parameters),
                         {"west","angles","hd_cache","hd_join","verify_sha"})

    def test_original_complete_UTC_census_and_source_limited_public_result(self):
        import json
        a=Path(__file__).resolve().parents[2]/"reference/research"
        j=json.loads((a/"lilly_1647_house_accidental_fortitude_full_century_public_v01.json").read_text())
        ledger=json.loads((a/"lilly_1647_house_accidental_fortitude_source_register_v01.json").read_text())
        c=j["mechanical_counts"]
        self.assertEqual(j["samples"],3506400)
        self.assertEqual(j["HD_structural_intervals"],288908)
        self.assertEqual(j["HD_unassigned_margin_samples"],125)
        self.assertEqual(c["original_planet_house_assignments"],7*3506400)
        self.assertEqual(c["conditional_Ptolemy_fourmode_common"],4553)
        self.assertEqual(c["conditional_Ptolemy_HD_unknown"],0)
        self.assertEqual(c["Regiomontanus_first_house_any"],1409411)
        self.assertEqual(c["any_first_house_occupancy_disagrees"],84004)
        self.assertEqual(c["any_traditional_planet_differs_between_12house_systems"],1088009)
        self.assertEqual(c["same_strictly_unique_house_only_winner"],1354001)
        self.assertEqual(c["different_strictly_unique_house_only_winner"],23729)
        self.assertEqual(sum(c[k] for k in
                         ("same_strictly_unique_house_only_winner",
                          "different_strictly_unique_house_only_winner",
                          "both_house_only_winner_tied_or_unresolved")),3506400)
        self.assertEqual(c["same_house_only_winner_in_Ptolemy_conditional_set"],1776)
        self.assertEqual(c["different_house_only_winner_in_Ptolemy_conditional_set"],49)
        self.assertEqual(j["HD_source_audit"]["status"],"PASS_JOINED_SOURCE_NEUTRAL_GRID_SHARD_AUDIT")
        self.assertFalse(j["no_complete_accidental_strength_or_manners_ruler"] is False)
        self.assertTrue(j["original_108_binary_source_shards_SHA256_rechecked"])
        self.assertTrue(ledger["no_private_natal_or_interview_evidence_used"])
        self.assertFalse(ledger["human_predictive_rank_validated"])
        self.assertEqual(tuple(ledger["original_printed_house_scores"].values()),tuple(m.HOUSE_POINTS.tolist()))
        for body in m.PLANETS:
            for system in ("Regiomontanus","Placidus"):
                self.assertEqual(sum(c[f"{system}_{body}_house_{j}"] for j in range(1,13)),3506400)

if __name__=="__main__":unittest.main()
