"""Static deterministic MN-007 calibration-corpus materializer and validator.

This module creates prospective workload definitions only. It has no model,
network, subprocess, runtime, or measured-evidence path.
"""
from __future__ import annotations

import json
import unicodedata
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Any, TypeVar

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = EXPERIMENT_ROOT / "materialization-contract.md"
DEFINITION_ROOT = EXPERIMENT_ROOT / "definition" / "calibration-corpus-v1"

CONTRACT_NAMESPACE = "mn007-materialization-contract-v1"
CALIBRATION_NAMESPACE = "mn007-calibration-v1"
SEMANTIC_SCHEMA = "mn007-semantic-case-v1"
PUBLIC_SCHEMA = "mn007-public-prompt-v1"
EVALUATOR_SCHEMA = "mn007-evaluator-oracle-v1"
ROOT_SEED_TEXT = (
    "mn007-state-recovery-operating-region|calibration|"
    "materialization-contract-v1|root-seed"
)
SEED_PREFIX = "MN007-SEED-V1"
US = "\x1f"
STATE_VOCABULARY = ("S0", "S1", "S2")
INITIAL_STATE = "S0"
UPDATES_PER_ENTITY = 3
GRAMMAR_ID = "mn007-bare-ordered-two-state-vector-v1"
GRAMMAR = 'root ::= state "," state\nstate ::= "S0" | "S1" | "S2"\n'
ARTIFACT_FILENAMES = (
    "semantic-cases.jsonl",
    "public-prompts.jsonl",
    "evaluator-records.jsonl",
    "manifest.json",
)


class MaterializationError(ValueError):
    """Raised when immutable MN-007 construction requirements are violated."""


@dataclass(frozen=True)
class Cell:
    entity_count: int
    placement: str
    source_query_blocks: tuple[int, int]
    source_distances: tuple[int, int]

    @property
    def cell_id(self) -> str:
        return f"{CALIBRATION_NAMESPACE}-e{self.entity_count}-{self.placement}"


CELLS = (
    Cell(3, "terminal", (2, 3), (3, 0)),
    Cell(3, "leading", (1, 2), (6, 3)),
    Cell(5, "terminal", (4, 5), (3, 0)),
    Cell(5, "leading", (1, 2), (12, 9)),
    Cell(7, "terminal", (6, 7), (3, 0)),
    Cell(7, "leading", (1, 2), (18, 15)),
)
VECTOR_ORDER = tuple(product(STATE_VOCABULARY, repeat=2))


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


def parse_vector(raw_output: str) -> tuple[str, str] | None:
    """Parse exactly the frozen bare ordered-vector grammar."""
    if not isinstance(raw_output, str):
        return None
    candidate = raw_output.strip(" \t\n\r\f\v")
    parts = candidate.split(",")
    if len(parts) != 2 or any(part not in STATE_VOCABULARY for part in parts):
        return None
    return (parts[0], parts[1])


def cell_case_id(cell: Cell, cell_ordinal: int) -> str:
    _require(1 <= cell_ordinal <= 18, "case ordinal must be 01 through 18")
    return f"{cell.cell_id}-c{cell_ordinal:02d}"


def vector_slot(cell_ordinal: int) -> int:
    _require(1 <= cell_ordinal <= 18, "case ordinal must be 01 through 18")
    return (cell_ordinal - 1) % len(VECTOR_ORDER)


def orientation_for(cell_ordinal: int) -> str:
    _require(1 <= cell_ordinal <= 18, "case ordinal must be 01 through 18")
    return "source_order" if cell_ordinal <= 9 else "reverse_source_order"


def _seed_preimage(
    *,
    scope: str,
    cell_id: str,
    pair_slot: int,
    case_ordinal: int,
    purpose: str,
    candidate: str | None = None,
) -> bytes:
    _require(scope in {"case-pair", "case"}, "seed scope differs from contract")
    _require(0 <= pair_slot <= 8, "pair slot differs from contract")
    if scope == "case-pair":
        _require(case_ordinal == 0, "case-pair seed must use ordinal sentinel 00")
    else:
        _require(1 <= case_ordinal <= 18, "case seed ordinal differs from contract")
    fields = (
        SEED_PREFIX,
        ROOT_SEED_TEXT,
        scope,
        cell_id,
        f"{pair_slot:02d}",
        f"{case_ordinal:02d}",
        purpose,
    )
    preimage = US.join(fields)
    if candidate is not None:
        preimage += US + candidate
    return preimage.encode("utf-8")


