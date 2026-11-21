#!/usr/bin/env python3
"""Source-qualified HD/Western *behavior hypotheses*, not a new natal rank.

A carrier witness is a chart fact, not evidence that a person behaves that way.
Use earlier frozen HD mappings/score records without modifying or reweighting
them. Ptolemy III.13 requires unimplemented governor and contrary testimony
arbitration; its sign/aspect witnesses are NEVER numerical support here.

CLI reads previous PRIVATE verified chart files and writes private results only;
repository tests use synthetic charts, not private dates or profile responses.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import timedelta
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = "reference/research/western_hd_source_behavior_contrast_v01.json"
RANK_SHA = "b930e87a366a7d06d0efe40c9ec83044be62116935ec1a986b06c3868fcf9bce"
WITNESS_STATUS = "SOURCE_CONDITION_WITNESS_ONLY_NO_WESTERN_PERSONALITY_SCORING"
RANK_STATUS = "EXPLORATORY_V37_CORRECTED_OBSERVABLES_REUSE_OF_V36_HD_PATHWAYS"
SELECTOR_STATUS = "NEW_POST_EXPOSURE_REPLAY_OF_OLD_V3_6_TARGET_MODEL_NOT_V43_PRODUCTION"
CHART_ABSENCE_IS_NOT_HUMAN_CONTRADICTION = True
HD_ACTIVE = "CARRIER_PRESENT_UNVALIDATED_HYPOTHESIS"
HD_ABSENT = "CARRIER_NOT_ACTIVE_NO_BEHAVIOR_CONTRADICTION"
HD_PARTIAL = "CARRIER_PRESENT_ATOMIC_SLICE_ABSTAIN_NEW_SCORE"
HD_COMPOUND = "CARRIER_PRESENT_COMPOUND_COMPONENT_ABSTAIN"
SOURCE_WITNESS = "WESTERN_GEOMETRIC_TESTIMONY_PRESENT_CONDITIONAL"
SOURCE_OTHER = "WESTERN_GEOMETRIC_TESTIMONY_NOT_PRESENT_NO_CONTRADICTION"
WESTERN_ABSTAIN = "ABSTAIN_WESTERN_GOVERNOR_HONORABILITY_UNRESOLVED"

def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def _sources(root: Path) -> dict:
    sys.path.insert(0, str(root / "scripts"))
    import replay_historical_v36_hd_on_verified_cache as old
    model = old.current_model(root)
    return {m["id"]: m for m in model["mappings"]}

def load_and_validate(root: Path = ROOT) -> tuple[dict, dict, dict]:
    """Reject missing, modified or automatically promoted source models."""
    graph = json.loads((root / REGISTRY_PATH).read_bytes())
    if graph.get("schema") != "astrohd_western_hd_behavior_source_contrast_v0.1":
        raise ValueError("Unknown behavioral source graph")
    if graph.get("original_ranking_sha256") != RANK_SHA:
        raise ValueError("Changing the frozen baseline score reference is forbidden")
    source = graph["source_files"]
    ledger = json.loads((root / source["hd_110_ledger"]).read_bytes())
    if len(ledger["entries"]) != 110 or any(r["accepted_into_new_model"] for r in ledger["entries"]):
        raise ValueError("Legacy 110-ID source inventory was altered/promoted")
    for record in ledger["source_reference"]:
        if digest(root / record["path"]) != record["digest"]:
            raise RuntimeError("Original source model drift: " + record["id"])
    registry = json.loads((root / source["western_register"]).read_bytes())
    if len(registry["rules"]) != 13 or any(r["automatically_scored"] for r in registry["rules"]):
        raise RuntimeError("Ptolemy source register has unauthorized promotions")
    west_ids = {r["id"] for r in registry["rules"]}
    hd = _sources(root)
    if len(hd) != 44 or len(graph["rules"]) < 10:
        raise RuntimeError("Unexpected historical coverage")
    ids = set()
    for rule in graph["rules"]:
        if rule["id"] in ids or rule["system"] not in {"HD", "WESTERN"}:
            raise ValueError("Duplicate/invalid atomic claim")
        ids.add(rule["id"])
        if rule.get("not_empirically_validated") is not True:
            raise ValueError("Behavior predictor incorrectly promoted as validated")
        if rule["system"] == "HD":
            original = hd.get(rule["source_id"])
            if original is None or not original.get("predicate") or not original.get("cluster"):
                raise ValueError("HD atomic claim lacks an older source anchor")
            if rule["source_scope"] not in {
                "whole_legacy_claim", "narrow_atomic_slice_of_broader_legacy_claim_no_new_score",
                "narrow_atomic_slice_of_compound_legacy_claim_abstain",
                "unobserved_compound_component_abstain",
                "potentially_discordant_compound_component_abstain",
            }:
                raise ValueError("Unreviewed HD source scope")
            if original["id"] == "CH_26_44_ENTERPRISE" and rule["source_scope"] == "whole_legacy_claim":
                raise ValueError("Compound channel cannot be called a whole observed claim")
            if rule["facet"] == "persuasive_ability" and rule["question_id"] != "ALREADY_CLARIFIED":
                raise ValueError("Do not re-interview already clarified persuasion capacity")
        else:
            if rule["source_id"] not in west_ids or rule["source_scope"] != "conditional_source_witness_only":
                raise ValueError("Unfounded scored Western behavior clause")
            if "honorability" in rule.get("required", ()) and "full_governance" not in rule["required"]:
                raise ValueError("Western planet character was detached from rulership")
    if len(set(graph["answered_questions"])) != len(graph["answered_questions"]):
        raise ValueError("Answered responses must remain uniquely identified")
    answered = set(graph["answered_questions"])
    for q in graph["new_unanswered_questions"]:
        if q["id"] in answered:
            raise ValueError("Cannot reopen answered question")
    return graph, hd, {r["id"]: r for r in registry["rules"]}

def _predicate(value: dict, chart: dict) -> bool | None:
    feature = value.get("feature")
    if feature == "channel":
        if "channels" not in chart:
            return None
        return tuple(sorted(map(int, str(value["equals"]).split("-")))) in chart["channels"]
    if feature == "gate":
        return int(value["equals"]) in chart["gates"] if "gates" in chart else None
    if feature == "type":
        return chart.get("type") == value["equals"] if "type" in chart else None
    if feature == "authority":
        return chart.get("auth") == value["equals"] if "auth" in chart else None
    if feature == "center":
        if "centers" not in chart:
            return None
        return (value["name"] in chart["centers"]) is value["defined"]
    # Don't silently treat a not-yet-compiled carrier as false.
    return None

def assess_hd(rule: dict, source: dict, chart: dict) -> dict:
    # IMPORTANT: V3.6 score_one() activates by predicate ONLY. Historical
    # "parents" condition the prevalence denominator, not carrier eligibility.
    # A 3/5 Self-Projected Projector may therefore carry 17–62 and Gate 52
    # despite failing the original requested Splenic parent context. Rejecting
    # the carrier based on that parent would misrepresent the old rank.
    carrier = _predicate(source["predicate"], chart)
    parent_context = [_predicate(p, chart) for p in source.get("parents", [])]
    if carrier is None:
        status = "ABSTAIN_MISSING_HD_FEATURE"
    elif not carrier:
        status = HD_ABSENT
    elif rule["source_scope"] == "whole_legacy_claim":
        status = HD_ACTIVE
    elif "compound" in rule["source_scope"]:
        status = HD_COMPOUND
    else:
        status = HD_PARTIAL
    return {
        "status": status, "carrier_present": carrier,
        "requested_prevalence_parent_context_satisfied":
            all(parent_context) if None not in parent_context else None,
        "source_parent_context_is_not_carrier_activation_gate": True,
        "dependency_cluster": source["cluster"],
        "source_scope": rule["source_scope"],
        "numeric_contribution": None,
        "behavior_confirmed": None,
        "behavior_contradicted": None,
    }

def _west_geometry(chart: dict, kind: str, value: str) -> bool | None:
    if kind in {"moon_mode", "mercury_mode"}:
        target = "Moon" if kind == "moon_mode" else "Mercury"
        focus = {r["source_character_focus"]: r for r in chart.get("character_focus_source_witnesses", ())}
        return focus[target]["mode"] == value if target in focus else None
    if kind in {"moon_solstitial", "mercury_solstitial"}:
        target = "Moon" if kind == "moon_solstitial" else "Mercury"
        focus = {r["source_character_focus"]: r for r in chart.get("character_focus_source_witnesses", ())}
        if target not in focus or "sign" not in focus[target]:
            return None
        # Ptolemy's III.13 has *solstitial* Cancer/Capricorn, not all
        # cardinal signs: Aries/Libra are equinoctial. No character score.
        if value != "Cancer|Capricorn":
            raise ValueError("Unexpected source sign vocabulary")
        return focus[target]["sign"] in {"Cancer", "Capricorn"}
    if kind == "moon_phase":
        return chart["moon_phase_witness"] == value if "moon_phase_witness" in chart else None
    if kind == "tight_jupiter_mercury":
        aspects = chart.get("all_seven_planet_tight_aspects_within_3deg")
        if aspects is None:
            return None
        # A tight aspect is not an established Ptolemaic soul-ruler alliance.
        return any(set(r["planets"]) == {"Jupiter", "Mercury"} for r in aspects)
    if kind == "sole_mercury_governor":
        return None  # Historical multi-ruler selection not compiled.
    raise ValueError("Unrecognized Western carrier kind")

def assess_western(rule: dict, chart: dict) -> dict:
    geometry = _west_geometry(chart, rule["test"]["kind"], rule["test"]["value"])
    status = (WESTERN_ABSTAIN if geometry is None
              else SOURCE_WITNESS if geometry else SOURCE_OTHER)
    return {
        "status": status, "carrier_present": geometry,
        "dependency_cluster": rule["dependency_cluster"],
        "unresolved_source_conditions": rule["required"],
        "numeric_contribution": None,
        "behavior_confirmed": None,
        "behavior_contradicted": None,
    }

def compare(graph: dict, old_hd: dict, western_sources: dict,
            actual_hd: dict, alternative_hd: dict,
            actual_western: dict, alternative_western: dict) -> dict:
    rows = []
    for rule in graph["rules"]:
        if rule["system"] == "HD":
            source = old_hd[rule["source_id"]]
            actual = assess_hd(rule, source, actual_hd)
            alternative = assess_hd(rule, source, alternative_hd)
        else:
            source = western_sources[rule["source_id"]]
            if source["automatically_scored"]:
                raise RuntimeError("Western rule illegally moved into scoring")
            actual = assess_western(rule, actual_western)
            alternative = assess_western(rule, alternative_western)
        if actual["carrier_present"] is None or alternative["carrier_present"] is None:
            classification = "UNRESOLVED_PREDICATE"
        elif actual["carrier_present"] == alternative["carrier_present"]:
            classification = "SHARED_CARRIER_OR_SHARED_ABSENCE"
        else:
            classification = "DIFFERENT_SOURCE_CARRIER_ONLY_NOT_BEHAVIOR_FIT"
        rows.append({
            "id": rule["id"], "system": rule["system"], "source_id": rule["source_id"],
            "facet": rule["facet"], "behavioral_hypothesis": rule["behavior"],
            "question_id": rule.get("question_id"),
            "contrast": classification,
            "reference": actual, "alternative": alternative,
        })
    assert all(r["reference"]["numeric_contribution"] is None for r in rows)
    assert all(r["alternative"]["numeric_contribution"] is None for r in rows)
    counts = Counter(r["contrast"] for r in rows)
    return {
        "schema": "astrohd_source_qualified_comparative_behavior_report_v0.1",
        "status": "POST_EXPOSURE_DEVELOPMENT_NOT_VALIDATED_AND_NOT_A_COMBINED_RANK",
        "development_epoch": graph["development_epoch"],
        "frozen_original_ranking_sha256": graph["original_ranking_sha256"],
        "personal_persuasion_source_sha256": graph["private_persuasion_source_sha256"],
        "personality_accuracy_comparison": "NOT_YET_COMPUTABLE",
        "new_hd_score": None, "new_western_score": None,
        "combined_rank": None, "complete_century_joint_coverage": False,
        "no_independent_human_validation": True,
        "unique_dependency_clusters": sorted({r["reference"]["dependency_cluster"] for r in rows}),
        "carrier_contrast_counts": dict(counts),
        "atomic_source_rules": rows,
        "unasked_questions": graph["new_unanswered_questions"],
        "answered_questions_not_reasked": graph["answered_questions"],
        "limitations": [
            "A source carrier being present is not evidence of the behavior; its absence is not a counterprediction.",
            "Old V3.7 rubric bits are not calibrated psychological log likelihoods.",
            "Western source testimony cannot receive a numeric score before soul governance/sect/honorability is compiled and all contrary witnesses adjudicated.",
            "Gate 26 and Channel 26–44 facets share one dependency cluster; they cannot be counted as independent endorsements.",
            "Historical Ptolemy sign qualities are conditional symbolic hypotheses, not modern empirical traits.",
            "Comparing an already exposed owner chart is developmental and cannot validate predictive natal astrology.",
        ],
    }

def overlay_private_development_evidence(
        report: dict, graph: dict, historic_hd: dict,
        original_v37_private_coding: dict) -> dict:
    """Add non-scoring, post-exposure target coding. Never copy rationale.

    This is a *semantic co-occurrence* audit, NOT a probability or an
    independent trial. A rule's target coding is immutable per participant
    and cannot be changed separately for the competing chart. It is never
    allowed to convert a missing carrier into a behavior contradiction.
    """
    if original_v37_private_coding.get("schema") != (
            "private_v37_profile_review_of_historical_hd_44_rules_v1"):
        raise ValueError("Wrong original V3.7 source-qualification record")
    if original_v37_private_coding.get("source_profile_sha256") != (
            "6f3f64143f83757636c34b7265d3980b85bb8643cc2ce975de26636431281295"):
        raise RuntimeError("Original V3.7 target profile source drift")
    judgments = original_v37_private_coding.get("judgments", {})
    if set(judgments) != set(historic_hd):
        raise RuntimeError("Expected all original 44 HD claim statuses")
    valid = {"directly_reported_observable", "conditional_or_compound",
             "potentially_discordant_not_automatic_penalty", "postselection_excluded"}
    if any(x.get("status") not in valid for x in judgments.values()):
        raise ValueError("Unknown prior target source coding")
    out = {**report, "atomic_source_rules": [dict(row) for row in report["atomic_source_rules"]]}
    counts = Counter()
    for row in out["atomic_source_rules"]:
        # Preserve original rows' reference+alternative; do not rank on this.
        if row["system"] != "HD":
            status = "NOT_IN_ORIGINAL_V37_TARGET_SOURCE_ADJUDICATION"
        elif row["source_id"] == "GATE_26_PERSUASION_ALT":
            # Owner later clarified rhetorical ability, NOT selling frequency.
            status = "DIRECT_PARTIAL_PERSUASION_CAPACITY_NO_NEW_SCORE"
        elif row["source_id"] == "CH_26_44_ENTERPRISE":
            status = "COMPOUND_UNRESOLVED_NO_FULL_RULE_VALIDATION"
        elif (judgments[row["source_id"]]["status"] == "directly_reported_observable"
              and any(rule["id"] == row["id"] and
                      rule["source_scope"] == "whole_legacy_claim"
                      for rule in graph["rules"])):
            status = "OLDER_DIRECT_SELF_REPORT_WHOLE_RULE_DEV_ONLY"
        else:
            status = "NO_ADMITTED_WHOLE_RULE_OBSERVATION"
        row["target_older_coding"] = status
        for side in ("reference", "alternative"):
            carrier = row[side]["carrier_present"]
            if carrier is None:
                coincidence = "ABSTAIN_MISSING_CHART_PREDICATE"
            elif status.startswith("OLDER_DIRECT"):
                coincidence = ("DIRECT_SELF_REPORT_AND_CARRIER_PRESENT_DEV_ONLY"
                               if carrier else "DIRECT_SELF_REPORT_WITH_NO_CARRIER_NOT_CONTRADICTION")
            elif status.startswith("DIRECT_PARTIAL"):
                coincidence = ("CLARIFIED_CAPACITY_AND_GATE_PRESENT_NO_EXTRA_CREDIT"
                               if carrier else "CLARIFIED_CAPACITY_NO_GATE_NO_NEGATIVE_CREDIT")
            else:
                coincidence = "ABSTAIN_NO_WHOLE_SOURCE_QUALIFIED_TARGET_MATCH"
            row[side] = {**row[side], "post_exposure_coincidence": coincidence}
            counts[(side, coincidence)] += 1
    out["development_target_overlap_counts"] = {
        side: dict(Counter({status: n for (tag, status), n in counts.items() if tag == side}))
        for side in ("reference", "alternative")
    }
    out["private_coding_layer_has_no_impact_on_ranking"] = True
    out["no_new_behavioral_p_values"] = True
    assert out["combined_rank"] is None
    assert all(x[side]["numeric_contribution"] is None
               for x in out["atomic_source_rules"] for side in ("reference", "alternative"))
    return out


def run_private(args: argparse.Namespace) -> dict:
    graph, old_hd, western_sources = load_and_validate(args.repo_root)
    if args.private_output.exists():
        raise FileExistsError("Private outputs are immutable: use a new name")
    selector = json.loads(args.private_selector.read_bytes())
    rank = json.loads(args.private_rank.read_bytes())
    witness = json.loads(args.private_western_witness.read_bytes())
    if selector.get("status") != SELECTOR_STATUS or rank.get("status") != RANK_STATUS:
        raise ValueError("Wrong original private source/HD ranking epoch")
    if digest(args.private_rank) != RANK_SHA:
        raise RuntimeError("Original 288,908-state HD ranking SHA mismatch")
    if witness.get("status") != WITNESS_STATUS:
        raise ValueError("Unapproved private Western source artifact")
    if witness.get("registered_source_sha256") != digest(
            args.repo_root / graph["source_files"]["western_register"]):
        raise RuntimeError("Private Western witness/source register mismatch")
    if witness.get("private_selector_sha256") != digest(args.private_selector):
        raise RuntimeError("Reference chart provenance mismatch")
    if witness.get("private_candidate_rank_sha256") != digest(args.private_rank):
        raise RuntimeError("Alternative chart provenance mismatch")
    if not all(witness[k]["source_preconditions_missing"]
               for k in ("reference", "alternative")):
        raise RuntimeError("Expected Western governance limitations absent")
    left_time = selector["reference_comparisons"][0]["input_utc"]
    top = rank["full_century_provisional_HD_only_ranking"]["top20"][0]
    sys.path.insert(0, str(args.repo_root / "scripts"))
    from replay_v37_development_direct_hd_observables import from_engine, utc
    from hdmatch.runtime.chart_adapter import ExactChartAdapter
    midpoint = utc(top["start_utc"]) + (
        utc(top["end_exclusive_utc"]) - utc(top["start_utc"])) / 2
    if witness["reference"]["UTC"] != utc(left_time).isoformat():
        raise RuntimeError("Western and HD reference timestamps differ")
    if witness["alternative"]["UTC"] != midpoint.isoformat():
        raise RuntimeError("Western and HD alternative timestamps differ")
    adapter = ExactChartAdapter(args.ephemeris)
    actual_hd = from_engine(adapter.calculate(utc(left_time)))
    alternative_hd = from_engine(adapter.calculate(midpoint))
    serialized_channels = ["-".join(map(str, x)) for x in sorted(alternative_hd["channels"])]
    if sorted(serialized_channels) != sorted(top["channels"]):
        raise RuntimeError("Top candidate chart did not reproduce source channels")
    report = compare(graph, old_hd, western_sources, actual_hd, alternative_hd,
                     witness["reference"], witness["alternative"])
    private_coding_sha = digest(args.private_coding)
    if private_coding_sha != graph["private_original_v37_coding_sha256"]:
        raise RuntimeError("Original private V3.7 behavioral coding changed")
    report = overlay_private_development_evidence(
        report, graph, old_hd, json.loads(args.private_coding.read_bytes()))
    report["source_hashes"] = {
        "graph": digest(args.repo_root / REGISTRY_PATH),
        "selector": digest(args.private_selector),
        "old_rank": digest(args.private_rank),
        "western_witness": digest(args.private_western_witness),
        "old_private_target_coding": private_coding_sha,
    }
    report["old_provisional_hd_rubric_bits_unmodified"] = {
        "reference": rank["comparison_charts"][0]["development_net_rubric_bits"],
        "leading_alternative": top["net_rubric_bits"],
    }
    if abs(report["old_provisional_hd_rubric_bits_unmodified"]["reference"]-9.4704565)>0.0000001:
        raise RuntimeError("Baseline reference score mismatch")
    if abs(report["old_provisional_hd_rubric_bits_unmodified"]["leading_alternative"]-10.4907557)>0.0000001:
        raise RuntimeError("Baseline comparator score mismatch")
    data = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    args.private_output.parent.mkdir(parents=True, exist_ok=True)
    args.private_output.write_bytes(data)
    summary = {"output_sha256": sha256(data).hexdigest(),
               "source_rules": len(report["atomic_source_rules"]),
               "carrier_contrasts": report["carrier_contrast_counts"],
               "distinct_clusters": len(report["unique_dependency_clusters"]),
               "old_scores_preserved": True, "joint_natal_rank": None}
    return summary

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=ROOT)
    p.add_argument("--private-selector", type=Path, required=True)
    p.add_argument("--private-rank", type=Path, required=True)
    p.add_argument("--private-coding", type=Path, required=True,
                   help="Exact archived V3.7 44-rule source-to-target coding")
    p.add_argument("--private-western-witness", type=Path, required=True)
    p.add_argument("--ephemeris", type=Path, required=True)
    p.add_argument("--private-output", type=Path, required=True)
    print(json.dumps(run_private(p.parse_args()), sort_keys=True))

if __name__ == "__main__":
    main()
