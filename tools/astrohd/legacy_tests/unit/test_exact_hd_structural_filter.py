"""Source-neutral regression for querying verified HD structural interval fields.

Never embed a real person's birth date or profile; tests use fabricated charts.
"""
from __future__ import annotations
import importlib.util
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
import unittest

SOURCE=Path(__file__).resolve().parents[2]/"scripts/query_exact_hd_structural_intervals.py"
SP=importlib.util.spec_from_file_location("query_hd_structure",SOURCE)
m=importlib.util.module_from_spec(SP)
SP.loader.exec_module(m)


def make_state(type_="projector",authority="splenic",profile="2/5"):
    return SimpleNamespace(chart_features=SimpleNamespace(
       type=type_,authority=authority,profile=profile,
       defined_centers=("Spleen","G","Throat"),
       channels=("1-8","26-44"),
       activation_gates={"personality:sun":19,"design:sun":44},
    ))

def criteria(**kwargs):
    return {
       "type":kwargs.get("type"),
       "authority":kwargs.get("authority"),
       "profile":kwargs.get("profile"),
       "channels":kwargs.get("channels",()),
       "centers":kwargs.get("centers",()),
       "gates":kwargs.get("gates",{}),
    }

class HDFilterTests(unittest.TestCase):
    def test_type_authority_profile_match(self):
        c=criteria(type="projector",authority="splenic",profile="2/5")
        self.assertTrue(m.score_condition(make_state(),c))
        self.assertFalse(m.score_condition(make_state(profile="5/1"),c))
        self.assertFalse(m.score_condition(make_state(authority="emotional"),c))
        self.assertFalse(m.score_condition(make_state(type_="generator"),c))

    def test_channel_and_activation_are_real_predicates(self):
        self.assertTrue(m.score_condition(make_state(),
              criteria(channels=("1-8",),gates={"personality:sun":19})))
        self.assertFalse(m.score_condition(make_state(),
              criteria(channels=("23-43",))))
        self.assertFalse(m.score_condition(make_state(),
              criteria(gates={"personality:sun":20})))

    def test_positive_centre_not_unset_centre(self):
        self.assertTrue(m.score_condition(make_state(),criteria(centers=("Throat",))))
        self.assertFalse(m.score_condition(make_state(),criteria(centers=("Sacral",))))

    def test_legacy_boolean_is_not_a_valid_gate_filter(self):
        for invalid in ("personality:sun=0","design:moon=65","north_node=19",
                        "personality:sun=abc","design:sun"):
            with self.assertRaises(ValueError):
                m.parse_gate_filter([invalid])

    def test_duplicate_carrier_predicate_fails_closed(self):
        with self.assertRaises(ValueError):
            m.parse_gate_filter(["personality:sun=19","personality:sun=44"])

    def test_utc_aware_requirements(self):
        self.assertEqual(m.parse_utc("2000-01-01T00:00:00Z"),
                         datetime(2000,1,1,tzinfo=timezone.utc))
        with self.assertRaises(ValueError):
            m.parse_utc("2000-01-01T00:00:00")
        with self.assertRaises(ValueError):
            m.parse_utc("2000-01-01T00:00:00+02:00")

if __name__=="__main__":
    unittest.main()
