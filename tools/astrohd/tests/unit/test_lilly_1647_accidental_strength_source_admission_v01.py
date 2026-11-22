"""Invented source-ledger mutations only: no participant or birth records."""
from pathlib import Path
from copy import deepcopy
import importlib.util
import json
import unittest

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"scripts/audit_lilly_1647_accidental_strength_admission_v01.py"
spec=importlib.util.spec_from_file_location("source_gate_1647",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
REGISTER=ROOT/"reference/research"

class OriginalFortitudeCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig=(REGISTER/m.LEDGER).read_bytes()
        cls.prior=(REGISTER/m.PRIOR).read_bytes()
    def audit(self,obj):
        return m.audit(json.dumps(obj).encode(),self.prior)
    def test_real_original_page_and_known_missing_status(self):
        o=m.audit(self.orig,self.prior)
        self.assertEqual(o["status"],"PASS_ORIGINAL_1647_ACCIDENTAL_FULL_STRENGTH_BLOCKED")
        self.assertGreaterEqual(o["original_source_rules"],34)
        self.assertGreater(o["blocked_required_components"],15)
        self.assertFalse(o["historical_final_manners_ruler_scored"])
        self.assertFalse(o["human_predictive_validation"])
    def test_mutual_reception_detriment_peregrine_present_as_unmodeled(self):
        s=json.loads(self.orig)
        rules={x["id"]:x for x in s["original_first_print_scored_components"]}
        self.assertEqual(rules["domicile_or_mutual_reception_by_house"]["points"],5)
        self.assertEqual(rules["exaltation_or_mutual_reception_by_exaltation"]["points"],4)
        self.assertEqual(rules["detriment"]["points"],-5)
        self.assertEqual(rules["fall"]["points"],-4)
        self.assertEqual(rules["peregrine"]["points"],-5)
        self.assertNotEqual(rules["detriment"]["implementation_status"],"IMPLEMENTED")
        self.assertFalse(s["prior_source_bound_output"]["actual_1647_complete_essential_dignity_with_receptions_and_penalties"])
    def test_fails_if_source_page_hash_tampered(self):
        x=json.loads(self.orig);x["source"]["original_page_render_sha256"]["115"]="0"*64
        with self.assertRaisesRegex(ValueError,"p115"):
            self.audit(x)
    def test_fails_if_prior_study_laundered_as_full_ruler(self):
        x=json.loads(self.orig)
        x["prior_source_bound_output"]["source_unique_Lilly_manners_ruler"]=True
        with self.assertRaisesRegex(ValueError,"Partial"):
            self.audit(x)
    def test_fails_if_fortitude_debility_polarity_reversed(self):
        x=json.loads(self.orig)
        next(z for z in x["original_first_print_scored_components"] if z["id"]=="retrograde")["points"]=5
        with self.assertRaisesRegex(ValueError,"polarity"):
            self.audit(x)
    def test_fails_if_malformed_stellar_source_accepted(self):
        x=json.loads(self.orig)
        next(z for z in x["original_first_print_scored_components"] if z["id"]=="malefic_partile_contact")["implementation_status"]="IMPLEMENTED"
        with self.assertRaisesRegex(ValueError,"glyph"):
            self.audit(x)
    def test_fails_if_missing_input_becomes_pretend_full_model(self):
        x=json.loads(self.orig)
        x["certified_software_inputs"]["complete_all_fortitude_rules_from_existing_cached_columns"]=True
        with self.assertRaisesRegex(ValueError,"Missing"):
            self.audit(x)
    def test_fails_if_historical_source_row_deleted(self):
        x=json.loads(self.orig)
        x["original_first_print_scored_components"]=[r for r in x["original_first_print_scored_components"] if r["id"]!="peregrine"]
        with self.assertRaisesRegex(ValueError,"missing source rules"):
            self.audit(x)
    def test_earlier_3_5m_source_neutral_aggregate_unchanged(self):
        z=json.loads(self.prior)
        self.assertEqual(z["samples"],3506400)
        self.assertEqual(z["sample_counts"]["ptolemy_four_mode_common"],4553)
        self.assertFalse(z["actual_Lilly_manners_ruler_computed"])
        self.assertFalse(z["personal_birth_or_interview_used"])

if __name__=="__main__":unittest.main()
