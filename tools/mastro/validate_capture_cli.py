"""Validate saved evidence only. Exit nonzero unless the requested gate passes."""
import argparse
import json
from pathlib import Path
import sys

from capture_validator import validate_capture


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--positions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.input.read_text())
        provenance = document.get("provenance")
        if provenance == "official_adb_reconstruction":
            expected = document["source_record"]
            result = validate_capture(document, args.positions.read_text(), expected,
                                      entry_mode="utc_reconstruction")
            source_pass = result["expected_source_comparison"]["passed"]
        elif provenance == "supplied_mastro_database":
            result = validate_capture(document, args.positions.read_text())
            source_pass = True
        else:
            raise ValueError(f"Unrecognized input provenance {provenance!r}")
        position_pass = bool(result["matching_time_interpretations"])
        unambiguous_instant = result["time_mode_ambiguity"] in {"none", "same_instant_no_effect", "observed_app_utc_bound_radio_unobserved"}
        passed = source_pass and position_pass and unambiguous_instant
        result.update(passed=passed, gate_checks={"source_input_match_required_and_passed": source_pass,
                      "position_match": position_pass, "unambiguous_effective_instant": unambiguous_instant},
                      input_provenance=provenance)
    except Exception as error:
        result = {"schema": 1, "passed": False, "status": "validation_error",
                  "error_type": type(error).__name__, "error": str(error)}
        passed = False
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"passed": passed, "status": result["status"],
                      "subject_id": result.get("subject_id"), "output": str(args.output)}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
