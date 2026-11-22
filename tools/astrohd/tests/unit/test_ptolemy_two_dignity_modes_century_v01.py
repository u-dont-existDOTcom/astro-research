"""Ptolemy III.13 first two candidate modes: mechanical regression only."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

HERE=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location(
    "p2",HERE/"scripts/ptolemy_mercury_moon_two_dignity_modes_century_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PtolemySourceGeometryTests(unittest.TestCase):
    def test_natal_longitudes_in_same_sign_share_domicile(self):
        r=m.source_geometry([9.0],[29.99])
        self.assertTrue(r["same_zodiac_sign"][0])
        self.assertTrue(r["same_domicile_lord"][0])
        self.assertTrue(r["any_shared_candidate_in_two_modes"][0])

    def test_different_signs_can_share_domicile(self):
        # Mercury domicile in Gemini AND Virgo, though no same-sign.
        r=m.source_geometry([60.0],[150.0])
        self.assertFalse(r["same_zodiac_sign"][0])
        self.assertTrue(r["same_domicile_lord"][0])

    def test_exaltation_domicile_cross_common_governor(self):
        # Mercury in Aries: domicile ruler Mars, exaltation Sun;
        # Moon in Scorpio: domicile ruler Mars, no exaltation.
        r=m.source_geometry([7.0],[215.0])
        self.assertTrue(r["same_domicile_lord"][0])
        # Mercury in Aries -> Sun exalts, Moon in Leo -> Sun domicile.
        r=m.source_geometry([7.0],[125.0])
        self.assertFalse(r["same_domicile_lord"][0])
        self.assertTrue(r["mercury_exaltation_moon_domicile_lord"][0])

    def test_reverse_cross_candidate(self):
        # Mercury in Leo -> Sun domicile, Moon Aries -> Sun exaltation
        r=m.source_geometry([125.0],[5.0])
        self.assertTrue(r["mercury_domicile_moon_exaltation_lord"][0])

    def test_no_exaltation_does_not_imply_every_sign_has_candidate(self):
        # Aquarius Saturn domicile with Gemini Mercury domicile, neither
        # has exaltation lord for its occupied sign.
        r=m.source_geometry([320.0],[66.0])
        self.assertFalse(r["any_shared_candidate_in_two_modes"][0])

    def test_exaltation_table_has_no_implied_exaltation_lord_for_five_signs(self):
        z=m.EXALTATION
        self.assertEqual(set(np.where(z<0)[0]),{2,4,7,8,10})
        self.assertEqual(len(set(int(x) for x in z if x>=0)),7)

    def test_longitudes_zero_and_just_below_sign_boundary(self):
        r=m.source_geometry([0.0,29.99999,30.0],[0.0,30.,359.99999])
        self.assertEqual(list(r["mercury_sign"]),[0,0,1])
        self.assertEqual(list(r["moon_sign"]),[0,1,11])

    def test_invalid_arrays_rejected(self):
        with self.assertRaises(ValueError):
            m.source_geometry([1.0,2.0],[1.0])
        with self.assertRaises(ValueError):
            m.source_geometry([-0.1],[7.0])
        with self.assertRaises(ValueError):
            m.source_geometry([10.0],[float("nan")])

    def test_source_manifest_contract_rejects_missing_shards(self):
        plan={
            "schema":m.SCHEMA,"record_order":list(m.PLANET_NAMES)+["Mercury_lon_speed"],
            "total_samples":3,"step_minutes":15,"record_bytes":64
        }
        manifest={
            "schema":m.SCHEMA,"total_samples":3,
            "chunks":[{"first_index":0,"count":3,"size_bytes":192,"sha256":"a"*64}]
        }
        self.assertEqual(m.validate_manifest(plan,manifest),3)
        manifest["chunks"][0]["first_index"]=1
        with self.assertRaisesRegex(ValueError,"chronological"):
            m.validate_manifest(plan,manifest)

    def test_legacy_three_way_language_is_not_scored(self):
        doc=(HERE/"reference/research/ptolemy_iii13_natal_character_claims_v1.json").read_text()
        self.assertIn("SOURCE_ADJUDICATION_INCOMPLETE_NO_WESTERN_PROFILE_SCORING",doc)
        source=(HERE/"scripts/ptolemy_mercury_moon_two_dignity_modes_century_v01.py").read_text()
        self.assertIn("does_not_assign_full_ptolemaic_governor",source)
        self.assertIn("term",source)
        self.assertIn("phase_or_aspect",source)
        self.assertNotRegex(source, r"/home/[^/\s]+/(?:Documents|Downloads)/")

if __name__=="__main__":
    unittest.main()
