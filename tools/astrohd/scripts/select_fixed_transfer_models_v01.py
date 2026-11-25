#!/usr/bin/env python3
"""Select existing fixed-model hypotheses on a development subject only.

No transfer-subject input, parameter fitting, universal dominance requirement,
or empirical validation claim. Select by conservative tie-aware rank.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from fractions import Fraction
import compare_full_grid_behavior_v01 as g
import compare_hd_archetype_century_v01 as h
import compare_hd_specific_observables_v01 as q
import compare_conditioned_character_century_v01 as co
import compare_planet_character_century_v01 as pc
import compare_lilly_character_century_v01 as lc
import compare_contextual_hd_evidence_v01 as ctx
b=g.b
FILES=("baseline","context","hd_archetype","hd_specific","western_fixed","western_conditioned","western_lilly")
RUNNERS={"context":ctx,"hd_archetype":h,"hd_specific":q,"western_fixed":pc,"western_conditioned":co,"western_lilly":lc}
N=g.N-125

def validate_rank(r):
    if set(r)!={"higher","lower","tied"} or any(type(v)!=int or v<0 for v in r.values()) or sum(r.values())!=N:
        raise ValueError("Rank denominator drift")

def record(group,tag,r,ref):
    validate_rank(r)
    return {"family":group,"tag":tag,"rank_counts":r,"reference":float(ref)}

def choose(rows):
    if not rows:raise ValueError("Empty development model registry")
    # Same grid denominator for all eligible rows. Minimize last tied rank
    # first, number strictly higher second. Preserve all exact co-winners.
    def key(r):
        c=r["rank_counts"];return c["higher"]+c["tied"],c["higher"]
    best=min(map(key,rows))
    tied=sorted((r for r in rows if key(r)==best),key=lambda r:(r["family"],r["tag"]))
    return {"primary":tied[0],"co_winners":tied,"evaluated":len(rows)}

def collect(receipts):
    H=[];W=[]
    o=receipts["baseline"]["profiles"][0]
    c=receipts["context"]["profiles"][0]
    H.append(record("structural","baseline",c["new_ranks"],c["new_reference_score"]))
    W.append(record("direct_sign","direct",o["counts"]["Western_direct"],o["reference_direct_scores"]["western_direct"]))
    for fam in ("hd_archetype","hd_specific"):
        for tag,z in receipts[fam]["profiles"][2].items():
            for k,v in z["ranks"].items():
                H.append(record(fam,tag+"|"+k,v["full_grid"],z["reference"][k]))
    z=receipts["western_fixed"]["profiles"][0]
    for tag,v in z["reference"].items():
        for arm,scores in v["scores"].items():
            if "western" in scores:
                W.append(record("western_fixed",tag+"|"+arm,z["counts"][tag+"|"+arm+"|western"],scores["western"]))
    z=receipts["western_conditioned"]["profiles"][0]
    for tag,v in z["reference"].items():
        for k in ("character","sign","blend"):
            W.append(record("western_conditioned",tag+"|"+k,z["counts"][tag+"|"+k],v["scores"][k]))
    z=receipts["western_lilly"]["profiles"][0]
    for tag,v in z["reference"].items():
        for k in ("single_strong","single_weak","mean_strong","mean_weak"):
            W.append(record("western_lilly",tag+"|"+k,z["scenarios"][tag][k+"|western"],v["scores"][k]["western"]))
    if len(H)!=121 or len(W)!=1153:raise ValueError(f"Unexpected development registry {len(H)} / {len(W)}")
    return H,W

def run(a):
    if any(p.resolve().is_relative_to(b.ROOT) for p in (a.output,*[getattr(a,k) for k in FILES])) or a.output.exists():raise ValueError("Private immutable inputs/output required")
    paths={k:getattr(a,k) for k in FILES}
    r={k:json.loads(p.read_text()) for k,p in paths.items()}
    for k,mod in RUNNERS.items():
        if r[k]["runner_sha256"]!=b.digest(mod.__file__):raise ValueError("Development runner changed: "+k)
    H,W=collect(r)
    out={"status":"FROZEN_DEVELOPMENT_SELECTION_NOT_VALIDATION","selection_rule":"Minimize higher+tied counts, then higher count, preserve all tied models and lexicographically select primary. Contextual-broad HD, original broad Western. Existing standalone point-score arms only. No cross-arm dominance criterion, no transfer subject used.",
         "HD":choose(H),"Western":choose(W),"HD_simple_baseline":H[0],"Western_simple_baseline":W[0],
         "by_family":{k:choose([x for x in H+W if x["family"]==k]) for k in sorted({x["family"] for x in H+W})},
         "ranked_rows":N,"development_receipts_sha256":{k:b.digest(p) for k,p in paths.items()},"selector_sha256":b.digest(__file__)}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Development model choices frozen before transfer scoring.")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in (*FILES,"output"):p.add_argument("--"+k.replace("_","-"),type=Path,required=True)
    run(p.parse_args())
if __name__=="__main__":main()
