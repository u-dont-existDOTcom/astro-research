#!/usr/bin/env python3
"""Same-row intersections of frozen point-score variants on the original grid.
No candidate shortlist, fitted weights, private publication, or human validation.
Historical uncertainty envelopes remain separate from the point-score analysis.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter,defaultdict
from datetime import timedelta
from itertools import combinations
from pathlib import Path
import numpy as np
import swisseph as swe
import compare_full_grid_behavior_v01 as g
import compare_bounded_behavior_v01 as b
import compare_planet_character_century_v01 as p
import compare_conditioned_character_century_v01 as c
import compare_lilly_character_panel_v01 as l
import compare_lilly_character_century_v01 as lc
import compare_saravali_combinations_century_v01 as v0
import compare_saravali_lunar_solar_century_v01 as v
import compare_chinese_behavior_century_v01 as z
import chinese_calendar_grid_v01 as cal

EPS=g.EPS
GROUPS={"direct_sign":1,"governor_sign":64,"fixed_character":384,
        "condition_character":128,"ptolemy_blend":128,"lilly":384,
        "vedic_union":16,"chinese_union":12}
PRIMARY=("ptolemy_blend","lilly","vedic_union","chinese_union")
RECEIPTS=("sign","planet","condition","lilly","vedic","chinese")
MODULES={"planet":p,"condition":c,"lilly":lc,"vedic":v,"chinese":z}

class Extrema:
    """Extrema across declared arms on the SAME row, not across people."""
    def __init__(self,n):
        self.lo=np.full(n,np.inf);self.hi=np.full(n,-np.inf)
        self.known=np.ones(n,bool)
        self.any_tie=np.zeros(n,bool)
        self.tags=set()
    def add(self,tag,delta,known):
        if tag in self.tags or delta.shape!=self.lo.shape or known.shape!=self.lo.shape:raise ValueError("Duplicate or unaligned arm")
        self.tags.add(tag)
        self.known&=known
        np.minimum(self.lo,delta,out=self.lo)
        np.maximum(self.hi,delta,out=self.hi)
        self.any_tie|=known&(np.abs(delta)<=EPS)

def metrics(ext,known,hd_delta):
    known=known&ext.known
    return Counter(rows=int(known.sum()),higher_any=int((known&(ext.hi>EPS)).sum()),
        higher_all=int((known&(ext.lo>EPS)).sum()),
        equal_any=int((known&ext.any_tie).sum()),
        equal_all=int((known&(ext.lo>=-EPS)&(ext.hi<=EPS)).sum()),
        ge_any=int((known&(ext.hi>=-EPS)).sum()),ge_all=int((known&(ext.lo>=-EPS)).sum()),
        hd_joint_higher_any=int((known&(hd_delta+ext.hi>2*EPS)).sum()),
        hd_joint_higher_all=int((known&(hd_delta+ext.lo>2*EPS)).sum()))

def cross(exts,common,hd):
    """Fixed group product, never choose a variant for a reported rank.
    Any/all quantify the Cartesian set of declared point-score choices.
    """
    low=[a.lo for a in exts];high=[a.hi for a in exts]
    hlo=hd>=-EPS;hhi=hd>EPS;hte=np.abs(hd)<=EPS
    out=Counter(rows=int(common.sum()))
    for q,arr in (("any",high),("all",low)):
        ge=np.logical_and.reduce([x>=-EPS for x in arr])
        gt=np.logical_and.reduce([x>EPS for x in arr])
        one=np.logical_or.reduce([x>EPS for x in arr])
        out["non_hd_all_strict_"+q]=int((common&gt).sum())
        out["all_strict_including_hd_"+q]=int((common&hhi&gt).sum())
        out["hd_tied_others_strict_"+q]=int((common&hte&gt).sum())
        out["weak_dominance_"+q]=int((common&hlo&ge).sum())
        out["pareto_"+q]=int((common&hlo&ge&(hhi|one)).sum())
        out["hd_plus_each_higher_"+q]=int((common&np.logical_and.reduce([hd+x>2*EPS for x in arr])).sum())
        # Equal-family average across this Cartesian product. Western
        # alternatives are evaluated separately, never double-weighted.
        if len(arr)==3:
            total=(hd+arr[0]+arr[1]+arr[2])/4
            out["equal_family_higher_"+q]=int((common&(total>EPS)).sum())
            out["equal_family_ge_"+q]=int((common&(total>=-EPS)).sum())
    tieall=common&hte&np.logical_and.reduce([(x.lo>=-EPS)&(x.hi<=EPS) for x in exts])
    tieany=common&hte&np.logical_and.reduce([x.any_tie for x in exts])
    out["all_systems_tied_every_variant"]=int(tieall.sum())
    out["all_systems_tied_some_variant"]=int(tieany.sum())
    return out

def record(exts,marginals,group,tag,score,target,h,h0,known):
    # Same formulas as frozen runners. Validate every per-arm standalone and
    # averaged rank against its earlier receipt after the complete grid run.
    exts[group].add(tag,score-target,known)
    k=group+"::"+tag
    marginals[k]["single"].update(g.exact_counts(score,target,known))
    marginals[k]["joint"].update(g.exact_counts((h+score)/2,(h0+target)/2,known))

def close(a,b0):
    if abs(float(a)-float(b0))>EPS:raise ValueError("Reference value replay mismatch")

def western(lon,alt,cusp,h,known,profiles,exts,marginals):
    cond=c.all_conditions(lon,alt)
    rows=np.arange(len(lon))
    signs=[g.vote_arrays(lon,q["hd_ev"]["western"]) for q in profiles]
    for i,(q,(ms,ls,ph),hh,ee,mm) in enumerate(zip(profiles,signs,h,exts,marginals,strict=True)):
        ww,_=b.family(ms[:,2],ls[:,1],ph,hh)
        record(ee,mm,"direct_sign","direct",ww,q["direct_ref"],hh,q["h0"],known)
    for tag,gm,pm,gl,pl in p.branches(lon,alt):
        ix=np.where(gm>=0,gm,p.U);iy=np.where(gl>=0,gl,p.U)
        im=np.maximum(gm,0);il=np.maximum(gl,0)
        for q,(ms,ls,ph),hh,ee,mm in zip(profiles,signs,h,exts,marginals,strict=True):
            h0=q["h0"];pr=q["prior"]["planet"]["reference"][tag]["scores"]
            sg,_=b.family(np.where(gm>=0,ms[rows,im],0),np.where(gl>=0,ls[rows,il],0),ph,hh)
            ref=q["prior"]["condition"]["reference"][tag+"|"+c.POLICIES[0]]["scores"]
            record(ee,mm,"governor_sign",tag,sg,ref["sign"],hh,h0,known)
            m,ll=q["planet_tables"]
            for arm in p.ARMS:
                ww=(m[arm][ix,iy]+ll[arm][ix,iy])/2
                record(ee,mm,"fixed_character",tag+"|"+arm,ww,pr[arm]["western"],hh,h0,known)
            t=q["cond_table"]
            for pol in c.POLICIES:
                cc=cond[pol];key=tag+"|"+pol
                mc=np.where(gm>=0,cc[rows,im],c.UNKNOWN)
                lc0=np.where(gl>=0,cc[rows,il],c.UNKNOWN)
                char=(np.where(gm>=0,t[mc,0,im],0.)+np.where(gl>=0,t[lc0,1,il],0.))/2
                rr=q["prior"]["condition"]["reference"][key]["scores"]
                record(ee,mm,"condition_character",key,char,rr["character"],hh,h0,known)
                record(ee,mm,"ptolemy_blend",key,(sg+char)/2,rr["blend"],hh,h0,known)
    for tag,status,single,primary,sc,sp,outer in l.branches(lon,alt,cusp[:,0],cusp[:,1]):
        mask=lc.encode(primary)
        for q,hh,ee,mm in zip(profiles,h,exts,marginals,strict=True):
            rr=q["prior"]["lilly"]["reference"][tag]["scores"]
            for arm in l.ARMS:
                ww=q["lilly_lut"][arm][mask]
                record(ee,mm,"lilly",tag+"|"+arm,ww,rr[arm]["western"],hh,q["h0"],known)

def eastern(lon,jds,start,ids,h,known,profiles,exts,marginals,registry,edges,cache,err):
    reg,prior,shared=registry
    for geom,mode in v.MODES:
        signs,graph,near,e=v.signs_and_graph(lon,jds,mode);err[geom]=max(err.get(geom,0.),e)
        for q,hh,ee,mm in zip(profiles,h,exts,marginals,strict=True):
            tab,obs=q["vedic_tables"]
            for tag,bits in v.compute(signs,graph,reg,edges,tab).items():
                if not tag.endswith("|all_union"):continue
                key=geom+"|"+tag;rr=q["prior"]["vedic"]["reference"][key]
                ww=v.score(bits,obs)["score"]
                record(ee,mm,"vedic_union",key,ww,rr["score"],hh,q["h0"],known&~near)
    bs,ls=cal.wall_arrays(start,len(ids))
    for clock,wall in zip(cal.CLOCKS,(bs,ls),strict=True):
        f=cal.features(bs,wall,cache)
        for q,hh,ee,mm in zip(profiles,h,exts,marginals,strict=True):
            table=q["chinese_tables"]
            for tag,bits,good in z.models(f,table):
                if not tag.startswith("union|"):continue
                key=clock+"|"+tag;rr=q["prior"]["chinese"]["reference"][key]
                ww=v.score(bits,table[2])["score"]
                record(ee,mm,"chinese_union",key,ww,rr["score"],hh,q["h0"],known&good)

def group_options(exts):
    # Keep the primary models distinct; also form a single Western
    # alternative class (Ptolemy blend OR Lilly, not two independent votes).
    a=exts["ptolemy_blend"];bb=exts["lilly"]
    out=Extrema(len(a.lo));out.lo=np.minimum(a.lo,bb.lo);out.hi=np.maximum(a.hi,bb.hi)
    out.known=a.known&bb.known;out.any_tie=a.any_tie|bb.any_tie
    return out

def summarize_chunk(exts,hd,known,index,counts,examples):
    for k,n in GROUPS.items():
        if len(exts[k].tags)!=n:raise ValueError("Declared arm count drift: "+k)
    common=known.copy()
    for x in exts.values():common&=x.known
    counts["coverage"].update(rows=len(known),HD_known=int(known.sum()),common=int(common.sum()),
         HD_strictly_higher=int((known&(hd>EPS)).sum()),HD_tied=int((known&(np.abs(hd)<=EPS)).sum()),
         HD_tied_common=int((common&(np.abs(hd)<=EPS)).sum()),HD_lower=int((known&(hd<-EPS)).sum()))
    ht=common&(np.abs(hd)<=EPS)
    for k,a in exts.items():
        counts["common|"+k].update(metrics(a,common,hd))
        counts["HD_tie|"+k].update(metrics(a,ht,hd))
    west=group_options(exts)
    allgroups={**exts,"western_alternatives":west}
    combos=[("ptolemy_blend","vedic_union","chinese_union"),("lilly","vedic_union","chinese_union"),
            ("western_alternatives","vedic_union","chinese_union"),
            ("ptolemy_blend","lilly","vedic_union","chinese_union")]
    # Other Western variants are retained as sensitivity comparisons, not
    # separate votes in an equal-family average.
    combos.extend((k,"vedic_union","chinese_union") for k in ("direct_sign","governor_sign","fixed_character","condition_character"))
    combos.extend(combinations(PRIMARY,2))
    for names in combos:
        key=" + ".join(names);aa=[allgroups[k] for k in names]
        counts[key].update(cross(aa,common,hd))
        if len(names)>=3:
            masks={"HD_tie_all_others_strict_any":ht&np.logical_and.reduce([x.hi>EPS for x in aa]),
                   "HD_tie_all_others_strict_all":ht&np.logical_and.reduce([x.lo>EPS for x in aa]),
                   "HD_tie_all_others_ge_all":ht&np.logical_and.reduce([x.lo>=-EPS for x in aa])}
            # Save exact indices of the key survivor sets privately, not names
            # of real people or a claim these hypothetical births occurred.
            if names in combos[:4]:
                for label,mask in masks.items():
                    ekey=key+"|"+label
                    examples[ekey].extend((index+np.flatnonzero(mask)).tolist())

def expected(q,group,tag):
    r=q["prior"]
    if group=="direct_sign":
        x=r["sign"]["counts"];return x["Western_direct"],x["joint_direct"]
    if group=="governor_sign":
        x=r["condition"]["counts"];k=tag+"|"+c.POLICIES[0]
        return x[k+"|sign"],x[k+"|joint_sign"]
    if group=="fixed_character":
        x=r["planet"]["counts"];return x[tag+"|western"],x[tag+"|joint"]
    if group in ("condition_character","ptolemy_blend"):
        k="character" if group=="condition_character" else "blend";x=r["condition"]["counts"]
        return x[tag+"|"+k],x[tag+"|joint_"+k]
    if group=="lilly":
        base,arm=tag.rsplit("|",1);x=r["lilly"]["scenarios"][base]
        return x[arm+"|western"],x[arm+"|joint"]
    if group in ("vedic_union","chinese_union"):
        f="vedic" if group=="vedic_union" else "chinese"
        x=r[f]["counts"][tag];return x[f],x["joint"]
    raise ValueError("Unknown score family")

def validate_marginals(q,actual):
    if len(actual)!=sum(GROUPS.values()):raise ValueError("Missing marginal comparisons")
    for key,z0 in actual.items():
        group,tag=key.split("::",1);a,bb=expected(q,group,tag)
        if z0["single"]!=a or z0["joint"]!=bb:
            raise ValueError("Frozen marginal replay drift: "+key)

def prepare(a,W,A,cache,receipts):
    reg=p.load_registry();lr,shared=l.load_map();vr,vp,_=v.load_map();zr,_=z.load_map()
    edges=v0.rule_edges(vp["rules"])
    inv=json.loads(a.inventory.read_text())
    ref=next(x["chart_midpoint"] for x in inv["comparison_units"] if x["private_id"]=="REFERENCE")
    w=ref["Western"]["source_witness"];at=g.timestamp(ref["utc"])
    if at!=g.timestamp(w["UTC"]) or any(float(w["site"][k])!=float(A[k]) for k in ("latitude","longitude","elevation_m")):raise ValueError("Reference site/time mismatch")
    lon=np.array([[float(w["traditional_planets"][name]["longitude_degrees"]) for name in p.BODIES]])
    alt=np.array([float(w["sun_true_altitude_degrees"])])
    mappings=b.load_mapping(a.mapping_library);profiles=[]
    for i,(hp,ep) in enumerate(zip(a.hd_evidence,a.evidence,strict=True)):
        he=json.loads(hp.read_text());ev=json.loads(ep.read_text())
        if he["inventory_sha256"]!=b.digest(a.inventory) or ev["map_sha256"]!=p.MAP_SHA or ev["hd_evidence_sha256"]!=b.digest(hp):raise ValueError("Evidence binding drift")
        prior={k:x["profiles"][i] for k,x in receipts.items()}
        if prior["sign"]["evidence_sha256"]!=b.digest(hp):raise ValueError("Sign evidence drift")
        for k in RECEIPTS[1:]:
            if prior[k]["HD_evidence_sha256"]!=b.digest(hp) or prior[k]["evidence_sha256"]!=b.digest(ep):raise ValueError("Historical evidence drift: "+k)
        h0=b.hd_score(ref["HD"],mappings,he["hd"])["score"]
        if h0!=prior["sign"]["reference_HD_score"]:raise ValueError("HD target drift")
        if any(q.get("reference_HD_score",h0)!=h0 for q in prior.values()):raise ValueError("Previous HD target mismatch")
        a0,_,_=p.tables(reg,ev["observations"]);m,ll=p.arm_tables(a0)
        ct,nc,_=c.score_table(reg,ev["observations"])
        direct,_=b.family(*[t[:,j] if j is not None else t for t,j in zip(g.vote_arrays(lon,he["western"]),(2,1,None),strict=True)],np.array([h0]))
        # Recompute exact reference scores with each original family.
        refp=p.make_ref(lon,alt,h0,m,ll,p.envelopes(m,ll))
        if refp!=prior["planet"]["reference"]:raise ValueError("Planet reference replay drift")
        refc=c.reference(lon,alt,h0,ct,nc,he["western"])
        if refc!=prior["condition"]["reference"]:raise ValueError("Conditioned reference replay drift")
        lvals,_,_=l.table(lr,shared,ev["observations"])
        masks=lc.MASKS;single=np.where(masks.sum(axis=1)==1,np.argmax(masks,axis=1),-1)
        lut={k:val["western"] for k,val in l.score(masks,single,masks,lvals,np.zeros(128)).items() if k in l.ARMS}
        xx,aa,c1,c2=l.chart(ref)
        for tag,st,sg,mask,sc,sp,outer in l.branches(xx,aa,c1,c2):
            vv=l.score(mask,sg,outer,lvals,np.array([h0]))
            for arm in l.ARMS:close(vv[arm]["western"][0],prior["lilly"]["reference"][tag]["scores"][arm]["western"])
        vt=v.make_tables(vr,vp,shared,ev["observations"])
        zt=z.make_tables(zr,shared,ev["observations"])
        def jd(dt):return swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60+dt.second/3600+dt.microsecond/3.6e9)
        refv,_=v.reference(lon,jd(at),vr,edges,[vt],[h0])
        for tag,q0 in refv[0].items():
            if tag.endswith("|all_union"):close(q0["score"],prior["vedic"]["reference"][tag]["score"])
        sec=cal.wall_seconds(at.astimezone(cal.BEIJING));local=cal.wall_seconds(at.astimezone(cal.ZoneInfo(cal.SITE_ZONE)))
        refz=z.reference(sec,local,cache,[zt],[h0])
        for tag,q0 in refz[0].items():
            if "|union|" in tag:close(q0["score"],prior["chinese"]["reference"][tag]["score"])
        profiles.append({"prior":prior,"hd_ev":he,"h0":h0,"direct_ref":float(direct[0]),
                         "planet_tables":(m,ll),"cond_table":ct,"lilly_lut":lut,
                         "vedic_tables":vt,"chinese_tables":zt,
                         "evidence_sha256":b.digest(ep),"HD_evidence_sha256":b.digest(hp)})
    lookups,idx,_=g.load_hd_scores(a.hd_cache,mappings,[q["hd_ev"] for q in profiles],at,ref["HD"])
    if any(h[idx]!=q["h0"] for h,q in zip(lookups,profiles,strict=True)):raise ValueError("HD exact reference drift")
    return profiles,lookups,(vr,vp,shared),edges

def run(a):
    files=[a.west,a.angles,a.hd_cache,a.join,a.ephemeris,a.calendar,a.inventory,a.mapping_library,a.output,*a.evidence,*a.hd_evidence,*[getattr(a,k) for k in RECEIPTS]]
    if any(x.resolve().is_relative_to(b.ROOT) for x in files) or a.output.exists():raise ValueError("Immutable private inputs/output outside public checkout required")
    if len(a.evidence)!=2 or len(a.hd_evidence)!=2:raise ValueError("Two frozen observation versions required")
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    if swe.version!=W["swisseph_version"] or W["requested_flags"]!="SWIEPH|SPEED" or W["record_order"][:7]!=list(p.BODIES):raise ValueError("Astronomical source drift")
    for name,sha in W["ephe_sha256"].items():
        if b.digest(a.ephemeris/name)!=sha:raise ValueError("Ephemeris SHA drift")
    swe.set_ephe_path(str(a.ephemeris));cal.witnesses()
    with np.load(a.calendar,allow_pickle=False) as f:cache={k:f[k] for k in f.files}
    if str(cache["runner_sha256"])!=b.digest(cal.__file__) or str(cache["grid_plan_sha256"])!=b.digest(a.west/"plan.json"):raise ValueError("Calendar provenance drift")
    receipts={k:json.loads(getattr(a,k).read_text()) for k in RECEIPTS}
    if any(x["grid_rows"]!=g.N for x in receipts.values()):raise ValueError("Prior grid changed")
    for k,mod in MODULES.items():
        if receipts[k]["runner_sha256"]!=b.digest(mod.__file__):raise ValueError("Prior scorer digest drift: "+k)
    if receipts["chinese"]["calendar_sha256"]!=b.digest(a.calendar):raise ValueError("Prior Chinese calendar changed")
    profiles,lookup,registry,edges=prepare(a,W,A,cache,receipts)
    start=g.timestamp(W["utc_start_inclusive"]);jd0=swe.julday(start.year,start.month,start.day,start.hour+start.minute/60)
    lat=float(A["latitude"]);long=float(A["longitude"])
    counts=[defaultdict(Counter) for q in profiles];marg=[defaultdict(lambda:defaultdict(Counter)) for q in profiles]
    examples=[defaultdict(list) for q in profiles];err={};processed=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Shard alignment drift")
        pp=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for path,meta,size in zip(pp,(wi,ai,hi),(64,136,4),strict=True):
            if path.stat().st_size!=n*size or b.digest(path)!=meta["sha256"]:raise ValueError("Shard integrity drift")
        P=np.memmap(pp[0],dtype="<f8",mode="r",shape=(n,8));AA=np.memmap(pp[1],dtype="<f8",mode="r",shape=(n,17));ids=np.memmap(pp[2],dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=g.HD_N):raise ValueError("HD index out of range")
        for off in range(0,n,25000):
            stop=min(n,off+25000);I=processed+off;nn=stop-off
            lon=np.asarray(P[off:stop,:7]);alt=np.asarray(AA[off:stop,4]);ii=np.asarray(ids[off:stop]);known=ii>=0
            h=[x[np.maximum(ii,0)] for x in lookup]
            jds=jd0+(I+np.arange(nn,dtype=float))/96.
            cusp=np.array([swe.houses_ex(jd,lat,long,b"R")[0][:2] for jd in jds])
            if np.max(np.abs((cusp[:,0]-AA[off:stop,0]+180)%360-180))>0.0002:raise ValueError("Original ASC drift")
            ext=[{k:Extrema(nn) for k in GROUPS} for q in profiles]
            western(lon,alt,cusp,h,known,profiles,ext,marg)
            eastern(lon,jds,start+timedelta(seconds=900*I),ii,h,known,profiles,ext,marg,registry,edges,cache,err)
            for i,(q,hh,ee,cc,ex) in enumerate(zip(profiles,h,ext,counts,examples,strict=True)):
                summarize_chunk(ee,hh-q["h0"],known,I,cc,ex)
        processed+=n
        if processed%500000==0 or processed==g.N:print("Cross-tradition overlap:",processed,"/",g.N,flush=True)
    if processed!=g.N:raise ValueError("Incomplete grid")
    result=[]
    for q,co,mm,ex in zip(profiles,counts,marg,examples,strict=True):
        validate_marginals(q,mm)
        if co["coverage"]["rows"]!=g.N or co["coverage"]["HD_known"]!=g.N-125:raise ValueError("HD denominator drift")
        hdcounts=q["prior"]["sign"]["counts"]["HD_direct"]
        if [co["coverage"][k] for k in ("HD_strictly_higher","HD_tied","HD_lower")]!=[hdcounts[k] for k in ("higher","tied","lower")]:raise ValueError("HD rank replay drift")
        for key,indices in ex.items():
            name,label=key.rsplit("|",1)
            metric={"HD_tie_all_others_strict_any":"hd_tied_others_strict_any","HD_tie_all_others_strict_all":"hd_tied_others_strict_all","HD_tie_all_others_ge_all":None}[label]
            if indices!=sorted(set(indices)) or (metric and len(indices)!=co[name][metric]):raise ValueError("Survivor identity accounting drift")
        result.append({"HD_evidence_sha256":q["HD_evidence_sha256"],"evidence_sha256":q["evidence_sha256"],"counts":dict(co),
                       "survivor_grid_indices":dict(ex),"replayed_marginal_arms":len(mm)})
    out={"status":"EXECUTED_FROZEN_POINT_SCORE_SAME_ROW_INTERSECTIONS_NOT_VALIDATION","grid_rows":processed,"groups":GROUPS,
         "runner_sha256":b.digest(__file__),"grid_proof":proof,"sidereal_sample_max_error_degrees":err,
         "prior_receipt_sha256":{k:b.digest(getattr(a,k)) for k in RECEIPTS},"profiles":result}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Cross-tradition receipt completed; every included marginal arm replayed exactly.",flush=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","ephemeris","calendar","inventory","mapping-library","output",*RECEIPTS):
        ap.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):ap.add_argument("--"+k,type=Path,action="append",required=True)
    run(ap.parse_args())
if __name__=="__main__":main()
