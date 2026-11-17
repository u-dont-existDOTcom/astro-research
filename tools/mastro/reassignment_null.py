#!/usr/bin/env python3
"""Optional private within-hemisphere BIO reassignment diagnostic, separate from primary analysis."""
import argparse
import datetime as dt
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

import numpy as np

from cohort_analysis import DEFAULT_MANIFEST, analyze, fraction_json, records, score, snapshot
from mastro_tree import parse_tree

PROTOCOL={
    "version":"current-within-hemisphere-bio-reassignment-20261117-v1",
    "frozen_before_real_null_results":True,
    "cohort":"All 141 validated current pairs, exactly 73 North and 68 South; primary comparison_input BIOs only.",
    "assignment":"Independently in each hemisphere, a uniform permutation without replacement assigns one whole BIO occurrence list to each intact standard/inverted chart pair. Self assignments are allowed.",
    "binary_statistic":"South minus North inversion-win fraction; exact rational ties receive half credit; upper tail >= observed.",
    "continuous_statistic":"South minus North mean(inverted minus standard weighted score); upper tail >= observed.",
    "draws":1000000,"seed":20261117,"p_value":"(upper_tail_count + 1) / (draws + 1)",
    "scope":"New conditional diagnostic using prior conventions, not an exact replay of a prior seed, not the primary endpoint and not new blinded validation.",
    "assumption":"Within each hemisphere, BIO identities are exchangeable over these chart pairs under the reassignment null. This does not control demographic or source-quality confounding."}


def prepare(matrix):
    """Rows are BIO identities, columns intact chart pairs; retain exact deltas."""
    size=len(matrix)
    if size<1 or any(len(row)!=size for row in matrix):
        raise ValueError("A nonempty square paired-delta matrix is required")
    exact=[[Fraction(value) for value in row] for row in matrix]
    floating=np.asarray([[float(value) for value in row] for row in exact],dtype=float)
    if not np.isfinite(floating).all():
        raise ValueError("Nonfinite score matrix")
    win2=np.asarray([[2 if value>0 else 1 if value==0 else 0 for value in row] for row in exact],dtype=np.int64)
    return {"exact":exact,"floating":floating,"win2":win2,"n":size}


def exact_continuous(north,south,pn,ps):
    return (sum((south["exact"][int(i)][j] for j,i in enumerate(ps)),Fraction())/south["n"]
           -sum((north["exact"][int(i)][j] for j,i in enumerate(pn)),Fraction())/north["n"])


def observed_statistics(north,south):
    nn,ns=north["n"],south["n"]
    identity_n,identity_s=list(range(nn)),list(range(ns))
    numerator=int(np.trace(south["win2"]))*nn-int(np.trace(north["win2"]))*ns
    binary=Fraction(numerator,2*ns*nn)
    return {"binary_numerator":numerator,"binary":binary,
            "continuous":exact_continuous(north,south,identity_n,identity_s)}


def precision(extreme,draws):
    """MC uncertainty concerns the sampled tail probability, not cohort sampling."""
    raw=extreme/draws
    z=1.959963984540054
    den=1+z*z/draws
    center=(raw+z*z/(2*draws))/den
    radius=z*math.sqrt(raw*(1-raw)/draws+z*z/(4*draws*draws))/den
    return {"upper_tail_count":extreme,"draws":draws,"plus_one_p":(extreme+1)/(draws+1),
        "raw_mc_tail_fraction":raw,"mc_standard_error":math.sqrt(raw*(1-raw)/draws),
        "mc_tail_probability_95_wilson_interval":[max(0.,center-radius),min(1.,center+radius)],
        "p_resolution":1/(draws+1)}


