import _paths
import hashlib
import importlib.util
import json
from pathlib import Path
from fractions import Fraction
import tempfile
import unittest
from contextlib import redirect_stdout,redirect_stderr
from io import StringIO
from unittest.mock import patch

from cohort_analysis import (analyze, analyze_person, binomial_half, continuous_effect,
    fisher_two_sided, mcnemar, paired_mean_randomization, records, score, vector_difference, write_report,hemisphere_continuous,jsonable,rating_info,main as cohort_main,validate_study_manifest)
from mastro_tree import parse_tree

HERE=Path(__file__).resolve().parent


def subject(sid="N001",hemisphere="North"):
    return {"subject_id":sid,"hemisphere":hemisphere,"subject_list_name":"Invented fixture "+sid,
            "comparison_input":{"records":[{"word":"x"}],"standard_global":1.,"inverted_global":2.},
            "bio_source":{"records":[{"word":"x"}]},
            "astro_source":{"arms":{"standard":{"keywords":[{"word":"x","weight":1}]},
                                      "inverted":{"keywords":[{"word":"x","weight":2}]}}}}


def tree(values):
    return "nodes="+str(len(values))+"\n"+"".join(f"{i+1:X}\t0\t{word} ({weight})\n" for i,(word,weight) in enumerate(values))


def write_pair(root,person,standard=None,inverted=None,engine="7.8.5",policy="fixture-policy"):
    folder=root/person["subject_id"];folder.mkdir()
    metadata={"subject_id":person["subject_id"],"hemisphere":person["hemisphere"],
        "engine":engine,"engine_sha256":"f"*64,"input_policy":policy,
        "provenance":"invented_test_fixture","candidate":{"source_database":"tutorial"}}
    (folder/"input.json").write_text(json.dumps(metadata))
    (folder/"standard-tree.txt").write_text(tree(standard or [("x",1)]))
    (folder/"inverted-tree.txt").write_text(tree(inverted or [("x",2)]))
    for name in ("birth-fields.txt","standard-positions.txt","inverted-positions.txt","inversion-settings.txt"):
        (folder/name).write_text("invented test evidence; not a real chart")
    (folder/"capture-validation.json").write_text(json.dumps({"passed":True,"status":"invented_fixture"}))
    bind(folder,len(standard or [("x",1)]),len(inverted or [("x",2)]),policy)
    return folder


