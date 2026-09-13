"""Frozen MN-005 Gate C contracts and deterministic helpers (no inference on import)."""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parents[1]
DEFINITION = ROOT / "definition"
RUNS = ROOT / "runs"
PREFLIGHT = ROOT / "preflight"
ECC006_ROOT = ROOT.parent / "mn-003-effective-context-capacity" / "experiments" / "ecc-006-state-tracking"
sys.path.insert(0, str(ECC006_ROOT / "scripts"))
import ecc006
import run_ecc006

ContractError = ecc006.ContractError
CASE_IDS = ("ecc006-001", "ecc006-002", "ecc006-003", "ecc006-004", "ecc006-005", "ecc006-006")
CONTROL_ARTIFACT = "\n".join(["pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO"] * 4)
CONTROL_INSTRUCTION = """Stage A instruction:
Do not answer the question. Do not use, restate, summarize, retrieve, rank,
classify, or reason about the event log or question. Output exactly these four
lines, in this order, with no surrounding text:
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO"""
RECONSTRUCTION_INSTRUCTION = """Stage A instruction:
Do not answer the question. Transcribe every source state-update event for the
queried entity in original source order. Output exactly four lines and nothing
else. Each line must be:
entity={exact queried entity identifier} | state={exact assigned source state}
Do not include an ordinal, current, latest, final, answer, summary, conclusion,
or any derived state."""


class TokenCounter(Protocol):
    def count_text(self, text: str) -> int: ...
    def count_prompt(self, content: str) -> int: ...


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def definition_fingerprint(value: dict[str, Any] | None = None) -> str:
    return sha256_bytes(canonical_json(value or load_definition()[0]))


def load_definition() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    value = load_json(DEFINITION / "experiment.json")
    required = {"id", "version", "authority", "model", "runtime", "workload", "budgets", "active_control_artifact", "support"}
    if value.get("id") != "mn-005-multi-pass-reconstruction" or required - set(value):
        raise ContractError("invalid MN-005 experiment definition")
    if value["active_control_artifact"] != CONTROL_ARTIFACT:
        raise ContractError("active-control grammar differs from frozen Gate B")
    if value["workload"]["case_ids"] != list(CASE_IDS) or value["workload"]["requested_input_tokens"] != 8192:
        raise ContractError("MN-005 workload differs from frozen six-case 8k contract")
    if value["budgets"] != {"arm_a": 16, "stage_a": 64, "stage_b": 16}:
        raise ContractError("MN-005 output budgets differ from Gate B")
    gates = {"gate_a_sha256": ROOT / "gate-a-hypothesis.md", "gate_b_sha256": ROOT / "gate-b-measurement-contract.md"}
    for name, path in gates.items():
        if sha256_file(path) != value["authority"][name]:
            raise ContractError(f"frozen authority mismatch: {name}")
    ecc_definition, cases = ecc006.load_definition()
    if ecc006.definition_fingerprint() != value["authority"]["ecc006_definition_fingerprint"]:
        raise ContractError("frozen ECC-006 authority fingerprint mismatch")
    if [case["id"] for case in cases] != list(CASE_IDS):
        raise ContractError("ECC-006 source case order differs from Gate B")
    return value, cases, ecc_definition


def question(case: dict[str, Any]) -> str:
    return f"What is the current state of {case['entity']}? Return only the state."


def source_for(runtime: TokenCounter, case: dict[str, Any], ecc_definition: dict[str, Any]) -> dict[str, Any]:
    built = ecc006.build_case(runtime, case, 8192, ecc_definition)
    context, arm_a, _prefix, _distractors = ecc006.compose(
        case, built.distractor_histories, ecc_definition["case_generation"]["seed"], built.distractor_histories_before
    )
    if arm_a != built.content or not arm_a.endswith(question(case)):
        raise ContractError("ECC-006 composition replay mismatch")
    return {"context": context, "arm_a": arm_a, "built": ecc006.built_case_dict(built), "source_sha256": sha256_bytes(context.encode("utf-8"))}


def stage_a_prompt(source: dict[str, Any], arm: str) -> str:
    if arm == "B":
        instruction = CONTROL_INSTRUCTION
    elif arm == "C":
        instruction = RECONSTRUCTION_INSTRUCTION
    else:
        raise ContractError("Stage A is defined only for B/C")
    return source["arm_a"] + "\n\n" + instruction