def seed_digest(
    *,
    scope: str,
    cell_id: str,
    pair_slot: int,
    case_ordinal: int,
    purpose: str,
    candidate: str | None = None,
) -> str:
    return sha256_bytes(
        _seed_preimage(
            scope=scope,
            cell_id=cell_id,
            pair_slot=pair_slot,
            case_ordinal=case_ordinal,
            purpose=purpose,
            candidate=candidate,
        )
    )


T = TypeVar("T")


def _ranked(
    candidates: Iterable[T],
    signature: Callable[[T], str],
    **seed_kwargs: Any,
) -> list[T]:
    return sorted(
        candidates,
        key=lambda candidate: (
            seed_digest(candidate=signature(candidate), **seed_kwargs),
            signature(candidate),
        ),
    )


def _active_entities(entity_count: int) -> tuple[str, ...]:
    _require(entity_count in {3, 5, 7}, "entity count differs from frozen landscape")
    return tuple(f"E{ordinal:02d}" for ordinal in range(1, entity_count + 1))


def _source_permutation(cell: Cell, pair_slot: int) -> tuple[str, ...]:
    return tuple(
        _ranked(
            _active_entities(cell.entity_count),
            lambda entity: f"entity:{entity}",
            scope="case-pair",
            cell_id=cell.cell_id,
            pair_slot=pair_slot,
            case_ordinal=0,
            purpose="entity-rank",
        )
    )


def _block_order(cell: Cell, permutation: tuple[str, ...]) -> tuple[str, ...]:
    q1, q2, *non_query = permutation
    if cell.placement == "terminal":
        return (*non_query, q1, q2)
    _require(cell.placement == "leading", "unknown frozen placement")
    return (q1, q2, *non_query)


def _all_histories() -> tuple[tuple[str, str, str], ...]:
    return tuple(
        history
        for history in product(STATE_VOCABULARY, repeat=UPDATES_PER_ENTITY)
        if history[0] != INITIAL_STATE
        and history[1] != history[0]
        and history[2] != history[1]
    )


HISTORY_CANDIDATES = _all_histories()


def _rank_histories(
    *,
    cell: Cell,
    pair_slot: int,
    case_ordinal: int,
    entity: str,
    final_state: str | None,
    queried: bool,
) -> list[tuple[str, str, str]]:
    candidates = [
        history
        for history in HISTORY_CANDIDATES
        if final_state is None or history[-1] == final_state
    ]
    _require(candidates, "no admissible direct-assignment history")
    purpose = "queried-history-rank" if queried else "non-query-history-rank"
    return _ranked(
        candidates,
        lambda history: f"entity:{entity}|history:{','.join(history)}",
        scope="case",
        cell_id=cell.cell_id,
        pair_slot=pair_slot,
        case_ordinal=case_ordinal,
        purpose=purpose,
    )


def replay(events: Iterable[Mapping[str, Any]], entities: Iterable[str]) -> dict[str, str]:
    state = {entity: INITIAL_STATE for entity in entities}
    for event in events:
        entity = str(event["entity_id"])
        assigned = str(event["assigned_state"])
        _require(entity in state and assigned in STATE_VOCABULARY, "event falls outside semantic vocabulary")
        state[entity] = assigned
    return state


def _choose_histories(
    *,
    cell: Cell,
    pair_slot: int,
    case_ordinal: int,
    active_entities: tuple[str, ...],
    source_queries: tuple[str, str],
    source_query_finals: tuple[str, str],
) -> dict[str, tuple[str, str, str]]:
    query_final_by_entity = dict(zip(source_queries, source_query_finals, strict=True))
    candidate_lists = [
        _rank_histories(
            cell=cell,
            pair_slot=pair_slot,
            case_ordinal=case_ordinal,
            entity=entity,
            final_state=query_final_by_entity.get(entity),
            queried=entity in query_final_by_entity,
        )
        for entity in active_entities
    ]
    for selected in product(*candidate_lists):
        counts = Counter(value for history in selected for value in history)
        if counts == Counter({state: cell.entity_count for state in STATE_VOCABULARY}):
            return dict(zip(active_entities, selected, strict=True))
    raise MaterializationError("no balanced history product exists; contract forbids resampling")


