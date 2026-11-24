"""Reconstruct Chinese calendar features with the prior pinned witnesses.

The original experimental reference-clock/civil-clock conventions are retained.
This module does not create predictions. It compares daily calendar records,
daily hour bins and exact solar-term transitions, then expands the finite grid.
"""
from __future__ import annotations
from datetime import datetime,date,timedelta,timezone
from importlib.metadata import version
from zoneinfo import ZoneInfo
import numpy as np

STEMS="甲乙丙丁戊己庚辛壬癸"
BRANCHES="子丑寅卯辰巳午未申酉戌亥"
JIE=("小寒","立春","惊蛰","清明","立夏","芒种","小暑","立秋","白露","寒露","立冬","大雪")
PINS={"sxtwl":"2.0.7","lunar-python":"1.4.8"}
CLOCKS=("beijing_reference_all","birthplace_wall_day_hour")
BEIJING=timezone(timedelta(hours=8))
SITE_ZONE="America/New_York"
EPOCH=date(1970,1,1)

def witnesses():
    import sxtwl
    from lunar_python import Solar
    for k,v in PINS.items():
        if version(k)!=v:raise ValueError("Calendar dependency version drift")
    return sxtwl,Solar

def day_number(d):
    return (d-EPOCH).days

def wall_seconds(t):
    return day_number(t.date())*86400+t.hour*3600+t.minute*60+t.second+t.microsecond/1e6

def lunar_solar_dt(x):
    return datetime(x.getYear(),x.getMonth(),x.getDay(),x.getHour(),x.getMinute(),x.getSecond())

def gz(s):
    return STEMS.index(s[0]),BRANCHES.index(s[1])

