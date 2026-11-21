"""Source-neutral Western-grid-to-exact-HD interval join regression tests."""
from __future__ import annotations
import importlib.util
from datetime import datetime,UTC
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
HAS_NUMPY=importlib.util.find_spec("numpy") is not None
if HAS_NUMPY:
    import numpy as np
    SP=importlib.util.spec_from_file_location(
        "join_western_hd",ROOT/"scripts/join_western_grid_exact_hd_structures.py")
    m=importlib.util.module_from_spec(SP)
    SP.loader.exec_module(m)

@unittest.skipUnless(HAS_NUMPY,"requires optional NumPy")
class HDGridJoinTests(unittest.TestCase):
    def setUp(self):
        self.starts=np.array([0,3_000_000_000,8_000_000_000],dtype=np.int64)
        self.ends=np.array([3_000_000_000,8_000_000_000,10_000_000_000],dtype=np.int64)

    def test_assigns_every_interior_sample_to_one_state(self):
        s=np.array([1_000_000_000,4_000_000_000,9_000_000_000],dtype=np.int64)
        out,flag=m.lookup(s,self.starts,self.ends,0)
        self.assertEqual(out.tolist(),[0,1,2])
        self.assertFalse(flag.any())

    def test_ambiguous_boundary_retains_unresolved_sentinel(self):
        s=np.array([0,3_000_000_000,8_000_000_000,
                    2_900_000_000,4_000_000_000],dtype=np.int64)
        out,flag=m.lookup(s,self.starts,self.ends,200_000_000)
        self.assertEqual(out.tolist(),[-1,-1,-1,-1,1])
        self.assertEqual(flag.tolist(),[True,True,True,True,False])

    def test_missing_cache_interval_detected(self):
        start=np.array([0,4_000_000_000],dtype=np.int64)
        end=np.array([2_000_000_000,10_000_000_000],dtype=np.int64)
        with self.assertRaisesRegex(RuntimeError,"uncovered"):
            m.lookup(np.array([3_000_000_000],dtype=np.int64),start,end,0)

    def test_outside_horizon_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,"(?i)uncovered"):
            m.lookup(np.array([-1],dtype=np.int64),self.starts,self.ends,0)
        with self.assertRaisesRegex(RuntimeError,"(?i)uncovered"):
            m.lookup(np.array([10_000_000_000],dtype=np.int64),self.starts,self.ends,0)

    def test_epoch_nanoseconds_preserve_microseconds(self):
        self.assertEqual(m.ns(datetime(1970,1,1,0,0,0,1,tzinfo=UTC)),1000)
        self.assertEqual(m.ns(datetime(1969,12,31,23,59,59,999999,tzinfo=UTC)),-1000)

if __name__=="__main__":unittest.main()
