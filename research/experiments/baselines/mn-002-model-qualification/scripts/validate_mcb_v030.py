#!/usr/bin/env python3
"""Canonical validation for frozen MCB v0.3.0 run artefacts."""
from __future__ import annotations

import json
from pathlib import Path

import mcb
import mcb_v030
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "v0.3.0"
LIMITS = {"instruction_following": .80, "structured_output": .90, "context_retrieval": .80, "state_tracking": .70, "causal_reasoning": .70}
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def valid(value, schema, label):
    errors = list(Draft202012Validator(load(SCHEMAS / schema)).iter_errors(value))
    if errors: raise RuntimeError(f"{label}: {errors[0].message}")
def validate_run(run):
    meta, summary = load(run / "metadata.json"), load(run / "summary.json"); valid(meta,"metadata.schema.json",run.name); valid(summary,"summary.schema.json",run.name)
    cases={c["id"]:c for c in mcb_v030.load_cases()}; rows=[json.loads(x) for x in (run/"results.jsonl").read_text(encoding="utf-8").splitlines() if x]
    if len(rows)!=100 or {r["case_id"] for r in rows}!=set(cases): raise RuntimeError(f"{run.name}: incomplete case coverage")
    groups={s:[] for s in mcb_v030.SUITES}
    for row in rows:
        valid(row,"result.schema.json",row["case_id"]); passed,_,_=mcb_v030.evaluate(cases[row["case_id"]],row["output"]["text"])
        if row["evaluation"]!={"passed":passed,"score":float(passed)}: raise RuntimeError(f"{run.name}/{row['case_id']}: incorrect score")
        groups[cases[row["case_id"]]["suite"]].append(row)
    suites={s:{"cases":len(v),"passed":sum(r["evaluation"]["passed"] for r in v),"score":sum(r["evaluation"]["score"] for r in v)/len(v)} for s,v in groups.items()}
    total=sum(v["passed"] for v in suites.values()); overall={"cases":100,"passed":total,"score":total/100}; reasons=([] if overall["score"]>=.8 else [f"overall {overall['score']:.2f} < 0.80"])+[f"{s} {suites[s]['score']:.2f} < {LIMITS[s]:.2f}" for s in mcb_v030.SUITES if suites[s]["score"]<LIMITS[s]]
    if summary["suites"]!=suites or summary["overall"]!=overall or summary["qualification"]!={"passed":not reasons,"failure_reasons":reasons}: raise RuntimeError(f"{run.name}: summary is not reproducible")
def selected_runs():
    selected={}; fingerprint=mcb_v030.definition_fingerprint()
    for run in mcb.RUNS.iterdir():
        if not (run/"metadata.json").is_file() or not (run/"summary.json").is_file(): continue
        meta,summary=load(run/"metadata.json"),load(run/"summary.json")
        if meta.get("benchmark",{}).get("version")==mcb_v030.VERSION and meta.get("definition_fingerprint")==fingerprint and meta.get("inference",{}).get("benchmark_version")==mcb_v030.VERSION and summary.get("run_status")=="valid": selected[meta["model"]["file"]]=run
    if set(selected)!=set(mcb.MODELS_REQUIRED): raise RuntimeError("exactly six valid v0.3 runs required")
    return selected
if __name__ == "__main__":
    mcb_v030.validate_definitions(); runs=selected_runs()
    for run in runs.values(): validate_run(run)
    print(f"Validated {len(runs)} MCB {mcb_v030.VERSION} runs; fingerprint {mcb_v030.definition_fingerprint()}")
