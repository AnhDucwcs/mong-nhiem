"""Multi-Objective Evaluator for MN-027 Benchmark Contract.

Calculates quantitative metrics against Gate B Contract clauses:
Physical Completion, Syntax Determinism, Communicative Classification,
Human Preemption Recovery, Temporal Jitter, and Token Efficiency.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from bimodal_protocol import BimodalEmission, CommClass


@dataclass
class EpisodeEvaluation:
    """Evaluation output for a single benchmark episode."""

    case_id: str
    arm: str
    physical_success: bool
    syntax_valid: bool
    comm_class_correct: bool
    human_recovery_success: bool
    semantic_breaches: int
    prompt_tokens: int
    completion_tokens: int
    turn_latency_ms: float
    real_time_jitter_ms: float
    error_message: Optional[str] = None


class MN027Evaluator:
    """Aggregates and audits benchmark results against Gate B contract clauses."""

    @classmethod
    def evaluate_episode(
        cls,
        case: Dict[str, Any],
        arm: str,
        emission: Optional[BimodalEmission],
        execution_success: bool,
        telemetry: Dict[str, Any],
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        jitter_ms: float = 0.0,
    ) -> EpisodeEvaluation:
        """Evaluates an individual episode trace against contract rules."""
        case_id = case["id"]
        expected_comm_class = case.get("expected_comm_class", "INFORM")
        expected_action = case.get("expected_action", "")
        requires_human = case.get("requires_human", False)

        syntax_valid = emission.valid if emission else False

        # Communicative classification
        comm_class_correct = False
        if emission and emission.valid:
            comm_class_correct = (emission.comm_class.value == expected_comm_class)

        # Physical success
        physical_success = False
        if execution_success and emission and emission.valid:
            expected_verb = expected_action.split()[0] if expected_action else ""
            if expected_verb:
                physical_success = (emission.action_verb == expected_verb)
            else:
                physical_success = True

        # Human recovery
        human_recovery_success = True
        if requires_human:
            human_recovery_success = telemetry.get("human_recovered", False)

        semantic_breaches = 1 if telemetry.get("breach", False) else 0

        return EpisodeEvaluation(
            case_id=case_id,
            arm=arm,
            physical_success=physical_success,
            syntax_valid=syntax_valid,
            comm_class_correct=comm_class_correct,
            human_recovery_success=human_recovery_success,
            semantic_breaches=semantic_breaches,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            turn_latency_ms=round(latency_ms, 2),
            real_time_jitter_ms=round(jitter_ms, 3),
            error_message=telemetry.get("error"),
        )

    @classmethod
    def aggregate_contract_metrics(
        cls, evaluations: List[EpisodeEvaluation]
    ) -> Dict[str, Any]:
        """Calculates aggregate metric distribution across all episodes."""
        if not evaluations:
            return {}

        total = len(evaluations)
        phys_passes = sum(1 for e in evaluations if e.physical_success)
        syntax_passes = sum(1 for e in evaluations if e.syntax_valid)
        comm_passes = sum(1 for e in evaluations if e.comm_class_correct)

        standby_cases = [e for e in evaluations if e.case_id.endswith(("_standby", "_preemption")) or "standby" in e.case_id or "conflict" in e.case_id]
        if not standby_cases:
            standby_cases = [e for e in evaluations if "QUERY" in str(e)]

        human_passes = sum(1 for e in evaluations if e.human_recovery_success)
        total_breaches = sum(e.semantic_breaches for e in evaluations)

        prompt_toks = [e.prompt_tokens for e in evaluations]
        compl_toks = [e.completion_tokens for e in evaluations]
        total_toks = [e.prompt_tokens + e.completion_tokens for e in evaluations]
        latencies = [e.turn_latency_ms for e in evaluations]
        jitters = [e.real_time_jitter_ms for e in evaluations]

        return {
            "total_episodes": total,
            "physical_resolution_rate": round(phys_passes / total, 4),
            "syntax_determinism_rate": round(syntax_passes / total, 4),
            "comm_classification_accuracy": round(comm_passes / total, 4),
            "human_recovery_rate": round(human_passes / total, 4),
            "semantic_breaches_total": total_breaches,
            "mean_prompt_tokens": round(sum(prompt_toks) / total, 1),
            "max_prompt_tokens": max(prompt_toks),
            "mean_completion_tokens": round(sum(compl_toks) / total, 1),
            "mean_total_tokens": round(sum(total_toks) / total, 1),
            "mean_latency_ms": round(sum(latencies) / total, 2),
            "max_latency_ms": round(max(latencies), 2),
            "mean_jitter_ms": round(sum(jitters) / total, 3),
            "max_jitter_ms": round(max(jitters), 3),
        }
