#!/usr/bin/env python3
"""Conditional Ptolemy III.13 planet-identity experiment; private outputs only.
Two-place single-body proxies and assumed alliance proxies are NOT historically
certified rulers or alliances. Every source scenario, both condition clauses,
and bounded uncertainty are kept. No rank-driven fit.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter,defaultdict
from itertools import product,combinations_with_replacement
from pathlib import Path
import numpy as np
import compare_full_grid_behavior_v01 as g
import compare_bounded_behavior_v01 as b
import ptolemy_iii13_five_mode_aspect_century_v01 as src

ROOT=b.ROOT
MAP=ROOT/"tools/astrohd/reference/research/ptolemy_iii13_planet_character_operational_v01.json"
MAP_SHA="84e0f6b14f26bb3985fc0a9355b0200a266b96b87c2d3dfc92c6c85392db0531"
REGISTER=MAP.parent/"ptolemy_iii13_natal_character_claims_v1.json"
BODIES=tuple(src.PLANETS)
FIVE=tuple(x for x in BODIES if x not in ("Sun","Moon"))
CONDITIONS=("dignified","opposite")
DOMAINS=("rational","sensory_affective")
# Index 7 means unresolved/no character profile. Luminaries are retained but
# their score is zero, not a substituted body or a negative behavior.
U=7
ARMS=tuple(f"separate_{a}_{c}" for a,c in product(CONDITIONS,repeat=2))+tuple(f"assumed_alliance_{a}" for a in CONDITIONS)

def load_registry():
    if b.digest(MAP)!=MAP_SHA:
        raise ValueError("Frozen planetary operational map SHA drift")
    x=json.loads(MAP.read_text())
    if x["source_register_sha256"]!=b.digest(REGISTER):
        raise ValueError("Original source register SHA drift")
    validate(x)
    return x

def validate(x):
    if x["schema"]!="ptolemy_iii13_planet_character_operational_v01":
        raise ValueError("Wrong map schema")
    sets=[set(x["domains"][d]) for d in DOMAINS]
    if sets[0]&sets[1] or not all(sets):
        raise ValueError("Disjoint nonempty rational/sensory item domains")
    desired={tuple(sorted(p)) for p in combinations_with_replacement(FIVE,2)}
    got=[tuple(r["bodies"]) for r in x["profiles"]]
    if len(got)!=15 or set(got)!=desired:
        raise ValueError("Exactly five solitary and ten mixed configurations required")
    for r in x["profiles"]:
        for k in CONDITIONS:
            if not r[k] or not r["source_locator"][k]:
                raise ValueError("Both source condition clauses required")
            if not set(r[k])<=sets[0]|sets[1] or any(type(v)!=int or v not in (-1,1) for v in r[k].values()):
                raise ValueError("Invalid mapped observable direction")

def tables(reg,obs):
    keys=set().union(*(set(reg["domains"][d]) for d in DOMAINS))
    b.checked_obs(obs,keys)
    # Fixed denominator per faculty, across every source configuration.
    # No reward/penalty for missing evidence or a source-unmentioned trait.
    den=[sum(obs.get(k) is not None for k in reg["domains"][d]) for d in DOMAINS]
    a=np.zeros((2,2,8,8),float)
    trace={}
    for row in reg["profiles"]:
        m,l=map(BODIES.index,row["bodies"])
        name="/".join(row["bodies"])
        trace[name]={}
        for c,cond in enumerate(CONDITIONS):
            trace[name][cond]={}
            for d,domain in enumerate(DOMAINS):
                q={k:v*obs[k] for k,v in row[cond].items() if k in reg["domains"][domain] and obs.get(k) is not None}
                value=sum(q.values())/den[d] if den[d] else 0
                a[c,d,m,l]=a[c,d,l,m]=value
                trace[name][cond][domain]={"contributions":q,"score":value}
    return a,den,trace

def arm_tables(a):
    # Separate single-body proxy: each place has its own condition choice.
    # Assumed alliance: both provisional bodies hypothetically form a pair,
    # with a common condition. The same-body diagonal uses the solitary text.
    m={};l={}
    for i,j in product(range(2),repeat=2):
        k=f"separate_{CONDITIONS[i]}_{CONDITIONS[j]}"
        m[k]=np.repeat(np.diag(a[i,0])[:,None],8,axis=1)
        l[k]=np.repeat(np.diag(a[j,1])[None,:],8,axis=0)
    for i,k0 in enumerate(CONDITIONS):
        k=f"assumed_alliance_{k0}"
        m[k]=a[i,0];l[k]=a[i,1]
    return m,l

def mask(p):
    if p.ndim!=2 or p.shape[1]!=7:
        raise ValueError("Seven-body possible sets required")
    return (p.astype(np.uint8)*(1<<np.arange(7,dtype=np.uint8))).sum(axis=1).astype(np.uint8)

def envelopes(m,l):
    # Candidate-pair Cartesian product outer relaxation. Include abstention
    # independently in each faculty. Source conditions remain unadjudicated.
    poss=[np.array([i for i in range(7) if k&(1<<i)]+[U]) for k in range(128)]
    out={}
    for family,names in (("separate",[k for k in ARMS if k.startswith("separate")]),
                         ("assumed_alliance",[k for k in ARMS if k.startswith("assumed")])):
        lo=np.zeros((128,128));hi=lo.copy()
        mn=np.minimum.reduce([m[k] for k in names]);mx=np.maximum.reduce([m[k] for k in names])
        ln=np.minimum.reduce([l[k] for k in names]);lx=np.maximum.reduce([l[k] for k in names])
        for i,mi in enumerate(poss):
            for j,lj in enumerate(poss):
                ix=np.ix_(mi,lj)
                lo[i,j]=(mn[ix].min()+ln[ix].min())/2
                hi[i,j]=(mx[ix].max()+lx[ix].max())/2
        out[family]=(lo,hi)
    return out

def branches(lon,alt):
    valid=np.abs(alt)>b.base.SUN_ALT_UNCERTAINTY
    aspects={}
    for tol,scope in product(src.TOLS,src.SCOPES):
        for ref,pols in ((1,("degree_near_rays",)),(2,src.MERCURY_POLICIES)):
            for pol in pols:
                lo,hi,_=src.aspect_bounds(lon,ref,tol,pol,scope)
                aspects[ref,tol,pol,scope]=(lo,hi)
    for scheme,co in src.VARIANTS:
        bm=b.base.four_mode_votes(lon[:,2],alt,scheme,co).astype(np.int16)
        bl=b.base.four_mode_votes(lon[:,1],alt,scheme,co).astype(np.int16)
        for tol,scope in product(src.TOLS,src.SCOPES):
            llo,lhi=aspects[1,tol,"degree_near_rays",scope]
            lunar={label:src.interval_leader(bl+llo,bl+upper,valid)
                   for label,upper in (("geometry",lhi),("phase_envelope",1))}
            for pol in src.MERCURY_POLICIES:
                mlo,mhi=aspects[2,tol,pol,scope]
                for label,upper in (("geometry",mhi),("phase_envelope",1)):
                    gm,pm=src.interval_leader(bm+mlo,bm+upper,valid)
                    gl,pl=lunar[label]
                    yield f"{scheme}|{co}|{tol}|{pol}|{scope}|{label}",gm,pm,gl,pl

def score_arrays(gm,pm,gl,pl,h,m,l,env):
    x=np.where(gm>=0,gm,U);y=np.where(gl>=0,gl,U)
    mm=mask(pm);ll=mask(pl)
    out={}
    for key in ARMS:
        rational=m[key][x,y];sensory=l[key][x,y]
        west=(rational+sensory)/2
        out[key]={"mercury":rational,"moon":sensory,"western":west,"joint":(h+west)/2}
    for key,(lo,hi) in env.items():
        wlo,whi=lo[mm,ll],hi[mm,ll]
        out[key+"_envelope"]={"western_lo":wlo,"western_hi":whi,
                               "joint_lo":(h+wlo)/2,"joint_hi":(h+whi)/2}
    return out

def make_ref(lon,alt,h,m,l,env):
    out={}
    for tag,gm,pm,gl,pl in branches(lon,alt):
        v=score_arrays(gm,pm,gl,pl,np.array([h]),m,l,env)
        out[tag]={"mercury_guaranteed":BODIES[gm[0]] if gm[0]>=0 else None,
                  "moon_guaranteed":BODIES[gl[0]] if gl[0]>=0 else None,
                  "mercury_possible":[BODIES[i] for i in np.flatnonzero(pm[0])],
                  "moon_possible":[BODIES[i] for i in np.flatnonzero(pl[0])],
                  "scores":{k:{f:float(x[0]) for f,x in v0.items()} for k,v0 in v.items()}}
    if len(out)!=64:
        raise ValueError("Missing historical scenarios")
    return out

def scan(lon,alt,ids,lookups,tablesets,refs,counts):
    known=ids>=0
    if np.any(ids< -1) or np.any(ids>=len(lookups[0])):
        raise ValueError("Invalid HD index")
    for co in counts:co["coverage"].update({"rows":len(ids),"ranked":int(known.sum()),"unknown_HD":int((~known).sum()),
                      "unknown_sect":int((np.abs(alt)<=b.base.SUN_ALT_UNCERTAINTY).sum())})
    hs=[h[np.maximum(ids,0)] for h in lookups]
    for tag,gm,pm,gl,pl in branches(lon,alt):
        for h,(m,l,env),ref,co in zip(hs,tablesets,refs,counts,strict=True):
            values=score_arrays(gm,pm,gl,pl,h,m,l,env)
            target=ref[tag]["scores"]
            for key in ARMS:
                for kind in ("western","joint"):
                    co[tag+"|"+key+"|"+kind].update(g.exact_counts(values[key][kind],target[key][kind],known))
            for f in ("separate","assumed_alliance"):
                key=f+"_envelope"
                for kind in ("western","joint"):
                    lo,hi=values[key][kind+"_lo"],values[key][kind+"_hi"]
                    t=(target[key][kind+"_lo"],target[key][kind+"_hi"])
                    co[tag+"|"+key+"|"+kind].update(g.bound_counts(lo,hi,t,known))

def validate_counts(co,ranked,scenario_count):
    # Parse the final two components, not a substring of the historical tag:
    # phase_envelope names a real historical scenario, not an interval metric.
    exact=[v for k,v in co.items() if k!="coverage" and k.rsplit("|",2)[-2] in ARMS]
    bound=[v for k,v in co.items() if k!="coverage" and k.rsplit("|",2)[-2] in
           ("separate_envelope","assumed_alliance_envelope")]
    if len(exact)!=scenario_count*len(ARMS)*2 or any(sum(x.values())!=ranked for x in exact):
        raise ValueError("Incomplete exact comparison counts")
    if len(bound)!=scenario_count*2*2 or any(
        x["certainly_lower"]+x["could_equal_or_exceed"]!=ranked or
        x["certainly_higher"]>x["could_equal_or_exceed"] for x in bound):
        raise ValueError("Incomplete bounded comparison counts")

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.output,*a.evidence,*a.hd_evidence]
    if any(x.resolve().is_relative_to(ROOT) for x in paths):
        raise ValueError("Private inputs/output outside public checkout required")
    if a.output.exists() or len(a.evidence)!=len(a.hd_evidence) or not a.evidence:
        raise ValueError("Immutable output and paired observation versions required")
    reg=load_registry()
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    mappings=b.load_mapping(a.mapping_library)
    inv=json.loads(a.inventory.read_text());u=next(x for x in inv["comparison_units"] if x["private_id"]=="REFERENCE")
    c=u["chart_midpoint"];w=c["Western"]["source_witness"];at=g.timestamp(c["utc"])
    if at!=g.timestamp(w["UTC"]) or any(float(w["site"][k])!=float(A[k]) for k in ("latitude","longitude","elevation_m")):
        raise ValueError("Reference time/site mismatch")
    lon=np.array([[float(w["traditional_planets"][z]["longitude_degrees"]) for z in BODIES]])
    alt=np.array([float(w["sun_true_altitude_degrees"])])
    hd_ev=[];specs=[];sets=[];refs=[];traces=[]
    for hpath,epath in zip(a.hd_evidence,a.evidence,strict=True):
        h=json.loads(hpath.read_text());e=json.loads(epath.read_text())
        if h["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=MAP_SHA:
            raise ValueError("Frozen evidence binding mismatch")
        if e["hd_evidence_sha256"]!=b.digest(hpath):
            raise ValueError("Wrong paired frozen HD observations")
        a0,den,trace=tables(reg,e["observations"])
        m,l=arm_tables(a0);env=envelopes(m,l)
        hv=b.hd_score(c["HD"],mappings,h["hd"])["score"]
        ref=make_ref(lon,alt,hv,m,l,env)
        hd_ev.append(h);specs.append({"observed_domains":den,"evidence_sha256":b.digest(epath),
                          "HD_evidence_sha256":b.digest(hpath),"reference_HD_score":hv})
        sets.append((m,l,env));refs.append(ref);traces.append(trace)
    lookups,refidx,signatures=g.load_hd_scores(a.hd_cache,mappings,hd_ev,at,c["HD"])
    if any(lookup[refidx]!=spec["reference_HD_score"] for lookup,spec in zip(lookups,specs,strict=True)):
        raise ValueError("HD reference replay mismatch")
    counts=[defaultdict(Counter) for e in hd_ev];processed=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not (wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):
            raise ValueError("Source row alignment drift")
        paths=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for p,meta,size in zip(paths,(wi,ai,hi),(64,136,4),strict=True):
            if p.stat().st_size!=n*size or b.digest(p)!=meta["sha256"]:
                raise ValueError("Grid shard size or SHA drift")
        P=np.memmap(paths[0],dtype="<f8",mode="r",shape=(n,8));Arows=np.memmap(paths[1],dtype="<f8",mode="r",shape=(n,17))
        ids=np.memmap(paths[2],dtype="<i4",mode="r",shape=(n,))
        scan(np.asarray(P[:,:7]),np.asarray(Arows[:,4]),ids,lookups,sets,refs,counts)
        processed+=n
        if processed%500000==0 or processed==g.N:print("Planet character scoring:",processed,"/",g.N,flush=True)
    if processed!=g.N:raise ValueError("Incomplete scan")
    for co in counts:
        if co["coverage"]!={"rows":g.N,"ranked":g.N-125,"unknown_HD":125,"unknown_sect":5049}:
            raise ValueError("Source count drift")
        validate_counts(co,g.N-125,64)
    out={"status":"EXECUTED_RETROSPECTIVE_CONDITIONAL_PLANET_CHARACTER_NOT_VALIDATION",
         "source_map_sha256":MAP_SHA,"runner_sha256":b.digest(__file__),"grid_proof":proof,
         "grid_rows":processed,"ranked_rows":processed-125,"historical_variants":64,
         "fixed_condition_arms":list(ARMS),"reference_in_grid":(at-g.timestamp(W["utc_start_inclusive"])).total_seconds()%900==0,
         "profiles":[{**spec,"reference":ref,"source_score_trace":trace,"counts":dict(co)}
           for spec,ref,trace,co in zip(specs,refs,traces,counts,strict=True)]}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Private result completed and all score rows reconciled.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ("west","angles","hd-cache","join","mapping-library","inventory","output"):
        p.add_argument("--"+n,required=True,type=Path)
    for n in ("evidence","hd-evidence"):
        p.add_argument("--"+n,required=True,type=Path,action="append")
    run(p.parse_args())

if __name__=="__main__":main()
