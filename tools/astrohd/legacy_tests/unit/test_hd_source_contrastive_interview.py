"""Generic source-predicate contrast interviews: nonleading public vs sealed key."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
S=ROOT/"scripts/prepare_hd_source_contrastive_interview.py"
sp=importlib.util.spec_from_file_location("hd_interview",S)
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)


class LegacyHDContrastTests(unittest.TestCase):
    def model(self):
        return {"mappings":[
          {"id":"CHANNEL_CREATION","cluster":"ORIGINAL","predicate":{"feature":"channel","equals":"1-8"}},
          {"id":"CHANNEL_DETAILS","cluster":"DETAIL","predicate":{"feature":"channel","equals":"17-62"}},
          {"id":"CARRIER_POSTSELECT","cluster":"DRIVE","predicate":{"feature":"activation","side":"personality","body":"moon","gate":24},"post_selection":True},
        ]}
    def bank(self):
        return {"schema":"astrohd_two_system_contrast_question_bank_v0.2",
                "questions":[
          {"id":"Q01","text":"Which projects involved inventing a process or refining details?",
           "source_ids":["CHANNEL_CREATION","CHANNEL_DETAILS"]},
          {"id":"Q02","text":"How did you handle routine work?",
           "source_ids":["CHANNEL_CREATION"]},
        ]}
    @staticmethod
    def matcher(state,predicate):
        return predicate["equals"] in state["channels"]
    def test_only_chart_disagreements_exposed(self):
        a,b=mod.make_queue(self.bank(),self.model(),self.matcher,
                           {"channels":{"1-8"}},
                           {"channels":{"1-8","17-62"}},
                           question_bank_sha="source-digest",
                           prior_receipt_sha="replay-digest")
        self.assertEqual([q["id"] for q in a["questions"]],["Q01"])
        self.assertFalse(a["has_candidate_birth_chart_or_direction"])
        self.assertNotIn("17-62",str(a))
        self.assertNotIn("reference_predicate",str(a))
        self.assertEqual(b["question_source_differences"][0]["actually_distinguishing_mappings"],["CHANNEL_DETAILS"])
        self.assertFalse(b["question_source_differences"][0]["source_mappings"]["CHANNEL_DETAILS"]["reference_predicate"])
        self.assertTrue(b["question_source_differences"][0]["source_mappings"]["CHANNEL_DETAILS"]["alternative_predicate"])

    def test_nonexistent_mapping_rejected(self):
        v=self.bank()
        v["questions"][0]["source_ids"]=["DOES_NOT_EXIST"]
        with self.assertRaisesRegex(ValueError,"Unknown source"):
            mod.inspect_source_question_bank(v,self.model())

    def test_postselected_mappings_rejected(self):
        v=self.bank()
        v["questions"][0]["source_ids"]=["CARRIER_POSTSELECT"]
        with self.assertRaisesRegex(ValueError,"Postselected"):
            mod.inspect_source_question_bank(v,self.model())

    def test_unknown_version_rejected(self):
        v=self.bank()
        v["schema"]="made-up-v1"
        with self.assertRaisesRegex(ValueError,"schema"):
            mod.inspect_source_question_bank(v,self.model())

    def test_duplicate_questions_rejected(self):
        v=self.bank()
        v["questions"].append(v["questions"][0])
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            mod.inspect_source_question_bank(v,self.model())

if __name__=="__main__":unittest.main()
