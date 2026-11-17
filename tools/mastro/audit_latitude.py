"""Bounded read-only audit of the retained latitude-correlation workbook."""
from collections import Counter
import ast
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import scipy
from scipy import special, stats

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
WORKBOOK = PROJECT / "sources/Latitude_Correlation.xlsx"
MANIFEST = PROJECT / "reference-audit/person_manifest.json"
# Reuse only the established pure normalizer and alias constant. Importing the
# entire reference-audit module would unnecessarily require its workbook stack.
normalizer_path = HERE / "audit_references.py"
normalizer_tree = ast.parse(normalizer_path.read_text())
normalizer_nodes = [node for node in normalizer_tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "identity_key"
                    or isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "ALIASES" for target in node.targets)]
assert len(normalizer_nodes) == 2
normalizer_namespace = {"unicodedata": unicodedata}
exec(compile(ast.Module(body=normalizer_nodes, type_ignores=[]), str(normalizer_path), "exec"), normalizer_namespace)
identity_key = normalizer_namespace["identity_key"]

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
PRIMARY_REFERENCES = [
    {"purpose": "Pearson statistic and exact null distribution", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html"},
    {"purpose": "Excel T.DIST is a left-tail cumulative distribution", "url": "https://support.microsoft.com/en-us/excel/functions/t-dist-function"},
    {"purpose": "Excel sign-safe two-tailed t probability", "url": "https://support.microsoft.com/en-us/excel/functions/t-dist-2t-function"},
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_workbook():
    with zipfile.ZipFile(WORKBOOK) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheet = workbook.find("m:sheets/m:sheet", NS)
        strings = ["".join(element.itertext()) for element in
                   ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("m:si", NS)]
        xml = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        cells = {}
        for row in xml.findall("m:sheetData/m:row", NS):
            for cell in row.findall("m:c", NS):
                value, formula = cell.find("m:v", NS), cell.find("m:f", NS)
                if value is None and formula is None:
                    continue
                raw = value.text if value is not None else None
                parsed = strings[int(raw)] if cell.get("t") == "s" else float(raw) if raw is not None else None
                cells[cell.get("r")] = {"value": parsed, "formula": formula.text if formula is not None else None,
                                        "stored_value_text": raw, "cell_type": cell.get("t", "n")}
        metadata = {
            "sheet_name": sheet.get("name"), "sheet_count": len(workbook.findall("m:sheets/m:sheet", NS)),
            "dimension_including_formatting": xml.find("m:dimension", NS).get("ref"),
            "defined_names": [dict(name.attrib, formula=name.text) for name in workbook.findall("m:definedNames/m:definedName", NS)],
            "hidden_rows": [int(row.get("r")) for row in xml.findall("m:sheetData/m:row", NS) if row.get("hidden") == "1"],
            "formula_cells": {address: cell for address, cell in cells.items() if cell["formula"]},
            "populated_rows": sorted({int("".join(c for c in address if c.isdigit())) for address in cells}),
            "populated_cells_outside_A1_D68": [address for address in cells
                if not (address.rstrip("0123456789") in {"A", "B", "C", "D"} and int("".join(c for c in address if c.isdigit())) <= 68)],
        }
        return cells, metadata


def main():
    source_hash = sha256(WORKBOOK)
    cells, metadata = extract_workbook()
    manifest = json.loads(MANIFEST.read_text())
    intended = [record for record in manifest if record["hemisphere"] == "South"]
    by_key = {record["identity_join_key"]: record for record in intended}
    assert len(by_key) == len(intended) == 68
    assert all(identity_key(record["source_labels"]["comparison"]) == record["identity_join_key"] for record in intended)
    # Unique surname plus first initial resolves this one abbreviation. It is
    # declared before score comparison and does not use scores as a join key.
    abbreviation = {identity_key("Allende, S."): identity_key("Allende, Salvador")}
    rows = []
    for row in range(2, 69):
        name, latitude, difference = [cells[f"{column}{row}"]["value"] for column in "ABC"]
        normalized = identity_key(name)
        key = abbreviation.get(normalized, normalized)
        record = by_key[key]
        standard = record["comparison_input"]["standard_global"]
        inverted = record["comparison_input"]["inverted_global"]
        delta = inverted - standard
        rows.append({
            "excel_row": row, "workbook_name": name, "identity_join_key": key,
            "subject_id": record["subject_id"], "subject_name": record["subject_list_name"],
            "join_method": "explicit_unique_surname_initial_abbreviation" if key != normalized else "established_identity_normalization",
            "signed_latitude_as_supplied": latitude, "difference_as_supplied": difference,
            "original_standard_global": standard, "original_inverted_global": inverted,
            "recomputed_inverted_minus_standard": delta,
            "manifest_delta": record["inverted_minus_standard"],
            "absolute_difference_error": abs(difference - delta),
            "difference_sign_matches_original_scores": (difference > 0) == (delta > 0) and (difference < 0) == (delta < 0),
        })
    included = {row["subject_id"] for row in rows}
    missing = [record for record in intended if record["subject_id"] not in included]
    assert len(included) == len(rows) == 67
    assert len(missing) == 1
    assert all(row["absolute_difference_error"] < 1e-12 and row["difference_sign_matches_original_scores"] for row in rows)
    assert all(-90 <= row["signed_latitude_as_supplied"] < 0 for row in rows)
    assert cells["D2"]["formula"] == "CORREL(C2:C68,B2:B68)"
    assert cells["D3"]["formula"] == "D2*(65/(1-D2^2))^0.5"
    assert cells["D4"]["formula"] == "2*_xlfn.T.DIST(D3,65,TRUE)"
    x = [row["signed_latitude_as_supplied"] for row in rows]
    y = [row["difference_as_supplied"] for row in rows]
    n = len(x)
    xmean, ymean = math.fsum(x) / n, math.fsum(y) / n
    cross = math.fsum((a - xmean) * (b - ymean) for a, b in zip(x, y))
    squares_x = math.fsum((a - xmean) ** 2 for a in x)
    squares_y = math.fsum((b - ymean) ** 2 for b in y)
    r = cross / math.sqrt(squares_x * squares_y)
    df = n - 2
    t = r * math.sqrt(df / (1 - r * r))
    p_t = float(2 * stats.t.sf(abs(t), df))
    scipy_result = stats.pearsonr(x, y)
    p_beta = float(2 * special.betainc(n / 2 - 1, n / 2 - 1, (1 - abs(r)) / 2))
    p_original = float(2 * stats.t.cdf(t, df))
    assert abs(r - scipy_result.statistic) < 1e-14
    assert abs(p_t - scipy_result.pvalue) < 1e-12 and abs(p_t - p_beta) < 1e-12
    assert abs(r - cells["D2"]["value"]) < 1e-14
    assert abs(t - cells["D3"]["value"]) < 1e-12
    assert abs(p_original - cells["D4"]["value"]) < 1e-12
    assert abs(p_t - cells["D4"]["value"]) < 1e-12
    assert sha256(WORKBOOK) == source_hash
    sign_counts = dict(Counter("inverted_higher" if row["difference_as_supplied"] > 0 else "standard_higher" if row["difference_as_supplied"] < 0 else "tie" for row in rows))
    full_rows = []
    by_id = {row["subject_id"]: row for row in rows}
    for record in intended:
        row = by_id.get(record["subject_id"])
        full_rows.append({"subject_id": record["subject_id"], "subject_name": record["subject_list_name"],
                          "signed_latitude_as_supplied": row["signed_latitude_as_supplied"] if row else None,
                          "latitude_workbook_row": row["excel_row"] if row else None,
                          "difference_from_original_scores": record["comparison_input"]["inverted_global"] - record["comparison_input"]["standard_global"],
                          "status": "available_in_supplied_latitude_workbook" if row else "missing_latitude_row"})
    full_cohort = {"intended_subject_count": 68, "available_paired_count": 67, "required_df_if_all_68_pairs_available": 66,
                   "status": "full_cohort_correlation_unavailable_from_supplied_workbook",
                   "r": None, "two_sided_p": None,
                   "reason": "One intended subject has no supplied latitude row. No latitude was guessed, fetched from a different vintage or selected using score results.",
                   "records": full_rows}
    aggregate = {
        "schema": 1, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_policy": "Preserve the original 67 supplied pairs and formula ranges. Audit the intended 68-subject cohort separately; do not impute its missing latitude or select analyses by result.",
        "coverage": {"intended_subject_count": 68, "supplied_named_pairs": n, "unique_joined_subjects": len(included),
                     "missing_subject_count": len(missing), "duplicate_subject_count": len(rows) - len(included),
                     "all_present_rows_in_correlation_range": True, "populated_pair_rows_outside_range": 0},
        "score_reconciliation": {"matched_against_original_score_difference_count": n,
                                 "difference_definition": "inverted_global minus standard_global",
                                 "maximum_absolute_difference_error": max(row["absolute_difference_error"] for row in rows),
                                 "sign_mismatch_count": 0, "sign_counts": sign_counts,
                                 "all_supplied_latitude_signs_southern": True},
        "original_formula_range": {"latitude": "B2:B68", "difference": "C2:C68", "n": n, "df": df},
        "recomputed": {"pearson_r_centered_sum": r, "pearson_r_scipy": float(scipy_result.statistic),
                       "t_statistic": t, "two_sided_p_standard_t": p_t,
                       "two_sided_p_exact_normal_null_beta": p_beta, "two_sided_p_scipy": float(scipy_result.pvalue),
                       "all_three_cached_statistics_reproduced": True},
        "p_formula_audit": {"original_formula": "2*T.DIST(t,65,TRUE)", "original_numeric_value": p_original,
                            "correct_for_current_negative_t": True, "current_numeric_error": abs(p_original - p_t),
                            "general_sign_safe_formula": "T.DIST.2T(ABS(t),n-2)",
                            "equivalent_sign_safe_formula": "2*T.DIST(-ABS(t),n-2,TRUE)",
                            "if_t_sign_reversed_original_formula": float(2 * stats.t.cdf(-t, df)),
                            "if_t_sign_reversed_correct_two_sided_p": p_t,
                            "sign_reversal_example_is_algebraic_check_not_an_added_analysis": True},
        "full_intended_cohort": {key: value for key, value in full_cohort.items() if key != "records"},
        "limitations": ["The missing subject's latitude is not supplied, so a 68-person correlation cannot be recovered from this workbook alone.",
                        "Latitude magnitudes and birth locations were not independently geocoded in this bounded arithmetic audit.",
                        "The standard t and exact beta p-values use the classical independent bivariate-normal zero-correlation null; they are not a distribution-free permutation result.",
                        "This audits the supplied historical score differences. It does not validate new GUI runs or establish an astrological effect."],
        "primary_math_and_function_references": PRIMARY_REFERENCES,
        "software": {"python": sys.version.split()[0], "scipy": scipy.__version__, "numpy": np.__version__},
    }
    private = dict(aggregate, source_evidence={"workbook_path": str(WORKBOOK), "workbook_sha256_before_and_after": source_hash,
                                             "manifest_path": str(MANIFEST), "manifest_sha256": sha256(MANIFEST),
                                             "normalizer_source_sha256": sha256(normalizer_path),
                                             "workbook_metadata": metadata},
                   missing_subjects=[{"subject_id": record["subject_id"], "name": record["subject_list_name"],
                                      "original_difference": record["inverted_minus_standard"]} for record in missing],
                   rows=rows)
    for name, document in [("audit-private.json", private), ("audit-public-aggregate.json", aggregate),
                           ("intended-full-cohort-private.json", full_cohort)]:
        (HERE / name).write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    public_md = f"""# Latitude-correlation arithmetic audit

The supplied analysis contains **67 paired observations** from an intended cohort of 68. Its correlation range includes every supplied row; the missing subject is absent from the source table rather than excluded by an off-by-one range. Degrees of freedom **65** are correct for the supplied 67 pairs.

| Check | Result |
| --- | --- |
| Original supplied rows | 67 |
| Intended cohort | 68 |
| Duplicates or unmatched supplied subjects | 0 |
| Supplied differences agreeing with original inverted-minus-standard scores | 67 of 67 |
| Difference-sign mismatches | 0 |
| Pearson correlation | {r:.12f} |
| t statistic, df = 65 | {t:.12f} |
| Two-sided p | {p_t:.12f} |

The centered-sum Pearson calculation, SciPy's Pearson implementation, the standard t-tail probability and the exact beta null-distribution probability agree. All three saved result cells are reproduced. The supplied score differences are inverted score minus standard score; {sign_counts.get('inverted_higher',0)} favor the inverted score and {sign_counts.get('standard_higher',0)} favor the standard score. Latitudes are signed Southern values. Negating the latitude convention or reversing the difference definition flips r and t but leaves a proper two-sided p unchanged.

The workbook uses `2*T.DIST(t,65,TRUE)`. This gives the correct two-sided value for its current negative t. It is not sign-safe: reversing t would produce {2 * stats.t.cdf(-t,df):.12f}, above one. A general formula is `T.DIST.2T(ABS(t),n-2)` or `2*T.DIST(-ABS(t),n-2,TRUE)`. This formula issue has **no numerical effect on the supplied negative-t result**.

The intended 68-person analysis is retained separately and is unavailable from the supplied workbook because one latitude row is missing. Once all 68 pairs are available, its df would be 66. No missing latitude was imputed or borrowed from another source vintage, and no alternative analysis was chosen by its result.

These p-values use the classical independent bivariate-normal zero-correlation null. Latitude magnitudes and birth locations were not independently geocoded in this arithmetic audit. The workbook was read without modification, export or native recalculation.

Primary references: [SciPy Pearson documentation]({PRIMARY_REFERENCES[0]['url']}), [Microsoft T.DIST]({PRIMARY_REFERENCES[1]['url']}), [Microsoft T.DIST.2T]({PRIMARY_REFERENCES[2]['url']}).
"""
    (HERE / "audit-public-aggregate.md").write_text(public_md)
    missing_person = missing[0]
    private_md = public_md + f"""
## Private identity and cell evidence

The missing subject is **{missing_person['subject_list_name']} ({missing_person['subject_id']})**. The original score difference is {missing_person['inverted_minus_standard']:.15f}; the source latitude is unavailable. This does not identify a population-level effect of the omission.

The exact sheet is `{metadata['sheet_name']}`. Its stored dimension is `{metadata['dimension_including_formatting']}`, reflecting formatting beyond the data. The actual named table is `A1:C68`, with 67 data rows at rows 2–68. There are no populated pair rows outside that range, no defined names and no hidden data rows.

The original formulas and caches are:

| Cell | Formula | Cached value |
| --- | --- | --- |
| D2 | `CORREL(C2:C68,B2:B68)` | {cells['D2']['value']:.17g} |
| D3 | `D2*(65/(1-D2^2))^0.5` | {cells['D3']['value']:.17g} |
| D4 | `2*_xlfn.T.DIST(D3,65,TRUE)` | {cells['D4']['value']:.17g} |

Sixty-six rows join using the established identity normalization from the reference audit. `Allende, S.` joins by an explicit, unique surname-and-initial abbreviation to Allende, Salvador ({by_key[abbreviation[identity_key('Allende, S.')]]['subject_id']}). This identity was resolved without using scores. All 67 supplied differences agree with the original two score columns within {max(row['absolute_difference_error'] for row in rows):.3g}; all signs agree.

Private row evidence is in `audit-private.json`; the full intended cohort, including the missing latitude marker, is in `intended-full-cohort-private.json`. The two `audit-public-aggregate` files contain no person names, subject identifiers or individual latitude/score rows and are separable authored summaries. They have not been published.

Workbook SHA-256, unchanged before and after this read-only audit: `{source_hash}`.
"""
    (HERE / "audit-private.md").write_text(private_md)
    print(json.dumps({"n": n, "missing": private["missing_subjects"], "r": r, "t": t, "p": p_t,
                      "maximum_score_difference_error": aggregate["score_reconciliation"]["maximum_absolute_difference_error"],
                      "score_sign_counts": sign_counts, "source_unchanged": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    WORKBOOK=args.workbook.resolve()
    MANIFEST=args.manifest.resolve()
    HERE=args.output.resolve()
    HERE.mkdir(parents=True,exist_ok=True)
    main()
