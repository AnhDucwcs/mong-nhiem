#!/usr/bin/env python3
"""Deterministic implementation of the frozen MN-004 Gate A/B contract."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFINITION = ROOT / "definition"
SCHEMAS = ROOT / "schemas"
CONFIGS = ROOT / "configs"
RUNS = ROOT / "runs"
ECC006 = ROOT.parent / "mn-003-effective-context-capacity" / "experiments" / "ecc-006-state-tracking"
ECC006_RUN = ECC006 / "runs" / "20260828T053342Z-ecc-006-llama-3.2-3b-ab958c23"


class ContractError(RuntimeError):
    """A frozen Gate A/B condition is not met."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def schema_errors(value: Any, name: str) -> list[str]:
    validator = Draft202012Validator(load_json(SCHEMAS / name))
    return [error.message for error in validator.iter_errors(value)]


def definition_fingerprint(definition: dict[str, Any] | None = None) -> str:
    definition = definition or load_json(DEFINITION / "experiment.json")
    return sha256_bytes(b"experiment.json\0" + canonical_json(definition))


def _authority_path(relative: str) -> Path:
    return (ROOT / "definition" / relative).resolve()


def validate_definition() -> dict[str, Any]:
    definition = load_json(DEFINITION / "experiment.json")
    errors = schema_errors(definition, "experiment-definition.schema.json")
    if errors:
        raise ContractError(f"definition schema failure: {errors[0]}")
    if definition["id"] != "mn-004-state-representation-intervention" or definition["version"] != "1.0.0":
        raise ContractError("unexpected experiment identity")
    authority = definition["authority"]
    for path_key, hash_key in (("gate_a_path", "gate_a_sha256"), ("gate_b_path", "gate_b_sha256")):
        path = _authority_path(authority[path_key])
        if not path.is_file() or sha256_file(path) != authority[hash_key]:
            raise ContractError(f"frozen authority mismatch: {path_key}")
    for name, expected in (("experiment.json", authority["ecc006_experiment_sha256"]), ("cases.json", authority["ecc006_cases_sha256"])):
        if sha256_file(ECC006 / "definition" / name) != expected:
            raise ContractError(f"frozen ECC-006 authority mismatch: {name}")
    ecc_definition = load_json(ECC006 / "definition" / "experiment.json")
    ecc_cases = load_json(ECC006 / "definition" / "cases.json")
    digest = hashlib.sha256()
    for name, value in (("experiment.json", ecc_definition), ("cases.json", ecc_cases)):
        digest.update(name.encode("utf-8")); digest.update(b"\0"); digest.update(canonical_json(value))
    if digest.hexdigest() != authority["ecc006_definition_fingerprint"]:
        raise ContractError("frozen ECC-006 definition fingerprint mismatch")
    workload, runtime = definition["workload"], definition["runtime"]
    if workload["context_levels"] != [512, 2048, 8192, 16384] or workload["failure_region"] != [8192, 16384] or workload["reference_levels"] != [512, 2048]:
        raise ContractError("frozen context-region contract mismatch")
    if runtime != {**runtime, "configured_context_size": 16896, "output_tokens": 16, "temperature": 0.0, "seed": 42, "threads": 12, "batch_size": 2048, "parallel_slots": 1, "flash_attention": True, "prompt_cache": False}:
        raise ContractError("runtime contract has unexpected missing fields")
    return definition


def frozen_cases() -> list[dict[str, Any]]:
    cases = load_json(ECC006 / "definition" / "cases.json")["cases"]
    return [{"id": row["id"], "origin": "frozen", "entity": row["entity"], "updates": row["updates"], "answer": row["answer"], "seed": 20260828} for row in cases]


