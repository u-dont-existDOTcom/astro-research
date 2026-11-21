"""Frozen GENERIC HD mapping structural-identifiability tests; synthetic owners only."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("hd_generic",ROOT/"scripts/audit_generic_frozen_hd_identifiability_v01.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
RULES=mod.frozen_predicates(ROOT/"mappings/mapping_library_v1.json")

def state(profile="2/5",authority="Splenic",centers=("Head","Ajna","Throat","G","Heart","Spleen"),type="Projector",dur=.1,channels=()):
    a,b=(int(z) for z in profile.split("/"))
    return {"type":type,"auth":authority,"profile":profile,"pl":a,"dl":b,
            "centers":frozenset(centers),"dur":dur,
            "channels":frozenset(channels),"gates":frozenset()}

class GenericFrozenHdTests(unittest.TestCase):
    def test_frozen_27_prior_mapping_only(self):
        self.assertEqual(len(RULES),27)
        self.assertEqual({v["feature"] for _,v in RULES},
                         {"type","authority","profile","defined_centers"})
        self.assertTrue(all(v["operator"] in mod.ALLOWED_OPERATORS for _,v in RULES))

    def test_original_mappings_fail_if_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake=Path(tmp)/"map.json"
            fake.write_text('{"model_version":"another"}')
            with self.assertRaisesRegex(RuntimeError,"changed"):
                mod.frozen_predicates(fake)

    def test_equal_observable_signatures_even_when_different_channels(self):
        first=state(channels=((26,44),))
        second=state(channels=((17,62),))
        self.assertEqual(mod.signature(first,RULES),mod.signature(second,RULES))
        out=mod.census([first,second],0,RULES)
        self.assertEqual(out["number_of_intervals_with_same_generic_signature_as_reference"],2)
        self.assertFalse(out["unique_rank_one_identifiability_for_any_score_based_only_on_27_frozen_predicates"])

    def test_no_automatic_personality_calibration(self):
        out=mod.census([state(),state(dur=.2)],0,RULES)
        self.assertTrue(out["no_human_match_proven"])
        self.assertTrue(out["no_scoring_weights_or_questionnaire_answers_used"])
        self.assertAlmostEqual(out["total_days_same_signature_as_reference"],.3)

    def test_different_profile_can_distinguish(self):
        self.assertNotEqual(mod.signature(state("2/5"),RULES),mod.signature(state("3/5"),RULES))

    def test_different_authority_can_distinguish(self):
        self.assertNotEqual(mod.signature(state(authority="Splenic"),RULES),
                            mod.signature(state(authority="Emotional Solar Plexus"),RULES))

    def test_heart_ego_alias_and_undefined_rule(self):
        p={"feature":"defined_centers","operator":"contains_any","values":["Ego"]}
        self.assertTrue(mod.truth(state(centers=("Heart",)),p))
        q={"feature":"defined_centers","operator":"not_contains_any","values":["Will"]}
        self.assertFalse(mod.truth(state(centers=("Heart",)),q))
        self.assertTrue(mod.truth(state(centers=("G",)),q))

    def test_emotional_authority_alias(self):
        p={"feature":"authority","operator":"equals_any","values":["Emotional"]}
        self.assertTrue(mod.truth(state(authority="Emotional Solar Plexus"),p))
        self.assertTrue(mod.truth(state(authority="Solar Plexus"),p))
        self.assertFalse(mod.truth(state(authority="Splenic"),p))

    def test_no_reference_or_empty_group(self):
        with self.assertRaises(ValueError):mod.census([],0,RULES)
        with self.assertRaises(ValueError):mod.census([state()],1,RULES)

    def test_signatures_no_synthetic_target_content(self):
        self.assertEqual(len(mod.frozen_predicates(ROOT/"mappings/mapping_library_v1.json")),27)
        self.assertFalse(any("personality_survey" in str(x) for x in RULES))

if __name__=="__main__":unittest.main()
