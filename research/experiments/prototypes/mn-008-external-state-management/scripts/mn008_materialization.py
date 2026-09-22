"""Static deterministic MN-008 corpus materializer and preflight validator.

This module creates prospective workload definitions for MN-008 Gate C Phase 1.
It implements the Latin Square counterbalanced 24-case corpus, deterministic
host state replay, scoped snapshot extraction, and prompt formatting for Arms A, B, and C.
It has no runtime inference or network dependencies.
"""
from __future__ import annotations

import json
import unicodedata
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Any

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DEFINITION_ROOT = EXPERIMENT_ROOT / "definition" / "corpus-v1"

CONTRACT_NAMESPACE = "mn008-measurement-contract-v1"
CORPUS_NAMESPACE = "mn008-corpus-v1"
SEMANTIC_SCHEMA = "mn008-semantic-case-v1"
PUBLIC_SCHEMA = "mn008-public-prompt-v1"
EVALUATOR_SCHEMA = "mn008-evaluator-oracle-v1"
MANIFEST_SCHEMA = "mn008-manifest-v1"

ROOT_SEED_TEXT = "mn008-external-state-management|corpus|measurement-contract-v1|root-seed"
SEED_PREFIX = "MN008-SEED-V1"
US = "\x1f"

CASE_COUNT = 24
UPDATES_PER_ENTITY = 3
ENTITY_COUNT = 5
ACTIVE_ENTITIES = ("E1", "E2", "E3", "E4", "E5")
QUERIED_ENTITIES = ("E1", "E2")

STATE_VOCABULARY = ("S0", "S1")
INITIAL_STATE = "S0"
STATE_PAIRS = (("S0", "S0"), ("S0", "S1"), ("S1", "S0"), ("S1", "S1"))
ACTION_VOCABULARY = ("ACTION_0", "ACTION_1", "ACTION_2", "ACTION_3")

ARM_B_GRAMMAR_ID = "mn008-arm-b-neutral-padding-v1"
ARM_B_GRAMMAR = (
    'root ::= line "\\n" line "\\n" line "\\n" line\n'
    'line ::= "pad=" token (" " token)*\n'
    'token ::= "KAPPA" | "LAMBDA" | "MU" | "NU" | "XI" | "OMICRON" | "PI" | "RHO"\n'
)
EVALUATION_REGEX = r"\b(ACTION_[0-3])\b"
MAX_ARM_C_PROMPT_TOKENS = 100

ARTIFACT_FILENAMES = (
    "semantic-cases.jsonl",
    "public-prompts.jsonl",
    "evaluator-records.jsonl",
    "manifest.json",
)

HISTORIES_S0 = (
    ("S1", "S0", "S0"),
    ("S0", "S1", "S0"),
    ("S1", "S1", "S0"),
)
HISTORIES_S1 = (
    ("S0", "S0", "S1"),
    ("S1", "S0", "S1"),
    ("S0", "S1", "S1"),
    ("S1", "S1", "S1"),
)


