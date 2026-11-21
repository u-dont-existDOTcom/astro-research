"""Synthetic mutants against nonrepresentative forum-screening claims."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("forum_audit",ROOT/"scripts/audit_disputed_predictor_corpus_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
PROTO=json.loads((ROOT/"reference/research/disputed_predictor_forum_audit_protocol_v01.json").read_bytes())
SEED=json.loads((ROOT/"reference/research/disputed_predictor_forum_seed_v01.json").read_bytes())

class ForumAuditTests(unittest.TestCase):
    def test_coverage_without_prevalence(self):
        result=m.audit(PROTO,SEED)
        self.assertEqual(result["source_claims_registered"],16)
        self.assertEqual(result["sampled_evidence_units"],28)
        self.assertEqual(len(result["stratum_coverage"]),8)
        self.assertFalse(result["any_per_system_top_frequency_rank_supported"])
        self.assertEqual(result["prospective_verified_prediction_records"],0)
        self.assertEqual(result["stratum_coverage"]["chinese_ziwei"]["claims_registered"],1)

    def test_no_unacknowledged_population_denominator(self):
        altered=copy.deepcopy(SEED)
        altered["claims"][0]["forum_population_denominator"]=20
        with self.assertRaisesRegex(RuntimeError,"invent"):
            m.audit(PROTO,altered)

    def test_disconfirming_claim_prospective_not_assumed(self):
        altered=copy.deepcopy(SEED)
        altered["evidence"][0]["prospective_prediction_record_verified"]=True
        with self.assertRaisesRegex(RuntimeError,"Prospective"):
            m.audit(PROTO,altered)

    def test_cannot_claim_previously_calibrated_accuracy(self):
        altered=copy.deepcopy(SEED)
        altered["evidence"][0]["scorable_accuracy_result"]=True
        with self.assertRaisesRegex(RuntimeError,"not a calibrated"):
            m.audit(PROTO,altered)

    def test_no_duplicate_evidence_count(self):
        altered=copy.deepcopy(SEED)
        altered["evidence"].append(copy.deepcopy(altered["evidence"][0]))
        with self.assertRaisesRegex(ValueError,"Repeated evidence"):
            m.audit(PROTO,altered)

    def test_source_link_required(self):
        altered=copy.deepcopy(SEED)
        altered["evidence"][0]["url"]="http://bad.example"
        with self.assertRaisesRegex(ValueError,"attribution"):
            m.audit(PROTO,altered)

    def test_broad_family_preservation(self):
        altered=copy.deepcopy(PROTO)
        altered["frozen_strata"]=altered["frozen_strata"][:-1]
        with self.assertRaisesRegex(RuntimeError,"coverage reduced"):
            m.audit(altered,SEED)

    def test_gene_keys_and_ziwei_not_conflated_with_failure(self):
        byid={x["id"]:x for x in SEED["claims"]}
        self.assertEqual(byid["GENEKEYS_SHADOW_GIFT"]["disposition"],"NOT_A_PREDICTION")
        self.assertEqual(byid["ZIWEI_ASTRO_AI_READING"]["disposition"],"CALCULATION_PARITY_ONLY")
        self.assertFalse(m.audit(PROTO,SEED)["any_per_system_top_frequency_rank_supported"])

    def test_no_falsification_from_unobserved_technical_error(self):
        altered=copy.deepcopy(SEED)
        altered["evidence"][-1]["evidence_type"]="unsupported_true_research_result"
        with self.assertRaisesRegex(ValueError,"evidence class"):
            m.audit(PROTO,altered)

if __name__=="__main__":
    unittest.main()
