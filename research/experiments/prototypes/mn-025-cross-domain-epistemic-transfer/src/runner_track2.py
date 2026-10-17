"""Track 2 Runner: Real Model Inference on Qwen3.5-2B for Milestone MN-025."""

from __future__ import annotations

import json
import os
import sys
import time
import zipfile
from pathlib import Path

# Add prototype root to pythonpath
prototype_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(prototype_root))

from src.agent_worker import AgentWorker
from src.benchmark_scenarios import generate_benchmark_scenarios
from src.evaluator import Evaluator
from src.microworld_engine import MicroworldEngine


def run_track2_benchmark(endpoint_url: str = "http://127.0.0.1:18502") -> str:
    """Executes the entire N=60 scenario suite across 3 arms (180 episodes) on Track 2."""
    timestamp = int(time.time())
    run_dir = prototype_root / "runs" / f"run_{timestamp}_track2_qwen"
    logs_dir = run_dir / "audit_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    scenarios = generate_benchmark_scenarios()
    worker = AgentWorker(endpoint_url=endpoint_url)

    episode_logs = []
    print(f"Starting Track 2 Real Inference: {len(scenarios)} scenarios x 3 arms = {len(scenarios)*3} episodes.")
    print(f"Endpoint: {endpoint_url}")

    for arm in [1, 2, 3]:
        for scen in scenarios:
            is_regime_shift = (scen.trap_type == "IMMEDIATE_REGIME_SHIFT")
            engine = MicroworldEngine(stage=scen.stage, domain_id=scen.domain_id, is_regime_shift_scenario=is_regime_shift)

            # Stage 3 Dynamic entity emergence setup
            if scen.stage == 3:
                is_phantom = (scen.trap_type == "IMMEDIATE_PHANTOM_ENTITY")
                is_trojan = (scen.trap_type == "LATENT_TROJAN_SLEEPER")
                engine.stochastic.register_dynamic_entity(
                    "emergency_battery_3", "POWER_REDUNDANCY", 50.0, is_phantom=is_phantom, is_trojan=is_trojan
                )

            # Stage-specific trap injections
            if scen.trap_type == "LATENT_CAVITATION":
                engine.stochastic.latent_state.cavitation_damage = 0.25
            elif scen.trap_type == "LATENT_PHASE_DRIFT":
                engine.stochastic.latent_state.harmonic_phase_drift = 0.25
            elif scen.trap_type == "LATENT_UNEXPRESSED_ASSUMPTION":
                engine.stochastic.latent_state.unexpressed_assumption_conflict = True
            elif scen.trap_type == "LATENT_MAINTENANCE_DEBT":
                engine.stochastic.latent_state.filter_particulate_ratio = 0.35
            elif scen.trap_type == "LATENT_FATIGUE_COLLAPSE":
                engine.stochastic.latent_state.structural_fatigue_microfracture = 0.40

            tokens_history = []
            latency_history = []
            episode_history = []

            for turn in range(1, 15):
                fact_card, tokens = engine.render_fact_card(target_arm=arm)
                tokens_history.append(tokens)

                chatml_prompt = worker.format_chatml_prompt(fact_card, role_name=f"agent_arm_{arm}")
                action, latency_ms = worker.query_local_model(chatml_prompt)
                latency_history.append(latency_ms)

                # Robust action fallback / cleaning
                clean_action = action.strip().split("\n")[0].strip()
                if not clean_action.startswith("ACTION:"):
                    clean_action = f"ACTION: {clean_action}"

                success, msg = engine.step(clean_action)
                episode_history.append({
                    "turn": turn,
                    "action": clean_action,
                    "success": success,
                    "message": msg,
                    "tokens": tokens,
                    "latency_ms": latency_ms,
                })

                if engine.is_resolved or engine.is_failed:
                    break

            ep_log = {
                "scenario_id": scen.scenario_id,
                "stage": scen.stage,
                "domain_id": scen.domain_id,
                "arm": arm,
                "is_trap": scen.is_trap,
                "trap_type": scen.trap_type,
                "is_resolved": engine.is_resolved,
                "is_failed": engine.is_failed,
                "failure_reason": engine.failure_reason,
                "total_ticks": engine.current_tick,
                "tokens_history": tokens_history,
                "latency_ms_history": latency_history,
                "physical_breach_count": engine.physical_breach_count,
                "concurrency_collision_count": engine.concurrency_collision_count,
                "negative_transfer_breach_count": engine.negative_transfer_breach_count,
                "demotion_count": engine.demotion_count,
                "history": episode_history,
            }

            log_file = logs_dir / f"{scen.scenario_id}_arm{arm}.json"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(ep_log, f, indent=2)

            episode_logs.append(ep_log)

    eval_result = Evaluator.evaluate_run(episode_logs)
    summary_file = run_dir / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(eval_result, f, indent=2)

    # Package logs into audit_logs.zip and remove loose files
    zip_path = run_dir / "audit_logs.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for json_file in logs_dir.glob("*.json"):
            zf.write(json_file, arcname=json_file.name)
            os.remove(json_file)
    os.rmdir(logs_dir)

    print(f"Track 2 Complete! Verdict: {eval_result['overall_verdict']}")
    print(f"Summary: {summary_file}")
    print(f"Audit Archive: {zip_path}")
    return str(run_dir)


if __name__ == "__main__":
    run_track2_benchmark()