def fresh_cases(definition: dict[str, Any]) -> list[dict[str, Any]]:
    vocab = definition["workload"]["state_vocab"]
    result: list[dict[str, Any]] = []
    for number, case_id in enumerate(definition["workload"]["fresh_case_ids"], start=1):
        updates = [vocab[(4 * (number - 1) + offset) % len(vocab)] for offset in range(4)]
        result.append({"id": case_id, "origin": "fresh", "entity": f"Unit Ledger {9200 + number}", "updates": updates, "answer": updates[-1], "seed": definition["workload"]["fresh_case_seed"]})
    return result


def validate_case_specs(definition: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    expected_ids = definition["workload"]["frozen_case_ids"] + definition["workload"]["fresh_case_ids"]
    if [case["id"] for case in cases] != expected_ids:
        raise ContractError("case identity/order mismatch")
    if len({case["entity"] for case in cases}) != len(cases):
        raise ContractError("case target entities must be unique")
    for case in cases:
        if len(case["updates"]) != 4 or len(set(case["updates"])) != 4 or case["answer"] != case["updates"][-1]:
            raise ContractError(f"{case['id']}: frozen four-update contract mismatch")
        if case["origin"] not in ("frozen", "fresh"):
            raise ContractError(f"{case['id']}: unknown origin")


def distractor_events(case_id: str, index: int, side: str, seed: int) -> list[dict[str, str]]:
    """Exact ECC-006 deterministic state-history construction, structured before rendering."""
    digest = hashlib.sha256(f"{seed}:{case_id}:{index}:{side}".encode()).digest()
    entity = f"Unit Drift {1000 + int.from_bytes(digest[:2], 'big') % 8000}"
    states = ("RED", "BLUE", "AMBER", "GREEN", "SILVER", "VIOLET", "ORANGE", "BLACK")
    return [{"entity": entity, "state": states[(digest[offset] + offset) % len(states)]} for offset in range(4)]


def question(target: str, definition: dict[str, Any]) -> str:
    return definition["rendering"]["question_template"].format(entity=target)


def render_natural(events: list[dict[str, str]], target: str, definition: dict[str, Any]) -> str:
    event_template = definition["rendering"]["untreated_event_template"]
    lines = [event_template.format(entity=event["entity"], state=event["state"]) for event in events]
    return "Context event log:\n" + "\n".join(lines) + "\n\nQuestion:\n" + question(target, definition)


def render_ledger(events: list[dict[str, str]], target: str, definition: dict[str, Any]) -> str:
    event_template = definition["rendering"]["ledger_event_template"]
    lines = [event_template.format(index=index, entity=event["entity"], state=event["state"]) for index, event in enumerate(events, start=1)]
    return definition["rendering"]["ledger_heading"] + "\n" + "\n".join(lines) + "\n\nQuestion:\n" + question(target, definition)


def _split_prompt(prompt: str, target: str, definition: dict[str, Any]) -> tuple[str, list[str]]:
    marker = "\n\nQuestion:\n"
    if prompt.count(marker) != 1:
        raise ContractError("prompt must contain one question separator")
    context, observed_question = prompt.split(marker)
    if observed_question != question(target, definition):
        raise ContractError("question semantics mismatch")
    return context, context.split("\n")


def parse_natural(prompt: str, target: str, definition: dict[str, Any]) -> list[dict[str, str]]:
    _context, lines = _split_prompt(prompt, target, definition)
    if not lines or lines[0] != "Context event log:" or len(lines) < 5:
        raise ContractError("natural rendering header/event count mismatch")
    prefix, suffix = "State update: ", " changed to "
    result: list[dict[str, str]] = []
    for line in lines[1:]:
        if not line.startswith(prefix) or not line.endswith(".") or suffix not in line:
            raise ContractError("natural rendering line mismatch")
        entity, state = line[len(prefix):-1].split(suffix, 1)
        if not entity or not state or "\n" in entity or "\n" in state:
            raise ContractError("natural rendering contains invalid fields")
        result.append({"entity": entity, "state": state})
    return result


def parse_ledger(prompt: str, target: str, definition: dict[str, Any]) -> list[dict[str, str]]:
    _context, lines = _split_prompt(prompt, target, definition)
    if not lines or lines[0] != definition["rendering"]["ledger_heading"] or len(lines) < 5:
        raise ContractError("ledger header/event count mismatch")
    result: list[dict[str, str]] = []
    for index, line in enumerate(lines[1:], start=1):
        match = re.fullmatch(r"event=([1-9][0-9]*) \| entity=([^|\n]+) \| new_state=([^|\n]+)", line)
        if not match or int(match.group(1)) != index:
            raise ContractError("ledger index or syntax mismatch")
        entity, state = match.group(2), match.group(3)
        if entity != entity.strip() or state != state.strip():
            raise ContractError("ledger fields may not be rewritten or padded")
        result.append({"entity": entity, "state": state})
    return result


def source_event_hash(events: list[dict[str, str]]) -> str:
    return sha256_bytes(canonical_json(events))


def target_event_indexes(events: list[dict[str, str]], target: str) -> list[int]:
    return [index for index, event in enumerate(events, start=1) if event["entity"] == target]


def validate_pair(case: dict[str, Any], events: list[dict[str, str]], natural: str, ledger: str, definition: dict[str, Any]) -> None:
    parsed_natural, parsed_ledger = parse_natural(natural, case["entity"], definition), parse_ledger(ledger, case["entity"], definition)
    if parsed_natural != events or parsed_ledger != events:
        raise ContractError(f"{case['id']}: renderers do not preserve ordered source events")
    indexes = target_event_indexes(events, case["entity"])
    if len(indexes) != 4 or [events[index - 1]["state"] for index in indexes] != case["updates"]:
        raise ContractError(f"{case['id']}: target sequence/answer was not preserved")
    prohibited = ("TARGET", "current_state", "final_state", "latest", "summary")
    ledger_context = ledger.split("\n\nQuestion:\n", 1)[0].casefold()
    if any(value.casefold() in ledger_context for value in prohibited):
        raise ContractError(f"{case['id']}: prohibited treatment cue")
    if "Context event log:" in ledger or "Chronological state-transition ledger:" in natural:
        raise ContractError(f"{case['id']}: duplicated or cross-condition log")


class TokenRuntime(Protocol):
    def count_text(self, text: str) -> int: ...
    def count_prompt(self, content: str) -> int: ...


class ServerClient:
    """The same llama.cpp `/apply-template` plus `/tokenize` accounting model as ECC-006."""

    def __init__(self, base_url: str, chat_template_kwargs: dict[str, Any]):
        self.base_url = base_url.rstrip("/")
        self.chat_template_kwargs = chat_template_kwargs

    def post(self, path: str, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
        request = urllib.request.Request(self.base_url + path, json.dumps(payload).encode("utf-8"), {"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def count_text(self, text: str) -> int:
        return len(self.post("/tokenize", {"content": text, "add_special": False})["tokens"])

    def count_prompt(self, content: str) -> int:
        template = self.post("/apply-template", {"messages": [{"role": "user", "content": content}], "add_generation_prompt": True, "chat_template_kwargs": self.chat_template_kwargs})["prompt"]
        return len(self.post("/tokenize", {"content": template, "add_special": True})["tokens"])

    def complete(self, content: str, inference: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        request = {"messages": [{"role": "user", "content": content}], "temperature": inference["temperature"], "seed": inference["seed"], "max_tokens": inference["output_tokens"], "chat_template_kwargs": self.chat_template_kwargs}
        return request, self.post("/v1/chat/completions", request)


@dataclass(frozen=True)
class MaterializedCase:
    case_id: str
    origin: str
    requested_input_tokens: int
    target: str
    expected_answer: str
    target_updates: list[str]
    source_events: list[dict[str, str]]
    source_event_hash: str
    target_event_indexes: list[int]
    distractor_histories: int
    distractor_histories_before: int
    natural_prompt: str
    ledger_prompt: str


def _build_for_level(runtime: TokenRuntime, case: dict[str, Any], level: int, definition: dict[str, Any]) -> MaterializedCase:
    def events_for(histories: int, before_histories: int | None = None) -> list[dict[str, str]]:
        before_histories = histories // 2 if before_histories is None else before_histories
        before = [event for index in range(1, before_histories + 1) for event in distractor_events(case["id"], index, "before", case["seed"])]
        after = [event for index in range(1, histories - before_histories + 1) for event in distractor_events(case["id"], index, "after", case["seed"])]
        return before + [{"entity": case["entity"], "state": state} for state in case["updates"]] + after

    def count(histories: int) -> int:
        return runtime.count_prompt(render_natural(events_for(histories), case["entity"], definition))

    if count(0) > level:
        raise ContractError(f"{case['id']} cannot fit the shortest frozen source at {level}")
    low, high = 0, 1
    while count(high) <= level:
        low, high = high, high * 2
        if high > level:
            break
    while low + 1 < high:
        middle = (low + high) // 2
        if count(middle) <= level:
            low = middle
        else:
            high = middle
    def placement(before_histories: int) -> tuple[float, int, list[dict[str, str]], int]:
        events = events_for(low, before_histories)
        natural = render_natural(events, case["entity"], definition)
        actual = runtime.count_prompt(natural)
        context = "Context event log:\n" + "\n".join(definition["rendering"]["untreated_event_template"].format(entity=event["entity"], state=event["state"]) for event in events)
        prefix_events = events[:4 * before_histories]
        prefix = "Context event log:\n" + ("\n".join(definition["rendering"]["untreated_event_template"].format(entity=event["entity"], state=event["state"]) for event in prefix_events) + "\n" if prefix_events else "")
        ratio = runtime.count_text(prefix) / runtime.count_text(context)
        return abs(ratio - definition["workload"]["target_ratio"]), before_histories, events, actual
    def ratio_for(before_histories: int) -> float:
        events = events_for(low, before_histories)
        context = "Context event log:\n" + "\n".join(definition["rendering"]["untreated_event_template"].format(entity=event["entity"], state=event["state"]) for event in events)
        prefix_events = events[:4 * before_histories]
        prefix = "Context event log:\n" + ("\n".join(definition["rendering"]["untreated_event_template"].format(entity=event["entity"], state=event["state"]) for event in prefix_events) + "\n" if prefix_events else "")
        return runtime.count_text(prefix) / runtime.count_text(context)

    # The prefix-token ratio is monotone as histories move from after to before.
    left, right = 0, low
    while left < right:
        middle = (left + right) // 2
        if ratio_for(middle) < definition["workload"]["target_ratio"]:
            left = middle + 1
        else:
            right = middle
    candidate_indexes = {
        max(0, min(low, index))
        for index in (left - 2, left - 1, left, left + 1, left + 2, low // 2)
    }
    candidates = [candidate for candidate in (placement(index) for index in sorted(candidate_indexes)) if candidate[3] <= level]

    if not candidates:
        raise ContractError(f"{case['id']} has no feasible midpoint placement")
    _distance, before_histories, events, _actual = min(candidates, key=lambda row: row[0])
    natural, ledger = render_natural(events, case["entity"], definition), render_ledger(events, case["entity"], definition)
    actual, shortfall = runtime.count_prompt(natural), level - runtime.count_prompt(natural)
    if not 0 <= shortfall <= definition["workload"]["maximum_target_shortfall_tokens"]:
        raise ContractError(f"{case['id']}@{level}: natural token shortfall violates frozen contract")
    if actual + definition["runtime"]["output_tokens"] > definition["runtime"]["configured_context_size"]:
        raise ContractError(f"{case['id']}@{level}: natural source overflows configured context")
    validate_pair(case, events, natural, ledger, definition)
    return MaterializedCase(case["id"], case["origin"], level, case["entity"], case["answer"], case["updates"], events, source_event_hash(events), target_event_indexes(events, case["entity"]), low, before_histories, natural, ledger)


def materialize_inventory(runtime: TokenRuntime, definition: dict[str, Any] | None = None) -> dict[str, Any]:
    definition = definition or validate_definition()
    cases = frozen_cases() + fresh_cases(definition)
    validate_case_specs(definition, cases)
    materialized = [_materialized_dict(_build_for_level(runtime, case, level, definition)) for level in definition["workload"]["context_levels"] for case in cases]
    inventory = {"version": 1, "definition_fingerprint": definition_fingerprint(definition), "source_sizing_model": definition["workload"]["source_sizing_model"], "cases": materialized}
    inventory["inventory_fingerprint"] = inventory_fingerprint(inventory)
    return inventory


def _materialized_dict(value: MaterializedCase) -> dict[str, Any]:
    return {"case_id": value.case_id, "origin": value.origin, "requested_input_tokens": value.requested_input_tokens, "target": value.target, "expected_answer": value.expected_answer, "target_updates": value.target_updates, "source_events": value.source_events, "source_event_hash": value.source_event_hash, "target_event_indexes": value.target_event_indexes, "distractor_histories": value.distractor_histories, "distractor_histories_before": value.distractor_histories_before, "natural_prompt": value.natural_prompt, "ledger_prompt": value.ledger_prompt}


def inventory_fingerprint(inventory: dict[str, Any]) -> str:
    stable = {key: value for key, value in inventory.items() if key != "inventory_fingerprint"}
    return sha256_bytes(b"inventory.json\0" + canonical_json(stable))


def validate_inventory(inventory: dict[str, Any], runtime: TokenRuntime, definition: dict[str, Any] | None = None) -> None:
    definition = definition or validate_definition()
    if inventory.get("definition_fingerprint") != definition_fingerprint(definition) or inventory.get("inventory_fingerprint") != inventory_fingerprint(inventory):
        raise ContractError("inventory fingerprint mismatch")
    expected = materialize_inventory(runtime, definition)
    if inventory != expected:
        raise ContractError("inventory cannot be reconstructed from frozen definition")


def normalize_answer(raw: str) -> str:
    raw = unicodedata.normalize("NFKC", raw).strip()
    raw = re.sub(r"[.!?]+$", "", raw).strip()
    return " ".join(raw.casefold().split())


def evaluate(target: str, expected: str, raw: str) -> tuple[bool, str]:
    normalized = normalize_answer(raw)
    accepted = {normalize_answer(expected), normalize_answer(f"The current state of {target} is {expected}")}
    return normalized in accepted, normalized


def classify_output(target: str, expected: str, events: list[dict[str, str]], raw: str, error: dict[str, Any] | None = None) -> tuple[str, str | None, str]:
    if error:
        return "runtime_or_infrastructure_error", None, ""
    passed, normalized = evaluate(target, expected, raw)
    if passed:
        return "correct", None, normalized
    if not normalized.isalpha() or " " in normalized:
        return "malformed_response", None, normalized
    target_states = [event["state"] for event in events if event["entity"] == target]
    if normalized in {normalize_answer(value) for value in target_states[:-1]}:
        return "incorrect_state", "prior_target_state", normalized
    distractor_states = [event["state"] for event in events if event["entity"] != target]
    if normalized in {normalize_answer(value) for value in distractor_states}:
        return "incorrect_state", "distractor_state", normalized
    return "incorrect_state", "other_or_unknown_state", normalized


def validate_evaluator_fixtures() -> None:
    events = [{"entity": "Unit Test 1", "state": state} for state in ("RED", "BLUE", "GREEN", "AMBER")] + [{"entity": "Unit Drift 2", "state": "BLACK"}]
    expected = {"AMBER": ("correct", None), "The current state of Unit Test 1 is AMBER.": ("correct", None), "GREEN": ("incorrect_state", "prior_target_state"), "BLACK": ("incorrect_state", "distractor_state"), "": ("malformed_response", None), "answer: AMBER": ("malformed_response", None)}
    for raw, outcome in expected.items():
        failure, diagnostic, _normal = classify_output("Unit Test 1", "AMBER", events, raw)
        if (failure, diagnostic) != outcome:
            raise ContractError(f"evaluator fixture failed for {raw!r}")


def validate_frozen_failure_diagnostics() -> int:
    cases = {case["id"]: case for case in frozen_cases()}
    rows = [json.loads(line) for line in (ECC006_RUN / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    observed = 0
    for row in rows:
        if row.get("failure") != "incorrect_state":
            continue
        case = cases[row["case_id"]]
        events = []
        for index in range(1, row["distractor_histories_before"] + 1): events.extend(distractor_events(case["id"], index, "before", case["seed"]))
        events.extend({"entity": case["entity"], "state": state} for state in case["updates"])
        for index in range(1, row["distractor_histories"] - row["distractor_histories_before"] + 1): events.extend(distractor_events(case["id"], index, "after", case["seed"]))
        failure, diagnostic, _normal = classify_output(case["entity"], case["answer"], events, row["output"]["raw_text"])
        if failure != "incorrect_state" or diagnostic != "prior_target_state":
            raise ContractError(f"frozen diagnostic mismatch: {row['case_id']}@{row['requested_input_tokens']}")
        observed += 1
    if observed != 21:
        raise ContractError(f"expected 21 frozen incorrect-state rows, saw {observed}")
    return observed


def event_token_positions(runtime: TokenRuntime, prompt: str, condition: str, target_indexes: list[int], target: str, definition: dict[str, Any]) -> list[int]:
    lines = prompt.split("\n")
    starts: list[int] = []
    for source_index in target_indexes:
        line_index = source_index
        prefix = "\n".join(lines[:line_index])
        starts.append(runtime.count_text(prefix + ("\n" if prefix else "")))
    return starts


def preflight_inventory(client: TokenRuntime, inventory: dict[str, Any], model_key: str, definition: dict[str, Any] | None = None) -> dict[str, Any]:
    definition = definition or validate_definition()
    if model_key not in definition["models"]:
        raise ContractError(f"unknown model {model_key}")
    records: list[dict[str, Any]] = []
    overflow: list[str] = []
    for item in inventory["cases"]:
        pair: dict[str, Any] = {"case_id": item["case_id"], "requested_input_tokens": item["requested_input_tokens"], "source_event_hash": item["source_event_hash"], "model": model_key, "conditions": {}}
        for condition, key in (("natural_language", "natural_prompt"), ("ledger", "ledger_prompt")):
            prompt = item[key]
            actual, content = client.count_prompt(prompt), client.count_text(prompt)
            fits = actual + definition["runtime"]["output_tokens"] <= definition["runtime"]["configured_context_size"]
            pair["conditions"][condition] = {"prompt_hash": sha256_text(prompt), "actual_prompt_tokens": actual, "content_tokens": content, "prompt_overhead_tokens": actual - content, "target_event_token_positions": event_token_positions(client, prompt, condition, item["target_event_indexes"], item["target"], definition), "fits_with_output_allowance": fits}
            if not fits:
                overflow.append(f"{model_key}:{item['case_id']}@{item['requested_input_tokens']}:{condition}:{actual}+{definition['runtime']['output_tokens']}")
        pair["token_delta_ledger_minus_natural"] = pair["conditions"]["ledger"]["actual_prompt_tokens"] - pair["conditions"]["natural_language"]["actual_prompt_tokens"]
        records.append(pair)
    return {"definition_fingerprint": definition_fingerprint(definition), "inventory_fingerprint": inventory["inventory_fingerprint"], "model": model_key, "configured_context_size": definition["runtime"]["configured_context_size"], "output_tokens": definition["runtime"]["output_tokens"], "records": records, "status": "feasible" if not overflow else "contract_not_executable", "overflow": overflow}


def validate_request_record(record: dict[str, Any]) -> None:
    errors = schema_errors(record, "request-result.schema.json")
    if errors:
        raise ContractError(f"request/result schema failure: {errors[0]}")

