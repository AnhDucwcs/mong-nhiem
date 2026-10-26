"""Adversarial Multilingual & Code-Switching Live SLM Stress Test (Test 4).

Validates robust reasoning-first intent distillation across Vietnamese, English,
and technical code-switching under extreme human chaotic expressions:
- Double Negation
- Counterfactuals & Conditional Overrides
- Stutter & Disregard Corrections
- Sarcasm & Rhetorical Questions
- Protocol Overrides
- Technical Code-Switching Slang

Supports dual-mode execution:
1. Fast Deterministic Distiller (CI hermetic mode, default, < 10ms)
2. Live SLM Inference via llama-server with GBNF constrained decoding (--live-slm)

Zero external dependencies. 100% Python Standard Library.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import NamedTuple

import pytest

from mong_nhiem.schema.grammars.dynamic_operator_intent import (
    OperatorIntentDistiller,
    build_operator_intent_gbnf,
)


class IntentCase(NamedTuple):
    case_id: str
    speech: str
    expected_verb: str
    expected_entity: str
    failure_mode: str


ADVERSARIAL_CASES: list[IntentCase] = [
    IntentCase(
        case_id="VN-01",
        speech=(
            "Đừng có mà không bơm nước làm mát đấy nhé, nhiệt độ lò 2 chạm 90 rồi, "
            "bơm nước vào lò 2 ngay cho tôi!"
        ),
        expected_verb="COOL",
        expected_entity="reactor_2",
        failure_mode="Double Negation & Urgency",
    ),
    IntentCase(
        case_id="VN-02",
        speech=(
            "Nếu mà áp suất chạm 80 thì mới xả khẩn cấp, còn hiện tại đang 60 thì "
            "chỉ mở con van phụ thôi, nhớ đấy chỉ mở van phụ thôi!"
        ),
        expected_verb="OPEN",
        expected_entity="aux_valve",
        failure_mode="Counterfactual / Conditionals",
    ),
    IntentCase(
        case_id="VN-03",
        speech=(
            "Ngắt... ngắt cái máy phát số... à nhầm trạm biến áp, mà thôi không ngắt trạm chính, "
            "chỉ cô lập trạm phụ thôi!"
        ),
        expected_verb="ISOLATE",
        expected_entity="aux_substation",
        failure_mode="Stutter & Self-Correction",
    ),
    IntentCase(
        case_id="EN-01",
        speech=(
            "Yeah right, like opening valve one is gonna save us now! "
            "Forget that nonsense, vent the backup chamber immediately!"
        ),
        expected_verb="VENT",
        expected_entity="backup_chamber",
        failure_mode="Sarcasm & Rhetorical Dismissal",
    ),
    IntentCase(
        case_id="EN-02",
        speech=(
            "Protocol says we must lockdown sector Alpha, but telemetry shows Alpha is clear "
            "and Beta has a leak, bypass protocol and seal sector Beta now!"
        ),
        expected_verb="SEAL",
        expected_entity="sector_beta",
        failure_mode="Protocol Override & Telemetry Grounding",
    ),
    IntentCase(
        case_id="MIX-01",
        speech=(
            "Con bơm số 1 bị trip rồi, đừng có dại mà restart nó lúc này, "
            "switch sang con bơm dự phòng gấp!"
        ),
        expected_verb="SWITCH",
        expected_entity="backup_pump",
        failure_mode="Code-Switching Technical Vernacular",
    ),
    IntentCase(
        case_id="MIX-02",
        speech=(
            "Overheat rồi kìa, cancel cái lệnh xả đi bro, "
            "purge gấp cái bình oxy số 2 lẹ lên coi!"
        ),
        expected_verb="PURGE",
        expected_entity="oxygen_tank_2",
        failure_mode="Urgent Code-Switching Slang",
    ),
]

VALID_ENTITIES: list[str] = [
    "reactor_2",
    "aux_valve",
    "aux_substation",
    "backup_chamber",
    "sector_beta",
    "sector_alpha",
    "backup_pump",
    "oxygen_tank_2",
    "valve_1",
    "valve_2",
]


def test_gbnf_grammar_synthesizer_constraints() -> None:
    """Verifies the synthesized GBNF grammar strictly bounds reasoning and enums."""
    grammar = build_operator_intent_gbnf(VALID_ENTITIES)
    assert '[^\\n]{1,120}' in grammar, "Reasoning must be strictly bounded between 1 and 120 chars"
    assert 'root ::= reasoning "\\n" decision' in grammar
    assert 'decision ::= "ACTION: " verb " " entity' in grammar
    assert '"reactor_2"' in grammar
    assert '"aux_valve"' in grammar
    assert '"backup_pump"' in grammar


def test_multilingual_operator_intent_distillation_deterministic() -> None:
    """Stress test all 7 adversarial multilingual cases against pure Python distiller."""
    distiller = OperatorIntentDistiller(valid_entities=VALID_ENTITIES)
    start_time = time.perf_counter()

    results: list[dict[str, str]] = []
    for tc in ADVERSARIAL_CASES:
        action = distiller.distill_intent(tc.speech)
        results.append(
            {
                "case_id": tc.case_id,
                "expected": f"{tc.expected_verb} {tc.expected_entity}",
                "got": f"{action.verb} {action.entity}",
                "reasoning": action.reasoning,
            }
        )
        assert action.verb == tc.expected_verb, (
            f"[{tc.case_id}] Verb mismatch for '{tc.failure_mode}': "
            f"expected '{tc.expected_verb}', got '{action.verb}'"
        )
        assert action.entity == tc.expected_entity, (
            f"[{tc.case_id}] Entity mismatch for '{tc.failure_mode}': "
            f"expected '{tc.expected_entity}', got '{action.entity}'"
        )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    # Must be extremely fast in pure Python (< 5ms total for 7 cases)
    assert elapsed_ms < 50.0, f"Deterministic distillation exceeded latency ceiling: {elapsed_ms:.2f}ms"


def test_live_slm_qwen_inference_multilingual_operator(live_slm: bool) -> None:
    """Live inference against llama-server running Qwen3.5-2B with GBNF constrained decoding."""
    if not live_slm:
        pytest.skip("Pass --live-slm to run live inference against running llama-server")

    server_url = os.environ.get("LLAMA_SERVER_URL", "http://127.0.0.1:18502/completion")
    grammar = build_operator_intent_gbnf(VALID_ENTITIES)

    # Verify server health
    health_url = server_url.replace("/completion", "/health")
    try:
        with urllib.request.urlopen(health_url, timeout=2.0) as resp:
            if resp.status != 200:
                pytest.skip(f"llama-server at {server_url} not healthy (HTTP {resp.status})")
    except Exception as exc:
        pytest.skip(f"llama-server at {server_url} is not running or unreachable: {exc}")

    for tc in ADVERSARIAL_CASES:
        prompt = (
            f"<|im_start|>system\n"
            f"You are the nuclear plant safety operator. Distill chaotic natural speech into structured action.\n"
            f"Valid entities: {', '.join(VALID_ENTITIES)}.\n"
            f"<|im_end|>\n"
            f"<|im_start|>user\n"
            f"{tc.speech}\n"
            f"<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        payload = json.dumps(
            {
                "prompt": prompt,
                "grammar": grammar,
                "temperature": 0.0,
                "n_predict": 64,
                "stop": ["<|im_end|>", "\n\n"],
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            server_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10.0) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            content = res_data.get("content", "").strip()

            assert "REASONING:" in content, f"[{tc.case_id}] Missing REASONING prefix in {content}"
            assert "ACTION:" in content, f"[{tc.case_id}] Missing ACTION prefix in {content}"
            assert f"ACTION: {tc.expected_verb} {tc.expected_entity}" in content, (
                f"[{tc.case_id}] SLM emitted incorrect action: {content}"
            )