def hour_formula(ds,hour):
    branch=((hour+1)//2)%12
    return ((ds+(hour==23))%5*2+branch)%10,branch

def calendar(start,end):
    """Build independent daily and exact term feature witnesses. End inclusive.
    The lunar-python time formula is the library's day-stem/hour-branch
    computation (late Zi uses next stem); compare it to sxtwl at every hour.
    """
    sxtwl,Solar=witnesses()
    first=start.date()-timedelta(days=4);last=end.date()+timedelta(days=4)
    days=(last-first).days+1
    vals=np.zeros((days,5),np.int16) # day stem, branch, lunar year, signed month, day
    d_ok=np.zeros(days,bool);l_ok=np.zeros(days,bool);h_ok=np.zeros((days,24),bool)
    term_a={};term_b={}
    # Previous and following year terms allow exact search across both edges.
    for y in range(first.year-1,last.year+2):
        L=Solar.fromYmdHms(y,1,1,0,0,0).getLunar()
        tb=L.getJieQiTable()
        for i,k in enumerate(JIE):
            dt=lunar_solar_dt(tb[k])
            if dt.year!=y:raise ValueError("Unexpected Jie reference year")
            after=dt+timedelta(seconds=120)
            ec=Solar.fromYmdHms(after.year,after.month,after.day,after.hour,after.minute,after.second).getLunar().getEightChar()
            term_b[y,i]=(wall_seconds(dt),*gz(ec.getYear()),*gz(ec.getMonth()))
    # sxtwl exact term collection only on the dates of the independent witness,
    # allowing adjacent calendar dates; check all 12 each year.
    for (y,i),(sec,*_) in term_b.items():
        d=EPOCH+timedelta(days=int(sec//86400))
        found=[]
        for offset in (-1,0,1):
            a=d+timedelta(days=offset);x=sxtwl.fromSolar(a.year,a.month,a.day)
            if x.hasJieQi() and x.getJieQi()==2*i+1:
                t=sxtwl.JD2DD(x.getJieQiJD())
                dt=datetime(int(t.Y),int(t.M),int(t.D),int(t.h),int(t.m))+timedelta(seconds=float(t.s))
                Y=x.getYearGZ(False);M=x.getMonthGZ()
                found.append((wall_seconds(dt),Y.tg,Y.dz,M.tg,M.dz))
        if len(found)!=1:raise ValueError("Missing or ambiguous independent Jie term")
        term_a[y,i]=found[0]
    if set(term_a)!=set(term_b):raise ValueError("Term universe mismatch")
    max_term_delta=max(abs(term_a[k][0]-term_b[k][0]) for k in term_a)
    if max_term_delta>86400:raise ValueError("Unexpected term discrepancy")
    direct_lp_hour_checks=0
    seen=set()
    for i in range(days):
        dt=first+timedelta(days=i);a=sxtwl.fromSolar(dt.year,dt.month,dt.day)
        lp=Solar.fromYmdHms(dt.year,dt.month,dt.day,0,0,0).getLunar()
        d=a.getDayGZ();s=a.getLunarMonth()*(-1 if a.isLunarLeap() else 1)
        vals[i]=(d.tg,d.dz,a.getLunarYear(True),s,a.getLunarDay())
        d_ok[i]=(d.tg,d.dz)==gz(lp.getDayInGanZhiExact2())
        l_ok[i]=(int(vals[i,2]),int(vals[i,3]),int(vals[i,4]))==(lp.getYear(),lp.getMonth(),lp.getDay())
        for hr in range(24):
            h=a.getHourGZ(hr,True);h_ok[i,hr]=(h.tg,h.dz)==hour_formula(d.tg,hr)
        # All day stem x 24 hours directly compared to second witness,
        # independent of any score or calendar date chosen for a person.
        if d.tg not in seen and d_ok[i]:
            seen.add(d.tg)
            for hr in range(24):
                l=Solar.fromYmdHms(dt.year,dt.month,dt.day,hr,0,0).getLunar()
                if gz(l.getTimeInGanZhi())!=hour_formula(d.tg,hr):
                    raise ValueError("Second witness hour formula drift")
                direct_lp_hour_checks+=1
    if len(seen)!=10:raise ValueError("Incomplete second witness hour formula test")
    keys=sorted(term_a)
    ta=np.array([term_a[k] for k in keys]);tb=np.array([term_b[k] for k in keys])
    if np.any(np.diff(ta[:,0])<=0) or np.any(np.diff(tb[:,0])<=0):
        raise ValueError("Unordered Jie sources")
    proof={"daily_dates":days,"day_witness_disagreements":int((~d_ok).sum()),
           "lunar_date_witness_disagreements":int((~l_ok).sum()),
           "hour_bin_witness_disagreements":int((~h_ok).sum()),
           "direct_second_hour_formula_checks":direct_lp_hour_checks,
           "jie_terms_each":len(keys),"jie_max_delta_seconds":max_term_delta,
           "jie_pillar_disagreement_terms":int(np.any(ta[:,1:]!=tb[:,1:],axis=1).sum())}
    return {"first":day_number(first),"daily":vals,"day_ok":d_ok,"lunar_ok":l_ok,
            "hour_ok":h_ok,"a":ta,"b":tb,"proof":proof}

def term_values(sec,table):
    i=np.searchsorted(table[:,0],sec,side="right")-1
    if np.any((i<0)|(i>=len(table)-1)):raise ValueError("Missing bracketing terms")
    near=(np.minimum(sec-table[i,0],table[i+1,0]-sec)<=60)
    return table[i,1:].astype(np.int16),near

def term_features(beijing_sec,c):
    a,an=term_values(beijing_sec,c["a"]);b,bn=term_values(beijing_sec,c["b"])
    return a,~(an|bn|np.any(a!=b,axis=1))

def wall_arrays(start,count,step=900):
    """Use exact UTC-to-zone conversions, never a single assumed DST offset."""
    base=wall_seconds(start.replace(tzinfo=None))
    beijing=base+np.arange(count,dtype=np.int64)*step+8*3600
    zone=ZoneInfo(SITE_ZONE);d=timedelta(seconds=step)
    local=np.fromiter((wall_seconds((start+i*d).astimezone(zone).replace(tzinfo=None)) for i in range(count)),dtype=np.int64,count=count)
    return beijing,local

def features(beijing_sec,wall,c):
    """Day/hour elements from chosen wall clock, year/month from Beijing.
    Zi Wei chart date follows the prior next-day late Zi policy.
    """
    ym,term_ok=term_features(beijing_sec,c)
    row=(wall//86400-c["first"]).astype(np.int64)
    hour=((wall%86400)//3600).astype(np.int64)
    nxt=row+(hour==23)
    if np.any((row<0)|(nxt>=len(c["daily"]))):raise ValueError("Calendar date outside verified cache")
    day=c["daily"][row]
    hs,hb=hour_formula(day[:,0],hour)
    # Historical adapter also abstained near a sxtwl term on local wall date;
    # use the symmetric dual-witness caution in both clock conventions.
    _,wall_ok=term_features(wall,c)
    ba_ok=term_ok&wall_ok&c["day_ok"][row]&c["hour_ok"][row,hour]
    z_ok=c["lunar_ok"][nxt]
    return {"bazi":np.column_stack((ym,day[:,:2],hs,hb)), "bazi_known":ba_ok,
            "ziwei":np.column_stack((c["daily"][nxt,2:],hb)), "ziwei_known":z_ok}
