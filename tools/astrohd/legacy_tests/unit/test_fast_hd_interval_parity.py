"""Boundary integrity regressions with invented feature strings and timestamps.

The real SwissEph parity checks run separately over explicit source-neutral
dated shards; no owner's natal chart enters these tests.
"""
from __future__ import annotations

from datetime import datetime,timedelta,timezone
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

SCRIPT=Path(__file__).resolve().parents[2]/"scripts/audit_fast_hd_structural_intervals.py"
SP=importlib.util.spec_from_file_location("audit_fast_hd_structural_intervals",SCRIPT)
audit=importlib.util.module_from_spec(SP)
SP.loader.exec_module(audit)
GRID=Path(__file__).resolve().parents[2]/"scripts/audit_fast_hd_state_grid.py"
SP2=importlib.util.spec_from_file_location("audit_fast_hd_state_grid",GRID)
grid=importlib.util.module_from_spec(SP2)
SP2.loader.exec_module(grid)


class ExactStateAuditTests(unittest.TestCase):
    def setUp(self):
        self.start=datetime(2000,1,1,tzinfo=timezone.utc)
        self.mid=self.start+timedelta(hours=1)
        self.end=self.start+timedelta(hours=2)
        self.exact=((self.start,self.mid,"A"),(self.mid,self.end,"B"))

    def fast(self,boundary_shift_seconds=0,features=("A","B")):
        new_mid=self.mid+timedelta(seconds=boundary_shift_seconds)
        return (
            SimpleNamespace(start_utc=self.start,end_utc=new_mid,chart_features=features[0]),
            SimpleNamespace(start_utc=new_mid,end_utc=self.end,chart_features=features[1]),
        )

    def test_exact_partition_passes(self):
        self.assertEqual(
          audit.audit_pairs(self.exact,self.fast(),self.start,self.end,tolerance_seconds=.1),
          0.)

    def test_numeric_crossing_within_tolerance_passes(self):
        self.assertAlmostEqual(
           audit.audit_pairs(self.exact,self.fast(.006),self.start,self.end,
                             tolerance_seconds=.1),.006)

    def test_missing_structural_event_fails_closed(self):
        short=(SimpleNamespace(start_utc=self.start,end_utc=self.end,chart_features="A"),)
        with self.assertRaisesRegex(ValueError,"Number"):
            audit.audit_pairs(self.exact,short,self.start,self.end,tolerance_seconds=.1)

    def test_larger_event_time_shift_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"Transition drift"):
            audit.audit_pairs(self.exact,self.fast(.5),self.start,self.end,tolerance_seconds=.1)

    def test_well_timed_but_wrong_feature_rejected(self):
        with self.assertRaisesRegex(ValueError,"Structural feature mismatch"):
            audit.audit_pairs(self.exact,self.fast(features=("A","WRONG")),
                              self.start,self.end,tolerance_seconds=.1)

    def test_incomplete_horizon_is_rejected(self):
        fast=(SimpleNamespace(start_utc=self.start+timedelta(seconds=1),
                              end_utc=self.mid,chart_features="A"),
              SimpleNamespace(start_utc=self.mid,end_utc=self.end,
                              chart_features="B"))
        with self.assertRaisesRegex(ValueError,"span"):
            audit.audit_pairs(self.exact,fast,self.start,self.end,tolerance_seconds=.1)

    def test_grid_index_and_boundary_guard(self):
        state=self.fast()
        self.assertEqual(grid.state_index_at(state,self.start),0)
        self.assertEqual(grid.state_index_at(state,self.mid),1)
        with self.assertRaises(RuntimeError):
            grid.state_index_at(state,self.end)
        self.assertTrue(grid.is_near_transition(state[0],self.start,.2))
        self.assertTrue(grid.is_near_transition(state[0],self.mid-timedelta(seconds=.1),.2))
        self.assertFalse(grid.is_near_transition(state[0],self.start+timedelta(minutes=15),.2))

if __name__=="__main__":unittest.main()