def stage_b_prompt(source: dict[str, Any], case: dict[str, Any], artifact: bytes) -> tuple[str, bytes, bytes]:
    try:
        artifact_text = artifact.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractError("Stage A response is not UTF-8 transportable") from error
    prefix = source["context"] + "\n\nIntermediate artifact (literal, unmodified):\n<artifact>\n"
    suffix = "\n</artifact>\n\nQuestion:\n" + question(case)
    content = prefix + artifact_text + suffix
    rendered = content.encode("utf-8")
    slot = rendered[len(prefix.encode("utf-8")) : len(rendered) - len(suffix.encode("utf-8"))]
    if slot != artifact:
        raise ContractError("literal artifact transport mismatch")
    return content, slot, rendered


def response_content(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ContractError("completion response lacks one choice")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str):
        raise ContractError("completion response lacks text content")
    return content


def finish_reason(response: dict[str, Any]) -> str | None:
    choices = response.get("choices", [])
    return choices[0].get("finish_reason") if choices else None


def final_evaluation(case: dict[str, Any], raw: str, finish: str | None) -> dict[str, Any]:
    passed, normalized = ecc006.evaluate(case, raw)
    output_limit = finish == "length"
    if output_limit:
        passed = False
    failure = "correct" if passed else "output_token_limit_reached" if output_limit else ecc006.failure(case, raw, None) or "incorrect_state"
    return {"passed": passed, "score": float(passed), "normalized": normalized, "failure_class": failure, "output_limit_reached": output_limit}


def reconstruction_diagnostic(case: dict[str, Any], artifact: bytes, finish: str | None) -> dict[str, Any]:
    text = artifact.decode("utf-8", errors="replace")
    lines = text.splitlines()
    expected = [f"entity={case['entity']} | state={state}" for state in case["updates"]]
    parsed: list[tuple[str, str]] = []
    for line in lines:
        match = re.fullmatch(r"entity=(.+) \| state=([A-Z]+)", line)
        if match:
            parsed.append((match.group(1), match.group(2)))
    prohibited = sorted(set(re.findall(r"\b(?:ordinal|current|latest|final|answer|summary|conclusion)\b", text.casefold())))
    actual_states = [state for entity, state in parsed if entity == case["entity"]]
    non_target = [line for line, parsed_line in zip(lines, [re.fullmatch(r"entity=(.+) \| state=([A-Z]+)", line) for line in lines]) if parsed_line and parsed_line.group(1) != case["entity"]]
    return {
        "format_valid": len(lines) == 4 and len(parsed) == 4,
        "emitted_row_count": len(lines),
        "target_update_recall": sum(state in actual_states for state in case["updates"]),
        "omitted_updates": [state for state in case["updates"] if state not in actual_states],
        "non_target_insertions": non_target,
        "duplicate_rows": len(lines) != len(set(lines)),
        "source_order_correct": actual_states == case["updates"],
        "entity_accuracy": sum(entity == case["entity"] for entity, _state in parsed) == 4,
        "state_token_accuracy": actual_states == case["updates"],
        "full_exact_reconstruction": lines == expected,
        "prohibited_fields": prohibited,
        "output_token_limit_reached": finish == "length",
    }


def control_diagnostic(artifact: bytes, finish: str | None) -> dict[str, Any]:
    text = artifact.decode("utf-8", errors="replace")
    return {"exact_fixed_grammar": text == CONTROL_ARTIFACT, "emitted_row_count": len(text.splitlines()), "output_token_limit_reached": finish == "length"}


