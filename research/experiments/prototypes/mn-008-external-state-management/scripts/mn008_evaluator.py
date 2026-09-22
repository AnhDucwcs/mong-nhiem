"""Evaluator for MN-008 Gate C Phase 2 evidence.

Reads persisted disk artifacts (raw_responses.jsonl) and computes exact deterministic
scores for Arms A, B, and C, checking all Gate B criteria and invariants.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DEFINITION_DIR = EXPERIMENT_ROOT / "definition" / "corpus-v1"
RUNS_DIR = EXPERIMENT_ROOT / "runs"

ACTION_REGEX = re.compile(r"\b(ACTION_[0-3])\b")
PAD_LINE_REGEX = re.compile(r"^pad=([A-Z]+(\s+[A-Z]+)*)$")
ALLOWED_PAD_TOKENS = {"KAPPA", "LAMBDA", "MU", "NU", "XI", "OMICRON", "PI", "RHO"}


def parse_action_token(text: str | None) -> str | None:
    if not text:
        return None
    match = ACTION_REGEX.search(text)
    return match.group(1) if match else None


def validate_arm_b1_grammar(content: str) -> tuple[bool, str]:
    """Validate Arm B Stage 1 output against frozen BNF neutral grammar."""
    lines = content.strip().splitlines()
    if len(lines) != 4:
        return False, f"Expected exactly 4 lines, got {len(lines)}"

    for idx, line in enumerate(lines, 1):
        line = line.strip()
        match = PAD_LINE_REGEX.match(line)
        if not match:
            return False, f"Line {idx} does not match pad= grammar: '{line}'"
        tokens = line[4:].split()
        if not tokens:
            return False, f"Line {idx} has empty pad tokens: '{line}'"
        for tok in tokens:
            if tok not in ALLOWED_PAD_TOKENS:
                return False, f"Line {idx} contains forbidden token '{tok}'"

    # Anti-leakage: must not contain state or entity tokens
    for forbidden in ("S0", "S1", "E1", "E2", "ACTION"):
        if forbidden in content:
            return False, f"Arm B1 content leaked state/action token: '{forbidden}'"

    return True, "VALID"


def binomial_tail_p(n: int, k: int, p: float = 0.25) -> float:
    """Exact one-sided binomial upper tail sum: P(X >= k | n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    tail = 0.0
    for j in range(k, n + 1):
        comb = math.comb(n, j)
        prob = comb * (p**j) * ((1.0 - p) ** (n - j))
        tail += prob
    return tail


def evaluate_run(run_dir: Path) -> dict[str, Any]:
    raw_path = run_dir / "raw_responses.jsonl"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw responses file: {raw_path}")

    # Load evaluator ground truth
    evaluator_records: dict[str, dict[str, Any]] = {}
    with open(DEFINITION_DIR / "evaluator-records.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                evaluator_records[rec["case_id"]] = rec

    # Load raw responses grouped by case
    calls_by_case: dict[str, dict[str, Any]] = {}
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                cid = rec["case_id"]
                arm = rec["arm"]
                if cid not in calls_by_case:
                    calls_by_case[cid] = {}
                calls_by_case[cid][arm] = rec

    total_cases = len(evaluator_records)
    case_results: list[dict[str, Any]] = []

    a_passes = 0
    b_passes = 0
    c_passes = 0
    regressions_b_pass_c_fail = 0

    for case_id, oracle in evaluator_records.items():
        calls = calls_by_case.get(case_id, {})
        target_action = oracle["target_action"]

        # 1. Arm A
        raw_a = calls.get("A", {}).get("extracted_content", "")
        pred_a = parse_action_token(raw_a)
        pass_a = (pred_a == target_action)
        if pass_a:
            a_passes += 1

        # 2. Arm B
        raw_b1 = calls.get("B1", {}).get("extracted_content", "")
        b1_valid, b1_err = validate_arm_b1_grammar(raw_b1)
        raw_b2 = calls.get("B2", {}).get("extracted_content", "")
        pred_b = parse_action_token(raw_b2)
        pass_b = (b1_valid and pred_b == target_action)
        if pass_b:
            b_passes += 1

        # 3. Arm C
        raw_c2 = calls.get("C2", {}).get("extracted_content", "")
        pred_c = parse_action_token(raw_c2)
        pass_c = (pred_c == target_action)
        if pass_c:
            c_passes += 1

        # Strict Non-Regression check: B passes but C fails
        if pass_b and not pass_c:
            regressions_b_pass_c_fail += 1

        case_results.append({
            "arm_a": {"pass": pass_a, "prediction": pred_a, "raw": raw_a},
            "arm_b": {
                "b1_grammar_valid": b1_valid,
                "b1_grammar_status": b1_err,
                "b1_raw": raw_b1,
                "b2_raw": raw_b2,
                "pass": pass_b,
                "prediction": pred_b,
            },
            "arm_c": {"pass": pass_c, "prediction": pred_c, "raw": raw_c2},
            "case_id": case_id,
            "case_ordinal": oracle["case_ordinal"],
            "target_action": target_action,
            "target_pair": oracle["target_pair"],
        })

    rate_a = a_passes / total_cases
    rate_b = b_passes / total_cases
    rate_c = c_passes / total_cases
    delta_c_b = (c_passes - b_passes) / total_cases
    delta_c_a = (c_passes - a_passes) / total_cases

    # Decision criteria evaluation
    criterion_a_compatibility = (a_passes <= 6)
    gate_c_efficacy = (c_passes >= 18)
    gate_c_b_utility = (c_passes - b_passes >= 10)
    policy_non_regression = (regressions_b_pass_c_fail == 0)

    p_value_c = binomial_tail_p(total_cases, c_passes, p=0.25)

    all_criteria_met = (
        criterion_a_compatibility
        and gate_c_efficacy
        and gate_c_b_utility
        and policy_non_regression
    )

    verdict = "SUPPORTED" if all_criteria_met else "UNSUPPORTED"

    report = {
        "case_count": total_cases,
        "case_results": case_results,
        "criteria": {
            "criterion_1_baseline_compatibility": {
                "actual": f"{a_passes}/{total_cases} ({rate_a:.1%})",
                "met": criterion_a_compatibility,
                "threshold": "<= 6/24 (25.0%)",
            },
            "criterion_2_primary_efficacy_gate": {
                "actual": f"{c_passes}/{total_cases} ({rate_c:.1%})",
                "exact_p_value": p_value_c,
                "met": gate_c_efficacy,
                "threshold": ">= 18/24 (75.0%)",
            },
            "criterion_3_causal_utility_gate": {
                "actual": f"{c_passes - b_passes}/24 ({delta_c_b:+.1%})",
                "met": gate_c_b_utility,
                "threshold": "C - B >= 10/24 (+41.7%)",
            },
            "criterion_4_strict_non_regression_policy": {
                "actual_violations": regressions_b_pass_c_fail,
                "met": policy_non_regression,
                "threshold": "n_{B=1,C=0} == 0",
            },
        },
        "metrics": {
            "arm_a_accuracy": rate_a,
            "arm_a_passes": a_passes,
            "arm_b_accuracy": rate_b,
            "arm_b_passes": b_passes,
            "arm_c_accuracy": rate_c,
            "arm_c_passes": c_passes,
            "delta_c_minus_a": delta_c_a,
            "delta_c_minus_b": delta_c_b,
            "p_value_c": p_value_c,
            "regressions_b_pass_c_fail": regressions_b_pass_c_fail,
        },
        "run_id": run_dir.name,
        "verdict": verdict,
    }

    report_path = run_dir / "eval_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate MN-008 execution runs.")
    parser.add_argument("--run-id", type=str, default="mn008-execution-run-0001")
    args = parser.parse_args()

    run_dir = RUNS_DIR / args.run_id
    if not run_dir.exists():
        print(f"Error: run directory does not exist: {run_dir}", file=sys.stderr)
        return 1

    report = evaluate_run(run_dir)

    print(f"\n========================================================")
    print(f"       MN-008 GATE C EVALUATION REPORT [{report['run_id']}]")
    print(f"========================================================")
    print(f"Cases Evaluated: {report['case_count']}")
    print(f"Arm A (Monolithic In-Context):  {report['metrics']['arm_a_passes']}/{report['case_count']} ({report['metrics']['arm_a_accuracy']:.1%})")
    print(f"Arm B (Active Two-Call):        {report['metrics']['arm_b_passes']}/{report['case_count']} ({report['metrics']['arm_b_accuracy']:.1%})")
    print(f"Arm C (External State Engine):  {report['metrics']['arm_c_passes']}/{report['case_count']} ({report['metrics']['arm_c_accuracy']:.1%})")
    print(f"Delta (C - B):                  {report['metrics']['delta_c_minus_b']:+.1%}")
    print(f"Delta (C - A):                  {report['metrics']['delta_c_minus_a']:+.1%}")
    print(f"Exact p-value (Arm C):          {report['metrics']['p_value_c']:.3e}")
    print(f"Regressions (B=1, C=0):         {report['metrics']['regressions_b_pass_c_fail']}")
    print(f"--------------------------------------------------------")
    print(f"1. Baseline Compatibility (A <= 6):      {'PASS' if report['criteria']['criterion_1_baseline_compatibility']['met'] else 'FAIL'}")
    print(f"2. Primary Efficacy Gate (C >= 18):       {'PASS' if report['criteria']['criterion_2_primary_efficacy_gate']['met'] else 'FAIL'}")
    print(f"3. Causal Utility Gate (C - B >= 10):    {'PASS' if report['criteria']['criterion_3_causal_utility_gate']['met'] else 'FAIL'}")
    print(f"4. Strict Non-Regression (n_B1,C0 == 0):  {'PASS' if report['criteria']['criterion_4_strict_non_regression_policy']['met'] else 'FAIL'}")
    print(f"--------------------------------------------------------")
    print(f"FINAL VERDICT: {report['verdict']}")
    print(f"========================================================\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
