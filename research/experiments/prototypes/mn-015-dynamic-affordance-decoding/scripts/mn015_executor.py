"""Execution runner, server manager, and cryptographic freeze coordinator for MN-015: Dual-Layer Affordance Steering."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
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

from coordinator import Coordinator, CoordinatorResult
from gbnf_client import LlamaServerClient
from mong_nhiem.context import ContextPacker
from protocol import parse_action, ActionType


def compute_freeze_manifest(stage: str = "pre") -> Path:
    """Compute and record SHA-256 manifest for pre-run or post-run freeze."""
    manifest_data: Dict[str, Any] = {
        "milestone": "MN-015",
        "stage": stage,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "files": {},
    }

    if stage == "pre":
        target_files = [
            CASES_FILE,
            DEFINITION_DIR / "corpus-v1" / "manifest.json",
            SCRIPTS_DIR / "mn015_executor.py",
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
        self.client = LlamaServerClient(host=host, port=port)

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
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    if limit:
        cases = cases[:limit]

    run_label = run_id or f"mn015-run-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-track{track}-arm{arm}"
    run_dir = RUNS_DIR / run_label
    audit_dir = run_dir / "audit_logs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    session: Optional[LlamaServerSession] = None
    if track == 2:
        session = LlamaServerSession()
        session.start()

    packer = ContextPacker(max_budget=512)

    def token_counter(text: str) -> int:
        return packer.count_tokens(text)

    def simulator_model_fn(prompt: str, grammar: Optional[str]) -> tuple[str, float]:
        """Track 1 deterministic simulator adhering strictly to dynamic grammar."""
        g = grammar or ""
        if "resolve-action" in g and "valid-resolve-target ::=" in g:
            line = [l for l in g.splitlines() if "valid-resolve-target ::=" in l][0]
            cands = re.findall(r'"([^"]+)"', line)
            if cands:
                return f"ACTION: RESOLVE {cands[0]}", 1.0

        if "valid-dispatch-call ::=" in g:
            line = [l for l in g.splitlines() if "valid-dispatch-call ::=" in l][0]
            cands = re.findall(r'"([^"]+)"', line)
            if cands:
                return f"ACTION: DISPATCH {cands[0]}", 1.0

        if "valid-inspect-target ::=" in g:
            line = [l for l in g.splitlines() if "valid-inspect-target ::=" in l][0]
            cands = re.findall(r'"([^"]+)"', line)
            if cands:
                return f"ACTION: INSPECT {cands[0]}", 1.0

        if "valid-read-target ::=" in g:
            line = [l for l in g.splitlines() if "valid-read-target ::=" in l][0]
            cands = re.findall(r'"([^"]+)"', line)
            if cands:
                return f"ACTION: READ {cands[0]}", 1.0

        return "ACTION: INVALID", 1.0

    def model_fn(prompt: str, grammar: Optional[str]) -> tuple[str, float]:
        if track == 1:
            return simulator_model_fn(prompt, grammar)
        assert session is not None
        # Call llama-server with per-turn dynamic grammar override
        res = session.client.complete(prompt=prompt, max_tokens=64, use_grammar=True, grammar_override=grammar)
        return res["content"], res["latency_ms"]

    results = []
    success_count = 0
    deadlock_cycles = 0
    total_rollbacks = 0
    total_turns = 0
    over_budget_turns = 0
    parse_failures = 0

    print(f"\n[MN-015 EXECUTION] Starting Track {track} Arm {arm} on {len(cases)} cases...")
    print(f"Run directory: {run_dir}\n")

    for idx, case in enumerate(cases, start=1):
        cid = case["case_id"]
        coordinator = Coordinator(
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

        is_success = False
        if res.status == "SUCCESS":
            if ans_clean == oracle_clean or exp_val in ans_clean:
                is_success = True
            elif coordinator.phase_gate.verify_predicate(res.final_environment, target_pred):
                is_success = True

        if is_success:
            success_count += 1
        if res.status == "DEADLOCK_CYCLE_DETECTED":
            deadlock_cycles += 1
        total_rollbacks += res.rollback_count
        total_turns += res.total_turns
        if not res.all_under_budget:
            over_budget_turns += 1

        for t in res.turns:
            if t.action.action_type == ActionType.INVALID:
                parse_failures += 1

        case_record = {
            "case_id": cid,
            "domain": case["domain"],
            "has_trap": case.get("has_trap", False),
            "status": res.status,
            "is_success": is_success,
            "turns_taken": res.total_turns,
            "rollback_count": res.rollback_count,
            "answer": res.answer,
            "oracle_answer": case["oracle_answer"],
            "all_under_budget": res.all_under_budget,
            "total_latency_ms": res.total_latency_ms,
        }
        results.append(case_record)

        audit_path = audit_dir / f"{cid}_audit.jsonl"
        with open(audit_path, "w", encoding="utf-8") as f:
            for t in res.turns:
                f.write(json.dumps({
                    "turn_index": t.turn_index,
                    "prompt_tokens": t.prompt_tokens,
                    "raw_response": t.raw_response,
                    "action_key": t.action.action_key,
                    "observation": t.observation,
                    "is_rollback": t.is_rollback,
                    "latency_ms": t.latency_ms,
                }) + "\n")

        status_flag = "PASS" if is_success else "FAIL"
        print(f"[{idx:02d}/{len(cases):02d}] {cid} ({case['domain']}) -> {status_flag} (turns: {res.total_turns}, rollbacks: {res.rollback_count})")

    summary = {
        "run_id": run_label,
        "track": track,
        "arm": arm,
        "total_cases": len(cases),
        "success_count": success_count,
        "accuracy": success_count / len(cases) if cases else 0.0,
        "deadlock_cycles": deadlock_cycles,
        "total_rollbacks": total_rollbacks,
        "total_turns": total_turns,
        "mean_turns": total_turns / len(cases) if cases else 0.0,
        "parse_failures": parse_failures,
        "over_budget_turns": over_budget_turns,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "cases": results,
    }

    summary_path = run_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[SUMMARY] Accuracy: {success_count}/{len(cases)} ({summary['accuracy']*100:.1f}%)")
    print(f"Total Turns: {total_turns}, Rollbacks: {total_rollbacks}, Deadlocks: {deadlock_cycles}")
    print(f"Parse Failures: {parse_failures}, Over Budget: {over_budget_turns}")
    print(f"Saved to: {summary_path}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="MN-015 Execution Harness")
    parser.add_argument("--track", type=int, default=2, choices=[1, 2], help="Track 1 (Simulator) or Track 2 (Model)")
    parser.add_argument("--arm", type=int, default=2, choices=[1, 2], help="Arm 1 (Static GBNF) or Arm 2 (Dual-Layer Affordance)")
    parser.add_argument("--freeze-manifest", type=str, choices=["pre", "post"], help="Generate freeze manifest")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases")
    args = parser.parse_args()

    if args.freeze_manifest:
        compute_freeze_manifest(stage=args.freeze_manifest)
        return

    run_benchmark(track=args.track, arm=args.arm, limit=args.limit)


if __name__ == "__main__":
    main()
