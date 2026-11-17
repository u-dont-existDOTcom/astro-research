import _paths
"""Public-safe tests using invented captures, dates and coordinates only.

Fixtures are self-contained. The fixed planetary baseline is for an invented
2001-01-01 01:30 UTC capture, calculated once using Swiss Ephemeris/Moshier.
There are no person records, private artifacts or source-note dependencies.
"""
import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from capture_validator import (angular_error_degrees, compare_expected,
                               compare_positions, parse_standard_longitudes,
                               parse_visible_fields, validate_capture)
from validate_capture_cli import main as cli_main

HERE = Path(__file__).resolve().parent
LONGITUDES = {
    "☉": 280.697107013866, "☽": 349.461580702294,
    "☿": 284.372902104288, "♀": 327.035789258824,
    "♂": 214.974354359955, "♃": 62.185023613585,
    "♄": 54.588349712121, "♅": 318.653096040792,
    "♆": 305.329391869051, "♇": 253.770291062390,
}


def invented_source():
    return {
        "status": "synthetic_fixture",
        "published_inputs": {"birth_date": "2000-12-31", "local_time": "22:30:00",
                             "reference_meridian_source": "h3w"},
        "derived_inputs": {"utc_instant": "2001-01-01T01:30:00Z", "utc_offset_seconds": -10800,
                           "latitude_degrees": -(12 + 34 / 60 + 56 / 3600),
                           "longitude_degrees": 45 + 6 / 60 + 7 / 3600},
    }


def invented_capture(utc_entry=False):
    """Invent a small semantic control tree, using arbitrary screen geometry."""
    fields = []

    def add(handle, text, x, y, width=30, kind="STATIC", parent="form"):
        fields.append({"handle": handle, "parent": parent, "text": text,
                       "x": x, "y": y, "w": width, "h": 20,
                       "cls": f"WindowsForms10.{kind}.synthetic", "enabled": True})

    add("year-label", "Année", 100, 100, 42)
    add("month-label", "Mois", 220, 100, 30)
    add("day-label", "Jour", 340, 100, 29)
    add("year", "2001" if utc_entry else "2000", 100, 120, 53, "EDIT")
    add("month", "Janvier" if utc_entry else "Décembre", 185, 120, 122, "COMBOBOX")
    add("day", "1" if utc_entry else "31", 330, 120, 46, "EDIT")
    add("time", "01:30:00" if utc_entry else "22:30:00", 100, 165, 73, "SysDateTimePick32")
    add("offset-label", "Différence de temps avec GMT:", 100, 230, 171)
    add("offset", "0" if utc_entry else "-3", 270, 227, 73, "EDIT")
    add("name-label", "Nom:", 100, 30, 33)
    add("name", "Invented fixture", 150, 27, 200, "EDIT")
    for handle, text, x in [("lat-deg", "12", 100), ("lat-dir", "S", 120),
                            ("lat-min", "34", 140), ("lat-sec", "56", 160)]:
        add(handle, text, x, 300, 18, "EDIT", "latitude-group")
    for handle, text, x in [("lon-deg", "045", 250), ("lon-dir", "E", 275),
                            ("lon-min", "06", 295), ("lon-sec", "07", 315)]:
        add(handle, text, x, 300, 18, "EDIT", "longitude-group")
    doc = {"provenance": "official_adb_reconstruction" if utc_entry else "supplied_mastro_database",
           "visible_fields": fields}
    if utc_entry:
        doc["source_record"] = invented_source()
    return doc


def set_field(document, handle, text):
    next(field for field in document["visible_fields"] if field["handle"] == handle)["text"] = text


def table_for(longitudes=None):
    lines = ["rows=10 columns=9"]
    for row, (symbol, value) in enumerate((longitudes or LONGITUDES).items()):
        rounded = round(value * 3600) % (360 * 3600)
        degrees, remainder = divmod(rounded, 3600)
        minutes, seconds = divmod(remainder, 60)
        lines.append(f'{row} | Interior | {symbol} | unused | {degrees}° {minutes:02d}\' {seconds:02d}" | unused')
    return "\n".join(lines)


