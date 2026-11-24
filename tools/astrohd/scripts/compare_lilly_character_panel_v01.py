#!/usr/bin/env python3
"""First conditional Lilly CVII/CVIII behavioral comparison, private panel.
Uses the existing 96-stage source rules; no historical strength resolution or
full-century Lilly behavioral result claimed. Strong/weak arms are explicit
assumptions, not inferred from Ptolemaic conditions or participant fit.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from itertools import product
import numpy as np
import swisseph as swe
import compare_planet_character_century_v01 as pc
import compare_bounded_behavior_v01 as b
import compare_full_grid_behavior_v01 as g
import lilly_cvii_ordered_stage_coverage_full_century_v01 as stage
import lilly_cvii_p535_secondary_dignity_participants_century_v01 as sec

MAP=pc.MAP.parent/"lilly_cviii_planet_character_operational_v01.json"
MAP_SHA="054d59281760071e8144384a2531054ae9f519734b023e87a4ae9a12a4c2087d"
BODIES=tuple(stage.PLANETS)
CLAUSES=("strong","weak")
ARMS=("single_strong","single_weak","mean_strong","mean_weak")

def load_map():
    if b.digest(MAP)!=MAP_SHA:raise ValueError("Lilly source map SHA drift")
    x=json.loads(MAP.read_text());shared=pc.load_registry()
    if x["schema"]!="lilly_cviii_planet_character_operational_v01" or x["shared_vocabulary_sha256"]!=pc.MAP_SHA:
        raise ValueError("Shared source vocabulary changed")
    profiles=x["profiles"]
    if len(profiles)!=5 or {v["body"] for v in profiles}!=set(pc.FIVE):raise ValueError("Missing/duplicate Lilly body")
    keys=set().union(*(set(v) for v in shared["domains"].values()))
    for row in profiles:
        for c in CLAUSES:
            if not row[c] or set(row[c])-keys or any(type(v)!=int or v not in (-1,1) for v in row[c].values()):
                raise ValueError("Invalid Lilly observable directions")
    return x,shared

def table(x,shared,obs):
    keys=set().union(*(set(v) for v in shared["domains"].values()))
    b.checked_obs(obs,keys)
    den=[sum(obs.get(k) is not None for k in shared["domains"][d]) for d in pc.DOMAINS]
    vals=np.zeros((2,7));trace={}
    for r in x["profiles"]:
        i=BODIES.index(r["body"]);trace[r["body"]]={}
        for c,cl in enumerate(CLAUSES):
            sub=[]
            for d,dom in enumerate(pc.DOMAINS):
                q={k:obs[k]*v for k,v in r[cl].items() if k in shared["domains"][dom] and obs.get(k) is not None}
                sub.append({"contributions":q,"score":sum(q.values())/den[d] if den[d] else 0.})
            vals[c,i]=(sub[0]["score"]+sub[1]["score"])/2
            trace[r["body"]][cl]=sub
    return vals,den,trace

def branches(lon,alt,cusp1,cusp2):
    old=stage.old
    n=len(lon)
    primary=old.s3.s1.first_stage_eligible(lon,cusp1,cusp2)
    first={m:e.any(axis=1) for m,e in primary.items()}
    certain,possible=sec.participant_rights_at_primary_places(lon,alt,primary)
    asc_lord,dispositor=old.s3.asc_lord_dispositor_indices(lon,cusp1)
    same=asc_lord==dispositor
    partile=old.partile_body_candidates(lon)
    _,_,stable=old.es.candidate_score_winners(lon[:,2],lon[:,1],alt)
    for orb_name,orbs in stage.ORBS.items():
        disposition=old.s3.old.dispositor_see(lon,cusp1,orbs)
        _,_,other_see=old.s3.individual_other_aspector_masks(lon,cusp1,orbs)
        joins={sc:old.s3.s2.candidates_joined_to_moon_or_mercury(lon,orbs,sc)["union"] for sc in stage.JOINS}
        for mode in stage.MODES:
            scertain=np.logical_and.reduce([certain[mode,t] for t in sec.TERMS])
            spossible=np.logical_or.reduce([possible[mode,t] for t in sec.TERMS])
            for scope in stage.JOINS:
                j=joins[scope]&(~first[mode])[:,None]
                for behold in stage.BEHOLDS:
                    for contact in stage.CONTACTS:
                        st=old.s3.source_s3_later_partitions(first[mode],j.any(axis=1),
                            disposition[behold],other_see[behold][contact].any(axis=1),same)
                        for partpol in stage.PARTILES:
                            tag="|".join((mode,orb_name,scope,behold,"all="+contact,partpol))
                            status,single=stage.stage_status(primary[mode],j,st,partile[partpol],stable,asc_lord)
                            # Preserve plural primaries in S1/S2, do not choose
                            # a higher-ranked planet; S4's force remains unknown.
                            mask=primary[mode]|j
                            chosen=single>=0
                            mask[np.arange(n)[chosen],single[chosen]]=True
                            unresolved=~mask.any(axis=1)
                            # For the intentionally incomplete historical
                            # paths use a maximally loose body/abstention
                            # envelope. It is not a claim all bodies eligible.
                            outer=(mask|spossible).copy()
                            outer[unresolved]=True
                            yield tag,status,single,mask,scertain,spossible,outer

def score(primary,single,outer,vals,hd):
    n=primary.sum(axis=1);r=np.arange(len(n));idx=np.maximum(single,0)
    result={}
    for c,cl in enumerate(CLAUSES):
        mean=(primary*vals[c]).sum(axis=1)/np.maximum(n,1)
        one=np.where(single>=0,vals[c,idx],0.)
        for key,z in (("single_"+cl,one),("mean_"+cl,mean)):
            result[key]={"western":z,"joint":(hd+z)/2}
    # convex mixture of any admitted body/condition; absent testimony zero;
    # uncertain secondary roles can only widen this partial-rubric envelope.
    lo=np.minimum(0,np.where(outer,vals.min(axis=0),2).min(axis=1))
    hi=np.maximum(0,np.where(outer,vals.max(axis=0),-2).max(axis=1))
    result["envelope"]={"western_lo":lo,"western_hi":hi,"joint_lo":(hd+lo)/2,"joint_hi":(hd+hi)/2}
    return result

def chart(c):
    w=c["Western"]["source_witness"];at=g.timestamp(c["utc"])
    if at!=g.timestamp(w["UTC"]):raise ValueError("Exact chart time mismatch")
    site=w["site"]
    jd=swe.julday(at.year,at.month,at.day,at.hour+at.minute/60+at.second/3600+at.microsecond/3.6e9)
    cu,_=swe.houses_ex(jd,float(site["latitude"]),float(site["longitude"]),b"R")
    stored=c["Western"]["regiomontanus_houses"]["regiomontanus_ascendant_longitude_degrees"]
    if abs((cu[0]-float(stored)+180)%360-180)>0.0002:raise ValueError("Exact Regiomontanus ascendant drift")
    return (np.array([[float(w["traditional_planets"][p]["longitude_degrees"]) for p in BODIES]]),
            np.array([float(w["sun_true_altitude_degrees"])]),np.array([cu[0]]),np.array([cu[1]]))

def compare(units,mappings,hdobs,obs):
    x,shared=load_map();vals,den,trace=table(x,shared,obs)
    cases={}
    for u in units:
        c=u["chart_midpoint"];h=b.hd_score(c["HD"],mappings,hdobs)["score"]
        lon,alt,c1,c2=chart(c);out={}
        for tag,st,single,mask,sc,sp,outer in branches(lon,alt,c1,c2):
            z=score(mask,single,outer,vals,np.array([h]))
            names=lambda q:[BODIES[i] for i in np.flatnonzero(q[0])]
            out[tag]={"stage":stage.LABELS[int(st[0])],"primary":names(mask),
                "secondary_all_terms_certain":names(sc),"secondary_any_term_possible":names(sp),
                "unresolved_primary":not bool(mask[0].any()),
                "scores":{k:{f:float(v[0]) for f,v in vv.items()} for k,vv in z.items()}}
        if len(out)!=96:raise ValueError("96 historical branches required")
        cases[u["private_id"]]=out
    if len(cases)!=len(units):raise ValueError("Duplicate panel identity")
    ranks={}
    for tag in next(iter(cases.values())):
        ranks[tag]={k:b.exact_rank({i:v[tag]["scores"][k]["joint"] for i,v in cases.items()}) for k in ARMS}
        ranks[tag]["envelope"]=b.ranks({i:(v[tag]["scores"]["envelope"]["joint_lo"],v[tag]["scores"]["envelope"]["joint_hi"]) for i,v in cases.items()})
    return {"status":"LILLY_CVIII_SELECTED_PANEL_CONDITIONAL_ONLY_NOT_VALIDATED","n":len(units),"observed_domains":den,"cases":cases,"ranks":ranks,"source_trace":trace}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("inventory","mapping-library","hd-evidence","evidence","output"):p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    if any(x.resolve().is_relative_to(b.ROOT) for x in vars(a).values()):raise ValueError("Private paths outside checkout")
    h=json.loads(a.hd_evidence.read_text());e=json.loads(a.evidence.read_text())
    if h["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=pc.MAP_SHA or e["hd_evidence_sha256"]!=b.digest(a.hd_evidence):raise ValueError("Frozen observation binding mismatch")
    u=json.loads(a.inventory.read_text())["comparison_units"]
    result=compare(u,b.load_mapping(a.mapping_library),h["hd"],e["observations"])
    result["source_hashes"]={k:b.digest(v) for k,v in vars(a).items() if k!="output"};result["map_sha256"]=MAP_SHA;result["runner_sha256"]=b.digest(__file__)
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Private Lilly panel scored:",result["n"],"units; 96 branches, four fixed arms and envelope.")

if __name__=="__main__":main()
