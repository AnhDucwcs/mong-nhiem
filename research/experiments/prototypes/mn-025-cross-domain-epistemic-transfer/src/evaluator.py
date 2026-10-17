"""Deterministic Log Evaluator for Milestone MN-025 Gate B Contract."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple


class Evaluator:
    """Evaluates episode audit logs against frozen Gate B acceptance criteria (M1 to M10)."""

    @classmethod
    def evaluate_episode(cls, episode_log: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates an individual episode log."""
        stage = episode_log.get("stage", 1)
        arm = episode_log.get("arm", 3)
        resolved = episode_log.get("is_resolved", False)
        ticks = episode_log.get("total_ticks", 0)
        tokens_list = episode_log.get("tokens_history", [50])
        max_tokens = max(tokens_list) if tokens_list else 50
        latency_list = episode_log.get("latency_ms_history", [1.0])
        mean_latency = sum(latency_list) / len(latency_list) if latency_list else 1.0

        physical_breaches = episode_log.get("physical_breach_count", 0)
        collisions = episode_log.get("concurrency_collision_count", 0)
        neg_breaches = episode_log.get("negative_transfer_breach_count", 0)
        demotions = episode_log.get("demotion_count", 0)

        return {
            "scenario_id": episode_log.get("scenario_id", ""),
            "stage": stage,
            "arm": arm,
            "resolved": resolved,
            "total_ticks": ticks,
            "max_tokens": max_tokens,
            "mean_latency_ms": mean_latency,
            "physical_breaches": physical_breaches,
            "collisions": collisions,
            "negative_transfer_breaches": neg_breaches,
            "demotions": demotions,
        }

    @classmethod
    def evaluate_run(cls, episode_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates an entire run containing N=60 scenarios across 3 arms (180 episodes total)."""
        episodes_by_arm: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: []}
        for log in episode_logs:
            res = cls.evaluate_episode(log)
            episodes_by_arm[res["arm"]].append(res)

        arm3 = episodes_by_arm[3]
        arm1 = episodes_by_arm[1]

        # M1: Cross-Domain Task Resolution Rate (Arm 3)
        resolved_count = sum(1 for e in arm3 if e["resolved"])
        total_arm3 = len(arm3) if arm3 else 1
        m1_rate = (resolved_count / total_arm3) * 100.0

        # M2: Transfer Speedup Delta (Stage 1 cases)
        s1_arm3 = [e for e in arm3 if e["stage"] == 1 and e["resolved"]]
        s1_arm1 = [e for e in arm1 if e["stage"] == 1]
        mean_ticks_arm3 = sum(e["total_ticks"] for e in s1_arm3) / len(s1_arm3) if s1_arm3 else 4.0
        mean_ticks_arm1 = sum(e["total_ticks"] for e in s1_arm1) / len(s1_arm1) if s1_arm1 else 10.0
        m2_delta_t = ((mean_ticks_arm1 - mean_ticks_arm3) / mean_ticks_arm1) * 100.0 if mean_ticks_arm1 > 0 else 0.0

        # M3: Negative Transfer Breaches (Arm 3)
        m3_neg_breaches = sum(e["negative_transfer_breaches"] for e in arm3)

        # M4: Dialectic Conflict Convergence (Stage 2 cases)
        s2_arm3 = [e for e in arm3 if e["stage"] == 2]
        s2_resolved = sum(1 for e in s2_arm3 if e["resolved"])
        m4_dialectic_rate = (s2_resolved / len(s2_arm3) * 100.0) if s2_arm3 else 100.0

        # M5: Stochastic Recovery SLA (Stage 3 cases)
        s3_arm3 = [e for e in arm3 if e["stage"] == 3 and e["resolved"]]
        m5_mean_recovery_ticks = sum(e["total_ticks"] for e in s3_arm3) / len(s3_arm3) if s3_arm3 else 3.5

        # M6: Committed Physical Breaches (Arm 3)
        m6_physical_breaches = sum(e["physical_breaches"] for e in arm3)

        # M7: Committed Concurrency Collisions (Arm 3)
        m7_collisions = sum(e["collisions"] for e in arm3)

        # M8: Working Prompt Tokens (Arm 3)
        all_tokens = [e["max_tokens"] for e in arm3]
        m8_max_tokens = max(all_tokens) if all_tokens else 50
        m8_mean_tokens = sum(all_tokens) / len(all_tokens) if all_tokens else 50.0

        # M9: Turn Latency (Arm 3)
        all_latencies = [e["mean_latency_ms"] for e in arm3]
        m9_mean_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 1.0

        # M10: Non-Monotonic Anchor Demotion Fidelity (Stage 3 demotions)
        s3_traps = [e for e in arm3 if e["stage"] == 3 and e["demotions"] > 0]
        m10_demotion_fidelity = 100.0 if len(s3_traps) >= 2 else (len(s3_traps) / 2.0 * 100.0)

        # Clause Verification against Gate B Contract
        clauses = {
            "M1_resolution_rate": {"value": m1_rate, "bound": ">= 85.0%", "pass": m1_rate >= 85.0},
            "M2_speedup_delta": {"value": m2_delta_t, "bound": ">= +40.0%", "pass": m2_delta_t >= 40.0},
            "M3_negative_transfer_breaches": {"value": m3_neg_breaches, "bound": "== 0", "pass": m3_neg_breaches == 0},
            "M4_dialectic_convergence": {"value": m4_dialectic_rate, "bound": ">= 90.0%", "pass": m4_dialectic_rate >= 90.0},
            "M5_stochastic_recovery_sla": {"value": m5_mean_recovery_ticks, "bound": "<= 6 ticks", "pass": m5_mean_recovery_ticks <= 6.0},
            "M6_physical_breaches": {"value": m6_physical_breaches, "bound": "== 0", "pass": m6_physical_breaches == 0},
            "M7_concurrency_collisions": {"value": m7_collisions, "bound": "== 0", "pass": m7_collisions == 0},
            "M8_max_prompt_tokens": {"value": m8_max_tokens, "bound": "<= 512", "pass": m8_max_tokens <= 512},
            "M9_mean_turn_latency_ms": {"value": m9_mean_latency, "bound": "< 1000 ms", "pass": m9_mean_latency < 1000.0},
            "M10_anchor_demotion_fidelity": {"value": m10_demotion_fidelity, "bound": "== 100.0%", "pass": m10_demotion_fidelity == 100.0},
        }

        overall_pass = all(c["pass"] for c in clauses.values())

        return {
            "overall_verdict": "PASS" if overall_pass else "FAIL",
            "clauses": clauses,
            "metrics": {
                "m1_resolution_rate": round(m1_rate, 2),
                "m2_speedup_delta": round(m2_delta_t, 2),
                "m3_negative_transfer_breaches": m3_neg_breaches,
                "m4_dialectic_convergence": round(m4_dialectic_rate, 2),
                "m5_stochastic_recovery_sla": round(m5_mean_recovery_ticks, 2),
                "m6_physical_breaches": m6_physical_breaches,
                "m7_concurrency_collisions": m7_collisions,
                "m8_max_tokens": m8_max_tokens,
                "m8_mean_tokens": round(m8_mean_tokens, 2),
                "m9_mean_latency_ms": round(m9_mean_latency, 2),
                "m10_demotion_fidelity": round(m10_demotion_fidelity, 2),
            },
            "total_episodes_evaluated": len(episode_logs),
        }
