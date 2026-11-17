import _paths
"""Invented-cohort tests; no retained person or current-run input is read."""
import copy
from contextlib import redirect_stdout
from io import StringIO
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from current_latitude_cli import (GateClosed, assemble_report, load_complete_evidence,
                                  main, pearson_summary, write_outputs)

HERE = Path(__file__).resolve().parent


def invented_cohort():
    manifest, people, captures, inputs, historical = [], [], {}, {}, []
    for hemisphere, count in [("North", 73), ("South", 68)]:
        for index in range(count):
            sid = f"invented-{hemisphere.lower()}-{index:03d}"
            old_delta = 0.03 * math.sin(index / 5) + 0.001 * index
            comparison = {"standard_global": 0.4, "inverted_global": 0.4 + old_delta}
            old_delta = comparison["inverted_global"] - comparison["standard_global"]
            manifest.append({"subject_id": sid, "hemisphere": hemisphere,
                             "subject_list_name": f"Invented {hemisphere} fixture {index}",
                             "comparison_input": comparison})
            review = hemisphere == "South" and index < 14
            people.append({"subject_id": sid, "included_in_cohort": True,
                           "capture_validation_passed": True,
                           "current_delta": 0.012 * math.cos(index / 4) - 0.0001 * index,
                           "metadata": {"engine_sha256": "a" * 64, "input_policy": "invented-consistent-policy",
                                        "provenance": "official_adb_reconstruction" if index % 2 else "supplied_mastro_database",
                                        "source_review_status": "review_required" if review else "verified_source",
                                        "source_quality_rating": "B" if review else "A",
                                        "historical_equivalence": "unverified"}})
            magnitude = 5 + 0.45 * index + 0.1 * math.sin(index)
            unresolved = hemisphere == "South" and index == 20
            captures[sid] = {"subject_id": sid, "passed": True,
                             "captured": {"latitude": {"degrees": -magnitude if hemisphere == "South" else magnitude}},
                             "status": "reported_utc_verified_source_convention_unresolved" if unresolved else "position_consistency_verified",
                             "source_convention_discrepancy": {"flag": "invented_unresolved_convention"} if unresolved else None}
            inputs[sid] = {"source_record": {"uncertainty": {"flags": ["invented_review_flag"] if review else []}}}
            if hemisphere == "South" and index < 67:
                historical.append({"subject_id": sid, "excel_row": index + 2,
                                   "signed_latitude_as_supplied": -(5 + 0.45 * index),
                                   "difference_as_supplied": old_delta})
    return manifest, historical, people, captures, inputs


class FullCompletionGateTests(unittest.TestCase):
    def test_partial_manifest_and_invalid_pair_block_before_inference(self):
        for mode in ["partial", "invalid"]:
            data = list(invented_cohort())
            if mode == "partial":
                data[0] = data[0][:-1]
            else:
                data[2][-1]["included_in_cohort"] = False
            with patch("current_latitude_cli.pearson_summary", side_effect=AssertionError("Inference must remain closed")) as inference:
                with self.assertRaises(GateClosed):
                    assemble_report(*data)
                inference.assert_not_called()

    def test_missing_completion_marker_blocks_before_shared_guard_or_inference(self):
        manifest = invented_cohort()[0]
        guard = Mock()
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            with self.assertRaises(GateClosed):
                load_complete_evidence(manifest, Path(directory), guard_module=guard)
        guard.analyze_person.assert_not_called()

    def test_mixed_engine_hash_or_input_policy_blocks(self):
        for key, different in [("engine_sha256", "b" * 64), ("input_policy", "invented-other-policy")]:
            data = list(invented_cohort())
            data[2][-1]["metadata"][key] = different
            with patch("current_latitude_cli.pearson_summary") as inference:
                with self.assertRaises(GateClosed):
                    assemble_report(*data)
                inference.assert_not_called()

    def test_bad_capture_binding_or_coordinate_blocks(self):
        for mode in ["identity", "nonfinite", "wrong_sign"]:
            data = list(invented_cohort())
            sid = data[1][0]["subject_id"]
            if mode == "identity":
                data[3][sid]["subject_id"] = "invented-unrelated-case"
            else:
                data[3][sid]["captured"]["latitude"]["degrees"] = float("nan") if mode == "nonfinite" else 15
            with patch("current_latitude_cli.pearson_summary") as inference:
                with self.assertRaises(GateClosed):
                    assemble_report(*data)
                inference.assert_not_called()

    def test_historical_score_drift_and_duplicate_identity_fail_closed(self):
        for mode in ["score_drift", "duplicate"]:
            data = list(invented_cohort())
            if mode == "score_drift":
                data[1][0]["difference_as_supplied"] += 0.01
            else:
                data[1][1]["subject_id"] = data[1][0]["subject_id"]
            with self.assertRaises(GateClosed):
                assemble_report(*data)

    def test_cli_partial_run_produces_no_analysis_artifacts(self):
        manifest = invented_cohort()[0]
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            folder = Path(directory)
            manifest_path = folder / "invented_manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            prefix = folder / "invented-report"
            with redirect_stdout(StringIO()) as output:
                code = main(["--manifest", str(manifest_path), "--results-dir", str(folder / "empty-run"),
                             "--out-prefix", str(prefix)])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(output.getvalue())["status"], "blocked_no_inference")
            self.assertFalse(prefix.with_suffix(".json").exists())
            self.assertFalse(prefix.with_name(prefix.name + "-public.json").exists())


