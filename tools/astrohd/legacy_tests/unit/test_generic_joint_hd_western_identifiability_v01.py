"""Synthetic finite-grid joins only, not the private owner natal chart."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("generic_joint",ROOT/"scripts/audit_generic_joint_hd_western_identifiability_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class GenericCombinedTests(unittest.TestCase):
    def test_exact_joint_membership_and_unresolved(self):
        # Both Moon=1 (Taurus), Mercury=9 (Capricorn) are toy values.
        west=np.zeros((6,8),dtype=float)
        west[:,1]=[35,35,5,35,35,35]
        west[:,2]=[275,275,275,275,50,275]
        hd=np.array([0,1,1,2,3,-1],dtype=np.int32)
        mask=np.array([True,True,False,False],dtype=np.bool_)
        n,u,states=m.compare_west_hd(hd,west,mask,1*12+9)
        self.assertEqual(n,2)
        self.assertEqual(u,1)
        self.assertEqual(states,{0,1})

    def test_identical_hd_not_enough_without_western_signs(self):
        west=np.zeros((2,8),dtype=float)
        west[:,1]=[0,35]
        west[:,2]=[275,20]
        n,u,states=m.compare_west_hd(
            np.array([0,0],dtype=np.int32),west,np.array([True]),1*12+9)
        self.assertEqual(n,0)
        self.assertEqual(states,set())

    def test_western_only_not_enough_without_hd_fingerprint(self):
        west=np.zeros((2,8),dtype=float)
        west[:,1]=35;west[:,2]=275
        n,_,_=m.compare_west_hd(np.array([1,2],dtype=np.int32),
                               west,np.array([True,False,False]),1*12+9)
        self.assertEqual(n,0)

    def test_fails_on_shard_width(self):
        with self.assertRaises(ValueError):
            m.compare_west_hd(np.zeros(1,dtype=np.int32),np.zeros((1,7)),
                              np.array([True]),0)

    def test_fails_on_unverified_out_of_range_index(self):
        with self.assertRaises(ValueError):
            m.compare_west_hd(np.array([100],dtype=np.int32),np.zeros((1,8)),
                              np.array([True]),0)

    def test_fixed_cache_provenance_pinned(self):
        self.assertEqual(m.JOIN_SHA,"b4426125ea94165ad198f6864f8a690b415f77de68560ea6b8a2435bd417ff85")
        self.assertEqual(len(m.GENERIC_CENSUS_SHA),64)
        self.assertEqual(m.CENTURY_MANIFEST_SHA,
                         "a7bec3c4e855d286bbdb93737a58043119cd11ae908c36e73ee118d7d467c746")

if __name__=="__main__":unittest.main()
