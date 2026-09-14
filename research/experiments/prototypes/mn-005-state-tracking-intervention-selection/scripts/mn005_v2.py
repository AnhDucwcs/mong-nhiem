"""Gate C v2 helpers for the frozen MN-005 Gate B v2 contract (no inference on import)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import mn005 as v1

ROOT = v1.ROOT
DEFINITION = ROOT / "definition"
PREFLIGHT = ROOT / "preflight"
RUNS = ROOT / "runs"
CASE_IDS = v1.CASE_IDS
CONTROL_ARTIFACT = v1.CONTROL_ARTIFACT
STAGE_A_MAX_TOKENS = 80
FINAL_MAX_TOKENS = 16
FIXED_MARGIN_TOKENS = 8
EXPECTED_ARM_B_ARTIFACT_TOKENS = 71
EXPECTED_ARM_C_ARTIFACT_TOKENS = {
    "ecc006-001": 52,
    "ecc006-002": 51,
    "ecc006-003": 50,
    "ecc006-004": 53,
    "ecc006-005": 50,
    "ecc006-006": 48,
}
EXPECTED_SOURCE_SHA256 = {
    "ecc006-001": "429f45745b56db4ba06f27f8a0c71e021a7383082e58548cb11fec67c6aebd04",
    "ecc006-002": "d04d15bbe3e245787bcb80b281fe0b52cfc635e6cadd92f8a0e40220700c1a20",
    "ecc006-003": "8439351dac678f23ebfaf36ae71f647c17965d568db7b78dc93dbffde3f377cc",
    "ecc006-004": "f4683c1728a0ac11886d8fa7d91464cd15d205ba2a3f61a4161eb1c9e8953a41",
    "ecc006-005": "8a0785d26317d5d89ad2e9b82f15186c564fa6dd2888f93c8b31ee227ba33acb",
    "ecc006-006": "205a44f2176da10935715c153aab21bff90445cbe8d768249da8cacb7d5c3982",
}

ContractError = v1.ContractError
Client = v1.Client


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def write_bytes_atomic(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def definition_fingerprint(value: dict[str, Any] | None = None) -> str:
    return v1.sha256_bytes(v1.canonical_json(value or load_definition()[0]))


def load_definition() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    value = load_json(DEFINITION / "experiment-v2.json")
    required = {"id", "version", "authority", "model", "runtime", "workload", "budgets", "active_control_artifact", "support", "sizing"}
    if value.get("id") != "mn-005-multi-pass-reconstruction" or value.get("version") != "2.0.0" or required - set(value):
        raise ContractError("invalid MN-005 Gate B v2 definition")
    if value["active_control_artifact"] != CONTROL_ARTIFACT:
        raise ContractError("active-control grammar differs from frozen Gate B v2")
    if value["budgets"] != {"arm_a": FINAL_MAX_TOKENS, "stage_a": STAGE_A_MAX_TOKENS, "stage_b": FINAL_MAX_TOKENS}:
        raise ContractError("MN-005 v2 output budgets differ from Gate B v2")
    if value["sizing"] != {"fixed_margin_tokens": FIXED_MARGIN_TOKENS, "arm_b_tokens": EXPECTED_ARM_B_ARTIFACT_TOKENS, "arm_c_tokens": EXPECTED_ARM_C_ARTIFACT_TOKENS}:
        raise ContractError("MN-005 v2 artifact sizing differs from Gate B v2")
    if value["workload"]["case_ids"] != list(CASE_IDS) or value["workload"]["requested_input_tokens"] != 8192:
        raise ContractError("MN-005 v2 workload differs from frozen six-case 8k contract")
    gates = {
        "gate_a_sha256": ROOT / "gate-a-hypothesis.md",
        "gate_b_v1_sha256": ROOT / "gate-b-measurement-contract.md",
        "gate_b_v2_sha256": ROOT / "gate-b-v2-measurement-contract.md",
    }
    for name, path in gates.items():
        if v1.sha256_file(path) != value["authority"][name]:
            raise ContractError(f"frozen authority mismatch: {name}")
    ecc_definition, cases = v1.ecc006.load_definition()
    if v1.ecc006.definition_fingerprint() != value["authority"]["ecc006_definition_fingerprint"]:
        raise ContractError("frozen ECC-006 authority fingerprint mismatch")
    if [case["id"] for case in cases] != list(CASE_IDS):
        raise ContractError("ECC-006 source case order differs from Gate B v2")
    return value, cases, ecc_definition


def ideal_artifact(case: dict[str, Any]) -> str:
    return "\n".join(f"entity={case['entity']} | state={state}" for state in case["updates"])


def assert_strict_fit(label: str, artifact_tokens: int, maximum: int = STAGE_A_MAX_TOKENS) -> None:
    if artifact_tokens + FIXED_MARGIN_TOKENS > maximum:
        raise ContractError(f"Gate B v2 strict-fit failure: {label} requires {artifact_tokens}+{FIXED_MARGIN_TOKENS}>{maximum}")


def validate_artifact_sizing(client: Client, cases: list[dict[str, Any]], definition: dict[str, Any]) -> dict[str, int]:
    counts = {"arm_b": client.count_text(CONTROL_ARTIFACT)}
    if counts["arm_b"] != definition["sizing"]["arm_b_tokens"]:
        raise ContractError("Gate B v2 Arm B tokenizer count differs from frozen authority")
    assert_strict_fit("Arm B fixed artifact", counts["arm_b"], definition["budgets"]["stage_a"])
    for case in cases:
        count = client.count_text(ideal_artifact(case))
        if count != definition["sizing"]["arm_c_tokens"][case["id"]]:
            raise ContractError(f"Gate B v2 Arm C tokenizer count differs for {case['id']}")
        assert_strict_fit(case["id"], count, definition["budgets"]["stage_a"])
        counts[case["id"]] = count
    return counts


def stage_a_prompt(source: dict[str, Any], arm: str) -> str:
    return v1.stage_a_prompt(source, arm)


def stage_b_prompt(source: dict[str, Any], case: dict[str, Any], artifact: bytes) -> tuple[str, bytes, bytes]:
    return v1.stage_b_prompt(source, case, artifact)


def response_content(response: dict[str, Any]) -> str:
    return v1.response_content(response)


def finish_reason(response: dict[str, Any]) -> str | None:
    return v1.finish_reason(response)


def final_evaluation(case: dict[str, Any], raw: str, finish: str | None) -> dict[str, Any]:
    return v1.final_evaluation(case, raw, finish)


def reconstruction_diagnostic(case: dict[str, Any], artifact: bytes, finish: str | None) -> dict[str, Any]:
    return v1.reconstruction_diagnostic(case, artifact, finish)


def control_diagnostic(artifact: bytes, finish: str | None) -> dict[str, Any]:
    return v1.control_diagnostic(artifact, finish)


def require_exact_control_artifact(artifact: bytes, finish: str | None) -> dict[str, Any]:
    diagnostic = control_diagnostic(artifact, finish)
    if not diagnostic["exact_fixed_grammar"]:
        raise ContractError("protocol invalid: active-control artifact differs from frozen neutral grammar")
    return diagnostic


def artifact_record(path: Path, artifact: bytes, slot: bytes | None = None) -> dict[str, Any]:
    write_bytes_atomic(path, artifact)
    try:
        stored_path = str(path.relative_to(ROOT))
    except ValueError:
        stored_path = str(path)
    record = {"path": stored_path, "stage_a_sha256": v1.sha256_bytes(artifact), "base64": v1.base64.b64encode(artifact).decode("ascii")}
    if slot is not None:
        record.update({"artifact_slot_sha256": v1.sha256_bytes(slot), "literal_equal": artifact == slot})
    return record


def preflight(client: Client, definition: dict[str, Any], cases: list[dict[str, Any]], ecc_definition: dict[str, Any]) -> dict[str, Any]:
    artifact_counts = validate_artifact_sizing(client, cases, definition)
    rows: list[dict[str, Any]] = []
    retained = {}
    attempt = RUNS / "attempt-0001" / "results.jsonl"
    for line in attempt.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("arm") == "A":
            retained[row["case_id"]] = row["source"]
    for case in cases:
        context = retained.get(case["id"])
        if not isinstance(context, str):
            raise ContractError("missing retained frozen source")
        source = {"context": context, "arm_a": context + "\n\nQuestion:\n" + v1.question(case), "source_sha256": v1.sha256_bytes(context.encode("utf-8"))}
        if source["source_sha256"] != EXPECTED_SOURCE_SHA256[case["id"]]:
            raise ContractError(f"frozen source fingerprint differs for {case['id']}")
        budget = definition["budgets"]
        a = v1.checked_prompt_tokens(client, source["arm_a"], budget["arm_a"], definition["runtime"]["configured_context_size"])
        b_a = v1.checked_prompt_tokens(client, stage_a_prompt(source, "B"), budget["stage_a"], definition["runtime"]["configured_context_size"])
        c_a = v1.checked_prompt_tokens(client, stage_a_prompt(source, "C"), budget["stage_a"], definition["runtime"]["configured_context_size"])
        b_content, _slot, _rendered = stage_b_prompt(source, case, CONTROL_ARTIFACT.encode("utf-8"))
        c_content, _slot, _rendered = stage_b_prompt(source, case, ideal_artifact(case).encode("utf-8"))
        b_b = v1.checked_prompt_tokens(client, b_content, budget["stage_b"], definition["runtime"]["configured_context_size"])
        c_b = v1.checked_prompt_tokens(client, c_content, budget["stage_b"], definition["runtime"]["configured_context_size"])
        rows.append({"case_id": case["id"], "source_sha256": source["source_sha256"], "source_actual_prompt_tokens": a, "arm_a_prompt_tokens": a, "arm_b_stage_a_prompt_tokens": b_a, "arm_b_artifact_completion_tokens": artifact_counts["arm_b"], "arm_b_stage_b_prompt_tokens": b_b, "arm_c_stage_a_prompt_tokens": c_a, "arm_c_ideal_artifact_completion_tokens": artifact_counts[case["id"]], "arm_c_stage_b_prompt_tokens_with_ideal_artifact": c_b, "context_size": definition["runtime"]["configured_context_size"], "final_completion_allowance": budget["stage_b"], "source_untruncated": True})
    return {"preflight_version": 2, "completed_at": v1.now(), "definition_fingerprint": definition_fingerprint(definition), "gate_b_v2_sha256": definition["authority"]["gate_b_v2_sha256"], "artifact_counts": artifact_counts, "cases": rows, "passed": len(rows) == len(CASE_IDS)}


def classify(arm_a: list[dict[str, Any]], pairs: list[dict[str, Any]], definition: dict[str, Any]) -> dict[str, Any]:
    return v1.classify(arm_a, pairs, definition)


def next_attempt_id() -> str:
    return v1.next_attempt_id()


def has_canonical_attempt() -> bool:
    return v1.has_canonical_attempt()


def validate_runtime(definition: dict[str, Any], server: Path, model: Path) -> dict[str, Any]:
    return v1.validate_runtime(definition, server, model)


def server_command(definition: dict[str, Any], server: Path, model: Path, port: int) -> list[str]:
    return v1.server_command(definition, server, model, port)


def cpu_static_server_command(definition: dict[str, Any], server: Path, model: Path, port: int) -> list[str]:
    runtime = definition["runtime"]
    return [str(server), "-m", str(model), "--host", "127.0.0.1", "--port", str(port), "-c", str(runtime["configured_context_size"]), "-t", str(runtime["threads"]), "-b", str(runtime["batch_size"]), "-np", "1", "--device", "none", "-ngl", "0", "-nkvo", "--no-op-offload", "-fit", "off", "--jinja", "--no-webui", "--no-cache-prompt", "--chat-template-kwargs", "{}"]


def gpu_snapshot() -> dict[str, Any]:
    return v1.gpu_snapshot()


def require_clean_gpu(snapshot: dict[str, Any], allowed_pids: set[int] | None = None) -> None:
    v1.require_clean_gpu(snapshot, allowed_pids)


def health(url: str) -> dict[str, Any]:
    return v1.health(url)


def command_result(command: list[str], timeout: int = 15) -> dict[str, Any]:
    return v1.command_result(command, timeout)
