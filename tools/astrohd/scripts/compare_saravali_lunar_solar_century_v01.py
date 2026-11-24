#!/usr/bin/env python3
"""Conditional Saravali Moon sign and adjacent solar/lunar yoga scoring.
Frozen observable vocabulary, family-wide item caps, prior conjunction replay.
Not a full Jyotisha interpretation or independent predictive validation.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter,defaultdict
from itertools import product
from pathlib import Path
import numpy as np
import swisseph as swe
import compare_saravali_combinations_century_v01 as old
import compare_planet_character_century_v01 as pc
import compare_full_grid_behavior_v01 as g
import compare_bounded_behavior_v01 as b

ROOT=b.ROOT
MAP=pc.MAP.parent/"saravali_xiii_xiv_xxiii_observable_v01.json"
MAP_SHA="0f4559dccc6c92c9fc66836f79d1b3b0a4f2558bc7a80ea951b627df0de3e62f"
MODES=(("lahiri_same_sign",swe.SIDM_LAHIRI),("raman_same_sign",swe.SIDM_RAMAN))
CAUSES=("exact_cause","inclusive_causes")
SCOPES=("exclude_moon_both","allow_moon_twelfth")
FAMILIES=("moon_sign","lunar_yoga","solar_yoga","new_union","all_union")
FIVE=np.array([2,3,4,5,6])
MAPS=old.MAPS
ARMS=tuple("|".join(q) for q in product(tuple(k for k,_ in MODES),CAUSES,SCOPES,MAPS,FAMILIES))

def load_map():
    if b.digest(MAP)!=MAP_SHA:raise ValueError("Frozen map changed")
    x=json.loads(MAP.read_text());prior,shared=old.load_map()
    if x["schema"]!="saravali_xiii_xiv_xxiii_observable_v01" or x["shared_vocabulary_sha256"]!=pc.MAP_SHA or x["prior_conjunction_map_sha256"]!=old.MAP_SHA:
        raise ValueError("Source bindings changed")
    r=x["rules"];keys=set().union(*(set(v) for v in shared["domains"].values()))
    if len(r)!=48 or [q["selector"]["index"] for q in r if q["family"]=="moon_sign"]!=list(range(12)):
        raise ValueError("Missing source clauses")
    for q in r:
        if q["family"] not in FAMILIES[:3] or set(q["direct"])&set(q["proxy"]):raise ValueError("Invalid mapping row")
        for k in ("direct","proxy"):
            if set(q[k])-keys or any(type(v)!=int or v not in (-1,1) for v in q[k].values()):
                raise ValueError("Invalid observable direction")
    return x,prior,shared

def active_rules(signs,rules,cause,scope):
    """Rows are explicit sign configurations; no physical aspect claims.
    General side categories are mutually exclusive; specific clauses only
    qualify in their named yoga category. Exact arms abstain on extra causes.
    """
    if signs.ndim!=2 or signs.shape[1]!=7 or np.any((signs<0)|(signs>11)):raise ValueError("Seven signs required")
    if cause not in CAUSES or scope not in SCOPES:raise ValueError("Unknown convention")
    lm=(signs-signs[:,1,None])%12
    sm=(signs-signs[:,0,None])%12
    before=(lm[:,FIVE]==11);after=(lm[:,FIVE]==1)
    sb=(sm[:,FIVE]==11);sa=(sm[:,FIVE]==1)
    nb=before.sum(axis=1);na=after.sum(axis=1)
    nsb=sb.sum(axis=1)+(sm[:,1]==11 if scope=="allow_moon_twelfth" else 0)
    nsa=sa.sum(axis=1)
    out=np.zeros((len(signs),len(rules)),bool)
    for j,q in enumerate(rules):
        sel=q["selector"];f=q["family"]
        if f=="moon_sign":
            out[:,j]=signs[:,1]==sel["index"];continue
        lunar=f=="lunar_yoga"
        n1,n2=(nb,na) if lunar else (nsb,nsa)
        y=sel["yoga"]
        side1=y in ("anapha","vasi")
        side2=y in ("sunapha","vesi")
        a=(n1>0)&(n2==0) if side1 else (n2>0)&(n1==0) if side2 else (n1>0)&(n2>0)
        if "body" in sel:
            i=old.BODIES.index(sel["body"])
            rel=lm if lunar else sm
            a=a&(rel[:,i]==(11 if side1 else 1))
            if cause=="exact_cause":a&=(n1==1 if side1 else n2==1)
        if "opposite_pair" in sel:
            i,k=map(old.BODIES.index,sel["opposite_pair"])
            a=a&(((lm[:,i]==11)&(lm[:,k]==1))|((lm[:,i]==1)&(lm[:,k]==11)))
            if cause=="exact_cause":a&=(n1==1)&(n2==1)
        out[:,j]=a
    return out

def signs_and_graph(lon,jds,mode):
    a=old.ayanamsas(jds,mode)
    err=old.parity(lon,jds,a,mode)
    sid=(lon-a[:,None])%360
    signs=np.floor(sid/30).astype(np.int8)
    graph,near=old.graph_from_signs(lon,a)
    return signs,graph,near,err

def table(rule_list,keys,mode):
    signed=np.array([[r["direct"].get(k,r["proxy"].get(k,0) if mode=="with_proxies" else 0) for k in keys] for r in rule_list],np.int8)
    bits=np.left_shift(np.uint64(1),np.arange(len(keys),dtype=np.uint64))
    return np.sum((signed==1)*bits,axis=1,dtype=np.uint64),np.sum((signed==-1)*bits,axis=1,dtype=np.uint64)

def bitset(active,t):
    pos,neg=t
    return np.bitwise_or.reduce(np.where(active,pos,0),axis=1,initial=np.uint64(0)),np.bitwise_or.reduce(np.where(active,neg,0),axis=1,initial=np.uint64(0))

def union(*args):
    return np.bitwise_or.reduce([v[0] for v in args],axis=0),np.bitwise_or.reduce([v[1] for v in args],axis=0)

def obs_masks(shared,obs):
    keys=tuple(k for d in pc.DOMAINS for k in shared["domains"][d])
    b.checked_obs(obs,set(keys))
    if len(keys)>64:raise ValueError("Observable bit mask overflow")
    r=[]
    for d in pc.DOMAINS:
        plus=sum(1<<i for i,k in enumerate(keys) if k in shared["domains"][d] and obs.get(k)==1)
        minus=sum(1<<i for i,k in enumerate(keys) if k in shared["domains"][d] and obs.get(k)==-1)
        n=(plus|minus).bit_count()
        r.append((np.uint64(plus),np.uint64(minus),.5/n if n else 0.))
    return keys,r

def score(bits,obs):
    p,n=bits
    out={k:np.zeros(len(p),dtype=float) for k in ("score","lo","hi")}
    out["known_items"]=np.zeros(len(p),np.int16);out["conflicting_items"]=out["known_items"].copy()
    for plus,minus,weight in obs:
        support=(p&plus)|(n&minus);oppose=(p&minus)|(n&plus)
        # Contributions with both signs cancel in the conditional arm.
        support_count=np.bitwise_count(support).astype(np.int16)
        oppose_count=np.bitwise_count(oppose).astype(np.int16)
        out["score"]+=(support_count-oppose_count)*weight
        out["lo"]-=oppose_count*weight;out["hi"]+=support_count*weight
        out["known_items"]+=np.bitwise_count((p|n)&(plus|minus))
        out["conflicting_items"]+=np.bitwise_count(p&n&(plus|minus))
    return out

def make_tables(reg,prior,shared,obs):
    keys,masks=obs_masks(shared,obs)
    return {mode:(table(reg["rules"],keys,mode),table(prior["rules"],keys,mode)) for mode in MAPS},masks

def compute(signs,graph,reg,prior_edges,tables):
    """Collapse duplicate seven-sign patterns before constructing rule bits."""
    if len(signs)!=len(graph):raise ValueError("Unaligned chart geometry")
    sig=np.sum(signs.astype(np.int64)*np.power(12,np.arange(7,dtype=np.int64)),axis=1)
    _,index,inverse=np.unique(sig,return_index=True,return_inverse=True)
    x=signs[index];graph=graph[index]
    conj=old.memberships(graph,prior_edges)["both_inclusive"]
    selectors={f:np.array([r["family"]==f for r in reg["rules"]]) for f in FAMILIES[:3]}
    result={}
    for mode,(nt,ct) in tables.items():
        cb=bitset(conj,ct)
        result["prior|"+mode]=tuple(v[inverse] for v in cb)
        for cause,scope in product(CAUSES,SCOPES):
            active=active_rules(x,reg["rules"],cause,scope)
            fam={f:bitset(active[:,sel],(nt[0][sel],nt[1][sel])) for f,sel in selectors.items()}
            fam["new_union"]=union(*(fam[f] for f in FAMILIES[:3]))
            fam["all_union"]=union(fam["new_union"],cb)
            for f,v in fam.items():
                result["|".join((cause,scope,mode,f))]=tuple(a[inverse] for a in v)
    return result

def compare_row(v,h,known,t):
    joint=(h+v["score"])/2
    matched=known&(v["known_items"]==t["known_items"])
    return {"vedic":g.exact_counts(v["score"],t["score"],known),
            "joint":g.exact_counts(joint,t["joint"],known),
            "matched_joint":g.exact_counts(joint,t["joint"],matched),
            "vedic_bounds":g.bound_counts(v["lo"],v["hi"],(t["lo"],t["hi"]),known),
            "joint_bounds":g.bound_counts((h+v["lo"])/2,(h+v["hi"])/2,(t["joint_lo"],t["joint_hi"]),known),
            "coverage":Counter(ranked=int(known.sum()),has_known_items=int((known&(v["known_items"]>0)).sum()),
                               conflict=int((known&(v["conflicting_items"]>0)).sum()),matched_known_items=int(matched.sum()))}

def reference(lon,jd,reg,edges,sets,hvs):
    refs=[{} for _ in sets];err={}
    for geom,mode in MODES:
        signs,graph,near,err[geom]=signs_and_graph(lon,np.array([jd]),mode)
        if near[0]:raise ValueError("Reference near sign boundary")
        for (tab,obs),hv,r in zip(sets,hvs,refs,strict=True):
            for tag,bits in compute(signs,graph,reg,edges,tab).items():
                v=score(bits,obs)
                t={k:float(a[0]) if k in ("score","lo","hi") else int(a[0]) for k,a in v.items()}
                t.update(joint=(hv+t["score"])/2,joint_lo=(hv+t["lo"])/2,joint_hi=(hv+t["hi"])/2)
                r[geom+"|"+tag]=t
    return refs,err

def scan(lon,jds,ids,lookups,reg,edges,sets,refs,counts,geo,err):
    hd_known=ids>=0
    if np.any(ids<-1) or np.any(ids>=g.HD_N):raise ValueError("Invalid HD join")
    geoms={}
    for name,mode in MODES:
        signs,graph,near,e=signs_and_graph(lon,jds,mode);err[name]=max(err[name],e)
        geoms[name]=(signs,graph,near)
        geo[name].update({"rows":len(ids),"ranked":int((hd_known&~near).sum()),
                          "unknown_HD":int((~hd_known).sum()),"geometry_unknown_with_known_HD":int((hd_known&near).sum())})
    common=hd_known.copy()
    for _,_,near in geoms.values():common&=~near
    for (tab,obs),lookup,ref,co in zip(sets,lookups,refs,counts,strict=True):
        h=lookup[np.maximum(ids,0)]
        higher_all=common.copy();higher_any=np.zeros(len(ids),bool);tied_all=common.copy()
        for name,(signs,graph,near) in geoms.items():
            known=hd_known&~near
            for tag,bits in compute(signs,graph,reg,edges,tab).items():
                k=name+"|"+tag;t=ref[k];v=score(bits,obs)
                for metric,values in compare_row(v,h,known,t).items():co[k][metric].update(values)
                if tag.endswith("|all_union"):
                    j=(h+v["score"])/2;hi=common&(j>t["joint"]+g.EPS)
                    higher_all&=hi;higher_any|=hi;tied_all&=common&(np.abs(j-t["joint"])<=g.EPS)
        co["across_all_union"]["coverage"].update(ranked=int(common.sum()),higher_all=int(higher_all.sum()),higher_any=int(higher_any.sum()),tied_all=int(tied_all.sum()))

def validate(co,refs,geo,prior):
    required=set(ARMS)|{name+"|prior|"+mode for name,_ in MODES for mode in MAPS}
    if set(refs)!=required or set(co)-{"across_all_union"}!=required:raise ValueError("Arm coverage drift")
    for tag in refs:
        r=co[tag];n=geo[tag.split("|")[0]]["ranked"]
        if r["coverage"]["ranked"]!=n or any(sum(r[k].values())!=n for k in ("vedic","joint")) or sum(r["matched_joint"].values())!=r["coverage"]["matched_known_items"]:raise ValueError("Exact count drift")
        for k in ("vedic_bounds","joint_bounds"):
            v=r[k]
            if v["certainly_lower"]+v["could_equal_or_exceed"]!=n or v["certainly_higher"]>v["could_equal_or_exceed"]:raise ValueError("Bound count drift")
        if "|prior|" in tag:
            prev=prior[tag.replace("|prior|","|both_inclusive|")]
            for k in ("vedic","joint","matched_joint","vedic_bounds","joint_bounds"):
                if r[k]!=prev[k]:raise ValueError("Prior conjunction count replay drift")

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.ephemeris,a.mapping_library,a.inventory,a.prior_saravali,*a.evidence,*a.hd_evidence,a.output]
    if any(p.resolve().is_relative_to(ROOT) for p in paths):raise ValueError("Private data outside public checkout required")
    if a.output.exists() or len(a.evidence)!=2 or len(a.hd_evidence)!=2:raise ValueError("Two frozen profiles and new output required")
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    if swe.version!=W["swisseph_version"] or W["requested_flags"]!="SWIEPH|SPEED" or W["record_order"][:7]!=list(old.BODIES):raise ValueError("Source coordinate convention drift")
    for name,sha in W["ephe_sha256"].items():
        if b.digest(a.ephemeris/name)!=sha:raise ValueError("Original ephemeris SHA drift")
    swe.set_ephe_path(str(a.ephemeris))
    reg,prior,shared=load_map();edges=old.rule_edges(prior["rules"])
    prev=json.loads(a.prior_saravali.read_text())
    if prev["grid_rows"]!=g.N or prev["source_map_sha256"]!=old.MAP_SHA or prev["runner_sha256"]!=b.digest(old.__file__):raise ValueError("Prior receipt drift")
    inv=json.loads(a.inventory.read_text());c=next(u["chart_midpoint"] for u in inv["comparison_units"] if u["private_id"]=="REFERENCE")
    w=c["Western"]["source_witness"];at=g.timestamp(c["utc"])
    if at!=g.timestamp(w["UTC"]) or any(float(w["site"][k])!=float(A[k]) for k in ("latitude","longitude","elevation_m")):raise ValueError("Reference site/time mismatch")
    def jd(dt):return swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60+dt.second/3600+dt.microsecond/3.6e9)
    jd0=jd(g.timestamp(W["utc_start_inclusive"]))
    lon=np.array([[float(w["traditional_planets"][z]["longitude_degrees"]) for z in old.BODIES]])
    mappings=b.load_mapping(a.mapping_library);hd_ev=[];sets=[];hvs=[];prov=[]
    for i,(hp,ep) in enumerate(zip(a.hd_evidence,a.evidence,strict=True)):
        h=json.loads(hp.read_text());e=json.loads(ep.read_text())
        if h["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=pc.MAP_SHA or e["hd_evidence_sha256"]!=b.digest(hp):raise ValueError("Frozen evidence binding drift")
        pr=prev["profiles"][i]
        if pr["HD_evidence_sha256"]!=b.digest(hp) or pr["evidence_sha256"]!=b.digest(ep):raise ValueError("Prior evidence changed")
        hv=b.hd_score(c["HD"],mappings,h["hd"])["score"]
        hd_ev.append(h);sets.append(make_tables(reg,prior,shared,e["observations"]));hvs.append(hv)
        prov.append({"HD_evidence_sha256":b.digest(hp),"evidence_sha256":b.digest(ep),"reference_HD_score":hv})
    refs,err=reference(lon,jd(at),reg,edges,sets,hvs)
    for i,r in enumerate(refs):
        for tag,t in r.items():
            if "|prior|" in tag:
                oldref=prev["profiles"][i]["reference"][tag.replace("|prior|","|both_inclusive|")]
                for k in t:
                    if abs(t[k]-oldref[k])>g.EPS:raise ValueError("Prior reference score replay drift")
    lookups,idx,_=g.load_hd_scores(a.hd_cache,mappings,hd_ev,at,c["HD"])
    if any(z[idx]!=hv for z,hv in zip(lookups,hvs,strict=True)):raise ValueError("HD reference drift")
    counts=[defaultdict(lambda:defaultdict(Counter)) for _ in refs];geo=defaultdict(Counter);processed=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Source grid alignment drift")
        p=a.west/"chunks"/wi["file"];hp=a.join/"shards"/hi["file"]
        if p.stat().st_size!=n*64 or hp.stat().st_size!=n*4 or b.digest(p)!=wi["sha256"] or b.digest(hp)!=hi["sha256"]:raise ValueError("Source shard drift")
        P=np.memmap(p,dtype="<f8",mode="r",shape=(n,8));ids=np.memmap(hp,dtype="<i4",mode="r",shape=(n,))
        for start in range(0,n,25000):
            stop=min(n,start+25000);jds=jd0+(processed+np.arange(start,stop,dtype=float))/96.
            scan(np.asarray(P[start:stop,:7]),jds,np.asarray(ids[start:stop]),lookups,reg,edges,sets,refs,counts,geo,err)
        processed+=n
        if processed%500000==0 or processed==g.N:print("Lunar/solar scoring:",processed,"/",g.N,flush=True)
    if processed!=g.N or any(z!=prev["geometry_coverage"][name] for name,z in geo.items()):raise ValueError("Prior grid coverage drift")
    for i,(co,r) in enumerate(zip(counts,refs,strict=True)):validate(co,r,geo,prev["profiles"][i]["counts"])
    out={"status":"EXECUTED_SARAVALI_LUNAR_SOLAR_SIGN_AND_CAPPED_UNION_FINITE_GRID_NOT_VALIDATION","grid_rows":processed,
         "arms":len(ARMS),"prior_baseline_arms":4,"source_map_sha256":MAP_SHA,"runner_sha256":b.digest(__file__),
         "prior_receipt_sha256":b.digest(a.prior_saravali),"geometry_coverage":dict(geo),"sidereal_sample_max_error_degrees":err,
         "grid_proof":proof,"profiles":[{**p,"reference":r,"counts":dict(c)} for p,r,c in zip(prov,refs,counts,strict=True)]}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Lunar/solar full-grid receipt completed; prior conjunction counts replayed exactly.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","ephemeris","mapping-library","inventory","prior-saravali","output"):
        p.add_argument("--"+k,required=True,type=Path)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,action="append",required=True,type=Path)
    run(p.parse_args())
if __name__=="__main__":main()