def invented_observed_clock_capture():
    document = invented_capture(True)
    document.pop("source_record")
    document["provenance"] = "supplied_mastro_database"
    document["subject_id"] = "invented-observed-clock"
    set_field(document, "time", "01:20:00")
    set_field(document, "offset", "0.1")
    main_fields = {"Nom:": "Invented fixture", "Date:": "2001/01/01",
                   "Heure:": "01:20:00", "TU:": "01:30:00 (1/1)"}
    raw = []
    for row, (label, value) in enumerate(main_fields.items()):
        for suffix, text, x, width in [("label", label, 500, 40), ("value", value, 560, 150)]:
            raw.append({"handle": f"main-{row}-{suffix}", "parent": "invented-main-panel",
                        "cls": "WindowsForms10.STATIC.synthetic", "text": text,
                        "x": x, "y": 100 + row * 20, "w": width, "h": 15})
    document["observed_utc_exception"] = {
        "schema": 1, "subject_id": "invented-observed-clock",
        "captured_source_name": "Invented fixture",
        "captured_local_datetime": "2001-01-01T01:20:00",
        "captured_offset_hours_text": "0.1", "reported_utc": "2001-01-01T01:30:00Z",
        "main_fields": main_fields, "raw_main_controls": raw,
        "observed_utc": "2002-01-01T00:00:00Z",
        "status": "unresolved_supplied_record_time_convention",
    }
    return document


class SyntheticCaptureTests(unittest.TestCase):
    def test_invented_french_date_offset_and_coordinate_signs(self):
        capture = parse_visible_fields(invented_capture()["visible_fields"])
        self.assertEqual(capture["date"], "2000-12-31")
        self.assertEqual(capture["gmt_offset_seconds"], -10800)
        self.assertEqual(capture["local_utc_candidate"], "2001-01-01T01:30:00Z")
        self.assertAlmostEqual(capture["latitude"]["degrees"], -(12 + 34 / 60 + 56 / 3600))
        self.assertAlmostEqual(capture["longitude"]["degrees"], 45 + 6 / 60 + 7 / 3600)

    def test_utc_reconstruction_checks_rollover_and_preserves_local_date(self):
        parsed = parse_visible_fields(invented_capture(True)["visible_fields"])
        result = compare_expected(parsed, invented_source(), "utc_reconstruction")
        self.assertTrue(result["passed"])
        self.assertEqual(result["source_local_date"], "2000-12-31")
        self.assertEqual(parsed["date"], "2001-01-01")
        parsed["displayed_datetime"] = "2000-12-31T01:30:00"
        self.assertFalse(compare_expected(parsed, invented_source(), "utc_reconstruction")["checks"]["date"])

    def test_wrong_offset_and_coordinate_sign_fail_expected_checks(self):
        doc = invented_capture(True)
        set_field(doc, "offset", "1")
        set_field(doc, "lat-dir", "N")
        result = compare_expected(parse_visible_fields(doc["visible_fields"]), invented_source(), "utc_reconstruction")
        self.assertFalse(result["checks"]["offset"])
        self.assertFalse(result["checks"]["latitude"])
        self.assertFalse(result["checks"]["source_derived_utc"])

    def test_unreadable_radio_same_instant_ambiguity_is_reported(self):
        result = validate_capture(invented_capture(True), table_for(), invented_source(), "utc_reconstruction")
        self.assertEqual(result["captured"]["time_radio_state"], "not_mechanically_observed")
        self.assertEqual(result["matching_time_interpretations"], ["local", "TU"])
        self.assertEqual(result["time_mode_ambiguity"], "same_instant_no_effect")

    def test_local_and_tu_candidates_are_discriminated_without_time_search(self):
        result = validate_capture(invented_capture(), table_for())
        self.assertEqual(result["matching_time_interpretations"], ["local"])
        self.assertEqual(result["effective_utc_supported_by_positions"], "2001-01-01T01:30:00Z")

    def test_wrong_hour_or_day_fails_position_check(self):
        for handle, replacement in [("time", "04:30:00"), ("day", "2")]:
            with self.subTest(field=handle):
                doc = invented_capture(True)
                set_field(doc, handle, replacement)
                self.assertEqual(validate_capture(doc, table_for())["matching_time_interpretations"], [])

    def test_invented_layout_translation_and_handle_remapping(self):
        doc = invented_capture()
        expected = parse_visible_fields(doc["visible_fields"])
        for field in doc["visible_fields"]:
            field["x"] += 91
            field["y"] += 117
            field["handle"] = "replacement-" + field["handle"]
            field["parent"] = "replacement-" + field["parent"]
        self.assertEqual(parse_visible_fields(doc["visible_fields"]), expected)

    def test_source_coordinate_seconds_sixty_is_rejected(self):
        doc = invented_capture()
        set_field(doc, "lat-sec", "60")
        with self.assertRaises(ValueError):
            parse_visible_fields(doc["visible_fields"])

    def test_missing_date_label_fails_closed(self):
        doc = invented_capture()
        doc["visible_fields"] = [f for f in doc["visible_fields"] if f["handle"] != "year-label"]
        with self.assertRaises(ValueError):
            parse_visible_fields(doc["visible_fields"])