class PrespecifiedReportsTests(unittest.TestCase):
    def test_exact_four_reports_and_separate_original_missing_latitude(self):
        data = invented_cohort()
        result = assemble_report(*data)
        self.assertEqual([analysis["id"] for analysis in result["analyses"]],
                         ["historical_original67", "current_scores_original67", "current_scores_current_latitudes68", "current_scores_current_latitudes_original67"])
        self.assertEqual([analysis["n"] for analysis in result["analyses"]], [67, 67, 68, 67])
        self.assertEqual([analysis["df"] for analysis in result["analyses"]], [65, 65, 66, 65])
        missing = [row for row in result["rows"] if row["original_latitude_missing"]]
        self.assertEqual(len(missing), 1)
        self.assertIsNone(missing[0]["original_latitude"])
        self.assertIsNotNone(missing[0]["current_captured_latitude"])
        self.assertTrue(missing[0]["current_latitude_newly_available_for_originally_missing_row"])
        self.assertIn("not historical reproduction", result["analyses"][2]["label"])

    def test_score_change_report_keeps_original_latitudes(self):
        data = invented_cohort()
        result = assemble_report(*data)
        by_id = {person["subject_id"]: person for person in data[2]}
        expected = pearson_summary([row["signed_latitude_as_supplied"] for row in data[1]],
                                   [by_id[row["subject_id"]]["current_delta"] for row in data[1]])
        self.assertEqual(result["analyses"][1]["r"], expected["r"])
        changed = copy.deepcopy(data)
        for capture in changed[3].values():
            if capture["captured"]["latitude"]["degrees"] < 0:
                capture["captured"]["latitude"]["degrees"] += 0.05 * math.sin(abs(capture["captured"]["latitude"]["degrees"]))
        changed_result = assemble_report(*changed)
        self.assertEqual(result["analyses"][0], changed_result["analyses"][0])
        self.assertEqual(result["analyses"][1], changed_result["analyses"][1])
        self.assertNotEqual(result["analyses"][2]["r"], changed_result["analyses"][2]["r"])

    def test_source_and_clock_uncertainty_are_reported_without_exclusion(self):
        result = assemble_report(*invented_cohort())
        uncertainty = result["public_safe_aggregate"]["source_and_time_uncertainty_counts"]
        self.assertEqual(uncertainty["source_review_status"]["review_required"], 14)
        self.assertEqual(uncertainty["unresolved_application_clock_conventions"], 1)
        self.assertEqual(result["analyses"][2]["n"], 68)
        self.assertEqual(result["exclusions_based_on_outcomes_or_uncertainty"], 0)

    def test_public_aggregate_contains_no_individual_id_or_name(self):
        data = invented_cohort()
        # Unexpected descriptive metadata remains private, never a public
        # Counter key merely because it happened to be present in an input.
        data[2][-1]["metadata"]["historical_equivalence"] = {"status": "unverified", "private_detail": "invented-private-note"}
        data[4][data[1][0]["subject_id"]]["source_record"]["uncertainty"]["flags"] = ["invented-private-flag-text"]
        result = assemble_report(*data)
        public = json.dumps(result["public_safe_aggregate"])
        self.assertNotIn("invented-private-note", public)
        self.assertNotIn("invented-private-flag-text", public)
        for record in data[0]:
            self.assertNotIn(record["subject_id"], public)
            self.assertNotIn(record["subject_list_name"], public)
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            prefix = Path(directory) / "invented-output"
            write_outputs(result, prefix)
            self.assertTrue(all(prefix.with_suffix(suffix).exists() for suffix in [".json", ".md", ".csv"]))
            self.assertEqual(json.loads(prefix.with_name(prefix.name + "-public.json").read_text()), result["public_safe_aggregate"])

    def test_two_sided_sign_symmetry_and_constant_inputs(self):
        x, y = [1, 2, 4, 5, 7], [2, 5, 3, 9, 8]
        positive = pearson_summary(x, y)
        negative = pearson_summary([-value for value in x], y)
        self.assertAlmostEqual(positive["r"], -negative["r"])
        self.assertAlmostEqual(positive["two_sided_p"], negative["two_sided_p"])
        self.assertGreaterEqual(positive["two_sided_p"], 0)
        self.assertLessEqual(positive["two_sided_p"], 1)
        self.assertEqual(pearson_summary([2, 2, 2], [1, 2, 3])["status"], "undefined_constant_input")


if __name__ == "__main__":
    unittest.main()
