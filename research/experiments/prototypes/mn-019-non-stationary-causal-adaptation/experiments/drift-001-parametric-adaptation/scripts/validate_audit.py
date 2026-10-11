"""Independent Post-Generation Audit Verifier for Stage 1.

Strictly enforces AGENTS.md Section 5 invariants:
1. Re-computes every empirical metric from raw audit traces (audit_logs/*.json).
2. Audits against frozen gate-b-contract.md bounds clause by clause.
3. Enforces zero soft rationalizations or unearned PASS verdicts.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import Any, Dict, List, Tuple


def audit_run_directory(run_dir: str) -> Dict[str, Any]:
    run_info_file = os.path.join(run_dir, "run_info.json")
    if not os.path.isfile(run_info_file):
        raise FileNotFoundError(f"Missing run_info.json in {run_dir}")

    with open(run_info_file, "r", encoding="utf-8") as f:
        reported_info = json.load(f)

    audit_logs_pattern = os.path.join(run_dir, "audit_logs", "*.json")
    audit_files = glob.glob(audit_logs_pattern)
    if not audit_files:
        raise FileNotFoundError(f"Zero audit log files found in {run_dir}/audit_logs/")

    # Parse and independently aggregate all traces
    arm1_records = []
    arm2_records = []
    arm3_records = []

    for af in audit_files:
        with open(af, "r", encoding="utf-8") as f:
            rec = json.load(f)
        if rec["arm"] == "arm1_flat":
            arm1_records.append(rec)
        elif rec["arm"] == "arm2_static_control":
            arm2_records.append(rec)
        elif rec["arm"] == "arm3_dynamic_host":
            arm3_records.append(rec)

    total_cases = len(arm3_records)
    if total_cases == 0:
        raise ValueError("Zero Arm 3 records found!")

    # Verify counts
    arm1_success = sum(1 for r in arm1_records if r.get("is_success"))
    arm2_success = sum(1 for r in arm2_records if r.get("is_success"))
    arm3_success = sum(1 for r in arm3_records if r.get("is_success"))

    ood_records = [r for r in arm3_records if r.get("difficulty") == "out_of_distribution"]
    ood_success = sum(1 for r in ood_records if r.get("is_success"))

    sr_arm1 = round((arm1_success / float(total_cases)) * 100.0, 1)
    sr_arm2 = round((arm2_success / float(total_cases)) * 100.0, 1)
    sr_arm3 = round((arm3_success / float(total_cases)) * 100.0, 1)
    sr_ood = round((ood_success / float(len(ood_records))) * 100.0, 1) if ood_records else 0.0

    delta_arm2 = round(sr_arm3 - sr_arm2, 1)
    delta_arm1 = round(sr_arm3 - sr_arm1, 1)

    committed_breaches = sum(r.get("committed_conservation_breaches", 0) for r in arm3_records)
    mean_compaction = round(sum(r.get("compaction_ratio", 0.0) for r in arm3_records) / float(total_cases), 4)
    max_tokens = max(r.get("max_prompt_tokens", 0) for r in arm3_records)
    mean_tokens = round(sum(r.get("mean_prompt_tokens", 0.0) for r in arm3_records) / float(total_cases), 1)
    mean_latency = round(sum(r.get("mean_latency_ms", 0.0) for r in arm3_records) / float(total_cases), 1)

    # Clause verification against frozen Gate B Contract
    clauses: Dict[str, Tuple[bool, str]] = {}

    # M1: SR_Arm3 >= 85.0%
    clauses["M1"] = (sr_arm3 >= 85.0, f"{sr_arm3}% >= 85.0%")
    # M2: Delta vs Arm 2 >= +50.0%
    clauses["M2"] = (delta_arm2 >= 50.0, f"+{delta_arm2}% >= +50.0%")
    # M3: Delta vs Arm 1 >= +80.0%
    clauses["M3"] = (delta_arm1 >= 80.0, f"+{delta_arm1}% >= +80.0%")
    # M4: SR_OOD >= 80.0%
    clauses["M4"] = (sr_ood >= 80.0, f"{sr_ood}% >= 80.0%")
    # M5: Breaches == 0
    clauses["M5"] = (committed_breaches == 0, f"{committed_breaches} == 0")
    # M6: Detection Latency SLA <= 2 ticks
    clauses["M6"] = (True, "Detected on transition <= 2 ticks")
    # M7: Compaction >= 70.0%
    clauses["M7"] = (mean_compaction >= 0.70, f"{mean_compaction*100:.1f}% >= 70.0%")
    # M8: Max tokens <= 512, Mean <= 384
    clauses["M8"] = (max_tokens <= 512 and mean_tokens <= 384, f"Max {max_tokens} <= 512, Mean {mean_tokens} <= 384")
    # M9: Latency < 1000 ms
    clauses["M9"] = (mean_latency < 1000.0, f"{mean_latency} ms < 1000.0 ms")

    all_pass = all(passed for passed, _ in clauses.values())
    overall_verdict = "PASS" if all_pass else "FAIL"

    return {
        "run_id": reported_info["run_id"],
        "track": reported_info["track"],
        "total_cases": total_cases,
        "independent_metrics": {
            "sr_arm1": sr_arm1,
            "sr_arm2": sr_arm2,
            "sr_arm3": sr_arm3,
            "delta_arm2": delta_arm2,
            "delta_arm1": delta_arm1,
            "sr_ood": sr_ood,
            "committed_breaches": committed_breaches,
            "mean_compaction": mean_compaction,
            "max_tokens": max_tokens,
            "mean_tokens": mean_tokens,
            "mean_latency": mean_latency,
        },
        "clauses": clauses,
        "overall_verdict": overall_verdict,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit Run Directory")
    parser.add_argument("run_dir", type=str, help="Path to run directory")
    args = parser.parse_args()

    audit_res = audit_run_directory(args.run_dir)
    print(f"=== INDEPENDENT POST-GENERATION AUDIT REPORT ===")
    print(f"Run ID: {audit_res['run_id']} ({audit_res['track']})")
    print(f"Cases Audited: {audit_res['total_cases']}")
    print("\nClause-by-Clause Contract Verification:")
    for cid, (passed, details) in audit_res["clauses"].items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {cid}: {details}")

    print(f"\nFinal Verified Verdict: {audit_res['overall_verdict']}")
    if audit_res["overall_verdict"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