def bind(folder,ns=1,ni=1,policy="fixture-policy"):
    value={"subject_id":folder.name,"standard_count":ns,"inverted_count":ni,
        "engine_sha256":"f"*64,"input_policy":policy,"independent_capture_validation":"passed",
        "geometry":{"rotation_residual_degrees":[0.]*11,"tolerance_degrees":.03},
        "file_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.name!="complete.json"}}
    (folder/"complete.json").write_text(json.dumps(value))


class ScoringTests(unittest.TestCase):
    def test_raw_rating_origins_and_unknowns(self):
        recovered={"provenance":"official_adb_reconstruction","source_record":{"published_inputs":{"rodden_rating":"DD"}}}
        self.assertEqual(rating_info(recovered)["source_quality_rating"],"DD")
        self.assertEqual(rating_info({})["source_quality_rating_status"],"missing")
        fields=[{"cls":"COMBOBOX","text":"A    label"},{"cls":"COMBOBOX","text":"B    label"}]
        self.assertEqual(rating_info({"visible_fields":fields})["source_quality_rating_status"],"unresolved_multiple_candidates")
        self.assertEqual(rating_info({"visible_fields":[{"cls":"COMBOBOX","x":1298,"y":345,"text":"?"}]})["source_quality_rating"],"unknown")

    def test_exact_tie_and_duplicate_denominator(self):
        a=records([{"word":"x","weight":2},{"word":"X","weight":9}])
        b=records([{"word":"x","weight":3},{"word":"other","weight":5},{"word":"other","weight":5}])
        self.assertEqual(score(["x"],a)[0],Fraction(1))
        self.assertEqual(score(["x"],b)[0],Fraction(1))
        self.assertEqual(score(["x","x"," x"],a)[0],Fraction(2))

    def test_duplicate_weight_order_changes_first_match_without_multiset_change(self):
        a=records([{"word":"x","weight":1},{"word":"x","weight":2}])
        b=records([{"word":"x","weight":2},{"word":"x","weight":1}])
        diff=vector_difference(a,b)
        self.assertTrue(diff["vector_multiset_equal"])
        self.assertEqual(diff["changed_weight_row_count"],2)
        self.assertEqual(diff["literal_first_match_change_count"],1)

    def test_shared_parser_preserves_parentheses_and_rejects_incomplete_tree(self):
        self.assertEqual(parse_tree(tree([("vitalité (manque)","0.6")]))[0]["word"],"vitalité (manque)")
        with self.assertRaises(ValueError):parse_tree("nodes=2\nA\t0\tx (1.0)\n")
        with self.assertRaises(ValueError):parse_tree("")

    def test_displayed_zero_rows_are_retained_in_the_denominator(self):
        values=parse_tree(tree([("x","1.0"),("z","0.0")]))
        self.assertEqual(len(values),2)
        self.assertEqual(values[1]["weight"],0)
        self.assertEqual(score(["x"],values)[0],Fraction(1,2))


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=HERE)
        self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()

    def test_source_bio_variant_changes_only_separate_scores_and_winner(self):
        p=subject();p["bio_source"]["records"]=[{"word":"y"},{"word":"y"}]
        folder=write_pair(self.root,p,standard=[("x",1),("y",4)],inverted=[("x",2),("y",1)])
        result=analyze([p,subject("S001","South")],self.root)
        person=result["people"][0]
        self.assertEqual(person["current_winner"],"inverted")
        self.assertEqual(person["arms"]["standard"]["current_global"],.5)
        self.assertEqual(person["bio_source_current_winner"],"standard")
        self.assertEqual(person["arms"]["standard"]["bio_source_current_global"],4)
        self.assertTrue(person["bio_source_variant_winner_changed"])
        sensitivity=result["sensitivities"]["bio_source_variant"]
        self.assertEqual(sensitivity["descriptive"]["persons_with_winner_change"],1)
        self.assertEqual(sensitivity["tests"]["status"],"not_run_primary_gate_closed")

    def test_rating_groups_and_A_AA_subset_preserve_unresolved(self):
        a,b=subject(),subject("S001","South")
        folders=[write_pair(self.root,a),write_pair(self.root,b)]
        for folder,rating in zip(folders,("AA    recorded","XX   unknown date")):
            metadata=json.loads((folder/"input.json").read_text())
            metadata["visible_fields"]=[{"cls":"COMBOBOX","x":1298,"y":345,"text":rating}]
            (folder/"input.json").write_text(json.dumps(metadata));bind(folder)
        result=analyze([a,b],self.root,descriptive_only=True)
        self.assertEqual(result["groups"]["source_quality_rating"]["XX"]["n"],1)
        self.assertEqual(result["groups"]["hemisphere_by_rating"]["North / AA"]["n"],1)
        self.assertEqual(result["sensitivities"]["raw_A_or_AA_subset"]["subject_ids"],["N001"])
        self.assertEqual(result["sensitivities"]["raw_A_or_AA_subset"]["tests"]["status"],"not_run_primary_gate_closed")

    def test_clock_review_flag_is_stratified_and_excluded_only_in_sensitivity(self):
        p=subject();folder=write_pair(self.root,p)
        metadata=json.loads((folder/"input.json").read_text())
        metadata["observed_utc_exception"]={"status":"unresolved_supplied_record_time_convention","reported_utc":"invented"}
        (folder/"input.json").write_text(json.dumps(metadata))
        (folder/"capture-validation.json").write_text(json.dumps({"passed":True,"status":"reported_utc_verified_source_convention_unresolved"}))
        bind(folder)
        report=analyze([p],self.root,descriptive_only=True)
        self.assertEqual(report["included_complete_pairs"],1)
        self.assertEqual(report["groups"]["clock_convention_review"]["True"]["n"],1)
        sensitivity=report["sensitivities"]["exclude_clock_convention_review"]
        self.assertEqual(sensitivity["n"],0)
        self.assertEqual(sensitivity["excluded_subject_ids"],["N001"])
        self.assertEqual(sensitivity["tests"]["status"],"not_run_primary_gate_closed")

    def test_explicit_pilot_and_reuse_flags_keep_capture_and_binding_times_separate(self):
        a,b=subject(),subject("S001","South")
        fa,fb=write_pair(self.root,a),write_pair(self.root,b)
        for folder,pilot,reused in [(fa,False,True),(fb,True,False)]:
            marker=json.loads((folder/"complete.json").read_text())
            marker.update(original_generation_completed_utc="2001-01-01T01:00:00Z",completed_utc="2001-01-02T01:00:00Z",
                          retrospectively_rebound_pilot=pilot,reused_prior_pair=reused)
            (folder/"complete.json").write_text(json.dumps(marker))
        report=analyze([a,b],self.root,descriptive_only=True)
        first,second=report["people"]
        self.assertFalse(first["retrospectively_rebound_pilot"])
        self.assertTrue(first["reused_prior_pair"])
        self.assertEqual(first["output_reuse_kind"],"reused_prior_pair")
        self.assertEqual(first["retained_generation_completed_utc"],"2001-01-01T01:00:00Z")
        self.assertEqual(first["generation_completed_utc"],"2001-01-01T01:00:00Z")
        self.assertEqual(first["binding_completed_utc"],"2001-01-02T01:00:00Z")
        self.assertTrue(second["retrospectively_rebound_pilot"])
        self.assertFalse(second["reused_prior_pair"])
        self.assertIsNone(second["retained_generation_completed_utc"])
        self.assertEqual(report["evidence_quality"]["reused_prior_pair_count"],1)
        self.assertEqual(report["evidence_quality"]["newly_generated_pair_count"],1)
        self.assertEqual(report["evidence_quality"]["retrospectively_rebound_pilot_count"],1)

    def test_legacy_original_pilot_time_still_marks_original_pilot(self):
        p=subject();folder=write_pair(self.root,p)
        marker=json.loads((folder/"complete.json").read_text())
        marker["original_generation_completed_utc"]="2001-01-01T01:00:00Z"
        (folder/"complete.json").write_text(json.dumps(marker))
        result=analyze_person(p,self.root)
        self.assertTrue(result["included_in_cohort"])
        self.assertTrue(result["retrospectively_rebound_pilot"])
        self.assertFalse(result["reused_prior_pair"])

    def test_malformed_pilot_or_reuse_flags_fail_closed(self):
        p=subject();folder=write_pair(self.root,p)
        original=json.loads((folder/"complete.json").read_text())
        for flag in ("retrospectively_rebound_pilot","reused_prior_pair"):
            for value in ("false","true",0,1,None):
                with self.subTest(flag=flag,value=value):
                    marker=dict(original);marker[flag]=value
                    (folder/"complete.json").write_text(json.dumps(marker))
                    result=analyze_person(p,self.root)
                    self.assertFalse(result["included_in_cohort"])
                    self.assertTrue(any("strict JSON boolean" in e for e in result["errors"]))

    def test_missing_marker_never_enters_cohort_or_triggers_partial_tests(self):
        p=subject();folder=write_pair(self.root,p);(folder/"complete.json").unlink()
        result=analyze([p],self.root)
        self.assertEqual(result["included_complete_pairs"],0)
        self.assertEqual(result["tests"]["status"],"not_run_incomplete_cohort")
        self.assertIn("missing_completion_marker",result["people"][0]["pending"])

    def test_changed_tree_after_completion_is_rejected(self):
        p=subject();folder=write_pair(self.root,p)
        (folder/"standard-tree.txt").write_text(tree([("x",3)]))
        result=analyze_person(p,self.root)
        self.assertFalse(result["included_in_cohort"])
        self.assertTrue(any("hash_binding_mismatch" in x for x in result["errors"]))

    def test_mismatched_person_or_build_is_rejected_even_with_fresh_bindings(self):
        p=subject();folder=write_pair(self.root,p,engine="7.8.0")
        result=analyze_person(p,self.root)
        self.assertFalse(result["included_in_cohort"])
        self.assertIn("metadata_engine_version_mismatch_or_missing",result["errors"])
        metadata=json.loads((folder/"input.json").read_text());metadata.update(engine="7.8.5",subject_id="S099")
        (folder/"input.json").write_text(json.dumps(metadata));bind(folder)
        result=analyze_person(p,self.root)
        self.assertIn("metadata_identity_or_hemisphere_mismatch",result["errors"])

    def test_legacy_marker_is_provisional_until_hash_and_capture_rebinding(self):
        p=subject();folder=write_pair(self.root,p)
        (folder/"complete.json").write_text(json.dumps({"subject_id":"N001","standard_count":1,"inverted_count":1}))
        result=analyze_person(p,self.root)
        self.assertFalse(result["included_in_cohort"])
        self.assertIn("completion_marker_needs_full_evidence_hash_binding",result["pending"])

    def test_complete_fixture_and_json_csv_md_round_trip(self):
        a,b=subject(),subject("S001","South")
        write_pair(self.root,a);write_pair(self.root,b)
        result=analyze([a,b],self.root,draws=99,bootstrap=100)
        self.assertTrue(result["complete_cohort"])
        self.assertEqual(result["tests"]["status"],"computed_for_full_current_cohort")
        self.assertEqual(result["overall_on_completed_subset"]["equal_vector_multisets"],4)
        self.assertFalse(result["claims"]["new_human_validation"])
        output=self.root/"report";write_report(result,output)
        self.assertEqual(json.loads(output.with_suffix(".json").read_text())["included_complete_pairs"],2)
        self.assertTrue(output.with_suffix(".csv").is_file());self.assertTrue(output.with_suffix(".md").is_file())

    def test_mixed_input_policies_do_not_get_pooled_tests(self):
        a,b=subject(),subject("S001","South")
        write_pair(self.root,a);write_pair(self.root,b,policy="different-policy")
        result=analyze([a,b],self.root,draws=99,bootstrap=100)
        self.assertEqual(result["included_complete_pairs"],2)
        self.assertEqual(result["tests"]["status"],"not_run_mixed_input_policies")

    def test_missing_geometry_receipt_is_not_a_completed_pair(self):
        p=subject();folder=write_pair(self.root,p)
        marker=json.loads((folder/"complete.json").read_text());del marker["geometry"]
        (folder/"complete.json").write_text(json.dumps(marker))
        result=analyze_person(p,self.root)
        self.assertFalse(result["included_in_cohort"])
        self.assertIn("inversion_geometry_receipt_missing",result["pending"])

    def test_exact_tie_is_reported_and_never_counted_as_inversion_win(self):
        p=subject();write_pair(self.root,p,standard=[("x",2),("X",9)],inverted=[("x",3),("other",5),("other",5)])
        result=analyze([p],self.root,descriptive_only=True)
        self.assertEqual(result["people"][0]["current_winner"],"tie")
        current=result["overall_on_completed_subset"]["current"]
        self.assertEqual(current["ties"],1);self.assertEqual(current["inverted_wins"],0)