class MaterializationError(ValueError):
    """Raised when immutable MN-008 construction requirements are violated."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MaterializationError(message)


def _normalized(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_normalized(item) for item in value]
    if isinstance(value, tuple):
        return [_normalized(item) for item in value]
    if isinstance(value, Mapping):
        return {
            unicodedata.normalize("NFC", str(key)): _normalized(item)
            for key, item in value.items()
        }
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Return contract-defined JSON bytes: UTF-8, sorted keys, compact, final LF."""
    return (
        json.dumps(
            _normalized(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def canonical_jsonl_bytes(records: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(record) for record in records)


def sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def root_seed_sha256() -> str:
    return sha256_bytes(ROOT_SEED_TEXT.encode("utf-8"))


def seed_digest(
    *,
    case_ordinal: int,
    entity: str,
    purpose: str,
    candidate: str = "",
) -> str:
    fields = (
        SEED_PREFIX,
        ROOT_SEED_TEXT,
        f"{case_ordinal:02d}",
        entity,
        purpose,
        candidate,
    )
    preimage = US.join(fields).encode("utf-8")
    return sha256_bytes(preimage)


def case_public_id(case_ordinal: int) -> str:
    _require(0 <= case_ordinal < CASE_COUNT, f"invalid case ordinal: {case_ordinal}")
    return f"mn008-case-{case_ordinal + 1:04d}"


def get_counterbalanced_mapping(case_ordinal: int) -> dict[tuple[str, str], str]:
    """Deterministically permute action labels across cases via Latin Square shift."""
    shift = case_ordinal % 4
    shifted_actions = ACTION_VOCABULARY[shift:] + ACTION_VOCABULARY[:shift]
    return dict(zip(STATE_PAIRS, shifted_actions, strict=True))


def get_case_target_pair_and_action(case_ordinal: int) -> tuple[tuple[str, str], str, int]:
    """Return target state pair, target action token, and pair index for case ordinal."""
    _require(0 <= case_ordinal < CASE_COUNT, f"invalid case ordinal: {case_ordinal}")
    wave = case_ordinal // 4
    slot = case_ordinal % 4
    pair_idx = (wave + slot) % 4
    target_pair = STATE_PAIRS[pair_idx]
    mapping = get_counterbalanced_mapping(case_ordinal)
    target_action = mapping[target_pair]
    return target_pair, target_action, pair_idx


def host_replay(events: Iterable[Mapping[str, Any]], entities: Iterable[str] = ACTIVE_ENTITIES) -> dict[str, str]:
    """Deterministic host state engine replay (O(N_events) time, O(E) space)."""
    state = {entity: INITIAL_STATE for entity in entities}
    for event in events:
        entity = str(event["entity_id"])
        assigned = str(event["assigned_state"])
        _require(entity in state, f"unknown entity in event: {entity}")
        _require(assigned in STATE_VOCABULARY, f"invalid state in event: {assigned}")
        state[entity] = assigned
    return state


def host_scoped_snapshot(
    events: Iterable[Mapping[str, Any]],
    queried_entities: tuple[str, str] = QUERIED_ENTITIES,
) -> str:
    """Extract minimal scoped snapshot for queried entities (O(1) memory lookup)."""
    state = host_replay(events, ACTIVE_ENTITIES)
    q1, q2 = queried_entities
    _require(q1 in state and q2 in state, "queried entity not in active state")
    return f"{q1}={state[q1]}; {q2}={state[q2]}"


def render_canonical_rules(
    mapping: dict[tuple[str, str], str],
    q1: str = "E1",
    q2: str = "E2",
) -> list[str]:
    """Render decision rules in the frozen canonical order of STATE_PAIRS."""
    rules = []
    for s1, s2 in STATE_PAIRS:
        action = mapping[(s1, s2)]
        rules.append(f"- IF {q1}={s1} AND {q2}={s2} THEN {action}")
    return rules


def render_arm_a_prompt(
    events: list[dict[str, Any]],
    mapping: dict[tuple[str, str], str],
    q1: str = "E1",
    q2: str = "E2",
) -> str:
    """Arm A prompt: raw events + canonical decision rules + query."""
    lines = ["All entities begin in S0.", "[EVENTS]"]
    lines.extend(f"{ev['entity_id']} STATE = {ev['assigned_state']}" for ev in events)
    lines.append("")
    lines.append("[DECISION RULES]")
    lines.extend(render_canonical_rules(mapping, q1, q2))
    lines.append("")
    lines.append("Action:")
    return "\n".join(lines) + "\n"


def render_arm_b_stage1_prompt(events: list[dict[str, Any]]) -> str:
    """Arm B Stage 1 prompt: raw events + neutral padding instruction."""
    lines = ["All entities begin in S0.", "[EVENTS]"]
    lines.extend(f"{ev['entity_id']} STATE = {ev['assigned_state']}" for ev in events)
    lines.append("")
    lines.append("Generate a 4-line padding block conforming to the neutral token format:")
    return "\n".join(lines) + "\n"


def render_arm_b_stage2_template(
    mapping: dict[tuple[str, str], str],
    q1: str = "E1",
    q2: str = "E2",
) -> str:
    """Arm B Stage 2 prompt template awaiting intermediate summary."""
    lines = ["[INTERMEDIATE SUMMARY]", "{intermediate_summary}", "", "[DECISION RULES]"]
    lines.extend(render_canonical_rules(mapping, q1, q2))
    lines.append("")
    lines.append("Action:")
    return "\n".join(lines) + "\n"


def render_arm_b_stage2_prompt(
    intermediate_summary: str,
    mapping: dict[tuple[str, str], str],
    q1: str = "E1",
    q2: str = "E2",
) -> str:
    """Arm B Stage 2 prompt: instantiated with actual Stage 1 output."""
    return render_arm_b_stage2_template(mapping, q1, q2).format(
        intermediate_summary=intermediate_summary.strip()
    )


def render_arm_c_stage2_prompt(
    snapshot: str,
    mapping: dict[tuple[str, str], str],
    q1: str = "E1",
    q2: str = "E2",
) -> str:
    """Arm C Stage 2 prompt: scoped snapshot + canonical decision rules + query."""
    lines = ["[STATE SNAPSHOT]", snapshot, "", "[DECISION RULES]"]
    lines.extend(render_canonical_rules(mapping, q1, q2))
    lines.append("")
    lines.append("Action:")
    return "\n".join(lines) + "\n"


def generate_case_events(
    case_ordinal: int,
    target_pair: tuple[str, str],
) -> tuple[list[dict[str, Any]], dict[str, tuple[str, str, str]]]:
    """Generate deterministic interleaved event stream and entity histories."""
    finals: dict[str, str] = {
        QUERIED_ENTITIES[0]: target_pair[0],
        QUERIED_ENTITIES[1]: target_pair[1],
    }
    for entity in ACTIVE_ENTITIES:
        if entity not in finals:
            finals[entity] = min(
                STATE_VOCABULARY,
                key=lambda s: seed_digest(
                    case_ordinal=case_ordinal,
                    entity=entity,
                    purpose="final-state-rank",
                    candidate=s,
                ),
            )

    histories: dict[str, tuple[str, str, str]] = {}
    for entity in ACTIVE_ENTITIES:
        candidates = HISTORIES_S0 if finals[entity] == "S0" else HISTORIES_S1
        histories[entity] = min(
            candidates,
            key=lambda h: seed_digest(
                case_ordinal=case_ordinal,
                entity=entity,
                purpose="history-rank",
                candidate=",".join(h),
            ),
        )

    events: list[dict[str, Any]] = []
    event_ordinal = 1
    for round_idx in range(UPDATES_PER_ENTITY):
        for entity in ACTIVE_ENTITIES:
            events.append(
                {
                    "assigned_state": histories[entity][round_idx],
                    "entity_id": entity,
                    "event_ordinal": event_ordinal,
                    "history_ordinal": round_idx + 1,
                }
            )
            event_ordinal += 1

    _require(len(events) == ENTITY_COUNT * UPDATES_PER_ENTITY, "event count mismatch")
    return events, histories


def build_case_records(
    case_ordinal: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build semantic, public prompt, and evaluator records for a single case."""
    case_id = case_public_id(case_ordinal)
    target_pair, target_action, pair_idx = get_case_target_pair_and_action(case_ordinal)
    mapping = get_counterbalanced_mapping(case_ordinal)

    events, histories = generate_case_events(case_ordinal, target_pair)

    replayed = host_replay(events, ACTIVE_ENTITIES)
    _require(
        replayed[QUERIED_ENTITIES[0]] == target_pair[0],
        f"{case_id}: E1 replay mismatch",
    )
    _require(
        replayed[QUERIED_ENTITIES[1]] == target_pair[1],
        f"{case_id}: E2 replay mismatch",
    )

    snapshot = host_scoped_snapshot(events, QUERIED_ENTITIES)
    expected_snapshot = f"{QUERIED_ENTITIES[0]}={target_pair[0]}; {QUERIED_ENTITIES[1]}={target_pair[1]}"
    _require(snapshot == expected_snapshot, f"{case_id}: snapshot mismatch")

    # Verify anti-tautology: snapshot must not contain action tokens
    for action in ACTION_VOCABULARY:
        _require(action not in snapshot, f"{case_id}: action token leak in snapshot")

    arm_a_prompt = render_arm_a_prompt(events, mapping)
    arm_b_stage1_prompt = render_arm_b_stage1_prompt(events)
    arm_b_stage2_template = render_arm_b_stage2_template(mapping)
    arm_c_stage2_prompt = render_arm_c_stage2_prompt(snapshot, mapping)

    rule_mapping_serializable = {
        f"{p[0]},{p[1]}": act for p, act in mapping.items()
    }

    semantic_record = {
        "active_entities": list(ACTIVE_ENTITIES),
        "case_id": case_id,
        "case_ordinal": case_ordinal,
        "difficulty": {
            "entity_count": ENTITY_COUNT,
            "event_count": len(events),
            "queried_entity_count": len(QUERIED_ENTITIES),
            "updates_per_entity": UPDATES_PER_ENTITY,
        },
        "entity_histories": {e: list(h) for e, h in histories.items()},
        "event_stream": events,
        "host_snapshot": snapshot,
        "initial_state": INITIAL_STATE,
        "pair_idx": pair_idx,
        "queried_entities": list(QUERIED_ENTITIES),
        "rule_mapping": rule_mapping_serializable,
        "schema_id": SEMANTIC_SCHEMA,
        "shift": case_ordinal % 4,
        "target_action": target_action,
        "target_pair": list(target_pair),
        "wave": case_ordinal // 4,
    }

    public_prompt_record = {
        "arm_a_prompt": arm_a_prompt,
        "arm_a_prompt_sha256": sha256_bytes(arm_a_prompt.encode("utf-8")),
        "arm_b_grammar": ARM_B_GRAMMAR,
        "arm_b_grammar_id": ARM_B_GRAMMAR_ID,
        "arm_b_stage1_prompt": arm_b_stage1_prompt,
        "arm_b_stage1_prompt_sha256": sha256_bytes(arm_b_stage1_prompt.encode("utf-8")),
        "arm_b_stage2_template": arm_b_stage2_template,
        "arm_c_stage2_prompt": arm_c_stage2_prompt,
        "arm_c_stage2_prompt_sha256": sha256_bytes(arm_c_stage2_prompt.encode("utf-8")),
        "case_id": case_id,
        "case_ordinal": case_ordinal,
        "schema_id": PUBLIC_SCHEMA,
    }

    evaluator_record = {
        "case_id": case_id,
        "case_ordinal": case_ordinal,
        "evaluation_regex": EVALUATION_REGEX,
        "rule_mapping": rule_mapping_serializable,
        "schema_id": EVALUATOR_SCHEMA,
        "target_action": target_action,
        "target_pair": list(target_pair),
    }

    return semantic_record, public_prompt_record, evaluator_record


def build_entire_corpus() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build all 24 cases and verify balance properties."""
    semantic_records: list[dict[str, Any]] = []
    public_records: list[dict[str, Any]] = []
    evaluator_records: list[dict[str, Any]] = []

    for case_ordinal in range(CASE_COUNT):
        sem, pub, eva = build_case_records(case_ordinal)
        semantic_records.append(sem)
        public_records.append(pub)
        evaluator_records.append(eva)

    # Balance verification
    pair_counts = Counter(tuple(rec["target_pair"]) for rec in semantic_records)
    action_counts = Counter(rec["target_action"] for rec in semantic_records)

    _require(len(semantic_records) == CASE_COUNT, "corpus size mismatch")
    _require(
        all(pair_counts[p] == 6 for p in STATE_PAIRS),
        f"state pair balance failed: {pair_counts}",
    )
    _require(
        all(action_counts[a] == 6 for a in ACTION_VOCABULARY),
        f"action target balance failed: {action_counts}",
    )

    return semantic_records, public_records, evaluator_records


def materialize_corpus(output_dir: Path = DEFINITION_ROOT) -> dict[str, Any]:
    """Materialize corpus files to disk with canonical bytes and SHA-256 manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)

    semantic_records, public_records, evaluator_records = build_entire_corpus()

    semantic_bytes = canonical_jsonl_bytes(semantic_records)
    public_bytes = canonical_jsonl_bytes(public_records)
    evaluator_bytes = canonical_jsonl_bytes(evaluator_records)

    (output_dir / "semantic-cases.jsonl").write_bytes(semantic_bytes)
    (output_dir / "public-prompts.jsonl").write_bytes(public_bytes)
    (output_dir / "evaluator-records.jsonl").write_bytes(evaluator_bytes)

    file_hashes = {
        "evaluator-records.jsonl": sha256_bytes(evaluator_bytes),
        "public-prompts.jsonl": sha256_bytes(public_bytes),
        "semantic-cases.jsonl": sha256_bytes(semantic_bytes),
    }

    manifest = {
        "case_count": CASE_COUNT,
        "corpus_id": CORPUS_NAMESPACE,
        "difficulty": {
            "entity_count": ENTITY_COUNT,
            "events_per_case": ENTITY_COUNT * UPDATES_PER_ENTITY,
            "queried_entities": list(QUERIED_ENTITIES),
            "updates_per_entity": UPDATES_PER_ENTITY,
        },
        "file_hashes": file_hashes,
        "latin_square": {
            "action_counts": {a: 6 for a in ACTION_VOCABULARY},
            "order": 4,
            "state_pair_counts": {f"{p[0]},{p[1]}": 6 for p in STATE_PAIRS},
            "waves": 6,
        },
        "root_seed_sha256": root_seed_sha256(),
        "schema_id": MANIFEST_SCHEMA,
    }

    manifest_bytes = canonical_json_bytes(manifest)
    (output_dir / "manifest.json").write_bytes(manifest_bytes)

    return manifest


def validate_corpus(corpus_dir: Path = DEFINITION_ROOT) -> dict[str, Any]:
    """Validate physical corpus artifacts against contract rules and manifest."""
    manifest_path = corpus_dir / "manifest.json"
    _require(manifest_path.exists(), "missing manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    _require(manifest.get("case_count") == CASE_COUNT, "invalid case count in manifest")
    _require(manifest.get("root_seed_sha256") == root_seed_sha256(), "root seed mismatch")

    for filename, expected_hash in manifest["file_hashes"].items():
        filepath = corpus_dir / filename
        _require(filepath.exists(), f"missing file: {filename}")
        actual_hash = sha256_file(filepath)
        _require(
            actual_hash == expected_hash,
            f"hash mismatch for {filename}: expected {expected_hash}, got {actual_hash}",
        )

    # Validate semantic records
    sem_path = corpus_dir / "semantic-cases.jsonl"
    sem_lines = [json.loads(line) for line in sem_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    _require(len(sem_lines) == CASE_COUNT, "semantic records count mismatch")

    pair_counts = Counter(tuple(r["target_pair"]) for r in sem_lines)
    action_counts = Counter(r["target_action"] for r in sem_lines)
    _require(all(pair_counts[p] == 6 for p in STATE_PAIRS), "state pair imbalance")
    _require(all(action_counts[a] == 6 for a in ACTION_VOCABULARY), "action target imbalance")

    # Validate public prompts
    pub_path = corpus_dir / "public-prompts.jsonl"
    pub_lines = [json.loads(line) for line in pub_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    _require(len(pub_lines) == CASE_COUNT, "public prompts count mismatch")

    # Validate evaluator records
    eva_path = corpus_dir / "evaluator-records.jsonl"
    eva_lines = [json.loads(line) for line in eva_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    _require(len(eva_lines) == CASE_COUNT, "evaluator records count mismatch")

    return {
        "status": "VALID",
        "case_count": len(sem_lines),
        "manifest_sha256": sha256_file(manifest_path),
        "file_hashes": manifest["file_hashes"],
    }
