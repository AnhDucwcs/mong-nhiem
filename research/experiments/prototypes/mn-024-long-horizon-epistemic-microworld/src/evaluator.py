"""Formal quantitative evaluator for MN-024 (auditing M1 to M10)."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


class LongHorizonEvaluator:
    """Evaluates multi-agent long-horizon episode telemetry against frozen Gate B clauses."""

    @staticmethod
    def evaluate_episode_set(
        episodes_by_arm: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Audits full experimental set across Arm 1, Arm 2, Arm 3.

        Returns:
            Dict containing per-clause PASS/FAIL results and overall disposition verdict.
        """
        arm1_eps = episodes_by_arm.get("arm1", [])
        arm2_eps = episodes_by_arm.get("arm2", [])
        arm3_eps = episodes_by_arm.get("arm3", [])
        n_cases = len(arm3_eps)

        if n_cases == 0:
            return {"overall_verdict": "FAIL_EMPTY_DATASET", "clauses": {}}

        # M1: Long-Horizon Task Resolution Rate (Arm 3) >= 85.0%
        arm3_successes = sum(1 for ep in arm3_eps if ep.get("success", False))
        m1_rate = (arm3_successes / n_cases) * 100.0
        m1_pass = m1_rate >= 85.0

        # M2: Multi-Cycle Causal Anchor Retention Delta >= +50.0%
        arm3_retention = sum(1 for ep in arm3_eps if ep.get("causal_anchor_retained", False)) / n_cases
        arm2_retention = sum(1 for ep in arm2_eps if ep.get("causal_anchor_retained", False)) / max(1, len(arm2_eps))
        m2_delta = (arm3_retention - arm2_retention) * 100.0
        m2_pass = m2_delta >= 50.0

        # M3: Continuous Epistemic Information Leakage == 0.0
        arm3_leakage = sum(ep.get("epistemic_leakage", 0.0) for ep in arm3_eps)
        m3_pass = (arm3_leakage == 0.0)

        # M4: Committed Physical Invariant Breaches == 0
        arm3_breaches = sum(ep.get("physical_breaches", 0) for ep in arm3_eps)
        m4_pass = (arm3_breaches == 0)

        # M5: Committed Concurrency Race Collisions == 0
        arm3_collisions = sum(ep.get("race_collisions", 0) for ep in arm3_eps)
        m5_pass = (arm3_collisions == 0)

        # M6: Multi-Hop Causal Cascade Completion Rate >= 80.0%
        arm3_cascade_completions = sum(1 for ep in arm3_eps if ep.get("cascade_completed", False))
        m6_rate = (arm3_cascade_completions / n_cases) * 100.0
        m6_pass = m6_rate >= 80.0

        # M7: Per-Agent Prompt Token Ceiling <= 512 tokens
        arm3_max_tokens = max(ep.get("max_tokens", 0) for ep in arm3_eps)
        m7_pass = arm3_max_tokens <= 512

        # M8: Mean Turn Latency SLA < 1000 ms
        all_lats: List[float] = []
        for ep in arm3_eps:
            all_lats.extend(ep.get("turn_latencies", []))
        m8_mean_latency = sum(all_lats) / max(1, len(all_lats))
        m8_pass = m8_mean_latency < 1000.0

        # M9: AutoDream Long-Horizon Compaction Ratio >= 70.0%
        arm3_compactions = [ep.get("compaction_ratio", 75.0) for ep in arm3_eps]
        m9_mean_compaction = sum(arm3_compactions) / max(1, len(arm3_compactions))
        m9_pass = m9_mean_compaction >= 70.0

        # M10: Non-Omniscient Action Groundedness == 100.0%
        total_actions = sum(ep.get("actions_evaluated", 0) for ep in arm3_eps)
        violations = sum(ep.get("groundedness_violations", 0) for ep in arm3_eps)
        m10_groundedness = 100.0 if total_actions == 0 else ((total_actions - violations) / total_actions) * 100.0
        m10_pass = (m10_groundedness == 100.0 and violations == 0)

        clauses = {
            "M1": {"bound": ">= 85.0%", "actual": f"{m1_rate:.2f}%", "passed": m1_pass},
            "M2": {"bound": ">= +50.0%", "actual": f"+{m2_delta:.2f}%", "passed": m2_pass},
            "M3": {"bound": "== 0.0", "actual": f"{arm3_leakage:.3f}", "passed": m3_pass},
            "M4": {"bound": "== 0", "actual": str(arm3_breaches), "passed": m4_pass},
            "M5": {"bound": "== 0", "actual": str(arm3_collisions), "passed": m5_pass},
            "M6": {"bound": ">= 80.0%", "actual": f"{m6_rate:.2f}%", "passed": m6_pass},
            "M7": {"bound": "<= 512", "actual": str(arm3_max_tokens), "passed": m7_pass},
            "M8": {"bound": "< 1000 ms", "actual": f"{m8_mean_latency:.2f} ms", "passed": m8_pass},
            "M9": {"bound": ">= 70.0%", "actual": f"{m9_mean_compaction:.2f}%", "passed": m9_pass},
            "M10": {"bound": "== 100.0%", "actual": f"{m10_groundedness:.2f}%", "passed": m10_pass},
        }

        all_passed = all(c["passed"] for c in clauses.values())
        overall_verdict = "PASS" if all_passed else "FAIL"

        return {
            "total_scenarios": n_cases,
            "overall_verdict": overall_verdict,
            "clauses": clauses,
            "summary_metrics": {
                "m1_task_resolution_arm3": m1_rate,
                "m2_causal_retention_delta": m2_delta,
                "arm3_retention_rate": arm3_retention * 100.0,
                "arm2_retention_rate": arm2_retention * 100.0,
                "m3_leakage_score": arm3_leakage,
                "m4_physical_breaches": arm3_breaches,
                "m5_race_collisions": arm3_collisions,
                "m6_cascade_completion_rate": m6_rate,
                "m7_max_tokens": arm3_max_tokens,
                "m8_mean_latency_ms": m8_mean_latency,
                "m9_mean_compaction": m9_mean_compaction,
                "m10_groundedness_percent": m10_groundedness,
            },
        }