class SyntheticPositionTests(unittest.TestCase):
    def test_point_zero_one_degree_tolerance_has_a_real_boundary(self):
        close = LONGITUDES.copy()
        close["☉"] -= 0.0099
        outside = LONGITUDES.copy()
        outside["☉"] -= 0.0101
        self.assertTrue(compare_positions("2001-01-01T01:30:00Z", close)["passed"])
        result = compare_positions("2001-01-01T01:30:00Z", outside)
        self.assertFalse(result["passed"])
        self.assertFalse(result["planets"]["Sun"]["passed"])

    def test_rounded_sixty_second_table_values_carry_and_wrap(self):
        table = table_for({symbol: 10.5 for symbol in LONGITUDES})
        carried = table.replace('10° 30\' 00"', '10° 29\' 60"', 1)
        self.assertEqual(parse_standard_longitudes(carried)["☉"], 10.5)
        wrapped = table.replace('10° 30\' 00"', '359° 59\' 60"', 1)
        self.assertEqual(parse_standard_longitudes(wrapped)["☉"], 0)
        with self.assertRaises(ValueError):
            parse_standard_longitudes(table.replace('10° 30\' 00"', '10° 29\' 61"', 1))

    def test_missing_and_duplicate_planet_rows_are_rejected(self):
        lines = table_for().splitlines()
        with self.assertRaises(ValueError):
            parse_standard_longitudes("\n".join(lines[:-1]))
        with self.assertRaises(ValueError):
            parse_standard_longitudes("\n".join(lines + [lines[1]]))
        self.assertAlmostEqual(angular_error_degrees(359.999, 0.001), 0.002)


