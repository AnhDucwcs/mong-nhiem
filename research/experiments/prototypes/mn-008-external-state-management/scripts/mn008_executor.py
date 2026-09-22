"""Hermetic model runner executor for MN-008 Gate C Phase 2.

Executes the 24-case corpus across Arms A, B, and C in case-interleaved order:
    (A_i -> B_1,i -> B_2,i -> C_2,i) for i in 0..23 (96 calls total).
Enforces persist-before-validate, stateless invocation, and strict hermetic preflight.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = EXPERIMENT_ROOT / "scripts"
DEFINITION_DIR = EXPERIMENT_ROOT / "definition" / "corpus-v1"
RUNS_DIR = EXPERIMENT_ROOT / "runs"

sys.path.insert(0, str(SCRIPTS_DIR))
import mn008_materialization as mat

REPO_ROOT = Path(__file__).resolve().parents[4]
MODEL_PATH = REPO_ROOT / "artifacts" / "models" / "mn-002" / "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
LLAMA_SERVER_PATH = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")

HOST = "127.0.0.1"
PORT = 18508
BASE_URL = f"http://{HOST}:{PORT}"
RUN_ID = "mn008-execution-run-0001"
TOTAL_CASES = 24
CALLS_PER_CASE = 4
EXPECTED_TOTAL_CALLS = TOTAL_CASES * CALLS_PER_CASE  # 96


class PreflightError(RuntimeError):
    """Raised when environment or static preflight fails."""


def run_cmd(args: list[str]) -> str:
    res = subprocess.run(args, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {args}\nStderr: {res.stderr}")
    return res.stdout.strip()


def check_git_status() -> str:
    status = run_cmd(["git", "status", "--porcelain"])
    if status != "":
        raise PreflightError(f"Working tree is dirty. Clean rerun requires a clean git state:\n{status}")
    return run_cmd(["git", "rev-parse", "HEAD"])


def check_gpu_status() -> tuple[int, int]:
    out = run_cmd(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"])
    mem, util = out.split(",")
    return int(mem.strip()), int(util.strip())


def check_no_stale_processes() -> None:
    res = subprocess.run(
        ["powershell", "-Command", "Get-Process -Name 'llama-server', 'llama-bench' -ErrorAction SilentlyContinue"],
        capture_output=True,
        text=True,
    )
    if res.stdout.strip() != "":
        raise PreflightError(f"Stale llama process detected:\n{res.stdout}")


def check_port_free(port: int) -> None:
    res = subprocess.run(
        ["powershell", "-Command", f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue"],
        capture_output=True,
        text=True,
    )
    if res.stdout.strip() != "":
        raise PreflightError(f"Port {port} is currently in use.")


def build_child_env() -> dict[str, str]:
    for k in os.environ.keys():
        if k.upper().startswith("LLAMA_"):
            raise PreflightError(f"Forbidden env var set: {k}")

    prog = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    appd = os.environ.get("APPDATA", r"C:\Users\Acer\AppData\Roaming")

    p1 = Path(prog) / "llama.cpp" / "config.ini"
    p2 = Path(appd) / "llama.cpp" / "config.ini"
    if p1.exists() or p2.exists():
        raise PreflightError("llama.cpp config.ini file detected; forbidden by contract")

    return {
        "PROGRAMDATA": prog,
        "APPDATA": appd,
        "SystemRoot": os.environ.get("SystemRoot", r"C:\Windows"),
        "SystemDrive": os.environ.get("SystemDrive", "C:"),
        "PATH": os.environ.get("PATH", ""),
        "USERPROFILE": os.environ.get("USERPROFILE", ""),
    }


def wait_for_server(base_url: str, deadline_seconds: int = 120) -> None:
    health_url = f"{base_url}/health"
    start = time.time()
    while time.time() - start < deadline_seconds:
        try:
            req = urllib.request.Request(health_url)
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("status") == "ok":
                        return
        except Exception:
            time.sleep(1)
    raise RuntimeError(f"Server at {base_url} failed to become healthy within {deadline_seconds}s")


def send_chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.0,
    seed: int = 42,
    max_tokens: int = 16,
    grammar: str | None = None,
    timeout_seconds: int = 120,
) -> tuple[dict[str, Any], float]:
    payload: dict[str, Any] = {
        "messages": messages,
        "temperature": temperature,
        "seed": seed,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if grammar is not None:
        payload["grammar"] = grammar

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/v1/chat/completions",
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        res_bytes = resp.read()
        latency_ms = (time.perf_counter() - t0) * 1000.0
        res_json = json.loads(res_bytes.decode("utf-8"))
        return res_json, latency_ms


def persist_raw_response(
    raw_path: Path,
    record: dict[str, Any],
) -> None:
    with open(raw_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def execute_runner() -> None:
    print(f"=== Starting MN-008 Gate C Phase 2 Hermetic Execution [{RUN_ID}] ===")

    # 1. Environment Preflight
    print("1. Performing static environment preflight...")
    git_head = check_git_status()
    print(f"   Git HEAD clean: {git_head}")

    mem, util = check_gpu_status()
    print(f"   GPU State: {mem} MiB used, {util}% util")
    if (mem, util) != (0, 0):
        raise PreflightError(f"GPU not clean: {mem} MiB used, {util}% util (must be 0, 0)")

    check_no_stale_processes()
    print("   No stale llama processes.")

    check_port_free(PORT)
    print(f"   Port {PORT} is available.")

    val_res = mat.validate_corpus(DEFINITION_DIR)
    print(f"   Corpus validation: {val_res['status']} (manifest: {val_res['manifest_sha256'][:16]}...)")

    child_env = build_child_env()
    print("   Child environment frozen.")

    # 2. Setup Run Directory
    run_dir = RUNS_DIR / RUN_ID
    if run_dir.exists():
        raise PreflightError(f"Run directory already exists: {run_dir}. Refusing to overwrite.")
    run_dir.mkdir(parents=True, exist_ok=False)

    raw_path = run_dir / "raw_responses.jsonl"

    # 3. Load Corpus
    public_prompts: list[dict[str, Any]] = []
    with open(DEFINITION_DIR / "public-prompts.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                public_prompts.append(json.loads(line))

    semantic_cases: list[dict[str, Any]] = []
    with open(DEFINITION_DIR / "semantic-cases.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                semantic_cases.append(json.loads(line))

    assert len(public_prompts) == TOTAL_CASES
    assert len(semantic_cases) == TOTAL_CASES

    # 4. Launch llama-server
    server_cmd = [
        str(LLAMA_SERVER_PATH),
        "-m",
        str(MODEL_PATH),
        "--host",
        HOST,
        "--port",
        str(PORT),
        "-c",
        "16896",
        "-t",
        "12",
        "-b",
        "2048",
        "-ub",
        "512",
        "-np",
        "1",
        "-fa",
        "on",
        "-ngl",
        "auto",
        "-sm",
        "layer",
        "-mg",
        "0",
        "--fit",
        "on",
        "--fit-target",
        "1024",
        "--fit-ctx",
        "4096",
        "--kv-offload",
        "--op-offload",
        "--load-mode",
        "auto",
        "--temp",
        "0",
        "--seed",
        "42",
        "--jinja",
        "--no-webui",
        "--no-cache-prompt",
        "--metrics",
        "--chat-template-kwargs",
        "{}",
    ]

    print("\n2. Launching llama-server on port 18508...")
    server = subprocess.Popen(
        server_cmd,
        env=child_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    t_start = datetime.now(timezone.utc)
    actual_persisted_calls = 0

    try:
        print("   Waiting for server health check...")
        wait_for_server(BASE_URL, deadline_seconds=120)
        print("   Server healthy.")

        print(f"\n3. Executing {TOTAL_CASES} cases in interleaved order (A_i -> B_1,i -> B_2,i -> C_2,i)...")

        for i in range(TOTAL_CASES):
            pub = public_prompts[i]
            sem = semantic_cases[i]
            case_id = pub["case_id"]
            case_ordinal = pub["case_ordinal"]

            mapping = mat.get_counterbalanced_mapping(case_ordinal)

            # --- 1. Arm A ---
            prompt_a = pub["arm_a_prompt"]
            res_a, lat_a = send_chat_completion(
                [{"role": "user", "content": prompt_a}],
                temperature=0.0,
                seed=42,
                max_tokens=16,
            )
            content_a = res_a["choices"][0]["message"]["content"]
            rec_a = {
                "arm": "A",
                "call_id": f"{case_id}-A",
                "call_ordinal": actual_persisted_calls + 1,
                "case_id": case_id,
                "case_ordinal": case_ordinal,
                "extracted_content": content_a,
                "latency_ms": lat_a,
                "prompt": prompt_a,
                "raw_response": res_a,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
            persist_raw_response(raw_path, rec_a)
            actual_persisted_calls += 1

            # --- 2. Arm B Stage 1 ---
            prompt_b1 = pub["arm_b_stage1_prompt"]
            grammar_b1 = pub["arm_b_grammar"]
            res_b1, lat_b1 = send_chat_completion(
                [{"role": "user", "content": prompt_b1}],
                temperature=0.0,
                seed=42,
                max_tokens=64,
                grammar=grammar_b1,
            )
            content_b1 = res_b1["choices"][0]["message"]["content"]
            rec_b1 = {
                "arm": "B1",
                "call_id": f"{case_id}-B1",
                "call_ordinal": actual_persisted_calls + 1,
                "case_id": case_id,
                "case_ordinal": case_ordinal,
                "extracted_content": content_b1,
                "latency_ms": lat_b1,
                "prompt": prompt_b1,
                "raw_response": res_b1,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
            persist_raw_response(raw_path, rec_b1)
            actual_persisted_calls += 1

            # --- 3. Arm B Stage 2 ---
            prompt_b2 = mat.render_arm_b_stage2_prompt(content_b1, mapping)
            res_b2, lat_b2 = send_chat_completion(
                [{"role": "user", "content": prompt_b2}],
                temperature=0.0,
                seed=42,
                max_tokens=16,
            )
            content_b2 = res_b2["choices"][0]["message"]["content"]
            rec_b2 = {
                "arm": "B2",
                "call_id": f"{case_id}-B2",
                "call_ordinal": actual_persisted_calls + 1,
                "case_id": case_id,
                "case_ordinal": case_ordinal,
                "extracted_content": content_b2,
                "latency_ms": lat_b2,
                "prompt": prompt_b2,
                "raw_response": res_b2,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
            persist_raw_response(raw_path, rec_b2)
            actual_persisted_calls += 1

            # --- 4. Arm C Stage 2 ---
            prompt_c2 = pub["arm_c_stage2_prompt"]
            res_c2, lat_c2 = send_chat_completion(
                [{"role": "user", "content": prompt_c2}],
                temperature=0.0,
                seed=42,
                max_tokens=16,
            )
            content_c2 = res_c2["choices"][0]["message"]["content"]
            rec_c2 = {
                "arm": "C2",
                "call_id": f"{case_id}-C2",
                "call_ordinal": actual_persisted_calls + 1,
                "case_id": case_id,
                "case_ordinal": case_ordinal,
                "extracted_content": content_c2,
                "latency_ms": lat_c2,
                "prompt": prompt_c2,
                "raw_response": res_c2,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
            persist_raw_response(raw_path, rec_c2)
            actual_persisted_calls += 1

            print(
                f"   [{i + 1:02d}/{TOTAL_CASES}] {case_id}: "
                f"A='{content_a.strip()}' | B='{content_b2.strip()}' | C='{content_c2.strip()}' "
                f"(Target: {sem['target_action']})"
            )

    finally:
        print("\n4. Terminating llama-server...")
        server.terminate()
        server.wait(timeout=30)
        print("   Server stopped.")

    t_end = datetime.now(timezone.utc)

    if actual_persisted_calls != EXPECTED_TOTAL_CALLS:
        raise RuntimeError(
            f"Execution incomplete: persisted {actual_persisted_calls}/{EXPECTED_TOTAL_CALLS} calls."
        )

    # 5. Write Run Metadata
    metadata = {
        "actual_persisted_calls": actual_persisted_calls,
        "corpus_manifest_sha256": val_res["manifest_sha256"],
        "duration_seconds": (t_end - t_start).total_seconds(),
        "end_time_utc": t_end.isoformat(),
        "expected_total_calls": EXPECTED_TOTAL_CALLS,
        "git_head": git_head,
        "host": HOST,
        "llama_server_path": str(LLAMA_SERVER_PATH),
        "model_path": str(MODEL_PATH),
        "port": PORT,
        "run_id": RUN_ID,
        "start_time_utc": t_start.isoformat(),
        "status": "COMPLETED",
        "total_cases": TOTAL_CASES,
    }
    with open(run_dir / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)

    print(f"\nExecution successful. Raw evidence persisted to:\n  {raw_path}")
    print(f"Run metadata written to:\n  {run_dir / 'run_metadata.json'}")


if __name__ == "__main__":
    try:
        execute_runner()
    except Exception as e:
        print(f"\nExecution failed: {e}", file=sys.stderr)
        sys.exit(1)
