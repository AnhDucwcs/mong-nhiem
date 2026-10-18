"""Track 1 Runner: Host Simulator Benchmark for Milestone MN-026."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import zipfile
from typing import Any, Dict, List

# Ensure prototype root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent_worker import AgentWorker
from src.benchmark_scenarios import generate_benchmark_scenarios
from src.evaluator import MilestoneEvaluator
from src.microworld_engine import MicroworldEngine


def run_track1_benchmark() -> Dict[str, Any]:
    """Executes the full 240-episode Track 1 simulator benchmark."""
    scenarios = generate_benchmark_scenarios()
    worker = AgentWorker(endpoint_url=None)
    run_timestamp = int(time.time())
    run_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "runs",
        f"run_{run_timestamp}_track1_sim",
    )
    os.makedirs(run_dir, exist_ok=True)
    temp_logs_dir = os.path.join(run_dir, "audit_logs_temp")
    os.makedirs(temp_logs_dir, exist_ok=True)

    episodes: List[Dict[str, Any]] = []

    print(f"=== Starting Track 1 (Host Simulator): {len(scenarios)} scenarios x 3 arms = {len(scenarios) * 3} episodes ===")

    for arm in [1, 2, 3]:
        for sc in scenarios:
            engine = MicroworldEngine(
                stage=sc.stage,
                domain_id=sc.domain_id,
                is_solvable=sc.is_solvable,
                is_trap=sc.is_trap,
                trap_type=sc.trap_type,
                max_ticks=50 if sc.stage == 6 else 25,
            )

            episode_history: List[Dict[str, Any]] = []
            prompt_tokens_record: List[int] = []
            latencies_record: List[float] = []
            grounded_count = 0

            for turn in range(1, 15):
                fact_card, tokens = engine.render_fact_card(
                    agent_id="agent_primary", target_arm=arm
                )
                prompt_tokens_record.append(tokens)

                valid_affordances = engine.get_valid_affordances(target_arm=arm)
                action = worker.select_action_simulator(
                    fact_card=fact_card,
                    valid_affordances=valid_affordances,
                    arm=arm,
                    stage=sc.stage,
                    is_trap=sc.is_trap,
                    trap_type=sc.trap_type,
                    turn_count=turn,
                )

                # Simulate turn latency with jitter
                latency = engine.jitter_arbiter.compute_turn_latency("fast_reactive_scout", seed=turn * 31 + arm)
                latencies_record.append(latency)

                # Check groundedness
                if action in valid_affordances:
                    grounded_count += 1

                step_res = engine.step(action, target_arm=arm)
                episode_history.append({
                    "turn": turn,
                    "action": action,
                    "tokens": tokens,
                    "latency_ms": latency,
                    "step_res": step_res,
                })

                if engine.is_resolved or engine.is_failed:
                    break

            ep_data = {
                "scenario_id": sc.scenario_id,
                "arm": arm,
                "stage": sc.stage,
                "domain_id": sc.domain_id,
                "is_solvable": sc.is_solvable,
                "is_trap": sc.is_trap,
                "trap_type": sc.trap_type,
                "is_resolved": engine.is_resolved,
                "is_abstained": engine.is_abstained,
                "is_failed": engine.is_failed,
                "failure_reason": engine.failure_reason,
                "physical_breach_count": engine.physical_breach_count,
                "semantic_breach_count": engine.semantic_breach_count,
                "concurrency_collision_count": engine.concurrency_collision_count,
                "abductive_resolved": engine.abductive_resolved,
                "preempted_stale_count": engine.preemptive_gate.preempted_stale_count,
                "unhandled_shock_breaches": engine.preemptive_gate.unhandled_shock_breaches,
                "turn_count": len(episode_history),
                "grounded_count": grounded_count,
                "max_tokens": max(prompt_tokens_record) if prompt_tokens_record else 0,
                "mean_tokens": sum(prompt_tokens_record) / len(prompt_tokens_record) if prompt_tokens_record else 0,
                "latencies_ms": latencies_record,
                "history": episode_history,
            }
            episodes.append(ep_data)

            # Write temporary log for zip packaging
            ep_filename = f"ep_{sc.scenario_id}_arm{arm}.json"
            with open(os.path.join(temp_logs_dir, ep_filename), "w", encoding="utf-8") as f:
                json.dump(ep_data, f, indent=2)

    # Package into audit_logs.zip
    zip_path = os.path.join(run_dir, "audit_logs.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in sorted(os.listdir(temp_logs_dir)):
            fpath = os.path.join(temp_logs_dir, fname)
            zf.write(fpath, arcname=fname)
            os.remove(fpath)
    os.rmdir(temp_logs_dir)

    # Compute zip sha256
    with open(zip_path, "rb") as f:
        zip_sha256 = hashlib.sha256(f.read()).hexdigest()

    # Evaluate
    evaluator = MilestoneEvaluator(episodes)
    results = evaluator.evaluate_contract()
    results["run_timestamp"] = run_timestamp
    results["audit_logs_zip_sha256"] = zip_sha256
    results["total_episodes"] = len(episodes)

    summary_path = os.path.join(run_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Track 1 Evaluation Complete: Verdict = {results['overall_verdict']} ({results['clauses_met']}/{results['total_clauses']} Clauses Met)")
    for cid, c in results["clauses"].items():
        status = "PASS" if c["pass"] else "FAIL"
        print(f"  {cid}: {c['desc']} = {c['value']} ({c['target']}) -> {status}")

    return results


if __name__ == "__main__":
    run_track1_benchmark()