def _render_prompt(events: list[dict[str, Any]], query_entities: tuple[str, str]) -> str:
    first, second = query_entities
    lines = ["All entities begin in S0."]
    lines.extend(f"{event['entity_id']} STATE = {event['assigned_state']}" for event in events)
    lines.extend(
        (
            f"For {first} and {second}, output their final states in this order.",
            "Output exactly two state tokens from S0, S1, S2 separated by one comma.",
        )
    )
    return "\n".join(lines) + "\n"


def _semantic_core(
    *,
    cell: Cell,
    global_ordinal: int,
    cell_ordinal: int,
) -> tuple[dict[str, Any], str]:
    pair_slot = vector_slot(cell_ordinal)
    orientation = orientation_for(cell_ordinal)
    expected_vector = VECTOR_ORDER[pair_slot]
    permutation = _source_permutation(cell, pair_slot)
    source_queries = (permutation[0], permutation[1])
    query_entities = (
        source_queries if orientation == "source_order" else tuple(reversed(source_queries))
    )
    source_query_finals = (
        expected_vector
        if orientation == "source_order"
        else tuple(reversed(expected_vector))
    )
    active_entities = _active_entities(cell.entity_count)
    histories = _choose_histories(
        cell=cell,
        pair_slot=pair_slot,
        case_ordinal=cell_ordinal,
        active_entities=active_entities,
        source_queries=source_queries,
        source_query_finals=source_query_finals,
    )
    block_order = _block_order(cell, permutation)
    events = [
        {
            "assigned_state": history_value,
            "entity_id": entity,
            "event_ordinal": event_ordinal,
            "history_ordinal": history_ordinal,
        }
        for event_ordinal, (entity, history_ordinal, history_value) in enumerate(
            (
                (entity, history_ordinal, histories[entity][history_ordinal - 1])
                for entity in block_order
                for history_ordinal in range(1, UPDATES_PER_ENTITY + 1)
            ),
            start=1,
        )
    ]
    replayed = replay(events, active_entities)
    query_final_states = tuple(replayed[entity] for entity in query_entities)
    _require(query_final_states == expected_vector, "replay differs from expected vector")
    source_final_states = tuple(replayed[entity] for entity in source_queries)
    source_block_positions = tuple(block_order.index(entity) + 1 for entity in source_queries)
    source_distances = tuple(
        UPDATES_PER_ENTITY * cell.entity_count - UPDATES_PER_ENTITY * block
        for block in source_block_positions
    )
    _require(source_block_positions == cell.source_query_blocks, "source query blocks differ")
    _require(source_distances == cell.source_distances, "latest-update distances differ")
    query_order_distances = (
        source_distances
        if orientation == "source_order"
        else tuple(reversed(source_distances))
    )
    state_counts = Counter(event["assigned_state"] for event in events)
    _require(
        state_counts == Counter({state: cell.entity_count for state in STATE_VOCABULARY}),
        "per-case assignment balance differs",
    )
    provenance = {
        "entity_rank_seed_sha256": seed_digest(
            scope="case-pair",
            cell_id=cell.cell_id,
            pair_slot=pair_slot,
            case_ordinal=0,
            purpose="entity-rank",
        ),
        "expected_vector_seed_sha256": seed_digest(
            scope="case",
            cell_id=cell.cell_id,
            pair_slot=pair_slot,
            case_ordinal=cell_ordinal,
            purpose="expected-vector",
        ),
        "history_seed_purpose": {
            "non_query": "non-query-history-rank",
            "queried": "queried-history-rank",
        },
        "query_orientation_seed_sha256": seed_digest(
            scope="case",
            cell_id=cell.cell_id,
            pair_slot=pair_slot,
            case_ordinal=cell_ordinal,
            purpose="query-orientation",
        ),
        "root_seed_sha256": root_seed_sha256(),
        "root_seed_text": ROOT_SEED_TEXT,
    }
    core = {
        "active_entities": list(active_entities),
        "assignment_histories": {entity: list(histories[entity]) for entity in active_entities},
        "case_id": cell_case_id(cell, cell_ordinal),
        "cell_id": cell.cell_id,
        "cell_ordinal": cell_ordinal,
        "difficulty": {
            "entity_count": cell.entity_count,
            "event_count": cell.entity_count * UPDATES_PER_ENTITY,
            "latest_update_distances": list(source_distances),
            "non_query_entity_count": cell.entity_count - 2,
            "placement": cell.placement,
            "updates_per_entity": UPDATES_PER_ENTITY,
        },
        "event_stream": events,
        "global_ordinal": global_ordinal,
        "initial_state": INITIAL_STATE,
        "query_entities": list(query_entities),
        "query_final_states": list(query_final_states),
        "query_order_latest_update_distances": list(query_order_distances),
        "query_orientation": orientation,
        "schema_id": SEMANTIC_SCHEMA,
        "seed_provenance": provenance,
        "source_block_order": list(block_order),
        "source_final_states": list(source_final_states),
        "source_query_entities": list(source_queries),
        "state_assignment_counts": {state: state_counts[state] for state in STATE_VOCABULARY},
        "state_vocabulary": list(STATE_VOCABULARY),
        "updates_per_entity": UPDATES_PER_ENTITY,
        "vector_slot": pair_slot,
    }
    semantic_history_id = f"mn007-sem-v1-{sha256_bytes(canonical_json_bytes(core))}"
    return core, semantic_history_id


