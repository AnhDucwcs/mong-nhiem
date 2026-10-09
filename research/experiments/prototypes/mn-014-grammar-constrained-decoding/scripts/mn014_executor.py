"""Execution runner, server manager, and cryptographic freeze coordinator for MN-014."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional

PROTOTYPE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROTOTYPE_ROOT.parents[3]
SRC_DIR = PROTOTYPE_ROOT / "src"

DEFINITION_DIR = PROTOTYPE_ROOT / "definition"
CASES_FILE = DEFINITION_DIR / "corpus-v1" / "cases.jsonl"
GRAMMAR_FILE = DEFINITION_DIR / "grammar" / "action_grammar.gbnf"
SCRIPTS_DIR = PROTOTYPE_ROOT / "scripts"
REPORTS_DIR = PROTOTYPE_ROOT / "reports"
RUNS_DIR = PROTOTYPE_ROOT / "runs"

DEFAULT_MODEL_GGUF = REPO_ROOT / "artifacts" / "models" / "mn-002" / "Qwen3.5-2B-Q4_K_M.gguf"
DEFAULT_LLAMA_SERVER = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

CORE_SRC = REPO_ROOT / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from coordinator import GrammarBacktrackingCoordinator, CoordinatorResult
from gbnf_client import LlamaServerClient
from mong_nhiem.context import ContextPacker
from protocol import parse_action


def compute_freeze_manifest(stage: str = "pre") -> Path:
    """Compute and record SHA-256 manifest for pre-run or post-run freeze."""
    manifest_data: Dict[str, Any] = {
        "milestone": "MN-014",
        "stage": stage,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "files": {},
    }

    if stage == "pre":
        target_files = [
            CASES_FILE,
            DEFINITION_DIR / "corpus-v1" / "manifest.json",
            GRAMMAR_FILE,
            SCRIPTS_DIR / "mn014_executor.py",
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


class LlamaServerSession:
    """Manages llama-server subprocess lifecycle."""

    def __init__(
        self,
        server_bin: Path = DEFAULT_LLAMA_SERVER,
        model_path: Path = DEFAULT_MODEL_GGUF,
        port: int = 18504,
        host: str = "127.0.0.1",
    ):
        self.server_bin = server_bin
        self.model_path = model_path
        self.port = port
        self.host = host
        self.proc: Optional[subprocess.Popen] = None
        self.client = LlamaServerClient(host=host, port=port, grammar_path=GRAMMAR_FILE)

    def start(self) -> None:
        if self.client.check_health():
            print(f"[llama-server] Existing server detected on port {self.port}, reusing.")
            return

        cmd = [
            str(self.server_bin),
            "-m", str(self.model_path),
            "--port", str(self.port),
            "--host", self.host,
            "-c", "4096",
            "-ngl", "99",
            "--temp", "0.0",
        ]
        print(f"[llama-server] Starting llama-server on port {self.port}...")
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            if self.client.check_health():
                print(f"[llama-server] Server ready at http://{self.host}:{self.port}")
                return
            time.sleep(0.5)
        raise RuntimeError("Failed to start llama-server within 30s")

    def stop(self) -> None:
        if self.proc:
            print("[llama-server] Stopping server...")
            self.proc.terminate()
            self.proc.wait()
            self.proc = None


def run_benchmark(
    track: int = 2,
    arm: int = 2,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    run_label = run_id or f"mn014-run-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-track{track}-arm{arm}"
    run_dir = RUNS_DIR / run_label
    audit_dir = run_dir / "audit_logs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    session: Optional[LlamaServerSession] = None
    if track == 2:
        session = LlamaServerSession()
        session.start()

    packer = ContextPacker(budget_tokens=512)

    def token_counter(text: str) -> int:
        return packer.count_tokens(text)

    def model_fn(prompt: str, use_grammar: bool):
        if track == 1:
            # Deterministic simulator fallback for smoke test
            return "ACTION: RESOLVE 42", 1.0
        assert session is not None
        # Call llama-server client with grammar flag
        res = session.client.complete(prompt=prompt, max_tokens=64, use_grammar=use_grammar)
        return res["content"], res["latency_ms"]

    results = []
    success_count = 0
    deadlock_cycles = 0
    total_rollbacks = 0
    total_turns = 0
    over_budget_turns = 0
    parse_failures = 0

    print(f"\n[MN-014 EXECUTION] Starting Track {track} Arm {arm} on {len(cases)} cases...")
    print(f"Run directory: {run_dir}\n")

    for idx, case in enumerate(cases, start=1):
        cid = case["case_id"]
        coordinator = GrammarBacktrackingCoordinator(
            model_fn=model_fn,
            token_counter_fn=token_counter,
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

        for turn in res.turns:
            if turn.action.action_type.value == "INVALID":
                parse_failures += 1

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

        # Audit log per case
        audit_file = audit_dir / f"{cid}_audit.jsonl"
        with open(audit_file, "w", encoding="utf-8") as af:
            for turn in res.turns:
                af.write(json.dumps({
                    "turn_index": turn.turn_index,
                    "prompt_tokens": turn.prompt_tokens,
                    "action": turn.action.raw,
                    "action_key": turn.action.action_key,
                    "observation": turn.observation,
                    "is_rollback": turn.is_rollback,
                    "latency_ms": turn.latency_ms,
                    "used_grammar": turn.used_grammar,
                }) + "\n")

        status_flag = "PASS" if is_success else f"FAIL ({res.status})"
        print(f"[{idx:02d}/{len(cases):02d}] {cid:16} | Trap: {str(case.get('has_trap', False)):5} | Turns: {res.total_turns} | Rollbacks: {res.rollback_count} | {status_flag}")

    summary = {
        "milestone": "MN-014",
        "track": track,
        "arm": arm,
        "case_count": len(cases),
        "success_count": success_count,
        "success_rate": round(success_count / len(cases), 4),
        "parse_failures": parse_failures,
        "total_rollbacks": total_rollbacks,
        "deadlock_cycle_count": deadlock_cycles,
        "over_budget_cases": over_budget_turns,
        "average_turns_per_case": round(total_turns / len(cases), 2),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }

    # Persist run results
    with open(run_dir / "arm_results.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    with open(run_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n=== SUMMARY: Track {track} Arm {arm} ===")
    print(f"Success Rate: {summary['success_count']}/{summary['case_count']} ({summary['success_rate']*100:.1f}%)")
    print(f"Parse Failures: {summary['parse_failures']}")
    print(f"Total Rollbacks: {summary['total_rollbacks']}")
    print(f"Deadlocks: {summary['deadlock_cycle_count']}")
    print(f"Summary written to: {run_dir / 'summary.json'}\n")

    if session:
        session.stop()

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MN-014 Benchmark Runner & Freeze Manager")
    parser.add_argument("--freeze-stage", choices=["pre", "post"], help="Compute cryptographic freeze manifest")
    parser.add_argument("--track", type=int, default=2, help="Evaluation track: 1 (Simulator), 2 (Real Model)")
    parser.add_argument("--arm", type=int, default=2, help="Experimental arm: 1 (Unconstrained), 2 (GBNF Constrained)")
    parser.add_argument("--run-id", type=str, default=None, help="Explicit run ID")
    args = parser.parse_args()

    if args.freeze_stage:
        compute_freeze_manifest(stage=args.freeze_stage)
    else:
        run_benchmark(track=args.track, arm=args.arm, run_id=args.run_id)
