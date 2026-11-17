"""Prespecified latitude reports, blocked until all 141 pairs pass evidence guards.

Read-only inputs. No GUI, chart generation, source edits or partial-run inference.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent


class GateClosed(ValueError):
    pass


def verify_manifest(manifest):
    ids = [record.get("subject_id") for record in manifest]
    groups = Counter(record.get("hemisphere") for record in manifest)
    if len(ids) != 141 or len(set(ids)) != 141 or any(not isinstance(sid, str) or not sid for sid in ids):
        raise GateClosed("The protocol requires exactly 141 unique subject identities")
    if groups != {"North": 73, "South": 68}:
        raise GateClosed("The protocol requires 73 North and 68 South subjects")


def load_guard_module():
    # Avoid creating cache files in the read-only reference-audit directory.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(HERE))
    return importlib.import_module("cohort_analysis")


def load_complete_evidence(manifest, results_dir, expected_engine="7.8.5", expected_hash=None, guard_module=None):
    verify_manifest(manifest)
    results_dir = Path(results_dir)
    missing_markers = [record["subject_id"] for record in manifest
                       if not (results_dir / record["subject_id"] / "complete.json").is_file()]
    if missing_markers:
        raise GateClosed(f"Completion gate closed: {len(missing_markers)} of 141 completion markers are missing; no latitude inference performed")
    guards = guard_module or load_guard_module()
    # Reuse its current tree, metadata, hash, geometry and independent-clock
    # checks. Do not call analyze/effect_tests or any partial-subset summaries.
    people = [guards.analyze_person(record, results_dir, expected_engine, expected_hash) for record in manifest]
    invalid = [person["subject_id"] for person in people
               if not person.get("included_in_cohort") or person.get("capture_validation_passed") is not True]
    if invalid:
        raise GateClosed(f"Completion gate closed: {len(invalid)} pairs fail the shared cohort evidence guards; no latitude inference performed")
    captures, inputs, receipt_hashes = {}, {}, {}
    for person in people:
        sid = person["subject_id"]
        folder = results_dir / sid
        for filename, destination in [("capture-validation.json", captures), ("input.json", inputs)]:
            text, digest, _ = guards.snapshot(folder / filename)
            if digest != person["input_hashes"].get(filename):
                raise GateClosed("Evidence changed after shared cohort validation")
            destination[sid] = guards.read_json(text)
        if captures[sid].get("subject_id") != sid or captures[sid].get("passed") is not True:
            raise GateClosed("Capture validation must pass and bind the exact subject identity")
        _, marker_hash, _ = guards.snapshot(folder / "complete.json")
        if marker_hash != person["input_hashes"].get("complete.json"):
            raise GateClosed("Completion receipt changed during evidence loading")
        receipt_hashes[sid] = dict(person["input_hashes"])
    return people, captures, inputs, receipt_hashes


def pearson_summary(x, y):
    from scipy import special, stats
    if len(x) != len(y) or len(x) < 3 or any(not math.isfinite(value) for value in x + y):
        raise ValueError("Pearson inputs must be complete finite pairs")
    n = len(x)
    xmean, ymean = math.fsum(x) / n, math.fsum(y) / n
    xx = math.fsum((value - xmean) ** 2 for value in x)
    yy = math.fsum((value - ymean) ** 2 for value in y)
    if not xx or not yy:
        return {"n": n, "df": n - 2, "status": "undefined_constant_input", "r": None, "t": None, "two_sided_p": None}
    r = math.fsum((a - xmean) * (b - ymean) for a, b in zip(x, y)) / math.sqrt(xx * yy)
    r = max(-1.0, min(1.0, r))
    df = n - 2
    if abs(r) == 1:
        t, p_t, p_beta = None, 0.0, 0.0
    else:
        t = r * math.sqrt(df / (1 - r * r))
        p_t = float(2 * stats.t.sf(abs(t), df))
        p_beta = float(2 * special.betainc(n / 2 - 1, n / 2 - 1, (1 - abs(r)) / 2))
    if abs(p_t - p_beta) > 1e-12:
        raise ValueError("Independent t/beta probability cross-check failed")
    return {"n": n, "df": df, "status": "computed", "r": r, "t": t,
            "two_sided_p": p_t, "exact_normal_null_beta_p": p_beta,
            "method": "Centered Pearson sums; two-sided standard t with exact normal-null beta cross-check"}


def assemble_report(manifest, historical_rows, people, captures, inputs):
    """Pure assembly after the shared guards; all checks precede inference."""
    verify_manifest(manifest)
    ids = {record["subject_id"] for record in manifest}
    if len(people) != 141 or {person["subject_id"] for person in people} != ids or len({person["subject_id"] for person in people}) != 141:
        raise GateClosed("All 141 unique guarded pairs are required before inference")
    if any(not person.get("included_in_cohort") or person.get("capture_validation_passed") is not True for person in people):
        raise GateClosed("A guarded pair is incomplete or invalid")
    hashes = {person["metadata"].get("engine_sha256") for person in people}
    policies = {person["metadata"].get("input_policy") for person in people}
    if len(hashes) != 1 or not next(iter(hashes)):
        raise GateClosed("Mixed or missing engine hashes cannot be pooled")
    if len(policies) != 1 or not next(iter(policies)):
        raise GateClosed("Mixed or missing input policies cannot be pooled")
    if set(captures) != ids or set(inputs) != ids:
        raise GateClosed("All validated captures and source metadata are required")
    south = [record for record in manifest if record["hemisphere"] == "South"]
    south_ids = {record["subject_id"] for record in south}
    old = {row["subject_id"]: row for row in historical_rows}
    if len(historical_rows) != 67 or len(old) != 67 or not set(old).issubset(south_ids):
        raise GateClosed("Historical baseline must preserve the original 67 unique Southern rows")
    by_id = {person["subject_id"]: person for person in people}
    rows = []
    for record in south:
        sid = record["subject_id"]
        person, capture, raw_input = by_id[sid], captures[sid], inputs[sid]
        if capture.get("subject_id") != sid or capture.get("passed") is not True:
            raise GateClosed("Exact capture identity/pass binding is required")
        latitude = capture.get("captured", {}).get("latitude", {}).get("degrees")
        if isinstance(latitude, bool) or not isinstance(latitude, (int, float)) or not math.isfinite(latitude) or not -90 <= latitude < 0:
            raise GateClosed("Current Southern latitude must be a finite signed captured coordinate")
        current_delta = person.get("current_delta")
        if not isinstance(current_delta, (int, float)) or not math.isfinite(current_delta):
            raise GateClosed("Current paired score difference is missing or nonfinite")
        original_delta = record["comparison_input"]["inverted_global"] - record["comparison_input"]["standard_global"]
        previous = old.get(sid)
        if previous:
            old_lat = previous["signed_latitude_as_supplied"]
            old_delta = previous["difference_as_supplied"]
            if not isinstance(old_lat, (int, float)) or not math.isfinite(old_lat) or not -90 <= old_lat < 0:
                raise GateClosed("Original supplied latitude is invalid")
            if abs(old_delta - original_delta) > 1e-12:
                raise GateClosed("Historical source-score reconciliation changed")
        source = raw_input.get("source_record", {})
        source_uncertainty = source.get("uncertainty", {}) if isinstance(source, dict) else {}
        source_flags = source_uncertainty.get("flags", [])
        if not isinstance(source_flags, list) or any(not isinstance(flag, str) for flag in source_flags):
            raise GateClosed("Source uncertainty flags must retain their declared string-list form")
        rows.append({"subject_id": sid, "name": record["subject_list_name"],
                     "original_workbook_row": previous.get("excel_row") if previous else None,
                     "original_latitude": previous["signed_latitude_as_supplied"] if previous else None,
                     "current_captured_latitude": latitude,
                     "original_latitude_missing": previous is None,
                     "current_latitude_newly_available_for_originally_missing_row": previous is None,
                     "historical_delta": original_delta,
                     "current_delta": current_delta,
                     "delta_change": current_delta - original_delta,
                     "input_provenance": person["metadata"].get("provenance", "unknown"),
                     "source_review_status": person["metadata"].get("source_review_status", "not_recorded"),
                     "source_quality_rating": person["metadata"].get("source_quality_rating", "unknown"),
                     "source_uncertainty_flags": source_flags,
                     "capture_validation_status": capture.get("status"),
                     "source_convention_discrepancy": capture.get("source_convention_discrepancy"),
                     "historical_equivalence": person["metadata"].get("historical_equivalence", "unverified")})
    # Every protocol/evidence/data check above runs before any Pearson call.
    old_order = [next(row for row in rows if row["subject_id"] == original["subject_id"]) for original in historical_rows]
    analyses = [
        {"id": "historical_original67", "label": "Historical reproduction: original 67 workbook latitudes and historical deltas",
         "latitude_source": "original_signed_workbook_latitudes", "score_source": "historical_inverted_minus_standard",
         **pearson_summary([row["original_latitude"] for row in old_order], [row["historical_delta"] for row in old_order])},
        {"id": "current_scores_original67", "label": "Current scores on original 67 workbook latitudes: score changes isolated",
         "latitude_source": "original_signed_workbook_latitudes", "score_source": "current_inverted_minus_standard",
         **pearson_summary([row["original_latitude"] for row in old_order], [row["current_delta"] for row in old_order])},
        {"id": "current_scores_current_latitudes68", "label": "Current full 68: current captured latitudes and current deltas; not historical reproduction",
         "latitude_source": "current_capture_validation_coordinates", "score_source": "current_inverted_minus_standard",
         **pearson_summary([row["current_captured_latitude"] for row in rows], [row["current_delta"] for row in rows])},
        {"id": "current_scores_current_latitudes_original67", "label": "Sensitivity: original 67 identities with current captured latitudes and current deltas",
         "latitude_source": "current_capture_validation_coordinates", "score_source": "current_inverted_minus_standard",
         **pearson_summary([row["current_captured_latitude"] for row in old_order], [row["current_delta"] for row in old_order])},
    ]
    safe_categories = {
        "input_provenance": {"supplied_mastro_database", "official_adb_reconstruction", "unknown"},
        "source_review_status": {"verified_source", "review_required", "missing", "not_recorded", "unknown"},
        "source_quality_rating": {"AA", "A", "B", "C", "DD", "X", "XX", "unknown"},
        "capture_validation_status": {"position_consistency_verified", "reported_utc_verified_source_convention_unresolved"},
        "historical_equivalence": {"verified", "unverified", "not_recorded", "unknown"},
    }
    def safe_category(key, value):
        if isinstance(value, dict):
            value = value.get("status")
        return value if isinstance(value, str) and value in safe_categories[key] else "other_unclassified"
    uncertainty = {key: dict(Counter(safe_category(key, row[key]) for row in rows)) for key in safe_categories}
    # Arbitrary source notes/flag strings stay in private rows. Public output
    # carries counts, never dynamically supplied text labels or note objects.
    uncertainty["subjects_with_recorded_source_uncertainty_flags"] = sum(bool(row["source_uncertainty_flags"]) for row in rows)
    uncertainty["recorded_source_uncertainty_flag_occurrences"] = sum(len(row["source_uncertainty_flags"]) for row in rows)
    uncertainty["unresolved_application_clock_conventions"] = sum(bool(row["source_convention_discrepancy"]) for row in rows)
    public = {"schema": 1, "status": "computed_after_all141_validated",
              "protocol": "Four prespecified signed-latitude correlations; all score differences are inverted minus standard",
              "validated_total_pairs": 141, "current_southern_pairs": 68, "original_latitude_pairs": 67,
              "originally_missing_latitude_count": 1,
              "newly_available_current_latitude_count": sum(row["original_latitude_missing"] for row in rows),
              "analyses": analyses, "source_and_time_uncertainty_counts": uncertainty,
              "exclusions_based_on_outcomes_or_uncertainty": 0,
              "limits": ["Current full-68 coordinates are current captured inputs, not a historical 68-person reconstruction.",
                         "No source/time uncertainty is resolved by a passing numerical gate; all subjects remain included.",
                         "Two-sided p-values use the classical independent bivariate-normal zero-correlation null.",
                         "These four known-cohort reports are not new human validation and have no multiplicity adjustment."]}
    return {**public, "generated_utc": datetime.now(timezone.utc).isoformat(), "rows": rows,
            "public_safe_aggregate": public, "engine_sha256": next(iter(hashes)), "input_policy": next(iter(policies))}


def write_outputs(report, prefix):
    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    prefix.with_name(prefix.name + "-public.json").write_text(json.dumps(report["public_safe_aggregate"], ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    rows = report["rows"]
    with prefix.with_suffix(".csv").open("w", newline="") as stream:
        columns = list(rows[0])
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value for key, value in row.items()})
    lines = ["# Prespecified current latitude reports", "", "All 141 pairs passed the shared completion/evidence guards before these calculations.", "",
             "| Prespecified analysis | n | df | Pearson r | Two-sided p |", "| --- | --- | --- | --- | --- |"]
    for analysis in report["analyses"]:
        lines.append(f"| {analysis['label']} | {analysis['n']} | {analysis['df']} | {analysis['r']} | {analysis['two_sided_p']} |")
    lines += ["", "Current full-68 coordinates are newly captured inputs and are not a historical full-cohort reproduction. The original workbook's missing latitude remains explicitly marked in the private rows.", "",
              "All Southern subjects are retained. Source ratings, source-review flags and unresolved observed-application UTC conventions are reported without outcome-driven exclusions. Numerical consistency does not establish true birth inputs or historical equivalence.", "",
              "Private JSON and CSV contain identities and individual inputs. The separate -public.json file contains aggregate results and uncertainty counts only.", ""]
    prefix.with_suffix(".md").write_text("\n".join(lines))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=PROJECT / "reference-audit/person_manifest.json")
    parser.add_argument("--results-dir", type=Path, default=PROJECT / "cohort-results")
    parser.add_argument("--historical-audit", type=Path, default=HERE / "audit-private.json")
    parser.add_argument("--historical-workbook", type=Path, default=PROJECT / "sources/Latitude_Correlation.xlsx")
    parser.add_argument("--out-prefix", type=Path, required=True)
    parser.add_argument("--expected-engine", default="7.8.5")
    parser.add_argument("--expected-engine-hash")
    args = parser.parse_args(argv)
    try:
        manifest_raw = args.manifest.read_bytes()
        manifest = json.loads(manifest_raw)
        verify_manifest(manifest)
        people, captures, inputs, receipts = load_complete_evidence(manifest, args.results_dir, args.expected_engine, args.expected_engine_hash)
        historical = json.loads(args.historical_audit.read_text())
        evidence = historical["source_evidence"]
        if hashlib.sha256(manifest_raw).hexdigest() != evidence["manifest_sha256"]:
            raise GateClosed("Historical-audit manifest hash differs from the requested manifest")
        if hashlib.sha256(args.historical_workbook.read_bytes()).hexdigest() != evidence["workbook_sha256_before_and_after"]:
            raise GateClosed("Historical latitude workbook differs from the audited source")
        report = assemble_report(manifest, historical["rows"], people, captures, inputs)
        report["input_receipt_sha256"] = receipts
        report["historical_source_sha256"] = evidence["workbook_sha256_before_and_after"]
        write_outputs(report, args.out_prefix)
        print(json.dumps({"status": report["status"], "validated_pairs": 141, "analysis_count": 4, "output_prefix": str(args.out_prefix)}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        # Do not compute, print, or save partial-cohort correlations.
        print(json.dumps({"status": "blocked_no_inference", "reason": str(error)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
