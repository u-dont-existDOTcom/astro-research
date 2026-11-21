#!/usr/bin/env python3
"""Non-bespoke minimal WESTERN Ptolemy Mercury/Moon SIGN-pair census.

Source: Tetrabiblos III.13 assigns rational qualities to Mercury, sensory to
the Moon. Inference under test is narrowly about these two sign labels,
NOT complete Ptolemaic governor/sect/aspect/horoscope character doctrine.
The 100y Swiss longitude index is 15-minute sampled; does not certify
continuous instants between grid marks. Because the signs must be reused
for any chart, counting same pairs tests uniqueness *ceiling*, not ranking
fit nor a statistical human personality outcome. Reference private.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

MANIFEST_SHA="da8a2164b0133599ea71a9c55b2a894c64b89a3ab39c9b3bc278478f0fcadbed"
WITNESS_SHA="499dea1082cf22d14d5530a5bf8d72337745c60fba20306ad389c0fabf79a1a2"
SHAPE=8
MOON_COL=1
MERCURY_COL=2
EXPECTED_SAMPLES=3506400
EXPECTED_STEP=15
SCHEMA="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL"

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def sign_number(position)->np.ndarray:
    arr=np.asarray(position,dtype=np.float64)
    if not np.all(np.isfinite(arr)) or np.any(arr<0) or np.any(arr>=360):
        raise ValueError("Longitude outside [0,360)")
    return np.floor(arr/30).astype(np.uint8)

def count_pairs(rows:np.ndarray)->np.ndarray:
    if rows.ndim!=2 or rows.shape[1]!=SHAPE:
        raise ValueError("Expected 8 Swiss longitude/speed columns")
    m=sign_number(rows[:,MOON_COL]);r=sign_number(rows[:,MERCURY_COL])
    return np.bincount((m.astype(np.int16)*12+r.astype(np.int16)),minlength=144)

def source_pair(witness:dict)->int:
    d=witness["reference"]["traditional_planets"]
    names=("Aries","Taurus","Gemini","Cancer","Leo","Virgo",
           "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")
    moon=d["Moon"]["sign"];mercury=d["Mercury"]["sign"]
    if moon not in names or mercury not in names:
        raise ValueError("Invalid traditional signs")
    return names.index(moon)*12+names.index(mercury)

def run(args:argparse.Namespace)->dict:
    if args.output.exists():raise FileExistsError("Immutable private census already exists")
    if sha(args.witness)!=WITNESS_SHA:
        raise RuntimeError("Private source chart witness changed")
    if sha(args.grid/"verified_manifest.json")!=MANIFEST_SHA:
        raise RuntimeError("Original Western verified grid manifest changed")
    plan_path=args.grid/"plan.json"
    plan=json.loads(plan_path.read_bytes())
    manifest=json.loads((args.grid/"verified_manifest.json").read_bytes())
    if plan.get("schema")!=SCHEMA or manifest.get("schema")!=SCHEMA:
        raise RuntimeError("Wrong Western grid schema")
    if (manifest["plan_sha256"]!=sha(plan_path) or
            plan["total_samples"]!=EXPECTED_SAMPLES or
            plan["step_minutes"]!=EXPECTED_STEP):
        raise RuntimeError("Wrong frozen grid horizon or model")
    witness=json.loads(args.witness.read_bytes())
    ref_pair=source_pair(witness)
    counts=np.zeros(144,dtype=np.int64)
    index=0
    for ch in manifest["chunks"]:
        p=args.grid/"chunks"/ch["file"]
        if ch["first_index"]!=index or p.stat().st_size!=ch["size_bytes"]:
            raise RuntimeError("Noncontiguous Western grid or bytes")
        if sha(p)!=ch["sha256"]:
            raise RuntimeError("Western source shard SHA differs")
        a=np.memmap(p,dtype="<f8",mode="r",shape=(ch["count"],8))
        counts+=count_pairs(a)
        index+=ch["count"]
    if index!=EXPECTED_SAMPLES or int(counts.sum())!=EXPECTED_SAMPLES:
        raise RuntimeError("Grid coverage/count failed")
    matching=int(counts[ref_pair])
    summary={
        "schema":"source_neutral_ptolemy_mercury_moon_sign_pair_15min_grid_census_v01",
        "source":"Ptolemy Tetrabiblos Book III chapter 13 Mercury/Moon sign inquiry",
        "method":"ALL 3506400 15-minute Western source-neutral Swiss tropical grid timestamps, no chart-to-person scoring",
        "verified_grid_manifest_sha256":sha(args.grid/"verified_manifest.json"),
        "private_reference_witness_sha256":sha(args.witness),
        "sample_count":index,
        "matched_same_mercury_and_moon_signs":matching,
        "distinct_sign_pairs_present":int(np.count_nonzero(counts)),
        "unique_best_fit_cannot_be_proven_by_this_two_sign_method":matching>1,
        "continuous_time_coverage":False,
        "conditional_governors_aspects_sect_angularity":"UNSCORED_UNCOVERED",
        "no_personality_probabilities_or_actual_western_rank":True,
        "all_144_sign_pair_counts":counts.tolist(),
    }
    args.output.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    return {k:v for k,v in summary.items() if k!="all_144_sign_pair_counts"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--grid",type=Path,required=True)
    p.add_argument("--witness",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    print(json.dumps(run(p.parse_args()),sort_keys=True))
if __name__=="__main__":main()
