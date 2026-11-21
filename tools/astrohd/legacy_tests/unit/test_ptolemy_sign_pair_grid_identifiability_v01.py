"""Synthetic Western 15m grid sign-pair identifiability tests; no owner data."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("ptolemy_pair",ROOT/"scripts/audit_ptolemy_sign_pair_grid_identifiability_v01.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fake(signmoon="Taurus",signmercury="Capricorn"):
    return {"reference":{"traditional_planets":{"Moon":{"sign":signmoon},
                                                 "Mercury":{"sign":signmercury}}}}

class PtolemyPairTests(unittest.TestCase):
    def test_zero_and_upper_bound_longitude(self):
        self.assertEqual(m.sign_number([0,29.9,30,359.9]).tolist(),[0,0,1,11])
        with self.assertRaises(ValueError):m.sign_number([360])
        with self.assertRaises(ValueError):m.sign_number([-1])
        with self.assertRaises(ValueError):m.sign_number([np.nan])

    def test_source_pair_independent_of_user_and_known_signs(self):
        self.assertEqual(m.source_pair(fake("Taurus","Capricorn")),1*12+9)
        self.assertEqual(m.source_pair(fake("Aries","Aries")),0)
        with self.assertRaises(ValueError):m.source_pair(fake("NotASign","Taurus"))

    def test_count_all_sign_pairs_not_only_selected_moon_mercury(self):
        a=np.zeros((4,8),dtype="<f8")
        a[:,1]=[31,31,45,150] # moon Taurus Taurus Taurus Virgo
        a[:,2]=[271,271,0,0] # mercury Capricorn Capricorn Aries Aries
        out=m.count_pairs(a)
        self.assertEqual(int(out.sum()),4)
        self.assertEqual(int(out[1*12+9]),2)
        self.assertEqual(int(out[1*12+0]),1)
        self.assertEqual(int(out[5*12+0]),1)

    def test_full_natal_chart_is_explicitly_uncovered(self):
        # Source file documents conditional school rather than pretending
        # the two signs alone are a complete Ptolemaic governor selection.
        source=(ROOT/"scripts/audit_ptolemy_sign_pair_grid_identifiability_v01.py").read_text()
        self.assertIn("NOT complete Ptolemaic governor",source)
        self.assertIn("continuous instants between grid marks",source)

    def test_shard_record_shape_error(self):
        with self.assertRaises(ValueError):m.count_pairs(np.zeros((2,7)))
        with self.assertRaises(ValueError):m.count_pairs(np.zeros(8))

    def test_verified_witness_and_grid_sha_frozen(self):
        self.assertEqual(len(m.WITNESS_SHA),64)
        self.assertEqual(len(m.MANIFEST_SHA),64)
        self.assertEqual(m.EXPECTED_SAMPLES,3506400)

if __name__=="__main__":unittest.main()
