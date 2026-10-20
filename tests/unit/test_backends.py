"""Unit tests for pluggable inference backends."""

from mong_nhiem.runtime.backends import (
    LlamaServerBackend,
    MockBackend,
    OpenAICompatBackend,
)


def test_mock_backend_default_and_mapping():
    backend = MockBackend(
        default_response="ACTION: DEFAULT_STEP\nCOMMUNICATE [INFORM]: \"Nominal\"",
        response_map={
            "LOW_BATTERY": "ACTION: RECHARGE\nCOMMUNICATE [INFORM]: \"Heading to charger\"",
            "CONFIRM_ENGAGE": "ACTION: PROCEED\nCOMMUNICATE [QUERY]: \"Confirm action?\"",
        },
    )

    # 1. Unmatched prompt -> returns default
    resp1 = backend.generate("Stimulus: Routine inspection")
    assert "DEFAULT_STEP" in resp1
    assert "Nominal" in resp1

    # 2. Matched trigger -> returns mapped response
    resp2 = backend.generate("Stimulus: LOW_BATTERY detected")
    assert "RECHARGE" in resp2

    # 3. Custom response_fn
    backend_fn = MockBackend(response_fn=lambda p: f"ACTION: ECHO_{len(p)}\nCOMMUNICATE [INFORM]: \"Echoed\"")
    resp3 = backend_fn.generate("Hello world")
    assert "ECHO_11" in resp3


def test_llama_server_backend_payload_construction():
    backend = LlamaServerBackend(
        endpoint="http://127.0.0.1:8080",
        slot_id=0,
        cache_prompt=True,
    )
    assert backend.endpoint == "http://127.0.0.1:8080"
    assert backend.slot_id == 0
    assert backend.cache_prompt is True


def test_openai_compat_backend_initialization():
    backend = OpenAICompatBackend(
        endpoint="http://127.0.0.1:11434/v1",
        model_name="qwen2.5:3b",
        api_key="secret-token",
    )
    assert backend.endpoint == "http://127.0.0.1:11434/v1"
    assert backend.model_name == "qwen2.5:3b"
    assert backend.api_key == "secret-token"
