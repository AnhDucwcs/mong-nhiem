"""Unit Tests for Mộng Nhiễm Living World Declarative Schema Integration.

Verifies schema compilation, continuous state evolution, action verb grammar,
and redline invariant safety triggers.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path

from mong_nhiem.kernel import MongNhiemKernel
from mong_nhiem.schema import DeclarativeSchemaLoader


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "demo" / "schema" / "living_world.json"


def test_living_world_schema_compilation() -> None:
    """Verifies that demo/schema/living_world.json compiles cleanly into CompiledWorldSchema."""
    assert SCHEMA_PATH.exists(), f"Schema file not found at {SCHEMA_PATH}"
    schema = DeclarativeSchemaLoader.load_from_file(str(SCHEMA_PATH))

    assert schema.schema_name == "mong_nhiem_living_world"
    expected_verbs = {"MOVE_TO", "FORAGE_BERRY", "DRINK_WATER", "SHELTER_BURROW", "REST_COLONY"}
    compiled_verbs = {p.action_verb for p in schema.preconditions}
    assert expected_verbs.issubset(compiled_verbs)

    trait_names = {t.name for t in schema.continuous_traits}
    assert {"hunger", "thirst", "energy", "predator_distance", "bush_north_amount"}.issubset(trait_names)


def test_living_world_kernel_instantiation_and_tick() -> None:
    """Verifies that MongNhiemKernel initializes and steps nominal ticks."""
    kernel = MongNhiemKernel.from_schema(str(SCHEMA_PATH))
    result = kernel.tick(stimulus="Nominal foraging observation", delta_time=0.05)

    assert result.tick >= 0
    assert result.delta_time == 0.05
    assert "hunger" in result.state_snapshot
    assert "energy" in result.state_snapshot
    assert result.in_standby is False


def test_living_world_predator_redline_trigger() -> None:
    """Verifies that predator proximity breaches trip the ReflexCircuitBreaker immediately."""
    kernel = MongNhiemKernel.from_schema(str(SCHEMA_PATH))
    # Simulate predator breaching the 35px safety threshold
    kernel.state_engine.set_variable("predator_distance", 25.0)

    result = kernel.tick(stimulus="Wolf ambush detected within safety perimeter")
    assert result.action_verb == "EMERGENCY_BURROW_EVAC"
    assert "CRITICAL REDLINE BREACH" in result.comm_message
    assert "EMERGENCY_BURROW_EVAC" in result.fired_invariants


def test_spatial_lookahead_evaluator() -> None:
    """Verifies that evaluate_spatial_lookahead correctly identifies safe and unsafe trajectories."""
    from demo.server import evaluate_spatial_lookahead

    # Case 1: Unsafe trajectory (breaching 35px margin)
    unsafe_res = evaluate_spatial_lookahead(
        waypoints=[[560.0, 320.0], [600.0, 300.0], [640.0, 280.0], [680.0, 260.0]],
        wolf_pos=[620.0, 280.0],
        wolf_vel=[-5.0, 2.0],
        scout_start=[520.0, 360.0],
        safety_dist=35.0,
    )
    assert unsafe_res["approved"] is False
    assert unsafe_res["min_distance"] < 35.0
    assert "REJECT" in unsafe_res["reason"]

    # Case 2: Safe trajectory (moving away to west thicket)
    safe_res = evaluate_spatial_lookahead(
        waypoints=[[480.0, 380.0], [420.0, 420.0], [360.0, 470.0], [320.0, 520.0]],
        wolf_pos=[750.0, 200.0],
        wolf_vel=[0.0, 0.0],
        scout_start=[520.0, 360.0],
        safety_dist=35.0,
    )
    assert safe_res["approved"] is True
    assert safe_res["min_distance"] >= 35.0
    assert "APPROVED" in safe_res["reason"]


def test_bridge_server_http_endpoints() -> None:
    """Verifies live HTTP interactions with the Cognitive Bridge Server."""
    import json
    import socketserver
    import threading
    import urllib.request
    from demo.server import LivingWorldBridgeHandler

    test_port = 8791
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    server = socketserver.ThreadingTCPServer(("", test_port), LivingWorldBridgeHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    base_url = f"http://localhost:{test_port}"
    try:
        # 1. GET /api/status
        req = urllib.request.urlopen(f"{base_url}/api/status")
        status_data = json.loads(req.read().decode("utf-8"))
        assert status_data["status"] == "ONLINE"
        assert status_data["schema_name"] == "mong_nhiem_living_world"

        # 2. POST /api/step (Nominal)
        step_payload = json.dumps({"stimulus": "Testing step"}).encode("utf-8")
        step_req = urllib.request.Request(f"{base_url}/api/step", data=step_payload, headers={"Content-Type": "application/json"})
        step_res = urllib.request.urlopen(step_req)
        step_data = json.loads(step_res.read().decode("utf-8"))
        assert step_data["success"] is True
        assert "action_verb" in step_data

        # 3. POST /api/verify_lookahead
        la_payload = json.dumps({
            "waypoints": [[560.0, 320.0], [600.0, 300.0]],
            "wolf_pos": [580.0, 310.0],
            "safety_dist": 35.0,
        }).encode("utf-8")
        la_req = urllib.request.Request(f"{base_url}/api/verify_lookahead", data=la_payload, headers={"Content-Type": "application/json"})
        la_res = urllib.request.urlopen(la_req)
        la_data = json.loads(la_res.read().decode("utf-8"))
        assert la_data["approved"] is False

    finally:
        server.shutdown()
        server.server_close()