def artifact_record(path: Path, artifact: bytes, slot: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(artifact)
    return {"path": str(path.relative_to(ROOT)), "stage_a_sha256": sha256_bytes(artifact), "artifact_slot_sha256": sha256_bytes(slot), "literal_equal": artifact == slot, "base64": base64.b64encode(artifact).decode("ascii")}


def classify(arm_a: list[dict[str, Any]], pairs: list[dict[str, Any]], definition: dict[str, Any]) -> dict[str, Any]:
    if len(arm_a) != 6 or len(pairs) != 6:
        return {"classification": "experiment_invalid", "reason": "incomplete required coverage"}
    if any(not row["protocol_valid"] or row["infrastructure_status"] != "complete" for row in [*arm_a, *pairs]):
        return {"classification": "experiment_invalid", "reason": "protocol or infrastructure failure"}
    a_passes = sum(row["evaluation"]["passed"] for row in arm_a)
    b = [row["B"]["evaluation"]["passed"] for row in pairs]
    c = [row["C"]["evaluation"]["passed"] for row in pairs]
    n10 = sum(not left and right for left, right in zip(b, c)); n01 = sum(left and not right for left, right in zip(b, c)); delta = sum(int(right) - int(left) for left, right in zip(b, c))
    contributing = [row for row in pairs if not row["B"]["evaluation"]["passed"] and row["C"]["evaluation"]["passed"]]
    clean = all(row["C"]["stage_a_diagnostic"]["full_exact_reconstruction"] and not row["C"]["stage_a_diagnostic"]["prohibited_fields"] and not row["C"]["stage_a_diagnostic"]["non_target_insertions"] for row in contributing)
    if a_passes != definition["support"]["arm_a_passes"]:
        verdict = "inconclusive"
    elif sum(c) >= definition["support"]["arm_c_minimum"] and n10 >= definition["support"]["n10_minimum"] and n01 == definition["support"]["n01_required"] and clean:
        verdict = "supported"
    elif delta <= 0:
        verdict = "unsupported"
    else:
        verdict = "inconclusive"
    return {"classification": verdict, "arm_a_passes": a_passes, "arm_b_passes": sum(b), "arm_c_passes": sum(c), "n10": n10, "n01": n01, "D": delta, "contributing_flips_clean": clean}


def next_attempt_id() -> str:
    ids = []
    for path in RUNS.glob("attempt-*"):
        match = re.fullmatch(r"attempt-(\d{4})", path.name)
        if match:
            ids.append(int(match.group(1)))
    return f"attempt-{max(ids, default=0) + 1:04d}"


def has_canonical_attempt() -> bool:
    for path in RUNS.glob("attempt-*/summary.json"):
        try:
            if load_json(path).get("attempt_status") == "canonical_valid":
                return True
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    return False


def command_result(command: list[str], timeout: int = 15) -> dict[str, Any]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"available": False, "error": f"{type(error).__name__}: {error}"}
    return {"available": result.returncode == 0, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def gpu_snapshot() -> dict[str, Any]:
    gpu = command_result(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,memory.free,utilization.gpu", "--format=csv,noheader,nounits"])
    processes = command_result(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits"])
    snapshot: dict[str, Any] = {"captured_at": now(), "gpu_query": gpu, "compute_query": processes, "gpus": [], "compute_processes": []}
    if gpu["available"]:
        for line in gpu["stdout"].splitlines():
            fields = [field.strip() for field in line.split(",")]
            if len(fields) == 6:
                snapshot["gpus"].append({"name": fields[0], "driver": fields[1], "total_mib": int(fields[2]), "used_mib": int(fields[3]), "free_mib": int(fields[4]), "utilization_percent": int(fields[5])})
    if processes["available"]:
        for line in processes["stdout"].splitlines():
            fields = [field.strip() for field in line.split(",")]
            if len(fields) == 3 and fields[0].isdigit():
                snapshot["compute_processes"].append({"pid": int(fields[0]), "name": fields[1], "used_mib": int(fields[2]) if fields[2].isdigit() else None})
    return snapshot


def require_clean_gpu(snapshot: dict[str, Any], allowed_pids: set[int] | None = None) -> None:
    if not snapshot["gpu_query"]["available"] or not snapshot["compute_query"]["available"] or not snapshot["gpus"]:
        raise ContractError("mandatory nvidia-smi environment telemetry unavailable")
    allowed_pids = allowed_pids or set()
    unexpected = [row for row in snapshot["compute_processes"] if row["pid"] not in allowed_pids]
    if unexpected:
        raise ContractError("environment_contaminated: unexpected GPU compute process")


def runtime_identity(server: Path) -> dict[str, Any]:
    return run_ecc006.runtime_identity(server)


def validate_runtime(definition: dict[str, Any], server: Path, model: Path) -> dict[str, Any]:
    if not server.is_file() or not model.is_file():
        raise ContractError("missing llama-server or model artifact")
    if sha256_file(model) != definition["model"]["sha256"]:
        raise ContractError("model artifact SHA-256 mismatch")
    identity = runtime_identity(server)
    for key in ("backend", "version", "build", "commit"):
        if identity.get(key) != definition["runtime"][key]:
            raise ContractError(f"runtime identity mismatch: {key}")
    return identity


def server_command(definition: dict[str, Any], server: Path, model: Path, port: int) -> list[str]:
    runtime = definition["runtime"]
    return [str(server), "-m", str(model), "--host", "127.0.0.1", "--port", str(port), "-c", str(runtime["configured_context_size"]), "-t", str(runtime["threads"]), "-b", str(runtime["batch_size"]), "-np", str(runtime["parallel_slots"]), "-fa", "on", "--temp", "0", "--seed", "42", "--jinja", "--no-webui", "--no-cache-prompt", "--metrics", "--chat-template-kwargs", "{}"]


def health(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url + "/health", timeout=2) as response:
            return {"observed_at": now(), "reachable": response.status == 200, "status": response.status}
    except (OSError, TimeoutError, urllib.error.URLError) as error:
        return {"observed_at": now(), "reachable": False, "error": f"{type(error).__name__}: {error}"}


class Client:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def post(self, path: str, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
        request = urllib.request.Request(self.base_url + path, json.dumps(payload).encode("utf-8"), {"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def count_text(self, text: str) -> int:
        return len(self.post("/tokenize", {"content": text, "add_special": False})["tokens"])

    def count_prompt(self, content: str) -> int:
        template = self.post("/apply-template", {"messages": [{"role": "user", "content": content}], "add_generation_prompt": True, "chat_template_kwargs": {}})["prompt"]
        return len(self.post("/tokenize", {"content": template, "add_special": True})["tokens"])

    def complete(self, content: str, maximum: int) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = {"messages": [{"role": "user", "content": content}], "temperature": 0, "seed": 42, "max_tokens": maximum, "chat_template_kwargs": {}}
        return payload, self.post("/v1/chat/completions", payload)


def checked_prompt_tokens(client: Client, content: str, output_budget: int, context: int) -> int:
    tokens = client.count_prompt(content)
    if tokens + output_budget > context:
        raise ContractError(f"context overflow: {tokens}+{output_budget}>{context}")
    return tokens


def preflight(client: Client, definition: dict[str, Any], cases: list[dict[str, Any]], ecc_definition: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for case in cases:
        source = source_for(client, case, ecc_definition)
        a = checked_prompt_tokens(client, source["arm_a"], 16, 16896)
        b_a = checked_prompt_tokens(client, stage_a_prompt(source, "B"), 64, 16896)
        c_a = checked_prompt_tokens(client, stage_a_prompt(source, "C"), 64, 16896)
        b_b_content, _slot, _rendered = stage_b_prompt(source, case, CONTROL_ARTIFACT.encode("utf-8"))
        b_b = checked_prompt_tokens(client, b_b_content, 16, 16896)
        c_empty, _slot, _rendered = stage_b_prompt(source, case, b"")
        c_empty_tokens = checked_prompt_tokens(client, c_empty, 16, 16896)
        conservative_c = c_empty_tokens + 64
        if conservative_c + 16 > 16896:
            raise ContractError("conservative Arm C Stage B capacity exceeds frozen context")
        rows.append({"case_id": case["id"], "source_sha256": source["source_sha256"], "source_actual_prompt_tokens": source["built"]["actual_input_tokens"], "arm_a_prompt_tokens": a, "arm_b_stage_a_prompt_tokens": b_a, "arm_b_stage_b_prompt_tokens": b_b, "arm_c_stage_a_prompt_tokens": c_a, "arm_c_stage_b_empty_prompt_tokens": c_empty_tokens, "arm_c_stage_b_conservative_prompt_tokens": conservative_c, "context_size": 16896, "source_untruncated": True})
    return {"preflight_version": 1, "completed_at": now(), "definition_fingerprint": definition_fingerprint(definition), "gate_b_sha256": definition["authority"]["gate_b_sha256"], "cases": rows, "passed": len(rows) == 6}
