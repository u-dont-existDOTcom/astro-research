"""Generic tests for V3.7 behavioral source reannotation of old 44 HD claims.

Use synthetic eligibility codings, never the owner's private questionnaire or
known natal time as a test fixture.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/replay_v37_development_direct_hd_observables.py"
SP=importlib.util.spec_from_file_location("v37_direct_hd",SCRIPT)
m=importlib.util.module_from_spec(SP)
SP.loader.exec_module(m)
PRIOR=ROOT/"scripts/replay_historical_v36_hd_on_verified_cache.py"
SP2=importlib.util.spec_from_file_location("old_44_model",PRIOR)
old=importlib.util.module_from_spec(SP2);SP2.loader.exec_module(old)

class SourceEligibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=old.current_model(ROOT)

    def blank(self):
        return {"schema":"private_v37_profile_review_of_historical_hd_44_rules_v1",
                "source_profile_sha256":m.TARGET_PROFILE_SHA,
                "judgments":{row["id"]:{
                      "status":"postselection_excluded" if row.get("post_selection")
                               else "conditional_or_compound",
                      "rationale":"synthetic test"} for row in self.model["mappings"]}}

    def test_all_source_records_must_be_evaluated(self):
        x=self.blank()
        self.assertEqual(len(m.eligibility_audit(self.model,x)),0)
        x["judgments"].pop(next(iter(x["judgments"])))
        with self.assertRaisesRegex(RuntimeError,"exact 44/44"):
            m.eligibility_audit(self.model,x)

    def test_source_postselected_refinements_must_not_auto_promote(self):
        x=self.blank()
        post=next(row for row in self.model["mappings"] if row.get("post_selection"))
        x["judgments"][post["id"]]["status"]=m.DIRECT
        with self.assertRaisesRegex(RuntimeError,"Postselection"):
            m.eligibility_audit(self.model,x)

    def test_direct_pathway_only_and_unknown_status_fails(self):
        x=self.blank()
        first=next(r for r in self.model["mappings"] if not r.get("post_selection"))
        x["judgments"][first["id"]]["status"]=m.DIRECT
        kept=m.eligibility_audit(self.model,x)
        self.assertEqual([r["id"] for r in kept],[first["id"]])
        x["judgments"][first["id"]]["status"]="independently_validated"
        with self.assertRaisesRegex(ValueError,"coder status"):
            m.eligibility_audit(self.model,x)

    def test_wrong_profile_source_sha_blocks_claim(self):
        x=self.blank()
        x["source_profile_sha256"]="0"*64
        with self.assertRaisesRegex(RuntimeError,"V3.7"):
            m.eligibility_audit(self.model,x)

    def test_canonical_case_adapter_synthetic_features(self):
        fake=SimpleNamespace(type="projector",authority="splenic",
            profile="4/6",definition="single_definition",
            defined_centers=("heart_ego","solar_plexus","g"),
            channels=("23-43","24-61"),
            activations={
              "personality:moon":SimpleNamespace(gate=12),
              "design:mars":SimpleNamespace(gate=35)})
        chart=m.from_engine(fake)
        self.assertEqual(chart["type"],"Projector")
        self.assertEqual(chart["auth"],"Splenic")
        self.assertEqual(chart["pl"],4)
        self.assertEqual(chart["dl"],6)
        self.assertEqual(chart["channels"],frozenset({(23,43),(24,61)}))
        self.assertIn("Solar Plexus",chart["centers"])
        self.assertIn("Heart",chart["centers"])
        self.assertEqual(chart["gates"],frozenset({12,35}))

    def test_utc_requirement(self):
        with self.assertRaises(ValueError):m.utc("2000-01-01T12:00:00")
        self.assertEqual(m.utc("2000-01-01T12:00:00Z").hour,12)

if __name__=="__main__":unittest.main()
