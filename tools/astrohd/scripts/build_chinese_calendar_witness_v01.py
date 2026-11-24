#!/usr/bin/env python3
"""Create an immutable external calendar cache for the declared source grid."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import numpy as np
import chinese_calendar_grid_v01 as c
from compare_bounded_behavior_v01 import ROOT,digest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if any(x.resolve().is_relative_to(ROOT) for x in (a.plan,a.output)) or a.output.exists():
        raise ValueError("External inputs and new immutable output required")
    w=json.loads(a.plan.read_text())
    if w["step_minutes"]!=15:raise ValueError("Unexpected source grid step")
    result=c.calendar(datetime.fromisoformat(w["utc_start_inclusive"]),datetime.fromisoformat(w["utc_end_exclusive"]))
    proof=result.pop("proof")
    os.umask(0o077)
    with a.output.open("xb") as f:
        np.savez_compressed(f,**result,proof=json.dumps(proof,sort_keys=True),
                            runner_sha256=digest(c.__file__),grid_plan_sha256=digest(a.plan))
    print("Calendar witness cache complete:",proof)
if __name__=="__main__":main()