def generate_case(cell: Cell, global_ordinal: int, cell_ordinal: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Construct one semantic case, public prompt record, and evaluator record."""
    core, semantic_history_id = _semantic_core(
        cell=cell,
        global_ordinal=global_ordinal,
        cell_ordinal=cell_ordinal,
    )
    prompt = _render_prompt(core["event_stream"], tuple(core["query_entities"]))
    prompt_bytes = prompt.encode("utf-8")
    _require(b"\r\n" not in prompt_bytes and not prompt_bytes.startswith(b"\xef\xbb\xbf"), "public prompt serialization differs")
    public = {
        "case_id": core["case_id"],
        "grammar": GRAMMAR,
        "grammar_id": GRAMMAR_ID,
        "prompt": prompt,
        "prompt_sha256": sha256_bytes(prompt_bytes),
        "schema_id": PUBLIC_SCHEMA,
    }
    semantic = {
        **core,
        "public_prompt_fingerprint": public["prompt_sha256"],
        "semantic_history_id": semantic_history_id,
    }
    evaluator = {
        "case_id": core["case_id"],
        "expected_vector": core["query_final_states"],
        "parser": {
            "accepted_form": "STATE,STATE",
            "grammar_id": GRAMMAR_ID,
            "state_vocabulary": list(STATE_VOCABULARY),
            "trim": "leading/trailing ASCII whitespace only",
        },
        "schema_id": EVALUATOR_SCHEMA,
    }
    return semantic, public, evaluator


def generate_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    semantic: list[dict[str, Any]] = []
    public: list[dict[str, Any]] = []
    evaluator: list[dict[str, Any]] = []
    global_ordinal = 1
    for cell in CELLS:
        for cell_ordinal in range(1, 19):
            semantic_record, public_record, evaluator_record = generate_case(
                cell,
                global_ordinal,
                cell_ordinal,
            )
            semantic.append(semantic_record)
            public.append(public_record)
            evaluator.append(evaluator_record)
            global_ordinal += 1
    validate_records(semantic, public, evaluator)
    return semantic, public, evaluator


def _assert_prompt_boundary(semantic: Mapping[str, Any], public: Mapping[str, Any]) -> None:
    prompt = str(public["prompt"])
    _require(public["case_id"] == semantic["case_id"], "semantic/public join differs")
    _require(public["grammar"] == GRAMMAR and public["grammar_id"] == GRAMMAR_ID, "public grammar differs")
    _require(prompt == _render_prompt(list(semantic["event_stream"]), tuple(semantic["query_entities"])), "public prompt differs from semantic renderer")
    _require(str(semantic["public_prompt_fingerprint"]) == sha256_bytes(prompt.encode("utf-8")), "prompt fingerprint differs")
    forbidden_values = [
        str(semantic["case_id"]),
        str(semantic["difficulty"]["placement"]),
        str(semantic["semantic_history_id"]),
        str(semantic["seed_provenance"]["root_seed_text"]),
        str(semantic["query_final_states"][0]) + "," + str(semantic["query_final_states"][1]),
    ]
    for value in forbidden_values:
        _require(value not in prompt, f"public prompt leaks evaluator-only metadata: {value}")
    _require("expected_vector" not in public and "query_final_states" not in public, "public record leaks oracle field")
    for forbidden_field in (
        "difficulty",
        "query_final_states",
        "semantic_history_id",
        "seed_provenance",
        "source_final_states",
        "vector_slot",
    ):
        _require(forbidden_field not in public, f"public record leaks evaluator-only field: {forbidden_field}")


def validate_records(
    semantic: list[Mapping[str, Any]],
    public: list[Mapping[str, Any]],
    evaluator: list[Mapping[str, Any]],
) -> None:
    _require(len(semantic) == len(public) == len(evaluator) == 108, "corpus must contain exactly 108 records")
    _require([record["global_ordinal"] for record in semantic] == list(range(1, 109)), "global record order differs")
    _require(len({record["case_id"] for record in semantic}) == 108, "case IDs are not unique")
    _require([record["case_id"] for record in semantic] == [record["case_id"] for record in public] == [record["case_id"] for record in evaluator], "artifact joins differ")
    by_cell: dict[str, list[Mapping[str, Any]]] = {}
    for record, public_record, evaluator_record in zip(semantic, public, evaluator, strict=True):
        _require(record["schema_id"] == SEMANTIC_SCHEMA, "semantic schema differs")
        _require(evaluator_record["schema_id"] == EVALUATOR_SCHEMA, "evaluator schema differs")
        _require(tuple(record["state_vocabulary"]) == STATE_VOCABULARY, "state vocabulary differs")
        _require(record["initial_state"] == INITIAL_STATE, "initial state differs")
        cell_id = str(record["cell_id"])
        by_cell.setdefault(cell_id, []).append(record)
        events = list(record["event_stream"])
        entities = tuple(record["active_entities"])
        _require(len(entities) == int(record["difficulty"]["entity_count"]), "entity count differs")
        _require(len(events) == UPDATES_PER_ENTITY * len(entities), "event count differs")
        _require(len(record["assignment_histories"]) == len(entities), "history coverage differs")
        counts = Counter(event["assigned_state"] for event in events)
        _require(counts == Counter({state: len(entities) for state in STATE_VOCABULARY}), "state balance differs")
        for entity in entities:
            history = tuple(record["assignment_histories"][entity])
            _require(len(history) == UPDATES_PER_ENTITY, "history length differs")
            predecessor = INITIAL_STATE
            for value in history:
                _require(value in STATE_VOCABULARY and value != predecessor, "no-op or invalid assignment")
                predecessor = value
        block_order = tuple(record["source_block_order"])
        _require(set(block_order) == set(entities) and len(block_order) == len(entities), "block order differs")
        _require(
            [event["entity_id"] for event in events]
            == [entity for entity in block_order for _ in range(UPDATES_PER_ENTITY)],
            "entity blocks are not contiguous",
        )
        replayed = replay(events, entities)
        expected = tuple(replayed[entity] for entity in record["query_entities"])
        _require(expected == tuple(record["query_final_states"]), "replay query vector differs")
        _require(expected == tuple(evaluator_record["expected_vector"]), "evaluator vector differs")
        _require(
            parse_vector(",".join(expected)) == expected,
            "expected vector is not strict-parser compatible",
        )
        source_queries = tuple(record["source_query_entities"])
        source_blocks = tuple(block_order.index(entity) + 1 for entity in source_queries)
        source_distances = tuple(UPDATES_PER_ENTITY * len(entities) - UPDATES_PER_ENTITY * block for block in source_blocks)
        _require(source_distances == tuple(record["difficulty"]["latest_update_distances"]), "distance differs")
        _assert_prompt_boundary(record, public_record)
        core = dict(record)
        semantic_id = core.pop("semantic_history_id")
        core.pop("public_prompt_fingerprint")
        _require(
            semantic_id == f"mn007-sem-v1-{sha256_bytes(canonical_json_bytes(core))}",
            "semantic history identity differs",
        )
    _require(set(by_cell) == {cell.cell_id for cell in CELLS}, "cell inventory differs")
    for cell in CELLS:
        records = by_cell[cell.cell_id]
        _require(len(records) == 18, "cell does not have exactly 18 cases")
        _require([record["cell_ordinal"] for record in records] == list(range(1, 19)), "cell ordinal differs")
        _require([tuple(record["query_final_states"]) for record in records] == list(VECTOR_ORDER) * 2, "vector coverage differs")
        orientations = Counter(record["query_orientation"] for record in records)
        _require(orientations == Counter({"source_order": 9, "reverse_source_order": 9}), "orientation balance differs")
        _require(
            tuple(records[0]["difficulty"]["latest_update_distances"]) == cell.source_distances,
            "frozen source distance differs",
        )


def expected_artifacts() -> tuple[dict[str, bytes], dict[str, Any]]:
    semantic, public, evaluator = generate_records()
    payloads = {
        "semantic-cases.jsonl": canonical_jsonl_bytes(semantic),
        "public-prompts.jsonl": canonical_jsonl_bytes(public),
        "evaluator-records.jsonl": canonical_jsonl_bytes(evaluator),
    }
    per_cell_hashes: dict[str, str] = {}
    for cell in CELLS:
        cell_records = [record for record in semantic if record["cell_id"] == cell.cell_id]
        per_cell_hashes[cell.cell_id] = sha256_bytes(canonical_jsonl_bytes(cell_records))
    manifest_core = {
        "artifact_sha256": {name: sha256_bytes(payload) for name, payload in payloads.items()},
        "calibration_namespace": CALIBRATION_NAMESPACE,
        "cell_count": 6,
        "contract_namespace": CONTRACT_NAMESPACE,
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "evaluator_schema": EVALUATOR_SCHEMA,
        "materializer_source_sha256": sha256_file(Path(__file__)),
        "per_cell_semantic_sha256": per_cell_hashes,
        "public_schema": PUBLIC_SCHEMA,
        "record_count": 108,
        "root_seed_sha256": root_seed_sha256(),
        "semantic_schema": SEMANTIC_SCHEMA,
        "state_vocabulary": list(STATE_VOCABULARY),
    }
    manifest = {
        **manifest_core,
        "manifest_core_sha256": sha256_bytes(canonical_json_bytes(manifest_core)),
    }
    payloads["manifest.json"] = canonical_json_bytes(manifest)
    return payloads, manifest


def write_artifacts(root: Path = DEFINITION_ROOT) -> dict[str, Any]:
    """Materialize static canonical bytes only; no model or measured-evidence path exists."""
    payloads, manifest = expected_artifacts()
    root.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        root.joinpath(name).write_bytes(payload)
    validate_materialized(root)
    return manifest


def validate_materialized(root: Path = DEFINITION_ROOT) -> dict[str, Any]:
    _require(root.is_dir(), "materialized corpus directory is missing")
    payloads, expected_manifest = expected_artifacts()
    _require({path.name for path in root.iterdir()} == set(ARTIFACT_FILENAMES), "artifact set differs")
    for name, expected in payloads.items():
        actual = root.joinpath(name).read_bytes()
        _require(actual == expected, f"artifact physical bytes differ: {name}")
        _require(not actual.startswith(b"\xef\xbb\xbf") and b"\r\n" not in actual, f"artifact EOL/BOM differs: {name}")
        _require(actual.endswith(b"\n"), f"artifact terminal LF differs: {name}")
    manifest = json.loads(root.joinpath("manifest.json").read_bytes())
    _require(manifest == expected_manifest, "manifest differs")
    return manifest


def compare_artifact_trees(first: Path, second: Path) -> None:
    first_names = sorted(path.name for path in first.iterdir())
    second_names = sorted(path.name for path in second.iterdir())
    _require(
        first_names == second_names == sorted(ARTIFACT_FILENAMES),
        "regeneration artifact set differs",
    )
    for name in first_names:
        _require(first.joinpath(name).read_bytes() == second.joinpath(name).read_bytes(), f"regeneration bytes differ: {name}")
