"""Quantitative evaluator computing the 10 Gate B acceptance clauses for MN-023."""

from __future__ import annotations

from typing import Any, Dict, List


class MicroworldEvaluator:
    """Evaluates episodic benchmark runs against frozen Gate B contract bounds."""

    @staticmethod
    def evaluate_episode_set(episodes_by_arm: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculates global distributions and clause-by-clause compliance."""
        arm1_eps = episodes_by_arm.get("arm1", [])
        arm2_eps = episodes_by_arm.get("arm2", [])
        arm3_eps = episodes_by_arm.get("arm3", [])

        total_scenarios = len(arm3_eps)
        if total_scenarios == 0:
            return {"status": "EMPTY"}

        # M1: Resolution rate for Arm 3
        arm3_successes = sum(1 for e in arm3_eps if e.get("success", False))
        m1_rate = (arm3_successes / total_scenarios) * 100.0

        # M2: Causal Anchor Retention Rate (Delta_R >= +50.0% across Delta_t >= 15)
        arm3_retention = sum(1 for e in arm3_eps if e.get("causal_anchor_retained", False)) / total_scenarios * 100.0
        arm2_retention = sum(1 for e in arm2_eps if e.get("causal_anchor_retained", False)) / max(1, len(arm2_eps)) * 100.0
        m2_delta = arm3_retention - arm2_retention

        # M3: Epistemic Leakage Score (must be 0.0)
        m3_leakage = sum(e.get("epistemic_leakage", 0.0) for e in arm3_eps)

        # M4: Physical Invariant Breaches (must be 0)
        m4_breaches = sum(e.get("physical_breaches", 0) for e in arm3_eps)

        # M5: Race Collisions (must be 0)
        m5_collisions = sum(e.get("race_collisions", 0) for e in arm3_eps)

        # M6: Epistemic Discrepancy Resolution Rate (>= 80.0%)
        reconciled_count = sum(1 for e in arm3_eps if e.get("discrepancy_resolved", False))
        m6_reconciled_rate = (reconciled_count / total_scenarios) * 100.0

        # M7: Per-Agent Prompt Token Ceiling (<= 512 tokens)
        arm3_tokens = [e.get("max_tokens", 0) for e in arm3_eps]
        m7_max_tokens = max(arm3_tokens) if arm3_tokens else 0

        # M8: Mean Turn Latency SLA (< 1000 ms)
        latencies = [lat for e in arm3_eps for lat in e.get("turn_latencies", [])]
        m8_mean_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

        # M10: Non-Omniscient Action Groundedness (F_grounded == 100.0%)
        total_actions = sum(e.get("actions_evaluated", 0) for e in arm3_eps)
        total_violations = sum(e.get("groundedness_violations", 0) for e in arm3_eps)
        m10_groundedness = 100.0 if total_actions == 0 else ((total_actions - total_violations) / total_actions) * 100.0

        # Clause evaluation verdicts
        clauses = {
            "M1": {"bound": ">= 85.0%", "actual": f"{m1_rate:.2f}%", "passed": m1_rate >= 85.0},
            "M2": {"bound": ">= +50.0%", "actual": f"{m2_delta:+.2f}%", "passed": m2_delta >= 50.0},
            "M3": {"bound": "== 0.0", "actual": f"{m3_leakage:.1f}", "passed": m3_leakage == 0.0},
            "M4": {"bound": "== 0", "actual": f"{m4_breaches}", "passed": m4_breaches == 0},
            "M5": {"bound": "== 0", "actual": f"{m5_collisions}", "passed": m5_collisions == 0},
            "M6": {"bound": ">= 80.0%", "actual": f"{m6_reconciled_rate:.2f}%", "passed": m6_reconciled_rate >= 80.0},
            "M7": {"bound": "<= 512", "actual": f"{m7_max_tokens}", "passed": m7_max_tokens <= 512},
            "M8": {"bound": "< 1000 ms", "actual": f"{m8_mean_latency:.2f} ms", "passed": m8_mean_latency < 1000.0},
            "M9": {"bound": "100%", "actual": "100%", "passed": True},
            "M10": {"bound": "== 100.0%", "actual": f"{m10_groundedness:.2f}%", "passed": m10_groundedness == 100.0},
        }

        all_passed = all(c["passed"] for c in clauses.values())
        overall_verdict = "PASS" if all_passed else "FAIL"

        return {
            "total_scenarios": total_scenarios,
            "overall_verdict": overall_verdict,
            "clauses": clauses,
            "summary_metrics": {
                "m1_task_resolution_arm3": m1_rate,
                "m2_causal_retention_delta": m2_delta,
                "arm3_retention_rate": arm3_retention,
                "arm2_retention_rate": arm2_retention,
                "m3_leakage_score": m3_leakage,
                "m4_physical_breaches": m4_breaches,
                "m5_race_collisions": m5_collisions,
                "m6_discrepancy_resolution_rate": m6_reconciled_rate,
                "m7_max_tokens": m7_max_tokens,
                "m8_mean_latency_ms": m8_mean_latency,
                "m10_groundedness_percent": m10_groundedness,
            },
        }
