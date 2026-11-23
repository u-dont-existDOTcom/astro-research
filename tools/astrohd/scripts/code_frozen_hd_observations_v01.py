#!/usr/bin/env python3
"""Chart-blind coding of exact generic HD response tokens, not free text.
The frozen map defines support and explicit contradictions; unknown answers
must not become negative evidence. Input and output are private.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
import compare_bounded_behavior_v01 as rubric

def code(rows, answers):
    if not isinstance(answers,dict) or any(
        not isinstance(k,str) or (v is not None and not isinstance(v,str)) for k,v in answers.items()):
        raise ValueError("Expected question IDs mapped to exact string tokens or null")
    result={}
    for r in rows:
        questions=r["question_ids"]
        if len(questions)!=1:
            raise ValueError("Unreviewed multiple-question mapping")
        q=questions[0];token=answers.get(q)
        support=set(r["predicted_response"]["support_answer_tokens"])
        contra=set((r.get("contradiction_rule") or {}).get("answer_tokens",[]))
        if support&contra:
            raise ValueError("Conflicting source response tokens")
        value=1 if token in support else -1 if token in contra else None
        result[r["mapping_id"]]={"observation":value,"question_id":q,
          "status":"SUPPORT" if value==1 else "EXPLICIT_CONTRADICTION" if value==-1 else
          "NO_RESPONSE" if token is None else "UNMAPPED_OR_NEUTRAL_RESPONSE"}
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("mapping-library","answers","output"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    if any(f.resolve().is_relative_to(rubric.ROOT) for f in (a.mapping_library,a.answers,a.output)):
        p.error("Private inputs and output must remain outside the public checkout")
    rows=rubric.load_mapping(a.mapping_library)
    result=code(rows,json.loads(a.answers.read_text()))
    obj={"status":"EXACT_FROZEN_RESPONSE_TOKEN_CODING_NOT_PREDICTIVE_VALIDATION",
         "mapping_sha256":rubric.digest(a.mapping_library),"answers_sha256":rubric.digest(a.answers),
         "hd":{k:v["observation"] for k,v in result.items()},"trace":result}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(obj,f,indent=2,sort_keys=True);f.write("\n")
    print("Private observation coding written. No chart or candidate rank used.")

if __name__=="__main__":main()
