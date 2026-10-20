"""Unit and Resilience Tests for Milestone MN-027 Prototype.

Verifies Bimodal Parser, Temporal Bridge, Continuous State Decay, Schema Loader,
and Human Supervisory Preemption.
100% Python Standard Library. Zero external dependencies.
"""

import os
import sys
import tempfile
import time
import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROTOTYPE_DIR = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(PROTOTYPE_DIR, "src")
REPO_ROOT = os.path.abspath(os.path.join(PROTOTYPE_DIR, "..", "..", "..", ".."))

sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from bimodal_protocol import BimodalEmission, BimodalParser, CommClass, compile_bimodal_gbnf_grammar
from continuous_state import ContinuousStateEngine
from human_preemption import HumanSupervisoryBridge
from microworld_engine import BimodalMicroworldEngine
from schema_loader import DeclarativeSchemaLoader
from temporal_bridge import ClockMode, TemporalBridge


def test_bimodal_parser_clean_cases():
    """Verifies that BimodalParser parses valid emissions with exact token fidelity."""
    raw = 'ACTION: LOG_TELEMETRY sensor=P1 val=102.5\nCOMMUNICATE [INFORM]: "Telemetry steady at 102.5."'
    emission = BimodalParser.parse(raw)

    assert emission.valid is True
    assert emission.action_verb == "LOG_TELEMETRY"
    assert emission.action_params == {"sensor": "P1", "val": "102.5"}
    assert emission.comm_class == CommClass.INFORM
    assert emission.comm_message == "Telemetry steady at 102.5."


def test_bimodal_parser_triadic_classes():
    """Verifies parsing of all three orthogonal communicative classes."""
    for cls in [CommClass.INFORM, CommClass.QUERY, CommClass.EXPRESS]:
        raw = f'ACTION: TEST_VERB\nCOMMUNICATE [{cls.value}]: "Message for {cls.value}"'
        emission = BimodalParser.parse(raw)
        assert emission.valid is True
        assert emission.comm_class == cls
        assert emission.comm_message == f"Message for {cls.value}"


def test_bimodal_gbnf_compilation():
    """Verifies GBNF grammar string compilation."""
    grammar = compile_bimodal_gbnf_grammar(
        allowed_verbs=["ADJUST_VALVE", "ENTER_STANDBY"],
        allowed_comm_classes=[CommClass.QUERY],
    )
    assert 'action-verb ::= "ADJUST_VALVE" | "ENTER_STANDBY"' in grammar
    assert 'comm-type ::= "QUERY"' in grammar


def test_temporal_bridge_dual_clock():
    """Verifies simulated stepping and real-time monotonic jitter tracking."""
    tb = TemporalBridge(mode=ClockMode.SIMULATED)
    assert tb.step_simulated(5) == 5

    # Switch to real-time and measure tick
    tb_real = TemporalBridge(mode=ClockMode.REAL_TIME, tick_interval_seconds=0.01)
    time.sleep(0.012)
    elapsed, jitter_ms = tb_real.measure_real_time_tick()

    assert elapsed > 0.01
    assert jitter_ms < 15.0  # Jitter within Gate B bound
    stats = tb_real.get_aggregate_jitter_stats()
    assert "mean_jitter_ms" in stats


def test_continuous_state_decay_and_triggers():
    """Verifies linear parameter decay and threshold event triggering."""
    engine = ContinuousStateEngine()
    engine.register_variable("energy", initial_value=25.0, min_val=0.0, max_val=100.0, rate_per_unit=2.0, is_decay=True)
    engine.register_trigger("energy", 15.0, "<=", "ALERT_LOW_ENERGY")

    # Step 4 seconds -> 25 - (2*4) = 17.0 (no trigger yet)
    fired1 = engine.step_time(4.0)
    assert len(fired1) == 0
    assert engine.variables["energy"].current_value == 17.0

    # Step 2 seconds -> 17 - (2*2) = 13.0 (triggers ALERT_LOW_ENERGY)
    fired2 = engine.step_time(2.0)
    assert len(fired2) == 1
    assert fired2[0] == "ALERT_LOW_ENERGY"
    assert engine.variables["energy"].current_value == 13.0


def test_continuous_state_persistence():
    """Verifies atomic state saving and loading with elapsed time calculation."""
    engine = ContinuousStateEngine()
    engine.register_variable("hunger", initial_value=10.0, min_val=0.0, max_val=100.0, rate_per_unit=1.0, is_decay=False)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        engine.save_to_disk(tmp_path)
        assert os.path.exists(tmp_path)

        # Load into new engine
        engine2 = ContinuousStateEngine()
        elapsed = engine2.load_from_disk(tmp_path, apply_elapsed_decay=False)
        assert "hunger" in engine2.variables
        assert engine2.variables["hunger"].current_value == 10.0
        assert elapsed >= 0.0
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_declarative_schema_loader():
    """Verifies declarative JSON/dict schema compilation into Host structures."""
    schema_dict = {
        "schema_name": "test_reactor",
        "entities": [{"name": "reactor_core", "properties": {"status": "ONLINE"}}],
        "invariants": [
            {
                "id": "temp_redline",
                "condition": "temperature >= 450",
                "trigger_action": "TRIGGER_SCRAM",
            }
        ],
        "preconditions": [
            {
                "action_verb": "ENGAGE_COOLING",
                "required_states": {"isolation_seal": "SEALED"},
            }
        ],
        "continuous_traits": [
            {"name": "coolant_level", "initial_value": 90.0, "rate_per_sec": 0.5, "is_decay": True}
        ],
    }

    compiled = DeclarativeSchemaLoader.load_from_dict(schema_dict)
    assert compiled.schema_name == "test_reactor"
    assert len(compiled.entities) == 1
    assert len(compiled.invariants) == 1
    assert compiled.invariants[0].threshold == 450.0
    assert len(compiled.preconditions) == 1
    assert len(compiled.continuous_traits) == 1


def test_human_supervisory_bridge():
    """Verifies standby state entry and human preemptive epoch advancement."""
    bridge = HumanSupervisoryBridge()
    assert bridge.in_standby is False

    bridge.enter_standby(reason="Sensor Blackout")
    assert bridge.in_standby is True
    assert bridge.awaiting_human is True

    # Inject human command
    old_epoch = bridge.preemption_gate.world_epoch
    new_epoch = bridge.inject_human_command("OVERRIDE_VALVE_MANUAL")

    assert new_epoch > old_epoch
    assert bridge.in_standby is False
    assert bridge.awaiting_human is False
    assert bridge.last_human_directive == "OVERRIDE_VALVE_MANUAL"


def test_microworld_integrated_bimodal_execution():
    """Verifies end-to-end microworld loading, prompt formatting, and emission execution."""
    engine = BimodalMicroworldEngine()
    case = {
        "id": "test_case",
        "domain": "scada",
        "stimulus": "Check pressure",
        "initial_state": {"sensors": {"P1": {"value": 100.0, "status": "ONLINE"}}},
    }
    engine.load_case_scenario(case)
    prompt = engine.format_working_prompt(case)

    assert "[MODE: OPERATIONAL]" in prompt
    assert "[SENSORS P1:ONLINE(100.0)]" in prompt
    assert len(prompt.split()) < 300  # Token count well below 512

    raw_emission = 'ACTION: LOG_TELEMETRY P1=100.0\nCOMMUNICATE [INFORM]: "Pressure verified nominal."'
    emission = BimodalParser.parse(raw_emission)
    ok, msg, telemetry = engine.execute_emission(emission)

    assert ok is True
    assert telemetry["comm_class"] == "INFORM"
    assert telemetry["standby"] is False
