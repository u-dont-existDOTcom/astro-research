"""Tests for location-scoped planet-independent angles and sect cache.

All fixtures use unrelated calendar dates and generic coordinates; no
participant birth input, chart answer key or surveyed behavior is present.
"""
import importlib.util
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"scripts/western_location_angle_cache.py"
SP=importlib.util.spec_from_file_location("western_location_angles",SRC)
m=importlib.util.module_from_spec(SP)
SP.loader.exec_module(m)
EPHE=Path(__import__("os").environ.get("ASTRO_EPHE", "ephe"))
WEST=Path(__import__("os").environ.get("ASTRO_WESTERN_GRID", "no_private_grid_attached"))

class LocationAnglesTests(unittest.TestCase):
    def test_fixed_float_shape(self):
        self.assertEqual(m.DATA_FORMAT.size,17*8)
        self.assertEqual(m.SOURCE.size,64)

    def test_civil_utc_validation(self):
        self.assertEqual(m.utc("2000-01-01T00:00:00Z"),
                          datetime(2000,1,1,tzinfo=timezone.utc))
        with self.assertRaises(ValueError):
            m.utc("2000-01-01T00:00:00")
        with self.assertRaises(ValueError):
            m.utc("2000-01-01T00:00:00+01:00")

    def test_generic_noon_and_night_sect_and_cusp(self):
        if not EPHE.exists():self.skipTest("Swiss ephemeris files not present")
        m.swe.set_ephe_path(str(EPHE))
        for iso,positive in [
          ("2000-01-01T17:00:00Z",True),
          ("2000-01-01T00:00:00Z",False)]:
            when=m.utc(iso)
            julian=m.swe.julday(when.year,when.month,when.day,
                               when.hour+when.minute/60)
            v,flag=m.swe.calc_ut(julian,m.swe.SUN,m.FLAGS)
            self.assertEqual(flag&m.EPH_MASK,m.swe.FLG_SWIEPH)
            row=m.point(when,39.9526,-75.1636,0.,v[0])
            self.assertEqual(len(row),17)
            self.assertEqual(row[4]>0.,positive)
            self.assertAlmostEqual(row[0],row[5],places=10)
            self.assertTrue(0<=row[0]<360)

    def test_never_accepts_changed_source_solar_position(self):
        if not EPHE.exists():self.skipTest("Swiss ephemeris files not present")
        m.swe.set_ephe_path(str(EPHE))
        when=m.utc("2000-01-01T17:00:00Z")
        jd=m.swe.julday(2000,1,1,17)
        v,_=m.swe.calc_ut(jd,m.swe.SUN,m.FLAGS)
        with self.assertRaisesRegex(RuntimeError,"Source-neutral longitude"):
            m.point(when,39.9526,-75.1636,0.,v[0]+0.01)

    def test_2020_source_plan_location_changes_are_rejected(self):
        if not (WEST/"verified_manifest.json").exists():self.skipTest("2020 grid pilot unavailable")
        args=SimpleNamespace(
            western_index=WEST,ephe=EPHE,
            latitude=39.9526,longitude=-75.1636,elevation=0.)
        plan=m.prepare(args)
        self.assertEqual(plan["sample_count"],35136)
        self.assertEqual(plan["record_bytes"],136)
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"location"
            m.load_or_freeze_plan(target,plan,create=True)
            m.load_or_freeze_plan(target,plan)
            other={**plan,"latitude":40.}
            with self.assertRaisesRegex(RuntimeError,"mismatch"):
                m.load_or_freeze_plan(target,other)

if __name__=="__main__":unittest.main()
