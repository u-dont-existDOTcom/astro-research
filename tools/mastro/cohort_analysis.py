"""Analyze CURRENT engine trees against the private historical 141-person manifest.

This module performs no chart generation, GUI action, publication or mail.
Only complete.json-marked, internally consistent pairs enter cohort summaries.
Partial runs receive descriptive results without significance tests or intervals.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import datetime as dt
from decimal import Decimal
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import statistics

from mastro_tree import parse_tree, first_matches

HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "person_manifest.json"


def exact(value):
    return value if isinstance(value, Fraction) else Fraction(Decimal(str(value)))


def records(values):
    result = []
    for value in values:
        label, weight = value["word"], Decimal(str(value["weight"]))
        if not isinstance(label, str) or not label or not weight.is_finite() or weight < 0:
            raise ValueError("Invalid keyword record")
        result.append({"word": label, "weight": weight})
    if not result:
        raise ValueError("Empty ASTRO vector")
    return result


def score(words, keywords):
    if not keywords:
        raise ValueError("Empty ASTRO vector")
    numerator = sum((exact(x) for x in first_matches(words, keywords)), Fraction())
    return numerator / len(keywords), numerator


def winner(delta):
    return "inverted" if delta > 0 else "standard" if delta < 0 else "tie"


def snapshot(path):
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("File changed while being read")
    return raw.decode("utf-8"), hashlib.sha256(raw).hexdigest(), after.st_mtime_ns


def read_json(text):
    def nonfinite(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(text, parse_constant=nonfinite)


def fraction_json(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def vector_difference(reference, current):
    old, new = defaultdict(list), defaultdict(list)
    for row in reference:
        old[row["word"]].append(row["weight"])
    for row in current:
        new[row["word"]].append(row["weight"])
    added, removed, changed = [], [], []
    for label in sorted(old.keys() | new.keys()):
        for ordinal, (a, b) in enumerate(itertools.zip_longest(old[label], new[label]), 1):
            if a is None:
                added.append({"word": label, "occurrence": ordinal, "weight": b})
            elif b is None:
                removed.append({"word": label, "occurrence": ordinal, "weight": a})
            elif a != b:
                changed.append({"word": label, "occurrence": ordinal,
                                "historical": a, "current": b, "change": b-a})
    def first(vector):
        result = {}
        for row in vector:
            result.setdefault(row["word"].lower(), row["weight"])
        return result
    first_old, first_new = first(reference), first(current)
    first_changes = [{"literal_key": key, "historical": first_old.get(key), "current": first_new.get(key)}
                     for key in sorted(first_old.keys() | first_new.keys())
                     if first_old.get(key) != first_new.get(key)]
    return {"historical_records": len(reference), "current_records": len(current),
            "added_keyword_rows": added, "removed_keyword_rows": removed,
            "added_keyword_row_count": len(added), "removed_keyword_row_count": len(removed),
            "changed_weight_rows": changed, "changed_weight_row_count": len(changed),
            "literal_first_match_changes": first_changes,
            "literal_first_match_change_count": len(first_changes),
            "historical_duplicate_literal_labels": {k:n for k,n in Counter(r["word"].lower() for r in reference).items() if n>1},
            "current_duplicate_literal_labels": {k:n for k,n in Counter(r["word"].lower() for r in current).items() if n>1},
            "keyword_sequence_equal": [r["word"] for r in reference] == [r["word"] for r in current],
            "ordered_vector_equal": reference == current,
            "vector_multiset_equal": Counter((r["word"], r["weight"]) for r in reference) == Counter((r["word"], r["weight"]) for r in current)}


RATINGS={"AA","A","B","C","DD","X","XX"}


def rating_info(value):
    """Preserve the declared raw quality label; never infer historical truth."""
    provenance=value.get("provenance","")
    source=value.get("source_record",{})
    if provenance=="official_adb_reconstruction":
        raw=source.get("published_inputs",{}).get("rodden_rating") if isinstance(source,dict) else None
        normalized=raw.strip().upper() if isinstance(raw,str) else None
        return {"source_quality_rating":normalized if normalized in RATINGS else "unknown",
                "source_quality_rating_raw":raw,"source_quality_rating_origin":"published_source_record",
                "source_quality_rating_status":"recognized" if normalized in RATINGS else "missing" if raw is None else "unrecognized"}
    visible=value.get("visible_fields",[])
    combos=[f for f in visible if isinstance(f,dict) and "COMBOBOX" in str(f.get("cls","")).upper()]
    located=[f for f in combos if f.get("x")==1298 and f.get("y")==345]
    def code(text):
        match=re.match(r"^\s*(AA|DD|XX|A|B|C|X)(?=\s|$)",str(text).upper())
        return match[1] if match else None
    possible=located if located else [f for f in combos if code(f.get("text"))]
    if len(possible)!=1:
        return {"source_quality_rating":"unknown","source_quality_rating_raw":[f.get("text") for f in possible],
                "source_quality_rating_origin":"captured_quality_combobox",
                "source_quality_rating_status":"missing" if not possible else "unresolved_multiple_candidates"}
    raw=possible[0].get("text")
    rating=code(raw)
    return {"source_quality_rating":rating or "unknown","source_quality_rating_raw":raw,
            "source_quality_rating_origin":"captured_quality_combobox_exact_position" if located else "unique_captured_rating_text",
            "source_quality_rating_status":"recognized" if rating else "unrecognized"}


def metadata_summary(value):
    candidate = value.get("candidate", {})
    source = value.get("source_record", {})
    if not isinstance(candidate, dict) or not isinstance(source, dict):
        raise ValueError("Malformed candidate/source metadata")
    engine = value.get("engine_version", value.get("engine"))
    if isinstance(engine, dict):
        engine = engine.get("version")
    match = re.search(r"\d+\.\d+\.\d+", str(engine))
    return {"subject_id": value.get("subject_id"), "hemisphere": value.get("hemisphere"),
            "provenance": value.get("provenance", value.get("input_provenance", "unknown")),
            "source_database": candidate.get("source_database", value.get("source_database", "unknown")),
            "source_review_status": source.get("status", value.get("source_status", "not_recorded")),
            "engine_version": match[0] if match else None,
            "engine_sha256": value.get("engine_sha256"),
            "input_policy": value.get("input_policy"), "ui_session": value.get("ui_session"),
            "historical_equivalence": value.get("historical_equivalence", "unverified"),
            "clock_convention_review":bool(value.get("observed_utc_exception")),
            "observed_utc_exception":value.get("observed_utc_exception"),
            "exact_displayname": candidate.get("exact_displayname"),**rating_info(value)}


def analyze_person(subject, results_dir, expected_engine="7.8.5", expected_hash=None):
    sid = subject["subject_id"]
    folder = results_dir / sid
    words = [r["word"] for r in subject["comparison_input"]["records"]]
    source_words=[r["word"] for r in subject["bio_source"]["records"]]
    if not words or any(not isinstance(w, str) or w == "" for w in words):
        raise ValueError("Invalid retained BIO list")
    if not source_words or any(not isinstance(w,str) or w=="" for w in source_words):
        raise ValueError("Invalid retained source BIO variant")
    person = {"subject_id": sid, "hemisphere": subject["hemisphere"],
              "name": subject["subject_list_name"], "bio_baseline": "actual historical comparison_input.records",
              "bio_occurrences": len(words),"source_bio_occurrences":len(source_words),
              "bio_source_word_multiset_differs":Counter(w.lower() for w in words)!=Counter(w.lower() for w in source_words),
              "arms": {}, "errors": [], "pending": [], "input_hashes": {},
              "metadata": {"provenance":"unknown", "source_database":"unknown", "source_review_status":"not_recorded"},
              "included_in_cohort": False}
    mtimes = {}
    current_scores, historical_scores,source_scores = {}, {}, {}
    for arm in ("standard", "inverted"):
        reference = records(subject["astro_source"]["arms"][arm]["keywords"])
        old_score, old_numerator = score(words, reference)
        supplied = subject["comparison_input"][arm + "_global"]
        if abs(float(old_score) - supplied) > 1e-12:
            raise ValueError("Historical manifest arithmetic drift")
        historical_scores[arm] = old_score
        person["arms"][arm] = {"historical_global": float(old_score),
            "historical_global_exact": fraction_json(old_score), "historical_matched_weight_sum": float(old_numerator),
            "historical_record_count": len(reference), "current_global": None,
            "historical_zero_weight_record_count":sum(r["weight"]==0 for r in reference),
            "historical_zero_weight_rows":[{"vector_row_ordinal":i+1,"word":r["word"]} for i,r in enumerate(reference) if r["weight"]==0]}
        path = folder / (arm + "-tree.txt")
        if not path.exists():
            person["pending"].append("missing_" + arm + "_tree")
            continue
        try:
            text, digest, modified = snapshot(path)
            current = records(parse_tree(text))
            value, numerator = score(words, current)
            source_value,source_numerator=score(source_words,current)
            current_scores[arm] = value
            source_scores[arm]=source_value
            person["input_hashes"][path.name] = digest
            mtimes[path.name] = modified
            person["arms"][arm].update(current_global=float(value), current_global_exact=fraction_json(value),
                current_matched_weight_sum=float(numerator), current_record_count=len(current),
                bio_source_current_global=float(source_value),bio_source_current_global_exact=fraction_json(source_value),
                bio_source_current_matched_weight_sum=float(source_numerator),
                bio_source_minus_primary_current_global=float(source_value-value),
                current_zero_weight_record_count=sum(r["weight"]==0 for r in current),
                current_zero_weight_rows=[{"vector_row_ordinal":i+1,"word":r["word"]} for i,r in enumerate(current) if r["weight"]==0],
                current_minus_historical_global=float(value-old_score), vector_difference=vector_difference(reference,current))
        except (ValueError, OSError, UnicodeError) as error:
            person["errors"].append(arm + "_tree: " + str(error))
    meta_path = folder / "input.json"
    if meta_path.exists():
        try:
            text, digest, modified = snapshot(meta_path)
            value = read_json(text)
            if not isinstance(value, dict):
                raise ValueError("Metadata must be an object")
            meta = metadata_summary(value)
            person["metadata"] = meta
            person["input_hashes"][meta_path.name] = digest
            mtimes[meta_path.name] = modified
            if meta["subject_id"] != sid or meta["hemisphere"] != person["hemisphere"]:
                person["errors"].append("metadata_identity_or_hemisphere_mismatch")
            if meta["engine_version"] != expected_engine:
                person["errors"].append("metadata_engine_version_mismatch_or_missing")
            if not isinstance(meta["engine_sha256"],str) or not re.fullmatch(r"[a-fA-F0-9]{64}",meta["engine_sha256"]):
                person["errors"].append("metadata_engine_hash_missing_or_malformed")
            elif expected_hash and meta["engine_sha256"] != expected_hash:
                person["errors"].append("metadata_engine_hash_mismatch")
        except (ValueError, OSError, UnicodeError, AttributeError) as error:
            person["errors"].append("input_metadata: " + str(error))
    else:
        person["pending"].append("missing_input_metadata")
    complete = folder / "complete.json"
    if complete.exists():
        try:
            text, digest, marker_time = snapshot(complete)
            marker = read_json(text)
            person["input_hashes"][complete.name] = digest
            person["generation_completed_utc"] = marker.get("original_generation_completed_utc",marker.get("completed_utc"))
            person["binding_completed_utc"] = marker.get("completed_utc")
            person["retrospectively_rebound_pilot"] = bool(marker.get("original_generation_completed_utc"))
            if marker.get("subject_id") != sid:
                person["errors"].append("completion_marker_identity_mismatch")
            for arm in ("standard", "inverted"):
                if marker.get(arm+"_count") != person["arms"][arm].get("current_record_count"):
                    person["errors"].append("completion_marker_"+arm+"_count_mismatch")
            if any(value > marker_time for value in mtimes.values()):
                person["errors"].append("input_or_tree_newer_than_completion_marker")
            # Honor cryptographic bindings if the writer supplies them. Older
            # markers contain only counts; their weaker binding is explicit.
            bindings = marker.get("file_sha256", marker.get("sha256", marker.get("file_hashes", {})))
            if not isinstance(bindings, dict):
                raise ValueError("Malformed completion hash bindings")
            for name, declared in bindings.items():
                if Path(name).name != name or name in {"complete.json","complete.json.tmp"}:
                    raise ValueError("Unsafe or self-referential completion binding")
                if name not in person["input_hashes"]:
                    _, extra_digest, extra_modified = snapshot(folder/name)
                    person["input_hashes"][name] = extra_digest
                    mtimes[name] = extra_modified
                if person["input_hashes"][name] != declared:
                    person["errors"].append("completion_hash_binding_mismatch:"+name)
                if mtimes[name] > marker_time:
                    person["errors"].append("bound_evidence_newer_than_completion_marker:"+name)
            person["completion_hash_binding"] = "hashes_supplied" if bindings else "counts_and_mtime_only_no_writer_hashes"
            required={"input.json","standard-tree.txt","inverted-tree.txt","capture-validation.json",
                      "birth-fields.txt","standard-positions.txt","inverted-positions.txt","inversion-settings.txt"}
            if not required.issubset(bindings):
                person["pending"].append("completion_marker_needs_full_evidence_hash_binding")
            if not marker.get("input_policy") or marker.get("input_policy") != person["metadata"].get("input_policy"):
                person["pending"].append("completion_input_policy_unbound_or_mismatched")
            person["completion_input_policy"] = marker.get("input_policy")
            if marker.get("engine_sha256") != person["metadata"].get("engine_sha256"):
                person["pending"].append("completion_engine_hash_unbound_or_mismatched")
            capture_path=folder/"capture-validation.json"
            if marker.get("independent_capture_validation")!="passed" or not capture_path.exists():
                person["pending"].append("independent_source_clock_validation_receipt_missing")
            else:
                capture_text,capture_digest,capture_modified=snapshot(capture_path)
                if capture_digest!=person["input_hashes"].get("capture-validation.json") or capture_modified>marker_time:
                    person["errors"].append("capture_validation_changed_after_binding")
                capture=read_json(capture_text)
                if capture.get("subject_id") not in (None,sid):
                    person["errors"].append("capture_validation_subject_id_mismatch")
                if capture.get("passed") is not True:
                    person["errors"].append("independent_source_clock_validation_failed")
                person["capture_validation_status"] = capture.get("status")
                person["capture_validation_passed"] = capture.get("passed")
                if capture.get("status")=="reported_utc_verified_source_convention_unresolved":
                    person["metadata"]["clock_convention_review"]=True
            geometry = marker.get("geometry", {})
            residuals, tolerance = geometry.get("rotation_residual_degrees"), geometry.get("tolerance_degrees")
            if residuals is None:
                person["pending"].append("inversion_geometry_receipt_missing")
            if residuals is not None:
                if len(residuals)!=11 or not isinstance(tolerance,(float,int)) or not math.isfinite(tolerance) or tolerance < 0:
                    raise ValueError("Malformed declared geometry check")
                if any(not isinstance(x,(float,int)) or not math.isfinite(x) or abs(x)>tolerance for x in residuals):
                    person["errors"].append("completion_declared_geometry_outside_tolerance")
                elif max(residuals)-min(residuals)>.002:
                    person["errors"].append("completion_declared_geometry_nonuniform_rotation")
            person["completion_geometry"] = geometry
        except (ValueError, OSError, UnicodeError, AttributeError, TypeError) as error:
            person["errors"].append("completion_marker: "+str(error))
    else:
        person["pending"].append("missing_completion_marker")
    old_delta = historical_scores["inverted"] - historical_scores["standard"]
    person.update(historical_delta=float(old_delta), historical_delta_exact=fraction_json(old_delta), historical_winner=winner(old_delta))
    if len(current_scores)==2 and not person["errors"]:
        delta = current_scores["inverted"] - current_scores["standard"]
        person.update(current_delta=float(delta), current_delta_exact=fraction_json(delta), current_winner=winner(delta),
                      winner_changed=winner(delta)!=winner(old_delta), delta_drift=float(delta-old_delta))
        source_delta=source_scores["inverted"]-source_scores["standard"]
        person.update(bio_source_current_delta=float(source_delta),bio_source_current_delta_exact=fraction_json(source_delta),
                      bio_source_current_winner=winner(source_delta),bio_source_variant_winner_changed=winner(source_delta)!=winner(delta),
                      bio_source_variant_any_score_changed=any(source_scores[arm]!=current_scores[arm] for arm in ("standard","inverted")))
    person["included_in_cohort"] = len(current_scores)==2 and not person["errors"] and not person["pending"]
    person["status"] = "complete_consistent_pair" if person["included_in_cohort"] else "invalid_or_inconsistent" if person["errors"] else "pending"
    return person


def describe(values):
    values = list(values)
    return {"n":len(values), "mean":statistics.fmean(values) if values else None,
            "median":statistics.median(values) if values else None,
            "sd":statistics.stdev(values) if len(values)>1 else None,
            "minimum":min(values) if values else None,"maximum":max(values) if values else None}


def summarize(people):
    result = {"n":len(people)}
    for era in ("historical","current","bio_source_current"):
        wins = Counter(p[era+"_winner"] for p in people)
        n, non_tied = len(people), wins["inverted"]+wins["standard"]
        result[era] = {"inverted_wins":wins["inverted"],"standard_wins":wins["standard"],"ties":wins["tie"],
            "strict_inverted_win_fraction":wins["inverted"]/n if n else None,
            "conditional_inverted_win_fraction_non_tied":wins["inverted"]/non_tied if non_tied else None,
            "split_tie_inverted_win_fraction":(wins["inverted"]+.5*wins["tie"])/n if n else None,
            "inverted_minus_standard":describe(p[era+"_delta"] for p in people),
            "standard_global":describe(p["arms"]["standard"][era+"_global"] for p in people),
            "inverted_global":describe(p["arms"]["inverted"][era+"_global"] for p in people)}
    result["winner_changes"] = sum(p["winner_changed"] for p in people)
    result["bio_source_variant"]={
        "label":"Sensitivity only: retained BIO workbook source, scored against the same CURRENT chart pair; primary comparison_input is unchanged.",
        "persons_with_word_multiset_difference":sum(p["bio_source_word_multiset_differs"] for p in people),
        "persons_with_any_score_change":sum(p["bio_source_variant_any_score_changed"] for p in people),
        "persons_with_winner_change":sum(p["bio_source_variant_winner_changed"] for p in people),
        "changed_person_ids":[p["subject_id"] for p in people if p["bio_source_variant_any_score_changed"]],
        "source_minus_primary_global":{arm:describe(p["arms"][arm]["bio_source_minus_primary_current_global"] for p in people) for arm in ("standard","inverted")}}
    result["delta_drift"] = describe(p["delta_drift"] for p in people)
    result["vector_discrepancies"] = {key:sum(p["arms"][arm]["vector_difference"][key] for p in people for arm in ("standard","inverted"))
        for key in ("added_keyword_row_count","removed_keyword_row_count","changed_weight_row_count","literal_first_match_change_count")}
    result["equal_vector_multisets"] = sum(p["arms"][arm]["vector_difference"]["vector_multiset_equal"] for p in people for arm in ("standard","inverted"))
    result["zero_weight_record_counts"]={era:sum(p["arms"][arm][era+"_zero_weight_record_count"] for p in people for arm in ("standard","inverted")) for era in ("historical","current")}
    return result


def binomial_half(successes, total):
    if not 0<=successes<=total:
        raise ValueError("Invalid binomial counts")
    if not total:
        return None
    return min(1.0, 2*sum(math.comb(total,k) for k in range(min(successes,total-successes)+1))/2**total)


def mcnemar(people):
    table = [[0,0],[0,0]]
    excluded = 0
    for person in people:
        old,new = person["historical_winner"],person["current_winner"]
        if "tie" in (old,new):
            excluded+=1
            continue
        table[old=="inverted"][new=="inverted"]+=1
    toward_inverted,toward_standard = table[0][1],table[1][0]
    discordant = toward_inverted+toward_standard
    return {"table_rows_historical_columns_current_standard_then_inverted":table,
        "excluded_due_to_tie":excluded,"flips_toward_inverted":toward_inverted,"flips_toward_standard":toward_standard,
        "exact_two_sided_p":binomial_half(toward_inverted,discordant) if discordant else 1.0,
        "paired_win_fraction_change_non_tied":(toward_inverted-toward_standard)/(len(people)-excluded) if len(people)>excluded else None}


def fisher_two_sided(table):
    (a,b),(c,d)=table
    if any(x<0 or not isinstance(x,int) for x in (a,b,c,d)):
        raise ValueError("Invalid contingency table")
    population,row,col=a+b+c+d,a+b,a+c
    if not population or not row or row==population:
        return 1.0
    denominator=math.comb(population,col)
    observed=math.comb(row,a)*math.comb(population-row,col-a)
    probability=sum(math.comb(row,x)*math.comb(population-row,col-x)
        for x in range(max(0,col-(population-row)),min(row,col)+1)
        if math.comb(row,x)*math.comb(population-row,col-x)<=observed)
    return probability/denominator


def hemisphere_binary(people,era="current"):
    groups={g:Counter(p[era+"_winner"] for p in people if p["hemisphere"]==g) for g in ("North","South")}
    n={g:groups[g]["inverted"]+groups[g]["standard"] for g in groups}
    if not all(n.values()):
        return {"status":"unavailable_no_non_tied_subjects_in_one_hemisphere"}
    pn,ps=groups["North"]["inverted"]/n["North"],groups["South"]["inverted"]/n["South"]
    pool=(groups["North"]["inverted"]+groups["South"]["inverted"])/(n["North"]+n["South"])
    variance=pool*(1-pool)*(1/n["North"]+1/n["South"])
    z=(ps-pn)/math.sqrt(variance) if variance else None
    ties=sum(groups[g]["tie"] for g in groups)
    expected=[n[g]*probability for g in groups for probability in (pool,1-pool)]
    return {"south_minus_north_inversion_win_fraction":ps-pn,
        "north_non_tied_n":n["North"],"south_non_tied_n":n["South"],"excluded_ties":ties,
        "tie_policy":"Conditional analysis excludes ties; ties remain reported separately. Original-protocol analog is directly comparable only when no ties occur.",
        "pooled_two_proportion_z":z,"z_two_sided_p":math.erfc(abs(z)/math.sqrt(2)) if z is not None else None,
        "normal_approximation_expected_cells":expected,"all_expected_cells_at_least_five":min(expected)>=5,
        "z_directional_south_greater_p":.5*math.erfc(z/math.sqrt(2)) if z is not None else None,
        "fisher_exact_two_sided_p":fisher_two_sided([[groups["South"]["inverted"],groups["South"]["standard"]],
                                                   [groups["North"]["inverted"],groups["North"]["standard"]]])}


def paired_mean_randomization(values, draws, seed):
    nonzero=[exact(x) for x in values if exact(x)!=0]
    observed=abs(sum(nonzero,Fraction()))
    if len(nonzero)<=15:
        extreme=0
        for signs in itertools.product((-1,1),repeat=len(nonzero)):
            extreme+=abs(sum((sign*x for sign,x in zip(signs,nonzero)),Fraction()))>=observed
        return {"method":"exact paired sign flips, absolute-statistic two-sided tail","nonzero_pairs":len(nonzero),
                "permutations":2**len(nonzero),"p":extreme/2**len(nonzero)}
    import numpy as np
    rng=np.random.default_rng(seed)
    array=np.asarray([float(x) for x in nonzero])
    threshold=float(observed)
    epsilon=100*np.finfo(float).eps*max(1.,float(abs(array).sum()))
    extreme=0
    for start in range(0,draws,256):
        signs=rng.integers(0,2,size=(min(256,draws-start),len(array)))*2-1
        extreme+=int(np.count_nonzero(np.abs((signs*array).sum(axis=1))>=threshold-epsilon))
    return {"method":"Monte Carlo paired sign flips, absolute-statistic two-sided tail, plus-one p",
        "nonzero_pairs":len(nonzero),"permutations":draws,"seed":seed,"extreme":extreme,"p":(extreme+1)/(draws+1),"comparison_epsilon":epsilon}


def continuous_effect(values,draws,bootstrap,seed):
    import numpy as np
    values=list(values)
    if not values:
        return {"status":"unavailable_no_pairs"}
    data=np.asarray([float(x) for x in values])
    mean=float(data.mean())
    positive=sum(x>0 for x in values);negative=sum(x<0 for x in values);zeros=len(values)-positive-negative
    result={"n":len(values),"mean_paired_difference":mean,"median_paired_difference":float(np.median(data)),
        "positive":positive,"negative":negative,"zero":zeros,
        "exact_sign_test_two_sided_p":binomial_half(positive,positive+negative),
        "paired_mean_randomization":paired_mean_randomization(values,draws,seed),
        "bootstrap_mean_95_percentile_interval":None,"paired_standardized_mean_difference_dz":None}
    if len(values)>1:
        rng=np.random.default_rng(seed+1)
        means=[]
        for start in range(0,bootstrap,256):
            index=rng.integers(0,len(data),size=(min(256,bootstrap-start),len(data)))
            means.extend(data[index].mean(axis=1).tolist())
        result["bootstrap_mean_95_percentile_interval"]=np.quantile(means,[.025,.975]).tolist()
        sd=float(data.std(ddof=1))
        result["paired_standardized_mean_difference_dz"]=mean/sd if sd else None
    result["bootstrap_resamples"]=bootstrap
    result["assumption"]= "Paired sign-flip randomization assumes exchangeability of condition labels within subjects (symmetric paired null). Bootstrap resamples people; intervals describe cohort sampling variability, not calibrated trait probabilities."
    return result


def hemisphere_continuous(people,era,draws,bootstrap,seed):
    """Compare subject-level paired differences across independent strata."""
    import numpy as np
    groups={group:[Fraction(p[era+"_delta_exact"]["numerator"],p[era+"_delta_exact"]["denominator"])
                   for p in people if p["hemisphere"]==group] for group in ("North","South")}
    north,south=groups["North"],groups["South"]
    if not north or not south:
        return {"status":"unavailable_missing_hemisphere"}
    observed=sum(south,Fraction())/len(south)-sum(north,Fraction())/len(north)
    pool=north+south
    allocations=math.comb(len(pool),len(south))
    if allocations<=32768:
        extreme=0
        total=sum(pool,Fraction())
        for indices in itertools.combinations(range(len(pool)),len(south)):
            selected=sum((pool[i] for i in indices),Fraction())
            contrast=selected/len(south)-(total-selected)/len(north)
            extreme+=abs(contrast)>=abs(observed)
        randomization={"method":"exact allocation of paired subject differences across hemisphere groups",
                       "allocations":allocations,"p":extreme/allocations}
    else:
        rng=np.random.default_rng(seed)
        array=np.asarray([float(v) for v in pool]);total=float(array.sum());threshold=abs(float(observed))
        epsilon=100*np.finfo(float).eps*max(1.,float(abs(array).sum()))
        extreme=0
        for _ in range(draws):
            selected=float(array[rng.permutation(len(array))[:len(south)]].sum())
            extreme+=int(abs(selected/len(south)-(total-selected)/len(north))>=threshold-epsilon)
        randomization={"method":"Monte Carlo hemisphere allocation of paired subject differences; absolute-tail plus-one p",
                       "draws":draws,"seed":seed,"extreme":extreme,"p":(extreme+1)/(draws+1),"comparison_epsilon":epsilon}
    interval=None
    if len(north)>1 and len(south)>1:
        rng=np.random.default_rng(seed+1);contrasts=[]
        north_array=np.asarray([float(v) for v in north]);south_array=np.asarray([float(v) for v in south])
        for start in range(0,bootstrap,256):
            count=min(256,bootstrap-start)
            n=north_array[rng.integers(0,len(north),size=(count,len(north)))].mean(axis=1)
            s=south_array[rng.integers(0,len(south),size=(count,len(south)))].mean(axis=1)
            contrasts.extend((s-n).tolist())
        interval=np.quantile(contrasts,[.025,.975]).tolist()
    return {"south_minus_north_mean_inversion_advantage":float(observed),
            "bootstrap_95_percentile_interval":interval,"bootstrap_resamples":bootstrap,
            "north_n":len(north),"south_n":len(south),"randomization":randomization,
            "assumption":"Exchangeability of subject-level paired differences across hemispheres under the group null. This does not remove demographic/cohort confounding and is not the earlier within-hemisphere BIO reassignment null."}


def effect_tests(people,draws=9999,bootstrap=5000,seed=20261117):
    result={"interpretation":"Exploratory current-engine analysis of a known development cohort; no multiplicity adjustment or new human accuracy claim.",
        "current_hemisphere_binary":hemisphere_binary(people),"historical_same_people_binary":hemisphere_binary(people,"historical"),
        "current_hemisphere_continuous":hemisphere_continuous(people,"current",draws,bootstrap,seed+3000),
        "historical_same_people_continuous":hemisphere_continuous(people,"historical",draws,bootstrap,seed+3100),
        "historical_to_current_paired_winner_changes":mcnemar(people),"by_hemisphere":{},"by_input_provenance":{},
        "stronger_BIO_person_reassignment_null":"Not recomputed by this module; paired sign flips test a different null."}
    groups={"all":people}
    groups.update({g:[p for p in people if p["hemisphere"]==g] for g in ("North","South")})
    for index,(group,members) in enumerate(groups.items()):
        deltas=[Fraction(p["current_delta_exact"]["numerator"],p["current_delta_exact"]["denominator"]) for p in members]
        drift=[Fraction(p["current_delta_exact"]["numerator"],p["current_delta_exact"]["denominator"])-Fraction(p["historical_delta_exact"]["numerator"],p["historical_delta_exact"]["denominator"]) for p in members]
        result["by_hemisphere"][group]={"current_inverted_minus_standard":continuous_effect(deltas,draws,bootstrap,seed+100*index),
            "current_minus_historical_inversion_advantage":continuous_effect(drift,draws,bootstrap,seed+100*index+10),
            "paired_winner_changes":mcnemar(members)}
    provenance=defaultdict(list)
    for person in people:
        provenance[str(person["metadata"].get("provenance","unknown"))].append(person)
    for index,(key,members) in enumerate(sorted(provenance.items())):
        deltas=[Fraction(p["current_delta_exact"]["numerator"],p["current_delta_exact"]["denominator"]) for p in members]
        result["by_input_provenance"][key]={"current_inverted_minus_standard":continuous_effect(deltas,draws,bootstrap,seed+1000+index),"paired_winner_changes":mcnemar(members)}
    return result


def sensitivity_reports(people,tests_status,draws,bootstrap,seed):
    """Keep alternative inputs and raw source labels separate from the primary endpoint."""
    quality=[p for p in people if p["metadata"].get("source_quality_rating") in {"A","AA"}]
    clock_clear=[p for p in people if not p["metadata"].get("clock_convention_review",False)]
    result={"bio_source_variant":{
        "label":"Retained BIO workbook source sensitivity; primary comparison_input scores are unchanged.",
        "descriptive":summarize(people)["bio_source_variant"],
        "by_hemisphere":{g:summarize([p for p in people if p["hemisphere"]==g])["bio_source_current"] for g in ("North","South")}},
        "raw_A_or_AA_subset":{
        "label":"Sensitivity restricted to current raw A/AA source labels; these labels do not establish historical input truth or source equivalence.",
        "selection":"Recognized A or AA only; unknown, unresolved and other ratings are excluded without imputation.",
        "n":len(quality),"subject_ids":[p["subject_id"] for p in quality],
        "descriptive":summarize(quality),
        "by_hemisphere":{g:summarize([p for p in quality if p["hemisphere"]==g]) for g in ("North","South")}},
        "exclude_clock_convention_review":{
        "label":"Sensitivity excluding observed-UTC exceptions with unresolved supplied-source clock conventions; primary provided-source reproduction remains unchanged.",
        "n":len(clock_clear),"excluded_subject_ids":[p["subject_id"] for p in people if p["metadata"].get("clock_convention_review",False)],
        "descriptive":summarize(clock_clear),
        "by_hemisphere":{g:summarize([p for p in clock_clear if p["hemisphere"]==g]) for g in ("North","South")}}}
    for entry in result.values():
        entry["tests"]={"status":"not_run_primary_gate_closed","primary_gate_status":tests_status}
    if tests_status=="computed_for_full_current_cohort":
        result["bio_source_variant"]["tests"]={"status":"computed_separate_sensitivity", "hemisphere_binary":hemisphere_binary(people,"bio_source_current"),
            "hemisphere_continuous":hemisphere_continuous(people,"bio_source_current",draws,bootstrap,seed+4000)}
        result["raw_A_or_AA_subset"]["tests"]={"status":"computed_separate_sensitivity", "hemisphere_binary":hemisphere_binary(quality),
            "hemisphere_continuous":hemisphere_continuous(quality,"current",draws,bootstrap,seed+4100)}
        result["exclude_clock_convention_review"]["tests"]={"status":"computed_separate_sensitivity", "hemisphere_binary":hemisphere_binary(clock_clear),
            "hemisphere_continuous":hemisphere_continuous(clock_clear,"current",draws,bootstrap,seed+4200)}
    return result


def analyze(manifest,results_dir,expected_engine="7.8.5",expected_hash=None,descriptive_only=False,draws=9999,bootstrap=5000,seed=20261117):
    if draws<1 or bootstrap<1:
        raise ValueError("Resampling counts must be positive")
    ids=[p["subject_id"] for p in manifest]
    if not ids or len(set(ids))!=len(ids):
        raise ValueError("Manifest subject IDs must be unique")
    people=[analyze_person(p,Path(results_dir),expected_engine,expected_hash) for p in manifest]
    included=[p for p in people if p["included_in_cohort"]]
    grouping={}
    for label,key in [("hemisphere",lambda p:p["hemisphere"]),
        ("input_provenance",lambda p:str(p["metadata"].get("provenance","unknown"))),
        ("source_database",lambda p:str(p["metadata"].get("source_database","unknown"))),
        ("source_review_status",lambda p:str(p["metadata"].get("source_review_status","not_recorded"))),
        ("source_quality_rating",lambda p:str(p["metadata"].get("source_quality_rating","unknown"))),
        ("hemisphere_by_rating",lambda p:p["hemisphere"]+" / "+str(p["metadata"].get("source_quality_rating","unknown"))),
        ("clock_convention_review",lambda p:str(p["metadata"].get("clock_convention_review",False))),
        ("hemisphere_by_provenance",lambda p:p["hemisphere"]+" / "+str(p["metadata"].get("provenance","unknown")))]:
        groups=defaultdict(list)
        for person in included:
            groups[key(person)].append(person)
        grouping[label]={name:summarize(members) for name,members in sorted(groups.items())}
    hashes=Counter(p["metadata"].get("engine_sha256") for p in included)
    policies=Counter(p["metadata"].get("input_policy") for p in included)
    residuals=[v for p in included for v in p.get("completion_geometry",{}).get("rotation_residual_degrees",[])]
    complete=len(included)==len(manifest)
    if not complete:
        tests={"status":"not_run_incomplete_cohort","reason":"No significance tests or confidence intervals until all expected pairs are complete and internally consistent."}
    elif len(hashes)!=1:
        tests={"status":"not_run_mixed_engine_hashes","reason":"Different operator-declared engine hashes cannot be silently pooled."}
    elif len(policies)!=1:
        tests={"status":"not_run_mixed_input_policies","reason":"Different input selection policies cannot be silently pooled."}
    elif descriptive_only:
        tests={"status":"not_run_requested_descriptive_only"}
    else:
        try:
            tests={"status":"computed_for_full_current_cohort",**effect_tests(included,draws,bootstrap,seed)}
        except ImportError as error:
            tests={"status":"not_run_missing_analysis_dependency","reason":str(error)}
    return {"schema":1,"generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "analysis_kind":"CURRENT engine regeneration versus retained historical vectors on a known development cohort",
        "expected_subjects":len(manifest),"included_complete_pairs":len(included),"complete_cohort":complete,
        "historical_full_manifest_zero_weight_records":sum(p["arms"][arm]["historical_zero_weight_record_count"] for p in people for arm in ("standard","inverted")),
        "missing_or_invalid_subjects":[{"subject_id":p["subject_id"],"status":p["status"],"pending":p["pending"],"errors":p["errors"]} for p in people if not p["included_in_cohort"]],
        "operator_declared_engine_hash_counts":dict(hashes),"operator_declared_input_policy_counts":dict(policies),"overall_on_completed_subset":summarize(included),
        "evidence_quality":{"capture_validation_passed_count":sum(p.get("capture_validation_passed") is True for p in included),
             "retrospectively_rebound_pilot_count":sum(p.get("retrospectively_rebound_pilot",False) for p in included),
             "completion_binding_counts":dict(Counter(p.get("completion_hash_binding") for p in included)),
             "operator_historical_equivalence_counts":dict(Counter(p["metadata"].get("historical_equivalence","unverified") for p in included)),
             "maximum_absolute_declared_rotation_residual_degrees":max(map(abs,residuals)) if residuals else None,
             "minimum_declared_rotation_residual_degrees":min(residuals) if residuals else None,
             "maximum_declared_rotation_residual_degrees":max(residuals) if residuals else None,
             "geometry_scope":"Completion receipt checks11 planetary/node rotations. Ascendant/Midheaven inversion and all factor rules are not independently recomputed by this module."},
        "groups":grouping,"people":people,"tests":tests,
        "sensitivities":sensitivity_reports(included,tests["status"],draws,bootstrap,seed),
        "claims":{"chart_generation_by_this_module":False,"new_human_validation":False,"forecast_accuracy_test":False,
                  "historical_birth_input_equivalence_certified":False,"historical_arithmetic_already_audited_separately":True},
        "rules":{"BIO_baseline":"retained actual comparison_input.records; separate BIO workbook variant is not silently substituted",
                 "matching":"lower() only; preserve whitespace; first duplicate ASTRO match; every BIO occurrence; divide by ASTRO record count",
                 "displayed_zeros":"Preserve displayed zero-weight rows and include them in the ASTRO denominator. No claim is made about hidden/unrounded precision.",
                 "ties":"Winner classification uses exact rational scores, without floating-point epsilon. Report ties separately; conditional sign/binomial/Fisher tests exclude ties explicitly.",
                 "missingness":"No historical score substitutes for missing current output. Historical summaries use the same completed subset.",
                 "provenance":"Grouped by operator input metadata. Supplied/reconstructed source labels do not establish historical input identity.",
                 "completion":"Both exact tree filenames, valid input.json identity/build, and complete.json identity/counts/chronology must agree. Writer hash bindings are verified when present.",
                 "excluded":"All INVALID-* filenames and non-manifest subject folders are ignored. No tree file outside the exact per-subject standard/inverted paths is used."},
        "resampling":{"paired_mean_randomization_draws":draws,"bootstrap_resamples":bootstrap,"seed":seed}}


def jsonable(value):
    if isinstance(value,Decimal):
        return str(value)
    if isinstance(value,Fraction):
        return fraction_json(value)
    if isinstance(value,dict):
        return {k:jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [jsonable(v) for v in value]
    return value


def write_report(report,out_prefix):
    prefix=Path(out_prefix)
    prefix.parent.mkdir(parents=True,exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(jsonable(report),ensure_ascii=False,indent=2,allow_nan=False))
    columns=["subject_id","hemisphere","name","status","included_in_cohort","provenance","source_database","source_review_status",
        "source_quality_rating","source_quality_rating_raw","source_quality_rating_origin","source_quality_rating_status","clock_convention_review","capture_validation_status",
        "input_policy","engine_version","engine_sha256","capture_validation_passed","completion_hash_binding",
        "historical_standard","historical_inverted","current_standard","current_inverted","historical_winner","current_winner","winner_changed",
        "historical_delta","current_delta","standard_current_records","inverted_current_records","standard_changed_weights","inverted_changed_weights",
        "standard_historical_zero_rows","standard_current_zero_rows","inverted_historical_zero_rows","inverted_current_zero_rows",
        "source_bio_occurrences","bio_source_current_standard","bio_source_current_inverted","bio_source_current_delta",
        "bio_source_current_winner","bio_source_variant_any_score_changed","bio_source_variant_winner_changed",
        "standard_added_keywords","standard_removed_keywords","inverted_added_keywords","inverted_removed_keywords"]
    with prefix.with_suffix(".csv").open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader()
        for person in report["people"]:
            row={k:person.get(k) for k in columns[:5]}
            row.update({k:person["metadata"].get(k) for k in ("provenance","source_database","source_review_status","input_policy","engine_version","engine_sha256",
                "source_quality_rating","source_quality_rating_raw","source_quality_rating_origin","source_quality_rating_status","clock_convention_review")})
            row.update({k:person.get(k) for k in ("capture_validation_passed","completion_hash_binding","capture_validation_status")})
            for era in ("historical","current","bio_source_current"):
                for arm in ("standard","inverted"):
                    row[era+"_"+arm]=person["arms"][arm].get(era+"_global")
            for key in ("historical_winner","current_winner","winner_changed","historical_delta","current_delta",
                "source_bio_occurrences","bio_source_current_delta","bio_source_current_winner","bio_source_variant_any_score_changed","bio_source_variant_winner_changed"):
                row[key]=person.get(key)
            for arm in ("standard","inverted"):
                data=person["arms"][arm];diff=data.get("vector_difference",{})
                row[arm+"_current_records"]=data.get("current_record_count")
                row[arm+"_historical_zero_rows"]=data.get("historical_zero_weight_record_count")
                row[arm+"_current_zero_rows"]=data.get("current_zero_weight_record_count")
                row[arm+"_changed_weights"]=diff.get("changed_weight_row_count")
                row[arm+"_added_keywords"]=diff.get("added_keyword_row_count")
                row[arm+"_removed_keywords"]=diff.get("removed_keyword_row_count")
            writer.writerow(row)
    lines=["# Current Mastro cohort analysis", "",f"Generated: {report['generated_utc']}","",
        f"Complete, internally consistent pairs: **{report['included_complete_pairs']} / {report['expected_subjects']}**.",
        "The historical spreadsheet arithmetic is a separate verified result. This report compares CURRENT engine output with retained historical vectors on the same known development cohort. It establishes no new human or forecast accuracy.","",
        "| Hemisphere | Complete pairs | Current inversion wins | Standard wins | Ties | Historical inversion wins on same subset |",
        "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name,group in report["groups"]["hemisphere"].items():
        lines.append(f"| {name} | {group['n']} | {group['current']['inverted_wins']} | {group['current']['standard_wins']} | {group['current']['ties']} | {group['historical']['inverted_wins']} |")
    lines.extend(["", "| Input provenance | Complete pairs | Current inversion wins | Standard wins | Ties |",
                  "| --- | ---: | ---: | ---: | ---: |"])
    for name,group in report["groups"]["input_provenance"].items():
        lines.append(f"| {name} | {group['n']} | {group['current']['inverted_wins']} | {group['current']['standard_wins']} | {group['current']['ties']} |")
    lines.extend(["", "| Raw source rating | Complete pairs | Current inversion wins | Standard wins | Ties |",
                  "| --- | ---: | ---: | ---: | ---: |"])
    for name,group in report["groups"]["source_quality_rating"].items():
        lines.append(f"| {name} | {group['n']} | {group['current']['inverted_wins']} | {group['current']['standard_wins']} | {group['current']['ties']} |")
    variant=report["sensitivities"]["bio_source_variant"]["descriptive"]
    quality=report["sensitivities"]["raw_A_or_AA_subset"]
    lines.extend(["",f"Separate retained-BIO-source sensitivity: {variant['persons_with_any_score_change']} people have a current score change and {variant['persons_with_winner_change']} have a winner change. Primary comparison-input scores remain unchanged.",
        f"The raw A/AA subset contains {quality['n']} completed people. Raw quality labels come from captured supplied-record fields or the recovered published source; they do not certify historical truth. Rating-by-hemisphere details and both sensitivity reports are in the JSON.",""])
    d=report["overall_on_completed_subset"]["vector_discrepancies"]
    lines.extend(["", f"Across included pairs: {d['added_keyword_row_count']} added keyword rows, {d['removed_keyword_row_count']} removed rows, and {d['changed_weight_row_count']} changed weights. Duplicate records are retained in counts and the original scoring denominator.","",
        f"Displayed zero-weight rows are retained. The full historical manifest contains {report['historical_full_manifest_zero_weight_records']}; on the completed subset the historical/current counts are {report['overall_on_completed_subset']['zero_weight_record_counts']['historical']} / {report['overall_on_completed_subset']['zero_weight_record_counts']['current']}. These rows remain in each chart's denominator; hidden precision is not inferred.","",
        "Statistics status: **"+report["tests"]["status"]+"**."])
    if report["tests"]["status"]=="computed_for_full_current_cohort":
        binary=report["tests"]["current_hemisphere_binary"]
        lines.append("All tests are diagnostic/exploratory on an already known cohort. They are unadjusted for multiple comparisons. Paired sign flips and the earlier within-hemisphere BIO/person reassignment test address different null hypotheses; the latter is not recomputed here.")
        lines.append("Binary hemisphere contrast: "+json.dumps(binary,ensure_ascii=False))
    else:
        lines.append(report["tests"].get("reason","Inferential calculations were not requested."))
    lines.extend(["", "Birth-input provenance remains operator-declared. Current source reconstruction, historical source equivalence and the numerical equality of output vectors are separate questions. Missing current scores are never filled with historical scores.","",
                  "## Missing or excluded pairs",""])
    for person in report["missing_or_invalid_subjects"]:
        lines.append("- "+person["subject_id"]+": "+", ".join(person["pending"]+person["errors"]))
    if not report["missing_or_invalid_subjects"]:
        lines.append("None.")
    lines.extend(["", "Complete person-level scores, exact-score fractions, difference details, source hashes, metadata groups and test assumptions are retained in the private JSON/CSV reports.",""])
    prefix.with_suffix(".md").write_text("\n".join(lines))


def validate_study_manifest(manifest):
    """The study CLI must never treat a shortened input file as a full cohort.

    Internal analyze() intentionally accepts generic cohorts for invented-data
    verification. This boundary enforces the actual study's intended identities.
    """
    expected={f"N{i:03d}":"North" for i in range(1,74)}|{f"S{i:03d}":"South" for i in range(1,69)}
    if not isinstance(manifest,list) or len(manifest)!=141 or any(not isinstance(p,dict) for p in manifest):
        raise ValueError("Study manifest requires exactly 141 intended records: N001..N073 and S001..S068")
    identities=[p.get("subject_id") for p in manifest]
    if any(not isinstance(sid,str) for sid in identities) or len(set(identities))!=141:
        raise ValueError("Study manifest subject IDs must be unique intended study identities")
    if {p["subject_id"]:p.get("hemisphere") for p in manifest}!=expected:
        raise ValueError("Study manifest requires N001..N073 in North and S001..S068 in South")


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,default=DEFAULT_MANIFEST)
    parser.add_argument("--out-prefix",type=Path,required=True)
    parser.add_argument("--expected-engine",default="7.8.5")
    parser.add_argument("--expected-engine-sha256")
    parser.add_argument("--descriptive-only",action="store_true")
    parser.add_argument("--randomizations",type=int,default=9999)
    parser.add_argument("--bootstrap",type=int,default=5000)
    parser.add_argument("--seed",type=int,default=20261117)
    args=parser.parse_args(argv)
    raw=args.manifest.read_bytes()
    manifest=read_json(raw.decode())
    try:
        validate_study_manifest(manifest)
    except ValueError as error:
        parser.error(str(error))
    report=analyze(manifest,args.results,args.expected_engine,args.expected_engine_sha256,
                   args.descriptive_only,args.randomizations,args.bootstrap,args.seed)
    report["manifest_sha256"]=hashlib.sha256(raw).hexdigest()
    report["results_directory"]=str(args.results.resolve())
    report["analysis_module_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    write_report(report,args.out_prefix)
    print(json.dumps({k:report[k] for k in ("expected_subjects","included_complete_pairs","complete_cohort")},indent=2))
    print("Statistics:",report["tests"]["status"])


if __name__=="__main__":
    main()
