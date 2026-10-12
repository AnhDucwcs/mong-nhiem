import json
import sys
from pathlib import Path

# Add prototype root to sys.path
PROTOTYPE_ROOT = Path(__file__).resolve().parent.parent
if str(PROTOTYPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_ROOT))

from benchmarks.corpus_v1_swarm import get_corpus
from src.agent_worker import AgentWorker
from src.orchestrator_swarm import SwarmOrchestrator


TARGET_IDS = [
    # 8 previously failed cases:
    "grid_010",
    "grid_021",
    "cluster_005",
    "cluster_006",
    "cluster_011",
    "cluster_019",
    "cluster_021",
    "cluster_025",
    # Representative baseline cases:
    "grid_001",
    "fleet_001",
    "cluster_001",
]


def run_targeted_eval(server_port: int = 18502):
    full_corpus = get_corpus()
    corpus_map = {s.scenario_id: s for s in full_corpus}

    selected = [corpus_map[sid] for sid in TARGET_IDS if sid in corpus_map]
    print(f"=== Running Targeted Patch Benchmark on {len(selected)} scenarios ===")
    print("M=5 homogeneous Qwen3.5-2B on port", server_port)

    results = []
    for idx, scenario in enumerate(selected, 1):
        workers = {
            f"agent_{i+1}": AgentWorker(
                agent_id=f"agent_{i+1}",
                assigned_goal=scenario.agent_goals.get(f"agent_{i+1}", ""),
                is_mock=False,
                server_port=server_port,
                model_name="Qwen3.5-2B-Q4_K_M",
            )
            for i in range(5)
        }

        orchestrator = SwarmOrchestrator(
            scenario=scenario,
            arm="arm3",
            min_latency=0,
            max_latency=5,
            workers=workers,
            seed=400 + idx,
        )

        res = orchestrator.run_episode()
        results.append(res)

        status_str = "PASS" if res["success"] else "FAIL"
        print(
            f"[{idx:02d}/{len(selected):02d}] {scenario.scenario_id:<12} | "
            f"{status_str:<4} | Ticks: {res['ticks_used']:02d}/{scenario.max_ticks:02d} | "
            f"Breaches: {res['physical_breaches']} | Collisions: {res['race_collisions']} | "
            f"MaxTok: {res['max_tokens']} | Latency: {res['mean_latency_ms']:.1f}ms"
        )

    passes = sum(1 for r in results if r["success"])
    total = len(results)
    print("\n" + "=" * 60)
    print(f"Targeted Patch Result: {passes}/{total} PASS ({passes/total*100:.1f}%)")
    failed_prior = [r for r in results if r["scenario_id"] in TARGET_IDS[:8]]
    failed_prior_passes = sum(1 for r in failed_prior if r["success"])
    print(f"Previously Failing Subset: {failed_prior_passes}/8 PASS ({failed_prior_passes/8*100:.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    run_targeted_eval()
