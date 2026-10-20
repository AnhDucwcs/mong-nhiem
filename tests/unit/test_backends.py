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


def test_auto_port_hunting():
    import socket

    from mong_nhiem.runtime.backends import find_free_port, is_port_in_use

    port = find_free_port()
    assert isinstance(port, int)
    assert 1024 <= port <= 65535

    # Bind a socket to test is_port_in_use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", port))
        s.listen(1)
        assert is_port_in_use(port) is True

    # After close, port is freed
    assert is_port_in_use(port) is False


def test_subprocess_llama_backend_auto_port_selection(monkeypatch, tmp_path):
    import socket

    from mong_nhiem.runtime.backends import SubprocessLlamaBackend, find_free_port

    dummy_weights = tmp_path / "model.gguf"
    dummy_weights.write_text("dummy")

    # Prevent actual binary spawning during test
    monkeypatch.setattr(SubprocessLlamaBackend, "_spawn_process", lambda *args, **kwargs: None)

    # Case 1: port=0 requested -> auto allocate free port
    backend_zero = SubprocessLlamaBackend(weights_path=str(dummy_weights), port=0)
    assert backend_zero.port > 0
    assert backend_zero.endpoint == f"http://127.0.0.1:{backend_zero.port}"

    # Case 2: requested port is already occupied -> auto fallback to free port
    occupied_port = find_free_port()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", occupied_port))
        s.listen(1)

        backend_fallback = SubprocessLlamaBackend(weights_path=str(dummy_weights), port=occupied_port)
        assert backend_fallback.port != occupied_port
        assert backend_fallback.port > 0
        assert backend_fallback.endpoint == f"http://127.0.0.1:{backend_fallback.port}"

