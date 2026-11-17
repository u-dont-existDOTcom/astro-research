"""Audit private retained research workbooks without editing their contents.

The scoring rule adapts the previously verified literal_score function in the
2026-11-09 Mastro comparison harness. This is historical arithmetic and input
reconciliation, not chart regeneration or a new behavioral/statistical test.
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import difflib
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

import openpyxl

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT.parent / "sources"
ALIASES = {"assangejulian": "assangejulien"}


def identity_key(text: str) -> str:
    """Join names only; never apply this normalization to keyword strings."""
    value = text.casefold().replace("ł", "l").replace("œ", "oe")
    key = "".join(c for c in unicodedata.normalize("NFKD", value) if c.isalnum())
    return ALIASES.get(key, key)


def word(value) -> bool:
    return isinstance(value, str) and value != ""


def traits_from_column(rows, column, first_row):
    return [{"row": i + 1, "word": row[column]} for i, row in enumerate(rows)
            if i >= first_row - 1 and word(row[column])]


def literal_matches(words: list[str], keywords: list[dict]) -> list[float]:
    first = {}
    for row in keywords:
        first.setdefault(row["word"].lower(), row["weight"])
    return [first.get(value.lower(), 0.0) for value in words]


def literal_score(words: list[str], keywords: list[dict]) -> float:
    if not keywords:
        raise ValueError("Cannot score an empty ASTRO list")
    return math.fsum(literal_matches(words, keywords)) / len(keywords)


def document_subjects():
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(SOURCES / "subjects.docx") as package:
        tree = ET.fromstring(package.read("word/document.xml"))
    paragraphs = ["".join(t.text or "" for t in p.findall(".//w:t", ns))
                  for p in tree.findall(".//w:p", ns)]
    result = {}
    cohort = None
    for paragraph in paragraphs:
        if "Northern Hemisphere" in paragraph:
            cohort = "North"
        elif "Southern Hemisphere" in paragraph:
            cohort = "South"
        elif ";" in paragraph:
            if cohort in result:
                raise ValueError("Multiple list paragraphs require explicit review")
            result[cohort] = [v.strip().rstrip(".").strip()
                              for v in paragraph.split(";") if v.strip()]
    assert len(result["North"]) == 73 and len(result["South"]) == 68
    return result


def sparse_sheet_rows(sheet, header_row, stride=1):
    header = next(sheet.iter_rows(min_row=header_row, max_row=header_row, values_only=True))
    active = [i for i in range(0, len(header), stride) if word(header[i])]
    if not active:
        raise ValueError("No labeled data columns")
    limit = max(active) + stride
    return list(sheet.iter_rows(max_col=limit, values_only=True)), active


def load_astro():
    book = openpyxl.load_workbook(SOURCES / "ASTRO_words.xlsx", read_only=True, data_only=True)
    result = {}
    for sheet in book:
        rows, columns = sparse_sheet_rows(sheet, 1, 4)
        for col in columns:
            name = rows[0][col]
            if identity_key(rows[0][col + 2]) != identity_key(name):
                raise ValueError(f"ASTRO pair has different identities: {sheet.title}, {col+1}")
            key = identity_key(name)
            if key in result:
                raise ValueError(f"Duplicate ASTRO subject block: {name}")
            arms = {}
            for condition, offset in [("standard", 0), ("inverted", 2)]:
                records = []
                declared_counts = None
                for i, row in enumerate(rows[1:], 2):
                    label, weight = row[col + offset:col + offset + 2]
                    if word(label) and isinstance(weight, (int, float)):
                        if not math.isfinite(weight):
                            raise ValueError("Nonfinite ASTRO weight")
                        records.append({"row": i, "word": label, "weight": weight})
                    elif i == 400 and isinstance(label, (int, float)) and isinstance(weight, (int, float)):
                        declared_counts = {"row": i, "keyword_count": label, "score_count": weight}
                    elif word(label) or isinstance(weight, (int, float)):
                        raise ValueError(f"Unpaired ASTRO record at {sheet.title}:{i},{col+offset+1}")
                if declared_counts and any(declared_counts[k] != len(records) for k in ("keyword_count", "score_count")):
                    raise ValueError("Declared ASTRO count differs from actual records")
                arms[condition] = {"column": col + offset + 1, "keywords": records,
                                   "source_count_cells": declared_counts}
            result[key] = {"name": name, "sheet": sheet.title, "arms": arms}
    return result


def load_bio():
    book = openpyxl.load_workbook(SOURCES / "BIO_words.xlsx", read_only=True, data_only=True)
    result = {}
    for sheet in book:
        rows, columns = sparse_sheet_rows(sheet, 1)
        for col in columns:
            name = rows[0][col]
            key = identity_key(name)
            if key in result:
                raise ValueError(f"Duplicate BIO identity: {name}")
            result[key] = {"name": name, "sheet": sheet.title, "column": col + 1,
                           "records": traits_from_column(rows, col, 2)}
    return result


def load_comparisons():
    book = openpyxl.load_workbook(SOURCES / "Comparisons.xlsx", read_only=True, data_only=True)
    result = {}
    for sheet in book:
        rows, columns = sparse_sheet_rows(sheet, 3, 3)
        for col in columns:
            name = rows[2][col]
            if not all(identity_key(rows[2][col + offset]) == identity_key(name) for offset in (1, 2)):
                raise ValueError("Comparison triple identity mismatch")
            records = []
            for i, row in enumerate(rows[3:], 4):
                if word(row[col]):
                    if not all(isinstance(row[col + offset], (int, float)) for offset in (1, 2)):
                        raise ValueError("A comparison trait lacks numeric matched scores")
                    records.append({"row": i, "word": row[col],
                                    "standard_match": row[col + 1],
                                    "inverted_match": row[col + 2]})
            key = identity_key(name)
            if key in result:
                raise ValueError("Duplicate comparison identity")
            result[key] = {"name": name, "hemisphere": sheet.title, "column": col + 1,
                           "records": records,
                           "standard_global": rows[1][col + 1],
                           "inverted_global": rows[1][col + 2]}
    return result


def workbook_structure():
    structures = []
    for path in sorted(SOURCES.glob("*.xlsx")):
        book = openpyxl.load_workbook(path, read_only=True, data_only=False)
        sheets = []
        for sheet in book:
            formulas = [cell.value for row in sheet for cell in row if cell.data_type == "f"]
            sheets.append({"name": sheet.title, "formula_count": len(formulas),
                           "lookup_formula_count": sum("LOOKUP" in f.upper() or "MATCH(" in f.upper() for f in formulas),
                           "declared_dimensions": [sheet.max_row, sheet.max_column]})
        structures.append({"file": path.name, "sheets": sheets,
                           "contains_interactive_evaluator_sheet_set":
                           {"astro", "bio", "analyse"}.issubset({s.title.casefold() for s in book})})
    return structures


def sequence_changes(before, after):
    changes = []
    for opcode, i, j, a, b in difflib.SequenceMatcher(
            a=[r["word"].lower() for r in before], b=[r["word"].lower() for r in after], autojunk=False).get_opcodes():
        if opcode != "equal":
            changes.append({"kind": opcode, "bio_source_rows": before[i:j], "comparison_rows": after[a:b]})
    return changes


def audit():
    subjects, astro, bio, comparisons = document_subjects(), load_astro(), load_bio(), load_comparisons()
    manifest, discrepancies, summaries, name_joins, multiset_differences = [], [], [], [], []
    totals = collections.Counter()
    for hemisphere, names in subjects.items():
        cohort = collections.Counter()
        for ordinal, source_name in enumerate(names, 1):
            key = identity_key(source_name)
            a, b, c = astro[key], bio[key], comparisons[key]
            if c["hemisphere"] != hemisphere:
                raise ValueError("Comparison cohort mismatch")
            comparison_words = [r["word"] for r in c["records"]]
            bio_words = [r["word"] for r in b["records"]]
            changes = sequence_changes(b["records"], c["records"])
            if changes:
                discrepancies.append({"subject_name": source_name, "hemisphere": hemisphere,
                                      "source_bio_count": len(bio_words), "comparison_bio_count": len(comparison_words),
                                      "differences_case_insensitive": changes})
            source_counts = collections.Counter(v.lower() for v in bio_words)
            comparison_counts = collections.Counter(v.lower() for v in comparison_words)
            if source_counts != comparison_counts:
                changed_words = set((source_counts - comparison_counts) + (comparison_counts - source_counts))
                multiset_differences.append({"subject_name": source_name, "hemisphere": hemisphere,
                    "source_bio_count": len(bio_words), "comparison_bio_count": len(comparison_words),
                    "occurrences_removed_in_comparison": dict(source_counts - comparison_counts),
                    "occurrences_added_in_comparison": dict(comparison_counts - source_counts),
                    "source_bio_rows_for_changed_words": [r for r in b["records"] if r["word"].lower() in changed_words],
                    "comparison_rows_for_changed_words": [r for r in c["records"] if r["word"].lower() in changed_words]})
            source_labels = {"subject_list": source_name, "astro": a["name"], "bio": b["name"], "comparison": c["name"]}
            if len(set(source_labels.values())) > 1:
                name_joins.append({"subject": source_name, "labels": source_labels,
                                   "rule": "explicit Julian/Julien alias" if "assange" in key else "identity-only Unicode/case/punctuation/spacing normalization"})
            results = {}
            for condition in ("standard", "inverted"):
                records = a["arms"][condition]["keywords"]
                calculated = literal_matches(comparison_words, records)
                supplied = [r[condition + "_match"] for r in c["records"]]
                failures = [{"row": c["records"][i]["row"], "word": comparison_words[i], "calculated": x,
                             "supplied": y} for i, (x, y) in enumerate(zip(calculated, supplied))
                            if not math.isclose(x, y, abs_tol=1e-12, rel_tol=0)]
                global_calculated = math.fsum(calculated) / len(records)
                global_difference = global_calculated - c[condition + "_global"]
                if failures or abs(global_difference) > 1e-12:
                    raise ValueError(f"Arithmetic mismatch for {source_name}/{condition}: {failures[:3]}, global {global_difference}")
                counts = collections.Counter(r["word"].lower() for r in records)
                results[condition] = {"astro_record_count": len(records),
                                      "repeated_astro_labels": {k: n for k, n in counts.items() if n > 1},
                                      "reconciled_comparison_cells": len(calculated),
                                      "comparison_input_global": global_calculated,
                                      "supplied_global": c[condition + "_global"],
                                      "source_bio_input_global": literal_score(bio_words, records),
                                      "absolute_global_error": abs(global_difference),
                                      "matched_weight_sum": math.fsum(calculated)}
                totals["reconciled_cells"] += len(calculated)
                totals["reconciled_global_scores"] += 1
            delta = results["inverted"]["comparison_input_global"] - results["standard"]["comparison_input_global"]
            winner = "inverted" if delta > 0 else "standard" if delta < 0 else "tie"
            cohort[winner] += 1
            source_delta = results["inverted"]["source_bio_input_global"] - results["standard"]["source_bio_input_global"]
            source_winner = "inverted" if source_delta > 0 else "standard" if source_delta < 0 else "tie"
            cohort["bio_source_" + source_winner] += 1
            cohort["comparison_words"] += len(comparison_words)
            cohort["bio_source_words"] += len(bio_words)
            record = {"subject_id": f"{hemisphere[0]}{ordinal:03d}", "hemisphere": hemisphere,
                      "subject_list_name": source_name, "identity_join_key": key, "source_labels": source_labels,
                      "astro_source": a, "bio_source": b, "comparison_input": c,
                      "evaluation": results, "inverted_minus_standard": delta,
                      "winner": winner, "bio_source_winner": source_winner,
                      "birth_inputs": None, "birth_inputs_status": "Not supplied in these reference workbooks; separate application database verification required."}
            manifest.append(record)
            summaries.append({"subject_id": record["subject_id"], "hemisphere": hemisphere,
                              "name": source_name, "comparison_bio_count": len(comparison_words),
                              "source_bio_count": len(bio_words), "standard_astro_count": results["standard"]["astro_record_count"],
                              "inverted_astro_count": results["inverted"]["astro_record_count"],
                              "standard_score": results["standard"]["comparison_input_global"],
                              "inverted_score": results["inverted"]["comparison_input_global"],
                              "inverted_minus_standard": delta, "winner": winner,
                              "source_bio_standard_score": results["standard"]["source_bio_input_global"],
                              "source_bio_inverted_score": results["inverted"]["source_bio_input_global"],
                              "source_bio_winner": source_winner})
        totals[hemisphere] = dict(cohort)
    intended = {identity_key(x) for names in subjects.values() for x in names}
    extra = [{"join_key": k, "name": v["name"], "sheet": v["sheet"],
              "columns": {arm: d["column"] for arm, d in v["arms"].items()},
              "record_counts": {arm: len(d["keywords"]) for arm, d in v["arms"].items()}}
             for k, v in astro.items() if k not in intended]
    summary = {"audit_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "status": "Historical arithmetic and reference-input audit only; no new chart output generated.",
               "subject_counts": {k: len(v) for k, v in subjects.items()},
               "manifest_person_count": len(manifest), "historical_vector_count": len(manifest) * 2,
               "totals": dict(totals), "extra_astro_subject_blocks": extra,
               "bio_variant_subject_count": len(discrepancies),
               "bio_multiset_variant_subject_count": len(multiset_differences),
               "bio_variant_count_difference": sum(d["comparison_bio_count"] - d["source_bio_count"] for d in discrepancies),
               "source_bio_score_variant_subject_count": sum(any(abs(v["comparison_input_global"] - v["source_bio_input_global"]) > 1e-12 for v in p["evaluation"].values()) for p in manifest),
               "source_bio_changed_winner_count": sum(p["winner"] != p["bio_source_winner"] for p in manifest),
               "maximum_absolute_global_reconciliation_error": max(v["absolute_global_error"] for p in manifest for v in p["evaluation"].values()),
               "source_name_join_variations": name_joins, "workbook_structure": workbook_structure(),
               "input_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCES.iterdir()) if p.suffix in (".xlsx", ".docx")},
               "rules": {"keyword_case": "lower()", "keyword_trimming": False,
                         "duplicate_astro": "first matching record", "duplicate_bio": "each occurrence contributes",
                         "normalization": "sum matched ASTRO weights / original ASTRO record count",
                         "summary_counts": "Numeric ASTRO counts on row400 are independently checked against actual record lengths and excluded from keyword vectors; numeric BIO summary counts are excluded from trait lists.",
                         "identity_normalization": "Unicode/case/punctuation/spacing for name joins only; explicit Julian to Julien alias",
                         "global_tolerance": 1e-12},
               "limitations": ["No original chart generation was run by this audit.",
                               "Original birth inputs and historical executable equivalence are not established by the reference workbooks.",
                               "The original BIO workbook and copied comparison BIO columns differ; both are preserved and scored separately.",
                               "No delivered workbook contains the demonstrated Astro/BIO/Analyse interactive-evaluator sheet set."]}
    assert len(manifest) == 141
    assert totals["reconciled_cells"] == 41940 and totals["reconciled_global_scores"] == 282
    assert totals["North"]["inverted"] == 26 and totals["South"]["inverted"] == 48
    (ROOT / "person_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    (ROOT / "reconciliation_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    (ROOT / "bio_input_differences.json").write_text(json.dumps(discrepancies, ensure_ascii=False, indent=2))
    (ROOT / "bio_multiset_differences.json").write_text(json.dumps(multiset_differences, ensure_ascii=False, indent=2))
    with (ROOT / "person_reconciliation.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    print(json.dumps({k: summary[k] for k in ("manifest_person_count", "historical_vector_count", "totals", "extra_astro_subject_blocks", "bio_variant_subject_count", "bio_variant_count_difference")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    SOURCES = args.sources.resolve()
    ROOT = args.output.resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    audit()
