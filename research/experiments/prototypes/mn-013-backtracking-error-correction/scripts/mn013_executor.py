"""Execution and verification runner for MN-013 Gate C.

Evaluates 60 stateful multi-turn cases across 3 domains comparing 4 experimental arms:
- Arm 1: Forward-Only Baseline (no rollback, no rewind)
- Arm 2: Naive History Accumulation (errors appended to prompt context)
- Arm 3: Context Rewind Only (state rolled back, context rewound, NO negative mask)
- Arm 4: Full MN-013 (Memento rollback + Context rewind + Negative mask + Phase gate)

Supports Dual-Track Execution:
- Track 1 (--track 1): Deterministic model simulation for exhaustive CI unit & invariant testing.
- Track 2 (--track 2): Real model execution via llama-server / llama-cli using Qwen3.5-2B-Q4_K_M.gguf.

Supports Ablation Slices:
- --ablation-slice (default for Arms 2 & 3 on Track 2): 6 representative trap cases (2 per domain).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

PROTOTYPE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROTOTYPE_ROOT / "scripts"
SRC_DIR = PROTOTYPE_ROOT / "src"
DEFINITION_DIR = PROTOTYPE_ROOT / "definition"
CASES_FILE = DEFINITION_DIR / "corpus-v1" / "cases.jsonl"
RUNS_DIR = PROTOTYPE_ROOT / "runs"
REPORTS_DIR = PROTOTYPE_ROOT / "reports"

RUNS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

REPO_ROOT = Path(__file__).resolve().parents[5]
CORE_SRC = REPO_ROOT / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from coordinator import BacktrackingCoordinator, CoordinatorResult
from mong_nhiem.context import ContextPacker
from protocol import parse_action

LLAMA_TOKENIZE = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-tokenize.exe")
LLAMA_CLI = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-cli.exe")
SERVER_BIN = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")
DEFAULT_MODEL_GGUF = REPO_ROOT / "artifacts" / "models" / "mn-002" / "Qwen3.5-2B-Q4_K_M.gguf"

ABLATION_SLICE_CASE_IDS = {
    "mn013-case-0011", "mn013-case-0012",  # Domain A: AST trap
    "mn013-case-0031", "mn013-case-0032",  # Domain B: Ledger trap
    "mn013-case-0051", "mn013-case-0052",  # Domain C: Registry trap
}


def compute_freeze_manifest(stage: str = "pre") -> Path:
    """Compute and write cryptographic SHA-256 manifest for pre-run or post-run stage."""
    manifest_data: Dict[str, Any] = {
        "milestone": "MN-013",
        "stage": stage,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "files": {},
    }

    if stage == "pre":
        target_files = [
            CASES_FILE,
            DEFINITION_DIR / "generate_corpus.py",
            DEFINITION_DIR / "corpus-v1" / "manifest.json",
            SCRIPTS_DIR / "mn013_executor.py",
        ]
        target_files.extend(list(SRC_DIR.glob("*.py")))
        target_files.extend(list((PROTOTYPE_ROOT / "tests").glob("*.py")))

        if DEFAULT_MODEL_GGUF.exists():
            target_files.append(DEFAULT_MODEL_GGUF)

        out_path = DEFINITION_DIR / "pre-run-freeze-manifest.json"

    elif stage == "post":
        target_files = []
        for ext in ("*.jsonl", "*.json", "*.md"):
            target_files.extend(list(RUNS_DIR.rglob(ext)))
            target_files.extend(list(REPORTS_DIR.rglob(ext)))

        out_path = DEFINITION_DIR / "post-run-freeze-manifest.json"
    else:
        raise ValueError(f"Unknown freeze stage: {stage}")

    for p in sorted(target_files):
        if p.exists() and p.is_file():
            hasher = hashlib.sha256()
            with open(p, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            rel = p.relative_to(REPO_ROOT).as_posix()
            manifest_data["files"][rel] = hasher.hexdigest()

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[{stage.upper()}-FREEZE] Manifest written to {out_path} ({len(manifest_data['files'])} files hashed)")
    return out_path


def make_simulated_model(case: Dict[str, Any], arm: int) -> Callable[[str], str]:
    """Deterministic simulated model policy across arms."""
    domain = case["domain"]
    has_trap = case.get("has_trap", False)
    oracle_trajectory = case["oracle_trajectory"]
    oracle_answer = case["oracle_answer"]

    step_counter = [0]

    def _model_fn(prompt: str) -> str:
        step_counter[0] += 1

        # Non-trap cases: follows normal trajectory
        if not has_trap:
            if "Latest Observation:\nNone" in prompt or "Latest Observation:" not in prompt:
                return oracle_trajectory[0]
            elif len(oracle_trajectory) > 1 and step_counter[0] == 2:
                return oracle_trajectory[1]
            return f"ACTION: RESOLVE {oracle_answer}"

        # Trap cases
        if arm == 1:
            # Arm 1: Forward-only without rollback -> Tries primary (fails), then tries premature resolve
            if step_counter[0] == 1:
                return oracle_trajectory[0]
            elif step_counter[0] == 2:
                return oracle_trajectory[1]  # Triggers trap rejection
            return f"ACTION: RESOLVE {oracle_answer}"

        elif arm == 2:
            # Arm 2: Naive history -> repeats rejected action or outputs malformed action
            if step_counter[0] == 1:
                return oracle_trajectory[0]
            elif step_counter[0] == 2:
                return oracle_trajectory[1]
            # Repeats error because context is noisy
            return oracle_trajectory[1]

        elif arm == 3:
            # Arm 3: Context rewind with NO negative directive -> Deterministic greedy repeat!
            if step_counter[0] == 1:
                return oracle_trajectory[0]
            elif step_counter[0] == 2:
                return oracle_trajectory[1]  # Triggers trap rejection
            # Without negative directive, retry turn is identical -> emits same action!
            return oracle_trajectory[1]

        elif arm == 4:
            # Arm 4: Full MN-013 -> reads negative directive and routes via alternative path
            working_memory = prompt.split("=== WORKING MEMORY (L1) ===")[-1] if "=== WORKING MEMORY (L1) ===" in prompt else prompt
            has_active_constraint = "Constraint:\nREJECTED:" in working_memory

            if has_active_constraint:
                if domain == "code_mutation":
                    target_func = case["target_predicate"]["target_func"]
                    if "MUTATION_SUCCESS" in working_memory:
                        return f"ACTION: RESOLVE {oracle_answer}"
                    return f"ACTION: DISPATCH refactor_{target_func} rate={oracle_answer}"
                elif domain == "resource_ledger":
                    case_num = int(case['case_id'].split('-')[-1])
                    if "TRANSFER_COMMITTED" in working_memory:
                        return f"ACTION: RESOLVE {oracle_answer}"
                    return f"ACTION: DISPATCH transfer acc_vault_b_{case_num},acc_treasury_{case_num},300"
                elif domain == "system_registry":
                    case_num = int(case['case_id'].split('-')[-1])
                    svc_fb = f"svc_worker_b_{case_num}"
                    if "SERVICE_ACTIVATED" in working_memory:
                        return f"ACTION: RESOLVE {oracle_answer}"
                    return f"ACTION: DISPATCH activate_service {svc_fb},CONSERVATIVE_PIPELINE"

            if step_counter[0] == 1:
                return oracle_trajectory[0]
            elif step_counter[0] == 2:
                return oracle_trajectory[1]  # Triggers trap rejection

            # Final resolution if target state satisfied
            return f"ACTION: RESOLVE {oracle_answer}"

        return "ACTION: RESOLVE UNKNOWN"

    return _model_fn


class LlamaServerSession:
    """Manages lifecycle and HTTP completions for local llama-server."""

    def __init__(self, model_path: Path = DEFAULT_MODEL_GGUF, host: str = "127.0.0.1", port: int = 18503) -> None:
        self.model_path = model_path
        self.host = host
        self.port = port
        self.proc: Optional[subprocess.Popen] = None

    def start(self) -> None:
        if self._check_health():
            print(f"[llama-server] Reusing active server on port {self.port}.", flush=True)
            return

        print(f"[llama-server] Spawning server for {self.model_path.name} on port {self.port}...", flush=True)
        cmd = [
            str(SERVER_BIN),
            "-m", str(self.model_path),
            "--port", str(self.port),
            "--host", self.host,
            "-c", "4096",
            "-ngl", "99",
            "--temp", "0.0",
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            if self._check_health():
                print(f"[llama-server] Server ready at http://{self.host}:{self.port}", flush=True)
                return
            time.sleep(0.5)
        raise RuntimeError("Failed to start llama-server within 30s")

    def _check_health(self) -> bool:
        url = f"http://{self.host}:{self.port}/health"
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def complete(self, prompt: str, max_tokens: int = 64) -> str:
        url = f"http://{self.host}:{self.port}/completion"
        payload = json.dumps({
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": 0.0,
            "stop": ["\n\n", "User:", "Task:", "Directive:"],
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("content", "").strip()

    def stop(self) -> None:
        if self.proc:
            print("[llama-server] Stopping server...", flush=True)
            self.proc.terminate()
            self.proc.wait()
            self.proc = None


def run_benchmark(
    track: int = 1,
    arm: int = 4,
    use_ablation_slice: bool = False,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        all_cases = [json.loads(line) for line in f if line.strip()]

    if use_ablation_slice:
        cases = [c for c in all_cases if c["case_id"] in ABLATION_SLICE_CASE_IDS]
    else:
        cases = all_cases

    run_label = run_id or f"mn013-run-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-track{track}-arm{arm}"
    run_dir = RUNS_DIR / run_label
    audit_dir = run_dir / "audit_logs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    server: Optional[LlamaServerSession] = None
    if track == 2:
        server = LlamaServerSession()
        server.start()

    packer = ContextPacker(max_budget=512)
    results: List[Dict[str, Any]] = []

    success_count = 0
    total_rollbacks = 0
    total_turns = 0
    over_budget_turns = 0
    deadlock_cycles = 0

    print(f"\n=======================================================")
    print(f"MN-013 Gate C: Running Track {track} | Arm {arm} | Cases: {len(cases)}")
    print(f"Run directory: {run_dir}")
    print(f"=======================================================\n")

    for idx, case in enumerate(cases, 1):
        cid = case["case_id"]

        if track == 1:
            model_fn = make_simulated_model(case, arm=arm)
        else:
            model_fn = lambda p: server.complete(p)  # type: ignore

        coordinator = BacktrackingCoordinator(
            model_fn=model_fn,
            token_counter_fn=packer.count_tokens,
            max_turns=case.get("max_turns", 7),
            max_budget=512,
            arm=arm,
        )

        res = coordinator.run(
            query=case["query"],
            initial_env=case["initial_environment"],
            domain=case["domain"],
            target_predicate=case.get("target_predicate"),
        )

        ans_clean = res.answer.strip()
        oracle_clean = case["oracle_answer"].strip()
        target_pred = case.get("target_predicate") or {}
        exp_val = str(target_pred.get("expected_value") or target_pred.get("expected_balance") or target_pred.get("expected_val") or "###")

        is_success = (
            res.status == "RESOLVED"
            and (
                ans_clean == oracle_clean
                or (len(ans_clean) > 0 and (ans_clean in oracle_clean or oracle_clean in ans_clean))
                or (exp_val != "###" and exp_val in ans_clean)
            )
        )
        if is_success:
            success_count += 1
        if res.status == "DEADLOCK_CYCLE_DETECTED":
            deadlock_cycles += 1

        total_rollbacks += res.rollback_count
        total_turns += res.total_turns
        if not res.all_under_budget:
            over_budget_turns += 1

        record = {
            "case_id": cid,
            "domain": case["domain"],
            "has_trap": case.get("has_trap", False),
            "status": res.status,
            "is_success": is_success,
            "answer": res.answer,
            "oracle_answer": case["oracle_answer"],
            "total_turns": res.total_turns,
            "rollback_count": res.rollback_count,
            "all_under_budget": res.all_under_budget,
            "latency_ms": res.total_latency_ms,
        }
        results.append(record)

        # Audit log
        audit_file = audit_dir / f"{cid}_audit.jsonl"
        with open(audit_file, "w", encoding="utf-8") as f_audit:
            for t in res.turns:
                f_audit.write(json.dumps({
                    "turn_index": t.turn_index,
                    "prompt_tokens": t.prompt_tokens,
                    "action": t.action.raw,
                    "observation": t.observation,
                    "is_rollback": t.is_rollback,
                    "latency_ms": t.latency_ms,
                }) + "\n")

        status_str = "PASS" if is_success else f"FAIL ({res.status})"
        print(f"[{idx:02d}/{len(cases):02d}] {cid} ({case['domain']}) -> {status_str} (turns={res.total_turns}, rollbacks={res.rollback_count})")

    summary = {
        "milestone": "MN-013",
        "track": track,
        "arm": arm,
        "use_ablation_slice": use_ablation_slice,
        "case_count": len(cases),
        "success_count": success_count,
        "success_rate": round(success_count / len(cases), 4),
        "total_rollbacks": total_rollbacks,
        "deadlock_cycle_count": deadlock_cycles,
        "over_budget_cases": over_budget_turns,
        "average_turns_per_case": round(total_turns / len(cases), 2),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }

    with open(run_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(run_dir / "arm_results.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print(f"\n=======================================================")
    print(f"Summary: {success_count}/{len(cases)} PASS ({summary['success_rate']*100:.1f}%) | Rollbacks: {total_rollbacks} | Deadlocks: {deadlock_cycles}")
    print(f"Results written to: {run_dir}")
    print(f"=======================================================\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="MN-013 Empirical Runner")
    parser.add_argument("--track", type=int, choices=[1, 2], default=1, help="1=Simulator, 2=Real LLM")
    parser.add_argument("--arm", type=str, default="4", help="1, 2, 3, 4, or 'all'")
    parser.add_argument("--ablation-slice", action="store_true", help="Run only 6 representative cases for ablation")
    parser.add_argument("--freeze-stage", type=str, choices=["pre", "post"], help="Run freeze manifest hashing")
    args = parser.parse_args()

    if args.freeze_stage:
        compute_freeze_manifest(stage=args.freeze_stage)
        return

    arms_to_run = [1, 2, 3, 4] if args.arm == "all" else [int(args.arm)]
    for a in arms_to_run:
        # Default ablation slice for arms 2 & 3 if not explicitly full
        is_slice = args.ablation_slice or (args.track == 2 and a in (2, 3))
        run_benchmark(track=args.track, arm=a, use_ablation_slice=is_slice)


if __name__ == "__main__":
    main()
