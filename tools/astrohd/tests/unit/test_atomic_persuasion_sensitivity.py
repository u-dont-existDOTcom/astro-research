"""Generic guards against post-hoc full-channel persuasion overfitting.

No owner's birth date, chart, questionnaire or source result in tests.
"""
from __future__ import annotations

import importlib.util
import copy
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[2]/"scripts/audit_full_channel_persuasion_hypothetical.py"
sp=importlib.util.spec_from_file_location("persuasion_hypo",P)
module=importlib.util.module_from_spec(sp)
sp.loader.exec_module(module)


def base():
    return {
       "id":module.ORIGINAL_ID,
       "cluster":"ENTERPRISE_PERSUASION_PATTERN",
       "predicate":{"feature":"channel","equals":"26-44"},
       "parents":[{"feature":"type","equals":"Projector"}],
       "source":"Historically defined channel theme",
       "behavior":"A compound of persuasion, bargaining and instinctive recognition",
       "confidence":0.9,"salience":0.8,"directness":0.75,"flexibility":0.75,
    }

class AtomicSensitivityGuardTests(unittest.TestCase):
    def test_what_if_is_new_post_selected_mapping(self):
        old=base();snapshot=copy.deepcopy(old)
        hypothetical=module.optional_atom(old,0.75)
        self.assertEqual(old,snapshot)
        self.assertNotEqual(old["id"],hypothetical["id"])
        self.assertEqual(old["cluster"],hypothetical["cluster"])
        self.assertEqual(old["predicate"],hypothetical["predicate"])
        self.assertTrue(hypothetical["post_selection"])
        self.assertIn("Hypothetical atomic",hypothetical["behavior"])

    def test_not_independent_new_cluster(self):
        atom=module.optional_atom(base(),.5)
        self.assertEqual(atom["cluster"],"ENTERPRISE_PERSUASION_PATTERN")
        self.assertNotEqual(atom["cluster"],"NEW_PERSUASION_EVIDENCE")

    def test_confidence_bounds(self):
        for val in (-.1,1.001):
            with self.assertRaises(ValueError):
                module.optional_atom(base(),val)

    def test_wrong_source_pathway_is_rejected(self):
        m=base();m["id"]="UNRELATED"
        with self.assertRaises(ValueError):
            module.optional_atom(m,0.5)

    def test_wrong_raw_user_clarification_not_accepted(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"test.json";p.write_text("source input")
            with self.assertRaisesRegex(RuntimeError,"source does not match"):
                module.validate(p,{"raw_clarification_sha256":"0"*64},{})

    def test_unsupported_scoring_version_does_not_pass_validation(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"test.txt";p.write_text("neutral report")
            conf={"raw_clarification_sha256":module.file_sha(p),
                  "target_version":"CONFIRMATORY_FROZEN",
                  "previous_HD_rank_sha256":module.BASELINE_SHA}
            with self.assertRaisesRegex(RuntimeError,"target version"):
                module.validate(p,conf,{})

if __name__=="__main__":unittest.main()
