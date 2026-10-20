"""Unit tests for MongNhiemKernel Façade."""

import os
import tempfile

from mong_nhiem.bimodal import CommClass
from mong_nhiem.kernel import MongNhiemKernel, StepResult
from mong_nhiem.runtime.backends import MockBackend
from mong_nhiem.temporal import ClockMode


def test_kernel_initialization_and_single_tick():
    schema_dict = {
        "schema_name": "smart_assistant",
        "continuous_traits": [
            {"name": "battery", "initial_value": 100.0, "rate_per_sec": 5.0, "is_decay": True}
        ],
        "invariants": [
            {"id": "inv_low_bat", "condition": "battery <= 20.0", "trigger_action": "FORCE_DOCK"}
        ],
        "preconditions": [
            {"action_verb": "EXECUTE_CLEANING", "required_states": {}, "prohibited_states": {}}
        ],
    }

    backend = MockBackend(
        default_response='ACTION: EXECUTE_CLEANING area=kitchen\nCOMMUNICATE [INFORM]: "Started cleaning kitchen."'
    )

    kernel = MongNhiemKernel(
        schema=schema_dict,
        backend=backend,
        clock_mode=ClockMode.SIMULATED,
    )

    result = kernel.tick(stimulus="Routine schedule", delta_time=2.0)

    assert isinstance(result, StepResult)
    assert result.action_verb == "EXECUTE_CLEANING"
    assert result.action_params == {"area": "kitchen"}
    assert result.comm_class == CommClass.INFORM
    assert result.comm_message == "Started cleaning kitchen."
    assert result.in_standby is False
    assert result.state_snapshot["battery"] == 90.0  # 100 - 5*2


def test_kernel_reflex_breaker_priority():
    schema_dict = {
        "schema_name": "fission_cooling",
        "continuous_traits": [
            {"name": "temp", "initial_value": 400.0, "rate_per_sec": 20.0, "is_decay": False}
        ],
        "invariants": [
            {"id": "inv_temp_limit", "condition": "temp >= 450.0", "trigger_action": "SCRAM"}
        ],
    }

    # Model tries to emit a nominal step, but Host reflex must intercept!
    backend = MockBackend(default_response='ACTION: NOMINAL_STEP\nCOMMUNICATE [INFORM]: "Proceeding"')

    kernel = MongNhiemKernel(
        schema=schema_dict,
        backend=backend,
        clock_mode=ClockMode.SIMULATED,
    )

    # Step 1: 400 + 20*1 = 420 (< 450)
    res1 = kernel.tick(delta_time=1.0)
    assert res1.action_verb == "NOMINAL_STEP"

    # Step 2: 420 + 20*2 = 460 (>= 450) -> Redline breach, SCRAM reflex takes precedence!
    res2 = kernel.tick(delta_time=2.0)
    assert res2.action_verb == "SCRAM"
    assert "CRITICAL REDLINE" in res2.comm_message
    assert res2.comm_class == CommClass.INFORM


def test_kernel_query_standby_and_human_preemption():
    schema_dict = {"schema_name": "drone_pilot"}

    backend = MockBackend(
        default_response='ACTION: REQUEST_LANDING\nCOMMUNICATE [QUERY]: "Confirm emergency landing on pad B?"',
        response_map={
            "Confirmed": 'ACTION: INITIATE_LANDING pad=B\nCOMMUNICATE [INFORM]: "Landing sequence executing on pad B."'
        },
    )

    kernel = MongNhiemKernel(schema=schema_dict, backend=backend, clock_mode=ClockMode.SIMULATED)

    # Turn 1: Model asks a question (QUERY) -> Host must enter SUPERVISED_STANDBY
    res1 = kernel.tick(stimulus="Low fuel warning")
    assert res1.comm_class == CommClass.QUERY
    assert res1.in_standby is True

    # Turn 2: Tick without user response -> Host maintains standby, does not re-query
    res2 = kernel.tick()
    assert res2.in_standby is True
    assert res2.action_verb == "ABSTAIN_STANDBY"

    # Turn 3: Human inputs directive -> Standby cleared, action dispatched
    res3 = kernel.tick(stimulus="Confirmed by operator", user_input="Confirmed, land immediately")
    assert res3.in_standby is False
    assert res3.preempted is True
    assert res3.action_verb == "INITIATE_LANDING"
    assert res3.comm_class == CommClass.INFORM


def test_kernel_atomic_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = os.path.join(tmpdir, "kernel_state.json")
        schema_dict = {
            "schema_name": "battery_system",
            "continuous_traits": [
                {"name": "charge", "initial_value": 100.0, "rate_per_sec": 10.0, "is_decay": True}
            ],
        }

        kernel1 = MongNhiemKernel(
            schema=schema_dict,
            state_file=state_file,
            clock_mode=ClockMode.SIMULATED,
        )
        kernel1.tick(delta_time=3.0)  # charge = 70.0
        kernel1.close()

        assert os.path.exists(state_file)

        # Restore from disk with new kernel instance
        kernel2 = MongNhiemKernel(
            schema=schema_dict,
            state_file=state_file,
            clock_mode=ClockMode.SIMULATED,
        )
        assert kernel2.state_engine.get_variable("charge") == 70.0


def test_kernel_auto_backend_from_schema():
    from mong_nhiem.runtime.backends import LlamaServerBackend, OpenAICompatBackend

    # 1. Schema with llama_server config
    schema_llama = {
        "schema_name": "llama_app",
        "model": {"type": "llama_server", "endpoint": "http://127.0.0.1:9090", "slot_id": 2},
    }
    kernel_llama = MongNhiemKernel(schema=schema_llama)
    assert isinstance(kernel_llama.backend, LlamaServerBackend)
    assert kernel_llama.backend.endpoint == "http://127.0.0.1:9090"
    assert kernel_llama.backend.slot_id == 2

    # 2. Schema with ollama config
    schema_ollama = {
        "schema_name": "ollama_app",
        "model": {"type": "ollama", "endpoint": "http://127.0.0.1:11434/v1", "model_name": "qwen3.5:2b"},
    }
    kernel_ollama = MongNhiemKernel(schema=schema_ollama)
    assert isinstance(kernel_ollama.backend, OpenAICompatBackend)
    assert kernel_ollama.backend.model_name == "qwen3.5:2b"
