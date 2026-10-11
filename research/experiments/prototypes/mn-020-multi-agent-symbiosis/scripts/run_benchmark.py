"""Benchmark Execution Runner for Milestone MN-020 with Automated Zip Packaging."""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path

# Add src and benchmarks to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks"))

from corpus_v1 import generate_benchmark_corpus
from orchestrator_symbiosis import SymbiosisOrchestrator
from pack_evidence_zip import EvidenceZipPacker


def run_benchmark_suite(
    track: int = 1,
    limit: int = 60,
    port: int = 18502,
    model_id: str = "Qwen3.5-2B-Q4_K_M",
    output_base: Optional[Path] = None,
) -> Path:
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    track_str = "track1-sim" if track == 1 else f"track2-{model_id}"
    run_id = f"mn020-run-{timestamp}-{track_str}"

    base_dir = output_base or (Path(__file__).parent.parent / "runs")
    run_dir = base_dir / run_id
    audit_dir = run_dir / "audit_logs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Starting MN-020 Multi-Agent Benchmark Suite ===")
    print(f"Run ID: {run_id} | Track: {track} | Limit: {limit} cases")
    print(f"Audit log output: {audit_dir}\n")

    corpus = generate_benchmark_corpus(n_per_domain=max(1, limit // 3))[:limit]

    arms = [
        "arm1_flat",
        "arm2_independent_control",
        "arm3_host_symbiosis",
    ]

    results_by_arm: Dict[str, Any] = {
        arm: {
            "successes": 0,
            "total": 0,
            "success_rate": 0.0,
            "committed_races": 0,
            "deadlocks": 0,
            "max_tokens": 0,
            "mean_tokens": 0.0,
        }
        for arm in arms
    }

    start_time = time.time()

    for idx, case in enumerate(corpus, 1):
        case_id = case["case_id"]
        domain = case["domain"]
        print(f"[{idx}/{len(corpus)}] Evaluating {case_id} ({domain})...")

        for arm in arms:
            orch = SymbiosisOrchestrator(
                domain=domain,
                initial_entities=case["initial_entities"],
                subgoals_agent1=case["subgoals_agent1"],
                subgoals_agent2=case["subgoals_agent2"],
                arm=arm,
                port=port,
                model_id=model_id,
                track=track,
            )
            res = orch.run_episode(case_id=case_id)

            # Record arm results
            arm_data = results_by_arm[arm]
            arm_data["total"] += 1
            if res["status"] == "PASS":
                arm_data["successes"] += 1
            arm_data["committed_races"] += res["committed_race_violations"]
            arm_data["deadlocks"] += res["deadlock_cycles_detected"]
            arm_data["max_tokens"] = max(arm_data["max_tokens"], res["max_prompt_tokens"])

            # Save individual audit trace
            log_file = audit_dir / f"{case_id}_{arm}_audit.json"
            log_file.write_text(json.dumps(res, indent=2), encoding="utf-8")

    duration = time.time() - start_time

    # Calculate final rates
    for arm in arms:
        data = results_by_arm[arm]
        data["success_rate"] = round((data["successes"] / max(data["total"], 1)) * 100.0, 1)

    print(f"\nBenchmark completed in {duration:.1f}s.")
    print("=== SUMMARY METRICS ===")
    for arm, d in results_by_arm.items():
        print(f"[{arm}] Success: {d['successes']}/{d['total']} ({d['success_rate']}%) | Races: {d['committed_races']} | Deadlocks: {d['deadlocks']} | Max Tok: {d['max_tokens']}")

    # -------------------------------------------------------------------------
    # AUTOMATED ZIP PACKAGING PROTOCOL
    # -------------------------------------------------------------------------
    print("\n[Audit Protocol] Packaging audit logs into audit_logs.zip...")
    zip_summary = EvidenceZipPacker.pack_audit_logs(run_dir=run_dir, remove_loose_files=True)
    print(f"Archive created: {zip_summary['archive_path']}")
    print(f"Files packed: {zip_summary['file_count']} | Raw: {zip_summary['raw_bytes']} B -> Compressed: {zip_summary['compressed_bytes']} B (Ratio: {zip_summary['compression_ratio']*100:.1f}%)")
    print(f"SHA-256 Fingerprint: {zip_summary['sha256']}")

    # Determine Verdict against Gate B
    arm3_rate = results_by_arm["arm3_host_symbiosis"]["success_rate"]
    arm2_rate = results_by_arm["arm2_independent_control"]["success_rate"]
    races = results_by_arm["arm3_host_symbiosis"]["committed_races"]
    deadlocks = results_by_arm["arm3_host_symbiosis"]["deadlocks"]

    verdict = "PASS" if (arm3_rate >= 85.0 and (arm3_rate - arm2_rate) >= 40.0 and races == 0 and deadlocks == 0) else "FAIL"

    run_info = {
        "run_id": run_id,
        "milestone": "mn-020-multi-agent-symbiosis",
        "track": track,
        "timestamp": timestamp,
        "total_cases": len(corpus),
        "model_id": model_id,
        "duration_seconds": round(duration, 2),
        "arms_evaluated": results_by_arm,
        "audit_logs_archive_sha256": zip_summary["sha256"],
        "overall_verdict": verdict,
    }

    run_info_file = run_dir / "run_info.json"
    run_info_file.write_text(json.dumps(run_info, indent=2), encoding="utf-8")
    print(f"\nRun info written to: {run_info_file}")
    print(f"Overall Gate B Verdict: {verdict}\n")

    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MN-020 Multi-Agent Benchmark Runner")
    parser.add_argument("--track", type=int, default=1, choices=[1, 2], help="Evaluation Track (1: Simulator, 2: LLM API)")
    parser.add_argument("--limit", type=int, default=60, help="Number of benchmark cases to evaluate")
    parser.add_argument("--port", type=int, default=18502, help="Local llama-server HTTP port")
    parser.add_argument("--model-id", type=str, default="Qwen3.5-2B-Q4_K_M", help="Model identifier string")

    args = parser.parse_args()
    run_benchmark_suite(
        track=args.track,
        limit=args.limit,
        port=args.port,
        model_id=args.model_id,
    )
