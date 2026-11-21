"""Regression: reusable fast century segment orchestration is deterministic.

No participant DOB, profile, identity, or real natal key in these fixtures.
"""
from __future__ import annotations
from datetime import UTC,datetime
from pathlib import Path
import importlib.util
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"scripts/orchestrate_existing_hd_century_segments.py"
SP=importlib.util.spec_from_file_location("hdcentury_orchestrator",SOURCE)
module=importlib.util.module_from_spec(SP)
SP.loader.exec_module(module)

class SegmentOrchestrationTests(unittest.TestCase):
    def t(self,y,m=1,d=1):
        return datetime(y,m,d,tzinfo=UTC)

    def test_decade_segmentation_covers_nonstandard_horizon(self):
        a=self.t(1926,11,19);b=self.t(1951)
        pieces=module.segments(a,b)
        self.assertEqual([x for x,y in pieces],[a,self.t(1930),self.t(1940),self.t(1950)])
        self.assertEqual([y for x,y in pieces],[self.t(1930),self.t(1940),self.t(1950),b])
        self.assertTrue(all(x<y for x,y in pieces))
        self.assertTrue(all(y==z for (x,y),(z,w) in zip(pieces,pieces[1:])))

    def test_century_divides_into_11_contiguous_parts(self):
        pieces=module.segments(self.t(1926,11,19),self.t(2026,11,19))
        self.assertEqual(len(pieces),11)
        self.assertEqual(pieces[0][0],self.t(1926,11,19))
        self.assertEqual(pieces[-1][-1],self.t(2026,11,19))

    def test_source_utc_must_be_explicit(self):
        self.assertEqual(module.utc("2000-01-01T00:00:00Z"),self.t(2000))
        with self.assertRaises(ValueError):
            module.utc("2000-01-01T00:00:00")
        with self.assertRaises(ValueError):
            module.utc("2000-01-01T00:00:00+01:00")

    def test_no_overwrite_or_plan_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"plan.json"
            module.freeze(p,b"freeze\n")
            module.freeze(p,b"freeze\n")
            with self.assertRaises(RuntimeError):
                module.freeze(p,b"replace\n")

    def test_invalid_range_rejected(self):
        with self.assertRaises(ValueError):
            module.segments(self.t(2000),self.t(2000))

if __name__=="__main__":unittest.main()
