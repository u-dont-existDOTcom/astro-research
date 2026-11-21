"""Tests for source-neutral UTC grid pilot: no private birth dates/profiles."""
from __future__ import annotations
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/western_utc_grid_cache_pilot.py"
SP=importlib.util.spec_from_file_location("western_utc_grid_cache_pilot",SCRIPT)
mod=importlib.util.module_from_spec(SP)
SP.loader.exec_module(mod)
EPHE=Path(__import__("os").environ.get("ASTRO_EPHE", "ephe"))


class FastGridCacheTests(unittest.TestCase):
    def test_utc_requires_explicit_offset_and_integral_minute(self):
        x=mod.utc_parse("2000-01-01T00:00:00Z")
        self.assertEqual(x.utcoffset().total_seconds(),0)
        with self.assertRaises(ValueError):mod.utc_parse("2000-01-01T00:00:00")
        with self.assertRaises(ValueError):mod.utc_parse("2000-01-01T00:00:00+01:00")
        with self.assertRaises(ValueError):mod.epoch_minutes(mod.utc_parse("2000-01-01T00:00:30Z"))

    def test_binary_order_and_longitudes(self):
        self.assertEqual(mod.RECORD.size,64)
        self.assertEqual(len(mod.PLANETS),7)
        if not EPHE.exists():self.skipTest("Swiss assets unavailable on this runner")
        mod.setup(EPHE)
        row=mod.calculate_at(mod.utc_parse("2000-01-01T12:00:00Z"))
        self.assertEqual(len(row),8)
        self.assertTrue(all(0<=x<360 for x in row[:7]))
        self.assertAlmostEqual(row[0],280.3689,places=3)
        self.assertAlmostEqual(mod.RECORD.unpack(mod.RECORD.pack(*row))[3],row[3],places=12)

    def test_plan_build_resume_and_verify_two_small_shards(self):
        if not EPHE.exists():self.skipTest("Swiss assets unavailable on this runner")
        from argparse import Namespace
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"store"
            a=Namespace(start_utc="2005-02-01T00:00:00Z",
                  end_utc="2005-02-01T02:00:00Z",step_minutes=15,
                  chunk_samples=5,ephe=EPHE,out=out,action="plan")
            plan=mod.prepare_plan(a)
            self.assertEqual(plan["total_samples"],8)
            mod.check_plan(out,plan,allow_create=True)
            mod.build(out,plan)
            self.assertEqual(len(list((out/"chunks").glob("*.bin"))),2)
            mod.verify(out,plan)
            v=json.loads((out/"verified_manifest.json").read_text())
            self.assertEqual(v["total_samples"],8)
            self.assertTrue(v["grid_only"])
            before={p.name:mod.sha_file(p) for p in (out/"chunks").iterdir()}
            mod.build(out,plan) # resumes; never overwrites
            after={p.name:mod.sha_file(p) for p in (out/"chunks").iterdir()}
            self.assertEqual(before,after)
            self.assertEqual([x["count"] for x in v["chunks"]],[5,3])

    def test_mismatched_model_window_fails_closed(self):
        if not EPHE.exists():self.skipTest("Swiss assets unavailable on this runner")
        from argparse import Namespace
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"store"
            args=Namespace(start_utc="2005-02-01T00:00:00Z",
                end_utc="2005-02-01T00:45:00Z",step_minutes=15,
                chunk_samples=100,ephe=EPHE)
            model=mod.prepare_plan(args)
            mod.check_plan(out,model,allow_create=True)
            mutated={**model,"step_minutes":5}
            with self.assertRaises(RuntimeError):mod.check_plan(out,mutated,allow_create=False)

    def test_corrupt_shard_is_rejected_before_use(self):
        if not EPHE.exists():self.skipTest("Swiss assets unavailable on this runner")
        from argparse import Namespace
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"store"
            args=Namespace(start_utc="2005-02-01T00:00:00Z",
                end_utc="2005-02-01T00:30:00Z",
                step_minutes=15,chunk_samples=4,ephe=EPHE)
            plan=mod.prepare_plan(args)
            mod.check_plan(out,plan,allow_create=True)
            mod.build(out,plan)
            path=out/"chunks"/"grid_00000.bin"
            raw=bytearray(path.read_bytes())
            raw[0]^=1
            path.write_bytes(raw)
            with self.assertRaises(RuntimeError):
                mod.verify(out,plan)

    def test_source_index_does_not_claim_human_prediction(self):
        self.assertIn("SOURCE-NEUTRAL",mod.SCHEMA.upper())
        self.assertIn("NONCANONICAL",mod.SCHEMA)
        self.assertNotIn("profile",mod.ORDER)
        self.assertEqual(mod.RECORD.size,8*8)


if __name__=="__main__":unittest.main()
