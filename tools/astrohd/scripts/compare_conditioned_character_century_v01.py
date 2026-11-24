#!/usr/bin/env python3
"""Extend PR38's two fixed partial condition policies to the PR37 grid.
Private retrospective results; no complete historical honorability or human
predictive validation. Preserve the original sign/character baselines.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter,defaultdict
from itertools import product
from pathlib import Path
import numpy as np
import compare_full_grid_behavior_v01 as g
import compare_bounded_behavior_v01 as b
import compare_planet_character_century_v01 as s
import compare_planet_character_condition_pilot_v01 as pilot
import ptolemy_iii13_five_mode_aspect_century_v01 as src

ROOT=b.ROOT
POLICIES=pilot.POLICIES
MODELS=("character","blend")
# condition state 0=dignified proxy, 1=opposite proxy, 2=abstain
UNKNOWN=2
FIVE=np.array([x in s.FIVE for x in s.BODIES],dtype=bool)

def condition_lut(policy):
    lut=np.full(16,UNKNOWN,np.int8)
    for own,match,opp,contrary in product((False,True),repeat=4):
        if match and opp:continue
        k=8*own+4*match+2*opp+contrary
        v=pilot.condition(own,match,opp,contrary,policy)
        lut[k]=v if v is not None else UNKNOWN
    return lut

def all_conditions(lon,alt):
    n=len(lon)
    out={p:np.full((n,7),UNKNOWN,np.int8) for p in POLICIES}
    for i in np.flatnonzero(FIVE):
        q=src.qualifier_flags(lon,alt,np.full(n,i,dtype=np.int8))
        own=q["own_domicile"];match=q["fixed_sect_matches_chart"];opp=q["fixed_sect_opposite_chart"]
        contrary=q["opposite_fixed_sect_preceding_square_witness"]
        if np.any(match&opp):raise ValueError("Conflicting fixed sect flags")
        k=8*own.astype(np.int8)+4*match.astype(np.int8)+2*opp.astype(np.int8)+contrary.astype(np.int8)
        for p in POLICIES:out[p][:,i]=condition_lut(p)[k]
    return out

def score_table(reg,obs):
    a,den,trace=s.tables(reg,obs)
    # diagonal only: solitary planet character applied to each place
    t=np.zeros((3,2,7));n=np.zeros((3,2,7),np.int8)
    for p,i in zip(s.BODIES,range(7)):
        if p not in s.FIVE:continue
        for c,cond in enumerate(s.CONDITIONS):
            for d,dom in enumerate(s.DOMAINS):
                t[c,d,i]=a[c,d,i,i]
                n[c,d,i]=len(trace[p+"/"+p][cond][dom]["contributions"])
    return t,n,den

def fixed_place(leader,possible,condition,values,counts,sign,domain):
    if np.any((leader< -1)|(leader>6)):raise ValueError("Invalid leader")
    r=np.arange(len(leader));i=np.maximum(leader,0)
    st=np.where(leader>=0,condition[r,i],UNKNOWN)
    t=values[condition,domain,np.arange(7)]
    n=counts[condition,domain,np.arange(7)]
    v=np.where(leader>=0,t[r,i],0.)
    num=np.where(leader>=0,n[r,i],0)
    sv=np.where(leader>=0,sign[r,i],0)
    # For the fixed proxy only, allow any possible leader or abstention.
    # Do not present this as an envelope for complete historical conditions.
    clo=np.minimum(0,np.where(possible,t,2).min(axis=1))
    chi=np.maximum(0,np.where(possible,t,-2).max(axis=1))
    slo=np.minimum(0,np.where(possible,sign,2).min(axis=1))
    shi=np.maximum(0,np.where(possible,sign,-2).max(axis=1))
    return {"condition":st,"character":v,"mapped":num,"sign":sv,
            "character_lo":clo,"character_hi":chi,"sign_lo":slo,"sign_hi":shi}

def model_arrays(m,l,phase,hd):
    char=(m["character"]+l["character"])/2
    sign=(m["sign"]+(l["sign"]+phase)/2)/2
    blend=(char+sign)/2 # fixed 50/50 within the Western family; no extra weight
    cl=(m["character_lo"]+l["character_lo"])/2
    ch=(m["character_hi"]+l["character_hi"])/2
    sl=(m["sign_lo"]+(l["sign_lo"]+np.minimum(0,phase))/2)/2
    sh=(m["sign_hi"]+(l["sign_hi"]+np.maximum(0,phase))/2)/2
    return {"character":char,"sign":sign,"blend":blend,
            "character_lo":cl,"character_hi":ch,
            "blend_lo":(cl+sl)/2,"blend_hi":(ch+sh)/2,
            "joint_character":(hd+char)/2,"joint_sign":(hd+sign)/2,
            "joint_blend":(hd+blend)/2,
            "joint_character_lo":(hd+cl)/2,"joint_character_hi":(hd+ch)/2,
            "joint_blend_lo":(hd+(cl+sl)/2)/2,
            "joint_blend_hi":(hd+(ch+sh)/2)/2}

def evaluate(gm,pm,gl,pl,condition,table,ct,signvotes,hd):
    ms,ls,ph=signvotes
    m=fixed_place(gm,pm,condition,table,ct,ms,0)
    l=fixed_place(gl,pl,condition,table,ct,ls,1)
    return m,l,model_arrays(m,l,ph,hd)

def reference(lon,alt,hd,table,ct,signobs):
    cond=all_conditions(lon,alt);sv=g.vote_arrays(lon,signobs)
    out={}
    for tag,gm,pm,gl,pl in s.branches(lon,alt):
        for pol in POLICIES:
            m,l,v=evaluate(gm,pm,gl,pl,cond[pol],table,ct,sv,np.array([hd]))
            out[tag+"|"+pol]={"mercury_condition":s.CONDITIONS[m["condition"][0]] if m["condition"][0]!=UNKNOWN else None,
                "moon_condition":s.CONDITIONS[l["condition"][0]] if l["condition"][0]!=UNKNOWN else None,
                "mercury_mapped":int(m["mapped"][0]),"moon_mapped":int(l["mapped"][0]),
                "mercury":float(m["character"][0]),"moon":float(l["character"][0]),
                "scores":{k:float(a[0]) for k,a in v.items()}}
    if len(out)!=128:raise ValueError("Missing historical policy arms")
    return out

def scan(lon,alt,ids,lookups,specs,refs,results):
    known=ids>=0
    if np.any(ids< -1) or np.any(ids>=len(lookups[0])):raise ValueError("Invalid HD indices")
    cond=all_conditions(lon,alt)
    vs=[g.vote_arrays(lon,x["signobs"]) for x in specs]
    hs=[l[np.maximum(ids,0)] for l in lookups]
    for co in results:co["coverage"].update({"rows":len(ids),"ranked":int(known.sum()),"unknown_HD":int((~known).sum()),"unknown_sect":int((np.abs(alt)<=b.base.SUN_ALT_UNCERTAINTY).sum())})
    # Across-policy/branch intersections, not selecting the best-fit policy.
    robust=[{k:[known.copy(),np.zeros(len(ids),bool),known.copy()] for k in ("joint_character","joint_blend")} for _ in specs]
    for tag,gm,pm,gl,pl in s.branches(lon,alt):
        for pol in POLICIES:
            name=tag+"|"+pol
            for k,(h,spec,sv,ref,co) in enumerate(zip(hs,specs,vs,refs,results,strict=True)):
                m,l,v=evaluate(gm,pm,gl,pl,cond[pol],spec["table"],spec["ct"],sv,h)
                target=ref[name];tv=target["scores"]
                # identical mapped observable counts per faculty (not identical items)
                matched=known&(m["mapped"]==target["mercury_mapped"])&(l["mapped"]==target["moon_mapped"])
                eligible=known&(m["condition"]!=UNKNOWN)&(l["condition"]!=UNKNOWN)
                coverage=co[name+"|coverage"]
                coverage.update({"ranked":int(known.sum()),"both_conditions":int(eligible.sum()),
                    "mercury_dignified":int((known&(m["condition"]==0)).sum()),
                    "mercury_opposite":int((known&(m["condition"]==1)).sum()),
                    "mercury_unknown":int((known&(m["condition"]==UNKNOWN)).sum()),
                    "moon_dignified":int((known&(l["condition"]==0)).sum()),
                    "moon_opposite":int((known&(l["condition"]==1)).sum()),
                    "moon_unknown":int((known&(l["condition"]==UNKNOWN)).sum()),
                    "no_mapped_character_observations":int((known&(m["mapped"]==0)&(l["mapped"]==0)).sum()),
                    "matched_observation_counts":int(matched.sum())})
                for kind in ("character","blend","sign","joint_character","joint_blend","joint_sign"):
                    co[name+"|"+kind].update(g.exact_counts(v[kind],tv[kind],known))
                    if kind.startswith("joint"):
                        co[name+"|matched_"+kind].update(g.exact_counts(v[kind],tv[kind],matched))
                    if kind in robust[k]:
                        allhi,anyhi,alltied=robust[k][kind]
                        hi=known&(v[kind]>tv[kind]+g.EPS)
                        allhi&=hi;anyhi|=hi;alltied&=known&(np.abs(v[kind]-tv[kind])<=g.EPS)
                for kind in ("character","blend","joint_character","joint_blend"):
                    co[name+"|bounds_"+kind].update(g.bound_counts(v[kind+"_lo"],v[kind+"_hi"],(tv[kind+"_lo"],tv[kind+"_hi"]),known))
    for co,r in zip(results,robust,strict=True):
        for kind,(allhi,anyhi,alltied) in r.items():
            co["across_all|"+kind].update({"higher_every":int(allhi.sum()),"higher_any":int(anyhi.sum()),"tied_every":int(alltied.sum())})

def validate(co,ref,n):
    if len(ref)!=128:raise ValueError("Invalid reference scenario count")
    for name,t in ref.items():
        coverage=co[name+"|coverage"]
        if coverage["ranked"]!=n or any(sum(coverage[p+"_"+q] for q in ("dignified","opposite","unknown"))!=n for p in ("mercury","moon")):
            raise ValueError("Incomplete condition coverage")
        for kind in ("character","blend","sign","joint_character","joint_blend","joint_sign"):
            if sum(co[name+"|"+kind].values())!=n:raise ValueError("Incomplete strict score counts")
            if kind.startswith("joint") and sum(co[name+"|matched_"+kind].values())!=coverage["matched_observation_counts"]:
                raise ValueError("Incomplete matched coverage counts")
        for kind in ("character","blend","joint_character","joint_blend"):
            z=co[name+"|bounds_"+kind]
            if z["certainly_lower"]+z["could_equal_or_exceed"]!=n or z["certainly_higher"]>z["could_equal_or_exceed"]:
                raise ValueError("Incomplete bounds counts")

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.prior_sign,a.prior_planet,a.prior_pilot,a.output,*a.evidence,*a.hd_evidence]
    if any(x.resolve().is_relative_to(ROOT) for x in paths):raise ValueError("Private inputs/output outside public checkout required")
    if a.output.exists() or len(a.evidence)!=len(a.hd_evidence) or len(a.evidence)!=2:raise ValueError("Two frozen codings and immutable output required")
    W,WM,A,AM,H,proof=g.verify_inputs(a);reg=s.load_registry()
    mappings=b.load_mapping(a.mapping_library)
    inv=json.loads(a.inventory.read_text())
    c=next(x["chart_midpoint"] for x in inv["comparison_units"] if x["private_id"]=="REFERENCE");w=c["Western"]["source_witness"];at=g.timestamp(c["utc"])
    if at!=g.timestamp(w["UTC"]) or any(float(w["site"][k])!=float(A[k]) for k in ("latitude","longitude","elevation_m")):raise ValueError("Reference site/time mismatch")
    lon=np.array([[float(w["traditional_planets"][z]["longitude_degrees"]) for z in s.BODIES]])
    alt=np.array([float(w["sun_true_altitude_degrees"])])
    prior=json.loads(a.prior_sign.read_text());planet=json.loads(a.prior_planet.read_text());pilot_receipt=json.loads(a.prior_pilot.read_text())
    if prior["grid_rows"]!=g.N or planet["grid_rows"]!=g.N or planet["source_map_sha256"]!=s.MAP_SHA:
        raise ValueError("Previous receipts not from same frozen model/grid")
    specs=[];refs=[];hd_ev=[];provenance=[]
    for k,(hp,ep) in enumerate(zip(a.hd_evidence,a.evidence,strict=True)):
        h=json.loads(hp.read_text());e=json.loads(ep.read_text())
        if h["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=s.MAP_SHA or e["hd_evidence_sha256"]!=b.digest(hp):
            raise ValueError("Frozen input binding mismatch")
        if prior["profiles"][k]["evidence_sha256"]!=b.digest(hp) or planet["profiles"][k]["evidence_sha256"]!=b.digest(ep) or planet["profiles"][k]["HD_evidence_sha256"]!=b.digest(hp):
            raise ValueError("Changed previous evidence")
        hv=b.hd_score(c["HD"],mappings,h["hd"])["score"]
        t,n,den=score_table(reg,e["observations"])
        ref=reference(lon,alt,hv,t,n,h["western"])
        # Scalar PR38 panel parity for both observation versions; also verify
        # previously written broader pilot receipt exactly.
        scalar=pilot.compare(inv["comparison_units"],mappings,reg,h["hd"],e["observations"])
        if k==0:
            if scalar["cases"]!=pilot_receipt["cases"] or scalar["ranks"]!=pilot_receipt["ranks"]:
                raise ValueError("Original private condition pilot changed")
        for u in inv["comparison_units"]:
            ch=u["chart_midpoint"];ww=ch["Western"]["source_witness"]
            p=np.array([[float(ww["traditional_planets"][z]["longitude_degrees"]) for z in s.BODIES]])
            aa=np.array([float(ww["sun_true_altitude_degrees"])])
            hvu=b.hd_score(ch["HD"],mappings,h["hd"])["score"]
            rr=reference(p,aa,hvu,t,n,h["western"])
            for tag,v in scalar["cases"][u["private_id"]].items():
                x=rr[tag]
                if any(x[j]!=v[j] for j in ("mercury_condition","moon_condition","mercury","moon")) or x["scores"]["joint_character"]!=v["joint"]:
                    raise ValueError("Vectorized vs scalar condition pilot mismatch")
        specs.append({"table":t,"ct":n,"signobs":h["western"]});refs.append(ref);hd_ev.append(h)
        provenance.append({"evidence_sha256":b.digest(ep),"HD_evidence_sha256":b.digest(hp),"observed_domains":den,"reference_HD_score":hv})
    lookups,idx,_=g.load_hd_scores(a.hd_cache,mappings,hd_ev,at,c["HD"])
    if any(l[idx]!=p["reference_HD_score"] for l,p in zip(lookups,provenance,strict=True)):raise ValueError("HD reference drift")
    counts=[defaultdict(Counter) for _ in specs];processed=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not (wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Grid alignment drift")
        pp=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for p,meta,size in zip(pp,(wi,ai,hi),(64,136,4),strict=True):
            if p.stat().st_size!=n*size or b.digest(p)!=meta["sha256"]:raise ValueError("Grid shard drift")
        P=np.memmap(pp[0],dtype="<f8",mode="r",shape=(n,8));AA=np.memmap(pp[1],dtype="<f8",mode="r",shape=(n,17));ids=np.memmap(pp[2],dtype="<i4",mode="r",shape=(n,))
        scan(np.asarray(P[:,:7]),np.asarray(AA[:,4]),ids,lookups,specs,refs,counts)
        processed+=n
        if processed%500000==0 or processed==g.N:print("Condition-policy scoring:",processed,"/",g.N,flush=True)
    if processed!=g.N:raise ValueError("Incomplete grid")
    for k,(co,ref) in enumerate(zip(counts,refs,strict=True)):
        if co["coverage"]!={"rows":g.N,"ranked":g.N-125,"unknown_HD":125,"unknown_sect":5049}:raise ValueError("Coverage drift")
        validate(co,ref,g.N-125)
        for tag in ref:
            # PR37 strict sign branch must be unchanged under both conditions.
            oldtag=tag.rsplit("|",1)[0]+"|strict_joint"
            if co[tag+"|joint_sign"]!=prior["profiles"][k]["counts"][oldtag]:
                raise ValueError("PR37 full-grid sign score baseline drift")
    result={"status":"EXECUTED_FULL_GRID_PARTIAL_CONDITION_POLICIES_NOT_VALIDATION","grid_rows":processed,"ranked_rows":processed-125,"grid_proof":proof,
        "policies":list(POLICIES),"historical_variants":64,"source_map_sha256":s.MAP_SHA,"runner_sha256":b.digest(__file__),
        "prior_receipts_sha256":{k:b.digest(p) for k,p in (("sign",a.prior_sign),("planet",a.prior_planet),("pilot",a.prior_pilot))},
        "profiles":[{**p,"reference":r,"counts":dict(co)} for p,r,co in zip(provenance,refs,counts,strict=True)]}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Private condition policy receipt completed. Prior sign baseline and panel parity verified.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ("west","angles","hd-cache","join","mapping-library","inventory","prior-sign","prior-planet","prior-pilot","output"):
        p.add_argument("--"+n,type=Path,required=True)
    for n in ("evidence","hd-evidence"):p.add_argument("--"+n,type=Path,required=True,action="append")
    run(p.parse_args())

if __name__=="__main__":main()