class SyntheticCliTests(unittest.TestCase):
    def run_cli(self, document, table):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            folder = Path(directory)
            capture_path, table_path, output_path = (folder / "capture_fixture.json",
                                                     folder / "table_fixture.txt", folder / "result.json")
            capture_path.write_text(json.dumps(document))
            table_path.write_text(table)
            with redirect_stdout(StringIO()):
                code = cli_main(["--input", str(capture_path), "--positions", str(table_path), "--output", str(output_path)])
            return code, json.loads(output_path.read_text())

    def test_cli_accepts_invented_source_matched_reconstruction(self):
        code, result = self.run_cli(invented_capture(True), table_for())
        self.assertEqual(code, 0)
        self.assertTrue(result["passed"])

    def test_cli_rejects_small_entry_error_even_if_ephemeris_is_close(self):
        doc = invented_capture(True)
        set_field(doc, "time", "01:30:30")
        code, result = self.run_cli(doc, table_for())
        self.assertEqual(code, 1)
        self.assertFalse(result["expected_source_comparison"]["checks"]["source_derived_utc"])

    def test_cli_rejects_distinct_instants_both_fitting(self):
        with patch("validate_capture_cli.validate_capture", return_value={
            "status": "position_consistency_verified", "matching_time_interpretations": ["local", "TU"],
            "time_mode_ambiguity": "distinct_instants_both_fit"}):
            code, result = self.run_cli(invented_capture(), table_for())
        self.assertEqual(code, 1)
        self.assertFalse(result["passed"])

    def test_cli_rejects_missing_source_and_unrecognized_provenance(self):
        for provenance in ["official_adb_reconstruction", "invented_unsupported_type"]:
            code, result = self.run_cli({"provenance": provenance}, "")
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "validation_error")

    def test_genuine_bound_observed_app_clock_uses_only_observed_instant(self):
        code, result = self.run_cli(invented_observed_clock_capture(), table_for())
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "reported_utc_verified_source_convention_unresolved")
        self.assertEqual(result["matching_time_interpretations"], ["observed_app_UTC"])
        self.assertEqual(result["effective_utc_supported_by_positions"], "2001-01-01T01:30:00Z")
        self.assertFalse(result["position_hypotheses"]["local"]["passed"])
        self.assertFalse(result["position_hypotheses"]["TU"]["passed"])
        self.assertEqual(result["source_convention_discrepancy"]["flag"], "supplied_record_time_convention_unresolved")
        self.assertEqual(result["position_hypotheses"]["observed_app_UTC"]["threshold_degrees"], 0.01)

    def test_observed_clock_subject_and_source_bindings_fail_closed(self):
        changes = {"subject_id": "different-invented-case", "captured_source_name": "Different invented fixture",
                   "captured_local_datetime": "2001-01-02T01:20:00", "captured_offset_hours_text": "-0.1",
                   "reported_utc": "2001-01-01T01:31:00Z"}
        for key, value in changes.items():
            with self.subTest(binding=key):
                document = invented_observed_clock_capture()
                document["observed_utc_exception"][key] = value
                code, result = self.run_cli(document, table_for())
                self.assertEqual(code, 1)
                self.assertEqual(result["status"], "validation_error")

    def test_observed_clock_raw_evidence_parent_and_value_mismatches_fail(self):
        for mode in ["value", "parent", "split_panel", "missing"]:
            with self.subTest(mode=mode):
                document = invented_observed_clock_capture()
                exception = document["observed_utc_exception"]
                if mode == "value":
                    exception["main_fields"]["TU:"] = "01:31:00 (1/1)"
                elif mode == "parent":
                    exception["raw_main_controls"][-1]["parent"] = "unrelated-main-panel"
                elif mode == "split_panel":
                    for field in exception["raw_main_controls"][-2:]:
                        field["parent"] = "unrelated-main-panel"
                else:
                    exception["raw_main_controls"] = []
                code, result = self.run_cli(document, table_for())
                self.assertEqual(code, 1)
                self.assertEqual(result["status"], "validation_error")

    def test_reconstructed_input_cannot_use_observed_clock_override(self):
        document = invented_capture(True)
        document["observed_utc_exception"] = copy.deepcopy(invented_observed_clock_capture()["observed_utc_exception"])
        code, result = self.run_cli(document, table_for())
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "validation_error")
        self.assertIn("forbidden", result["error"])

    def test_observed_clock_position_mismatch_cannot_fall_back(self):
        document = invented_observed_clock_capture()
        table = table_for({symbol: (value + 1) % 360 for symbol, value in LONGITUDES.items()})
        code, result = self.run_cli(document, table)
        self.assertEqual(code, 1)
        self.assertFalse(result["passed"])
        self.assertEqual(result["matching_time_interpretations"], [])


if __name__ == "__main__":
    unittest.main()