def simulate(north,south,draws,seed,batch_size=2048):
    if draws<1 or batch_size<1:
        raise ValueError("Positive simulation counts required")
    observed=observed_statistics(north,south)
    rng=np.random.default_rng(seed)
    nn,ns=north["n"],south["n"]
    cn,cs=np.arange(nn),np.arange(ns)
    # Roundoff only decides whether to invoke an exact rational comparison.
    # No epsilon changes a tail decision: all close cases are recomputed exactly.
    epsilon=512*np.finfo(float).eps*(1+np.abs(north["floating"]).max()+np.abs(south["floating"]).max()+abs(float(observed["continuous"])))
    binary_extreme=continuous_extreme=exact_fallbacks=0
    start=time.perf_counter()
    for offset in range(0,draws,batch_size):
        count=min(batch_size,draws-offset)
        pn=rng.permuted(np.broadcast_to(cn,(count,nn)),axis=1)
        ps=rng.permuted(np.broadcast_to(cs,(count,ns)),axis=1)
        bn=north["win2"][pn,cn].sum(axis=1)
        bs=south["win2"][ps,cs].sum(axis=1)
        binary_extreme+=int(np.count_nonzero(bs*nn-bn*ns>=observed["binary_numerator"]))
        values=south["floating"][ps,cs].mean(axis=1)-north["floating"][pn,cn].mean(axis=1)
        threshold=float(observed["continuous"])
        continuous_extreme+=int(np.count_nonzero(values>threshold+epsilon))
        near=np.flatnonzero(np.abs(values-threshold)<=epsilon)
        exact_fallbacks+=len(near)
        for row in near:
            continuous_extreme+=exact_continuous(north,south,pn[row],ps[row])>=observed["continuous"]
    return {"observed":{"binary":float(observed["binary"]),"binary_exact":fraction_json(observed["binary"]),
            "continuous":float(observed["continuous"]),"continuous_exact":fraction_json(observed["continuous"])},
        "binary":precision(int(binary_extreme),draws),"continuous":precision(int(continuous_extreme),draws),
        "draws":draws,"seed":seed,"batch_size":batch_size,"numpy_version":np.__version__,
        "random_generator":type(rng.bit_generator).__name__,
        "continuous_exact_fallback_count":exact_fallbacks,"floating_boundary_detection_bound":float(epsilon),
        "tie_decisions":"Exact rational deltas; binary statistic uses integer doubled credits.",
        "continuous_boundary_policy":"Floating reductions away from a conservative roundoff boundary; every boundary case uses the original exact rational matrix, with >= including equality.",
        "elapsed_seconds":time.perf_counter()-start}


def enumerate_tiny(north,south):
    """Engineering reference only; exhaustive cross-product of tiny assignments."""
    if math.factorial(north["n"])*math.factorial(south["n"])>100000:
        raise ValueError("Enumeration is limited to tiny invented fixtures")
    observed=observed_statistics(north,south)
    binary=continuous=total=0
    for pn in itertools.permutations(range(north["n"])):
        for ps in itertools.permutations(range(south["n"])):
            bn=sum(int(north["win2"][i,j]) for j,i in enumerate(pn))
            bs=sum(int(south["win2"][i,j]) for j,i in enumerate(ps))
            binary+=bs*north["n"]-bn*south["n"]>=observed["binary_numerator"]
            continuous+=exact_continuous(north,south,pn,ps)>=observed["continuous"]
            total+=1
    return {"assignments":total,"binary_upper_tail":binary,"continuous_upper_tail":continuous,
            "binary_exact_p":binary/total,"continuous_exact_p":continuous/total}


def validate_full(manifest,results,expected_hash=None):
    expected={f"N{i:03d}":"North" for i in range(1,74)}|{f"S{i:03d}":"South" for i in range(1,69)}
    if len(manifest)!=141 or {p["subject_id"]:p["hemisphere"] for p in manifest}!=expected:
        raise ValueError("Reassignment requires the complete intended 73 North / 68 South manifest")
    report=analyze(manifest,results,expected_hash=expected_hash,descriptive_only=True)
    if not report["complete_cohort"] or report["included_complete_pairs"]!=141:
        raise ValueError(f"Full-cohort gate closed: {report['included_complete_pairs']} / 141 validated pairs")
    if len(report["operator_declared_engine_hash_counts"])!=1 or len(report["operator_declared_input_policy_counts"])!=1:
        raise ValueError("One consistent engine hash and input policy are required")
    return report


def build_matrices(manifest,results,validated_report):
    matrices={};sources={p["subject_id"]:p for p in validated_report["people"]}
    for hemisphere in ("North","South"):
        members=[p for p in manifest if p["hemisphere"]==hemisphere]
        bios=[[r["word"] for r in p["comparison_input"]["records"]] for p in members]
        pairs=[]
        for person in members:
            pair={}
            for arm in ("standard","inverted"):
                path=Path(results)/person["subject_id"]/(arm+"-tree.txt")
                content,digest,_=snapshot(path)
                if digest!=sources[person["subject_id"]]["input_hashes"][path.name]:
                    raise ValueError("A validated chart changed during reassignment preparation")
                pair[arm]=records(parse_tree(content))
            pairs.append(pair)
        matrix=[[score(bio,pair["inverted"])[0]-score(bio,pair["standard"])[0] for pair in pairs] for bio in bios]
        matrices[hemisphere]=prepare(matrix)
        # Diagonal must reproduce the guarded primary per-person score exactly.
        for index,person in enumerate(members):
            exact=sources[person["subject_id"]]["current_delta_exact"]
            if matrix[index][index]!=Fraction(exact["numerator"],exact["denominator"]):
                raise ValueError("Primary diagonal reconciliation failed")
    return matrices