class StudyCliTests(unittest.TestCase):
    def test_short_relabelled_duplicate_or_wrong_hemisphere_blocks_before_analysis(self):
        full=[subject(f"N{i:03d}") for i in range(1,74)]+[subject(f"S{i:03d}","South") for i in range(1,69)]
        for mode in ("short","relabelled","duplicate","wrong_hemisphere"):
            manifest=json.loads(json.dumps(full))
            if mode=="short":manifest.pop()
            elif mode=="relabelled":manifest[-1]["subject_id"]="S069"
            elif mode=="duplicate":manifest[-1]["subject_id"]="S067"
            else:manifest[-1]["hemisphere"]="North"
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(dir=HERE) as directory:
                root=Path(directory);path=root/"manifest.json";path.write_text(json.dumps(manifest));prefix=root/"no-report"
                with patch("cohort_analysis.analyze",side_effect=AssertionError("Invalid CLI manifest reached analysis")) as analysis, \
                     patch("cohort_analysis.write_report") as writer,redirect_stderr(StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        cohort_main(["--manifest",str(path),"--results",str(root/"captures"),"--out-prefix",str(prefix)])
                    self.assertEqual(raised.exception.code,2)
                    analysis.assert_not_called();writer.assert_not_called()
                self.assertFalse(prefix.with_suffix(".json").exists())

    def test_valid_full_manifest_with_missing_captures_remains_descriptive(self):
        manifest=[subject(f"N{i:03d}") for i in range(1,74)]+[subject(f"S{i:03d}","South") for i in range(1,69)]
        validate_study_manifest(manifest)
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            root=Path(directory);path=root/"manifest.json";path.write_text(json.dumps(manifest));prefix=root/"partial"
            with patch("cohort_analysis.effect_tests",side_effect=AssertionError("Partial captures reached inference")) as inference,redirect_stdout(StringIO()):
                cohort_main(["--manifest",str(path),"--results",str(root/"captures"),"--out-prefix",str(prefix)])
                inference.assert_not_called()
            report=json.loads(prefix.with_suffix(".json").read_text())
            self.assertEqual(report["expected_subjects"],141)
            self.assertEqual(report["included_complete_pairs"],0)
            self.assertEqual(report["tests"]["status"],"not_run_incomplete_cohort")


class NumericalTests(unittest.TestCase):
    def test_exact_binomial_and_fisher_reference_values(self):
        self.assertEqual(binomial_half(10,10),.001953125)
        # Official SciPy Fisher example [[6,2],[1,4]] has lower-probability
        # masses28+140+8 out of1716, i.e.4/39 (two-sided).
        self.assertAlmostEqual(fisher_two_sided([[6,2],[1,4]]),4/39,places=14)

    def test_exact_mcnemar_on_discordant_pairs(self):
        people=[{"historical_winner":"standard","current_winner":"inverted"}]
        people += [{"historical_winner":"inverted","current_winner":"standard"}]*7
        people += [{"historical_winner":"tie","current_winner":"standard"}]
        result=mcnemar(people)
        self.assertEqual(result["exact_two_sided_p"],.0703125)
        self.assertEqual(result["excluded_due_to_tie"],1)

    def test_exact_sign_flips_and_reproducible_bootstrap(self):
        self.assertEqual(paired_mean_randomization([1,2,3],999,5)["p"],.25)
        a=continuous_effect([Fraction(1,3),Fraction(2,3),Fraction(0)],99,100,42)
        b=continuous_effect([Fraction(1,3),Fraction(2,3),Fraction(0)],99,100,42)
        self.assertEqual(a,b)

    def test_exact_hemisphere_allocation_on_four_paired_differences(self):
        people=[]
        for hemisphere,value in [("North",0),("North",0),("South",1),("South",1)]:
            people.append({"hemisphere":hemisphere,"current_delta_exact":{"numerator":value,"denominator":1}})
        result=hemisphere_continuous(people,"current",99,100,42)
        self.assertEqual(result["south_minus_north_mean_inversion_advantage"],1.)
        self.assertAlmostEqual(result["randomization"]["p"],1/3)
        self.assertEqual(result["bootstrap_95_percentile_interval"],[1.,1.])

    def test_monte_carlo_branches_return_json_serializable_repeatable_results(self):
        people=[]
        for hemisphere,value in [("North",0)]*9+[("South",1)]*9:
            people.append({"hemisphere":hemisphere,"current_delta_exact":{"numerator":value,"denominator":1}})
        result=hemisphere_continuous(people,"current",19,20,4)
        self.assertIn("Monte Carlo",result["randomization"]["method"])
        json.dumps(jsonable(result),allow_nan=False)
        randomization=paired_mean_randomization([Fraction(i,17) for i in range(1,18)],19,4)
        json.dumps(jsonable(randomization),allow_nan=False)
        self.assertEqual(randomization,paired_mean_randomization([Fraction(i,17) for i in range(1,18)],19,4))


if __name__=="__main__":unittest.main()
