from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-003-effective-context-capacity" / "experiments" / "ecc-004-llama-position-confirmation" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import ecc004


class FakeRuntime:
    @staticmethod
    def count_text(text: str) -> int:
        return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))

    def count_prompt(self, content: str) -> int:
        return self.count_text(content) + 12


class CountingFakeRuntime(FakeRuntime):
    def __init__(self) -> None:
        self.calls = 0

    def count_prompt(self, content: str) -> int:
        self.calls += 1
        return super().count_prompt(content)


def test_fresh_inventory_is_deterministic_unique_and_historically_disjoint() -> None:
    definition, cases = ecc004.load_definition()
    assert definition["case_generation"]["semantic_cases"] == 40
    assert [case["id"] for case in cases] == [f"ecc004-{index:03d}" for index in range(1, 41)]
    entities, answers = ecc004._historical_targets()
    assert not ({case["entity"] for case in cases} & entities)
    assert not ({case["answer"] for case in cases} & answers)


def test_bounded_builder_preserves_frozen_positions() -> None:
    definition, cases = ecc004.load_definition()
    runtime = CountingFakeRuntime()
    for position in ("early", "middle", "late"):
        built = ecc004.build_case(runtime, cases[0], 16384, position, definition)
        assert 0 <= built.requested_input_tokens - built.actual_input_tokens <= 160
        assert abs(built.evidence_position_ratio - ecc004.position_spec(definition, position)["target_ratio"]) <= 0.05
    assert runtime.calls <= 24


def test_diagnostics_do_not_change_exact_score() -> None:
    definition, cases = ecc004.load_definition()
    case = cases[0]
    _context, _content, _prefix, distractors = ecc004.compose(case, 6, "late", definition["case_generation"]["seed"])
    assert ecc004.classify_failure(case, f"The access code is {case['answer']}.", 6, "late", definition) == {"kind": "expected_code_with_extra_text"}
    assert ecc004.classify_failure(case, distractors[0]["answer"], 6, "late", definition) == {"kind": "tracked_distractor_code", "selected_distractor": distractors[0]}
    assert ecc004.classify_failure(case, "ZZ-9999", 6, "late", definition) == {"kind": "invented_code"}
    assert ecc004.classify_failure(case, "ZZ-99", 6, "late", definition) == {"kind": "partial_or_malformed_code"}
    assert ecc004.classify_failure(case, "I cannot determine it", 6, "late", definition) == {"kind": "other_text"}
    assert ecc004.ecc002.evaluate(case["answer"], f"The access code is {case['answer']}.")[0] is False


def _records() -> list[dict]:
    records: list[dict] = []
    for level in (8192, 16384):
        for position in ("early", "middle", "late"):
            for index in range(40):
                passed = level == 8192 or position != "late" or index >= 6
                records.append({"case_id": f"ecc004-{index + 1:03d}", "requested_input_tokens": level, "requested_evidence_position": position, "actual_input_tokens": level - 1, "evaluation": {"passed": passed}, "error": None, "truncated": False, "timing": {"total_ms": float(index + 1)}, "failure": None if passed else {"kind": "other_text"}})
    return records


def test_summary_derives_pairwise_transitions_and_predeclared_replication() -> None:
    definition, cases = ecc004.load_definition()
    summary = ecc004.summarize("run", _records(), [8192, 16384], ["early", "middle", "late"], [case["id"] for case in cases], True, definition)
    endpoint = summary["position_metrics"][1]
    assert endpoint["accuracy_by_position"] == {"early": 1.0, "middle": 1.0, "late": 0.85}
    assert endpoint["pairwise_differences"]["early_minus_late"] == pytest.approx(0.15)
    paired = summary["paired_transitions"][1]["comparisons"]["early_vs_late"]
    assert paired == {"early_pass_late_fail": 6, "early_fail_late_pass": 0, "paired_cases": 40}
    assert summary["confirmation"]["status"] == "replicated"


def test_definition_schema_and_llama_only_scope() -> None:
    definition, _ = ecc004.load_definition()
    assert ecc004.schema_errors(definition, "experiment-definition.schema.json") == []
    assert definition["model_scope"]["models"] == ["llama-3.2-3b"]


def test_validator_rejects_corrupted_diagnostic(tmp_path: Path) -> None:
    definition, cases = ecc004.load_definition()
    case = cases[0]
    built = ecc004.build_case(FakeRuntime(), case, 8192, "middle", definition)
    raw = f"The access code is {case['answer']}."
    record = {**{key: value for key, value in ecc004.built_case_dict(built).items() if key != "content"}, "configured_context_size": 16896, "output_token_budget": 16, "request": {"messages": [{"role": "user", "content": built.content}], "temperature": 0.0, "seed": 42, "max_tokens": 16, "chat_template_kwargs": {}}, "output": {"raw_text": raw, "normalized_text": ecc004.ecc002.normalize_answer(raw), "response": {"choices": [{"message": {"content": raw}}], "usage": {"prompt_tokens": built.actual_input_tokens}}}, "evaluation": {"passed": False, "score": 0.0}, "failure": {"kind": "expected_code_with_extra_text"}, "truncated": False, "timing": {"total_ms": 1.0}, "error": None}
    run = tmp_path / "run"
    run.mkdir()
    metadata = {"run_id": "ecc-004-test", "created_at": "2026-08-28T00:00:00+00:00", "experiment": {"id": definition["id"], "version": definition["version"]}, "definition_fingerprint": ecc004.definition_fingerprint(), "repository": {"commit": "test", "dirty": False}, "model": {"key": "llama-3.2-3b", "name": "test", "file": "test.gguf", "size_bytes": 1, "sha256": "0" * 64, "qualified_by": "test"}, "runtime": {}, "hardware": {}, "inference": {"temperature": 0.0, "seed": 42, "configured_context_size": 16896, "output_tokens": 16, "chat_template_kwargs": {}}, "selection": {"context_levels": [8192], "evidence_positions": ["middle"], "case_ids": [case["id"]], "complete_definition_coverage": False}, "command": {"server": [], "runner": []}}
    summary = ecc004.summarize("ecc-004-test", [record], [8192], ["middle"], [case["id"]], False, definition)
    ecc004.dump_json(run / "metadata.json", metadata)
    (run / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    ecc004.dump_json(run / "summary.json", summary)
    assert ecc004.validate_run(run) == summary
    corrupted = copy.deepcopy(record)
    corrupted["failure"] = {"kind": "other_text"}
    (run / "results.jsonl").write_text(json.dumps(corrupted) + "\n", encoding="utf-8")
    with pytest.raises(ecc004.ContractError, match="diagnostic"):
        ecc004.validate_run(run)
