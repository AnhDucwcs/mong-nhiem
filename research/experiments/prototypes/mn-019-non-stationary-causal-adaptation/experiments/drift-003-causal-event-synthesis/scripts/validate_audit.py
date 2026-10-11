"""Independent Post-Generation Audit Validator for Stage 3.

Audits execution logs directly to verify frozen Gate B evaluation contract clauses M1–M9.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple


def audit_run_directory(run_dir: str) -> Dict[str, Any]:
    run_info_file = os.path.join(run_dir, "run_info.json")
    logs_dir = os.path.join(run_dir, "audit_logs")

    if not os.path.isfile(run_info_file):
        raise FileNotFoundError(f"Missing run_info.json in {run_dir}")

    with open(run_info_file, "r", encoding="utf-8") as f:
        reported_info = json.load(f)

    log_files = [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.endswith("_audit.json")]
    if not log_files:
        raise ValueError(f"No audit logs found in {logs_dir}")

    arm3_records = []
    arm2_records = []
    arm1_records = []

    for fpath in log_files:
        with open(fpath, "r", encoding="utf-8") as f:
            rec = json.load(f)
            arm = rec.get("arm", "")
            if arm == "arm3_counterfactual_causal_host":
                arm3_records.append(rec)
            elif arm == "arm2_reactive_control":
                arm2_records.append(rec)
            elif arm == "arm1_flat":
                arm1_records.append(rec)

    total_cases = len(arm3_records)
    sr_arm3 = round((sum(1 for r in arm3_records if r.get("is_success")) / float(total_cases)) * 100.0, 1)
    sr_arm2 = round((sum(1 for r in arm2_records if r.get("is_success")) / float(len(arm2_records))) * 100.0, 1) if arm2_records else 0.0
    sr_arm1 = round((sum(1 for r in arm1_records if r.get("is_success")) / float(len(arm1_records))) * 100.0, 1) if arm1_records else 0.0

    delta_arm2 = round(sr_arm3 - sr_arm2, 1)
    delta_arm1 = round(sr_arm3 - sr_arm1, 1)

    ood_records = [r for r in arm3_records if r.get("difficulty") == "out_of_distribution"]
    sr_ood = round((sum(1 for r in ood_records if r.get("is_success")) / float(len(ood_records))) * 100.0, 1) if ood_records else 0.0

    committed_violations = sum(r.get("committed_violations", 0) for r in arm3_records)
    total_bypasses = sum(r.get("proactive_bypasses", 0) for r in arm3_records)
    mean_compaction = round(sum(r.get("compaction_ratio", 0.0) for r in arm3_records) / float(total_cases), 4)
    max_tokens = max(r.get("max_prompt_tokens", 0) for r in arm3_records)
    mean_tokens = round(sum(r.get("mean_prompt_tokens", 0.0) for r in arm3_records) / float(total_cases), 1)
    mean_latency = round(sum(r.get("mean_latency_ms", 0.0) for r in arm3_records) / float(total_cases), 1)

    clauses: Dict[str, Tuple[bool, str]] = {}

    # M1: SR_Arm3 >= 85.0%
    clauses["M1"] = (sr_arm3 >= 85.0, f"{sr_arm3}% >= 85.0%")
    # M2: Delta vs Arm 2 >= +40.0%
    clauses["M2"] = (delta_arm2 >= 40.0, f"+{delta_arm2}% >= +40.0%")
    # M3: Delta vs Arm 1 >= +80.0%
    clauses["M3"] = (delta_arm1 >= 80.0, f"+{delta_arm1}% >= +80.0%")
    # M4: SR_OOD >= 80.0%
    clauses["M4"] = (sr_ood >= 80.0, f"{sr_ood}% >= 80.0%")
    # M5: Committed violations == 0
    clauses["M5"] = (committed_violations == 0, f"{committed_violations} == 0")
    # M6: Proactive Latent Trap Bypass Rate >= 80.0%
    bypass_rate = (total_bypasses / float(total_cases)) * 100.0 if total_cases > 0 else 0.0
    clauses["M6"] = (bypass_rate >= 80.0, f"{bypass_rate:.1f}% >= 80.0% ({total_bypasses}/{total_cases} bypasses)")
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
            "committed_violations": committed_violations,
            "total_bypasses": total_bypasses,
            "bypass_rate": bypass_rate,
            "mean_compaction": mean_compaction,
            "max_tokens": max_tokens,
            "mean_tokens": mean_tokens,
            "mean_latency": mean_latency,
        },
        "clauses": clauses,
        "overall_verdict": overall_verdict,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit Stage 3 Execution Logs against Gate B Contract")
    parser.add_argument("run_dir", type=str, help="Path to run directory")
    args = parser.parse_args()

    audit = audit_run_directory(args.run_dir)
    print("=== INDEPENDENT POST-GENERATION AUDIT REPORT (STAGE 3) ===")
    print(f"Run ID: {audit['run_id']} (Track {audit['track']})")
    print(f"Cases Audited: {audit['total_cases']}")
    print("\nClause-by-Clause Contract Verification:")
    for cid, (passed, msg) in audit["clauses"].items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {cid}: {msg}")

    print(f"\nFinal Verified Verdict: {audit['overall_verdict']}")
    if audit["overall_verdict"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