def verify_evidence_unchanged(results,validated_report):
    """Fail closed if any bound input changed during matrix preparation."""
    for person in validated_report["people"]:
        for name,expected in person["input_hashes"].items():
            _,actual,_=snapshot(Path(results)/person["subject_id"]/name)
            if actual!=expected:
                raise ValueError("Validated evidence changed before inference: "+person["subject_id"]+"/"+name)


def invented_benchmark():
    rng=np.random.default_rng(20261117)
    matrices=[]
    for n in (73,68):
        values=rng.integers(-100,101,size=(n,n))
        matrices.append(prepare([[Fraction(int(value),137) for value in row] for row in values]))
    result=simulate(*matrices,draws=10000,seed=20261117)
    # Engineering benchmark intentionally omits null p-values; no real cohort is read.
    return {"kind":"Invented matrix engineering benchmark, no research observations read", "draws":10000,
        "matrix_dimensions":[73,68],"seed":20261117,"numpy_version":np.__version__,
        "elapsed_seconds":result["elapsed_seconds"],"extrapolated_million_draw_seconds":100*result["elapsed_seconds"],
        "exact_boundary_fallbacks":result["continuous_exact_fallback_count"],
        "dense_numpy_matrix_bytes":sum(x["floating"].nbytes+x["win2"].nbytes for x in matrices),
        "memory_scope":"Dense floating/integer score matrices only; exact Python fractions and simulation batches add overhead."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,default=DEFAULT_MANIFEST)
    parser.add_argument("--results",type=Path)
    parser.add_argument("--out-prefix",type=Path,required=True)
    parser.add_argument("--expected-engine-sha256")
    parser.add_argument("--benchmark-invented",action="store_true")
    args=parser.parse_args()
    args.out_prefix.parent.mkdir(parents=True,exist_ok=True)
    if args.benchmark_invented:
        result=invented_benchmark()
    else:
        if args.results is None:parser.error("--results is required for real diagnostic")
        manifest_text,manifest_hash,_=snapshot(args.manifest)
        manifest=json.loads(manifest_text)
        report=validate_full(manifest,args.results,args.expected_engine_sha256)
        matrices=build_matrices(manifest,args.results,report)
        verify_evidence_unchanged(args.results,report)
        result={"protocol":PROTOCOL,"generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "manifest_sha256":manifest_hash,"module_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "engine_hash_counts":report["operator_declared_engine_hash_counts"],
            "input_policy_counts":report["operator_declared_input_policy_counts"],
            "subject_evidence":{p["subject_id"]:p["input_hashes"] for p in report["people"]},
            "matrix_axes":{g:[p["subject_id"] for p in manifest if p["hemisphere"]==g] for g in ("North","South")},
            "result":simulate(matrices["North"],matrices["South"],PROTOCOL["draws"],PROTOCOL["seed"])}
    args.out_prefix.with_suffix(".json").write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    if args.benchmark_invented:
        lines=["# Invented-matrix benchmark", "",json.dumps(result,indent=2),""]
    else:
        lines=["# Optional BIO reassignment diagnostic", "",PROTOCOL["scope"],"",PROTOCOL["assignment"],"",PROTOCOL["assumption"],"",
            "| Statistic | Observed South − North | Upper-tail plus-one p | Monte Carlo SE |",
            "| --- | ---: | ---: | ---: |"]
        for key in ("binary","continuous"):
            r=result["result"]
            lines.append(f"| {key} | {r['observed'][key]:.12g} | {r[key]['plus_one_p']:.8g} | {r[key]['mc_standard_error']:.4g} |")
        lines.extend(["", "Both tails include equality. Exact ties receive half credit. Full protocol, Monte Carlo intervals, source hashes and precision policy are retained in the JSON.",""])
    args.out_prefix.with_suffix(".md").write_text("\n".join(lines))
    print(json.dumps({"saved":str(args.out_prefix.with_suffix('.json')),"kind":result.get("kind",PROTOCOL["version"])}))


if __name__=="__main__":main()
