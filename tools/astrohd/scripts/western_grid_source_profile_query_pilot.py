#!/usr/bin/env python3
"""Query a verified, source-neutral Western UTC grid with a FROZEN V3.8 rubric.

For each grid timestamp, compute exact V3.8 categorical chart predicates
in NumPy using the float64 Swiss Ephemeris longitude records, and score a
user-selected response vector. This is an *exploratory symbolic overlap*
search over the explicitly declared sampling grid, not predictive validity
or a certified continuous-time sweep.

The V3.8 question bank is a *post-exposure development* model. The complete
V4.3 HD century cache/search remains separate, as required by AGENTS.md.

Usage: ... --cache verified_grid_dir --bank v38.json --answers private.json
    --threshold 2.666667 --out private_results_dir
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timedelta,timezone
from hashlib import sha256
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import os
from time import perf_counter

import numpy as np

BANK_SHA="a464a09604451275850efd009cbd399f8c1b688a511499bfb1c316f55deb2527"
ORIGINAL_SCALAR_SHA="f25b8b6287366b289eaab3986e45c7990b935fdb9a0b3c85fbea84e4b71704ba"
INDEX_SCHEMA="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL"
NAMES=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")
RULERS=("Mars","Venus","Mercury","Moon","Sun","Mercury",
        "Venus","Mars","Jupiter","Saturn","Saturn","Jupiter")
EXALT={"Sun":0,"Moon":1,"Mercury":5,"Venus":11,
       "Mars":9,"Jupiter":3,"Saturn":6}
ORBS={"Sun":15.,"Moon":12.,"Mercury":7.,"Venus":7.,
      "Mars":7.,"Jupiter":9.,"Saturn":9.}
ANGLES={0:("conjunction",0.),2:("sextile",60.),3:("square",90.),
        4:("trine",120.),6:("opposition",180.),8:("trine",120.),
        9:("square",90.),10:("sextile",60.)}
GROUPS={"analytical_inquiry":("Q01","Q04","Q18"),
        "trust_and_affection":("Q03","Q05"),
        "relaxed_baseline":("Q02",),
        "ethical_philosophical_interest":("Q07",)}
CONTRARY="Q09"
ORDER=(0,1,2,3,4,5,6)
FIXED_FLAGS=(
"mercury_jupiter_favorable","mercury_saturn_favorable",
"mercury_venus_favorable","moon_venus_favorable",
"moon_jupiter_favorable","jupiter_venus_favorable",
"moon_mercury_favorable","mercury_mars_strained",
"moon_mars_strained","moon_mercury_strained","moon_jupiter_strained",
"jupiter_saturn_strained","moon_saturn_close","saturn_ruler_of_moon",
"saturn_essential_dignity","moon_essential_debility","moon_waning",
"moon_fixed_sign","moon_mutable_sign","mercury_fixed_sign",
"mercury_mutable_sign","mercury_essential_dignity",
"mercury_essential_debility","mercury_combust","mercury_direct",
)


def sha_bytes(data:bytes)->str:return sha256(data).hexdigest()
def sha_file(path:Path)->str:return sha_bytes(path.read_bytes())
def canon(obj:dict)->bytes:
    return (json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\n").encode()
def utc_parse(s:str)->datetime:
    d=datetime.fromisoformat(s.replace("Z","+00:00"))
    if d.tzinfo is None or d.utcoffset()!=timedelta(0):raise ValueError("UTC ISO time required")
    return d.astimezone(timezone.utc)


def data_flags(data:np.ndarray)->dict[str,np.ndarray]:
    """Vectorized exact replications of old v38 Python flag calculations."""
    if len(data.shape)!=2 or data.shape[1]!=8:raise ValueError("Expected n by 8 float64")
    x={n:data[:,i] for i,n in enumerate(NAMES)}
    sg={n:np.floor(x[n]/30.).astype(np.int8) for n in NAMES}
    n=data.shape[0]
    def aspect(a,b):
        s=(sg[b]-sg[a])%12
        sep=np.abs((x[a]-x[b]+180.)%360.-180.)
        target=np.zeros(n,dtype=float)
        valid=np.zeros(n,dtype=bool)
        labels=np.zeros(n,dtype=np.int8)  # 1 conj 2 sext 3 sq 4 tri 5 opp
        for diff,(kind,degrees) in ANGLES.items():
            mask=s==diff
            if not np.any(mask):continue
            target[mask]=degrees;valid[mask]=True
            labels[mask]={"conjunction":1,"sextile":2,"square":3,
                          "trine":4,"opposition":5}[kind]
        close=valid & (np.abs(sep-target)<=(ORBS[a]+ORBS[b])/2.)
        return labels,close
    def fav(a,b):
        label,close=aspect(a,b)
        return close & np.isin(label,(1,2,4))
    def strained(a,b):
        label,close=aspect(a,b)
        return close & np.isin(label,(3,5))
    def dignity(planet):
        return (np.asarray(RULERS)[sg[planet]]==planet) | (sg[planet]==EXALT[planet])
    def debility(planet):
        return (np.asarray(RULERS)[(sg[planet]+6)%12]==planet)|(((EXALT[planet]+6)%12)==sg[planet])
    moon_saturn,moon_saturn_close=aspect("Moon","Saturn")
    sunmer=np.abs((x["Mercury"]-x["Sun"]+180.)%360.-180.)
    moon_phase=(x["Moon"]-x["Sun"])%360.
    flags={
      "mercury_jupiter_favorable":fav("Mercury","Jupiter"),
      "mercury_saturn_favorable":fav("Mercury","Saturn"),
      "mercury_venus_favorable":fav("Mercury","Venus"),
      "moon_venus_favorable":fav("Moon","Venus"),
      "moon_jupiter_favorable":fav("Moon","Jupiter"),
      "jupiter_venus_favorable":fav("Jupiter","Venus"),
      "moon_mercury_favorable":fav("Moon","Mercury"),
      "mercury_mars_strained":strained("Mercury","Mars"),
      "moon_mars_strained":strained("Moon","Mars"),
      "moon_mercury_strained":strained("Moon","Mercury"),
      "moon_jupiter_strained":strained("Moon","Jupiter"),
      "jupiter_saturn_strained":strained("Jupiter","Saturn"),
      "moon_saturn_close":moon_saturn_close & np.isin(moon_saturn,(1,3,5)),
      "saturn_ruler_of_moon":np.asarray(RULERS)[sg["Moon"]]=="Saturn",
      "saturn_essential_dignity":dignity("Saturn"),
      "moon_essential_debility":debility("Moon"),
      "moon_waning":(moon_phase>180.) & (~np.isclose(moon_phase,180.,atol=1e-9,rtol=0.)),
      "moon_fixed_sign":np.isin(sg["Moon"],(1,4,7,10)),
      "moon_mutable_sign":np.isin(sg["Moon"],(2,5,8,11)),
      "mercury_fixed_sign":np.isin(sg["Mercury"],(1,4,7,10)),
      "mercury_mutable_sign":np.isin(sg["Mercury"],(2,5,8,11)),
      "mercury_essential_dignity":dignity("Mercury"),
      "mercury_essential_debility":debility("Mercury"),
      "mercury_combust":(sunmer>17./60.)&(sunmer<=8.5),
      "mercury_direct":data[:,7]>0.
    }
    if set(flags)!=set(FIXED_FLAGS):raise AssertionError("Missing frozen flags")
    return flags


def code_status(bank:dict,flags:dict)->dict[str,np.ndarray]:
    """0 abstain, 1 support-only, 2 qualifier-only, 3 mixed."""
    n=len(next(iter(flags.values())))
    status={}
    for q in bank["questions"]:
        support=np.zeros(n,dtype=bool)
        qualify=np.zeros(n,dtype=bool)
        for name in q["support_any"]:
            if name not in flags:raise ValueError("Missing requested support flag "+name)
            support|=flags[name]
        for name in q["qualifying_any"]:
            if name not in flags:raise ValueError("Missing requested qualifier flag "+name)
            qualify|=flags[name]
        status[q["id"]]=support.astype(np.uint8)+2*qualify.astype(np.uint8)
    return status


def score_status(status:dict,answers:dict)->np.ndarray:
    n=len(next(iter(status.values())))
    total=np.zeros(n,dtype=float)
    for qs in GROUPS.values():
        selected=[q for q in qs if q in answers and answers[q] in (True,False)]
        if not selected:continue
        vals=[]
        for q in selected:
            s=status[q]
            direction=1. if answers[q] else -1.
            vals.append(np.where(s==1,direction,
                        np.where(s==2,-0.5*direction,0.)))
        total+=sum(vals)/len(vals)
    if answers.get(CONTRARY) is False:
        total-=0.5*(status[CONTRARY]==1)
    elif answers.get(CONTRARY) is True:
        total+=(status[CONTRARY]==1)*1. -(status[CONTRARY]==2)*0.5
    return total


def load_python(filename:Path):
    if sha_file(filename)!=ORIGINAL_SCALAR_SHA:
        raise RuntimeError("Frozen original V3.8 scalar scorer digest differs")
    spec=importlib.util.spec_from_file_location("independent_scalar_v38",filename)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def verify_scalar_arrays(data:np.ndarray, flags:dict,status:dict,mod,bank:dict,
                         answers:dict,vector_scores:np.ndarray):
    """Independent original scorer parity at deterministic first/mid/last."""
    n=len(data)
    for i in sorted({0,n//2,n-1}):
        chart={name:{"longitude":float(data[i,j]),
                      "speed":float(data[i,7]) if name=="Mercury" else 0.}
               for j,name in enumerate(NAMES)}
        scalar=mod.evaluate_bank(chart,bank)
        flag_orig=scalar["flags"]
        for k,v in flags.items():
            if bool(v[i])!=bool(flag_orig[k]):
                raise RuntimeError("Vectorized flag disagrees with original: "+k)
        target_status={r["id"]:{"ABSTAIN":0,"SUPPORT_ONLY":1,
                          "QUALIFIER_ONLY":2,"MIXED":3}[r["status"]]
                       for r in scalar["survey_questions"]}
        if any(int(status[q][i])!=target_status[q] for q in status):
            raise RuntimeError("Question classifications differ")
        score=0.
        for qs in GROUPS.values():
            selected=[q for q in qs if answers.get(q) in (True,False)]
            if selected:
                score+=sum((1. if answers[q] else -1.) if target_status[q]==1
                   else (-.5 if answers[q] else .5) if target_status[q]==2
                   else 0. for q in selected)/len(selected)
        if answers.get(CONTRARY) is False:
            score-=.5 if target_status[CONTRARY]==1 else 0.
        elif answers.get(CONTRARY) is True:
            score+=1. if target_status[CONTRARY]==1 else -.5 if target_status[CONTRARY]==2 else 0.
        if abs(score-float(vector_scores[i]))>1e-9:
            raise RuntimeError("Score disagrees with scalar source")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cache",type=Path,required=True)
    p.add_argument("--bank",type=Path,required=True)
    p.add_argument("--scalar-source",type=Path,required=True)
    p.add_argument("--answers",type=Path,required=True)
    p.add_argument("--threshold",type=float,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if not math.isfinite(args.threshold):raise ValueError("Invalid threshold")
    if args.out.exists():
        raise FileExistsError("Results already exist; use a new path")
    args.out.mkdir(parents=True,exist_ok=True)
    plan=json.loads((args.cache/"plan.json").read_bytes())
    verify=json.loads((args.cache/"verified_manifest.json").read_bytes())
    if plan["schema"]!=INDEX_SCHEMA or verify["schema"]!=INDEX_SCHEMA:
        raise ValueError("Not a compatible source-neutral index")
    if verify["plan_sha256"]!=sha_file(args.cache/"plan.json"):
        raise ValueError("Source plan changed")
    if sha_file(args.bank)!=BANK_SHA:raise RuntimeError("Frozen V3.8 bank mismatch")
    bank=json.loads(args.bank.read_bytes())
    mod=load_python(args.scalar_source)
    answers=json.loads(args.answers.read_bytes())
    if not isinstance(answers,dict) or any(type(v) not in (bool,type(None)) for v in answers.values()):
        raise ValueError("Answers must be three-valued true,false,null")
    if not set(answers).issubset({q["id"] for q in bank["questions"]}):
        raise ValueError("Unknown answer ID")
    if not all(q in answers for qs in GROUPS.values() for q in qs):
        raise ValueError("Missing required developmental comparison answer")
    start=utc_parse(plan["utc_start_inclusive"])
    step=plan["step_minutes"]
    absolute_index=0;included_count=0;windows=[]
    pending=None;max_score_all=-float("inf")
    start_time=perf_counter()
    signature_counts=Counter()
    def finish_interval(a):
        if a is None:return
        first=start+timedelta(minutes=a["first_index"]*step)
        last=start+timedelta(minutes=(a["last_index"]+1)*step)
        windows.append({"first_sample_utc":first.isoformat(),
             "end_exclusive_grid_cell_utc":last.isoformat(),
             "grid_samples":a["count"],"max_symbolic_score":round(a["max"],6),
             "start_index":a["first_index"],"end_index":a["last_index"],
             "note":"Contiguous WINNING SAMPLE CELLS; NOT certified continuous state intervals"})
    for shard in verify["chunks"]:
        fname=args.cache/"chunks"/shard["file"]
        if sha_file(fname)!=shard["sha256"]:
            raise RuntimeError("Astronomy cache shard hash mismatch")
        if shard["first_index"]!=absolute_index:
            raise RuntimeError("Missing noncontiguous cache coverage")
        m=np.memmap(fname,dtype="<f8",mode="r",shape=(shard["count"],8))
        flags=data_flags(m)
        status=code_status(bank,flags)
        score=score_status(status,answers)
        verify_scalar_arrays(m,flags,status,mod,bank,answers,score)
        accepted=score>args.threshold+1e-9
        # A signature is all 18 categorical source-prediction classes.
        # Identical signatures are fully equivalent ONLY under this V3.8 bank;
        # they may have very different natal houses or HD structures.
        signatures=np.zeros(shard["count"],dtype=np.uint64)
        for j,q in enumerate(bank["questions"]):
            signatures |= status[q["id"]].astype(np.uint64) << np.uint64(2*j)
        values,counts=np.unique(signatures[accepted],return_counts=True)
        signature_counts.update({int(k):int(n) for k,n in zip(values,counts)})
        max_score_all=max(max_score_all,float(score.max()))
        for i,win in enumerate(accepted):
            idx=absolute_index+i
            if win:
                included_count+=1
                if pending is None:
                    pending={"first_index":idx,"last_index":idx,"count":1,"max":float(score[i])}
                else:
                    pending["last_index"]=idx;pending["count"]+=1
                    pending["max"]=max(pending["max"],float(score[i]))
            elif pending is not None:
                finish_interval(pending)
                pending=None
        absolute_index+=shard["count"]
    finish_interval(pending)
    if absolute_index!=plan["total_samples"]:
        raise RuntimeError("Index did not cover complete declared grid")
    windows.sort(key=lambda x:(-x["max_symbolic_score"],-x["grid_samples"],x["start_index"]))
    elapsed=perf_counter()-start_time
    report={"status":"POST_EXPOSURE_V38_SYMBOLIC_GRID_QUERY_ONLY",
        "record_count":absolute_index,"matched_grid_samples":included_count,
        "matching_windows":len(windows),"max_score":round(max_score_all,6),
        "threshold_strictly_greater":args.threshold,
        "UTC_grid_start":plan["utc_start_inclusive"],
        "UTC_grid_end_exclusive":plan["utc_end_exclusive"],
        "step_minutes":step,
        "scorer_sha256":BANK_SHA,
        "query_script_sha256":sha_file(Path(__file__)),
        "distinct_frozen_v38_status_signatures_among_hits":len(signature_counts),
        "largest_matching_signature_frequencies":[{"packed_signature":str(k),"samples":n} for k,n in signature_counts.most_common(12)],
        "source_neutral_grid_manifest_sha256":sha_file(args.cache/"verified_manifest.json"),
        "answers_sha256":sha_file(args.answers),
        "scalar_parity_checked_first_mid_last_each_shard":True,
        "time_seconds_query":round(elapsed,4),
        "no_claim_between_samples":True,
        "no_claim_human_profile_predictive_validity":True,
        "windows":windows,
    }
    b=canon(report)
    (args.out/"query.json").write_bytes(b)
    print("GRID_QUERY_DONE",json.dumps({
         "records":absolute_index,"hits":included_count,"windows":len(windows),
         "max_score":round(max_score_all,6),"elapsed_sec":round(elapsed,4),
         "report_sha256":sha_bytes(b)},sort_keys=True))


if __name__=="__main__":main()
