"""Unit Tests for Promoted Declarative Schema Loader."""

import os
import tempfile

from mong_nhiem.schema import DeclarativeSchemaLoader


def test_schema_loader_from_dict():
    raw_dict = {
        "schema_name": "smart_datacenter",
        "entities": [
            {"name": "server_rack_1", "properties": {"status": "ONLINE", "power_draw": 450}},
            {"name": "chiller_a", "properties": {"status": "ACTIVE"}},
        ],
        "invariants": [
            {"id": "inv_thermal", "condition": "temp >= 85.0", "trigger_action": "THROTTLE_NODES"}
        ],
        "preconditions": [
            {
                "action_verb": "OVERCLOCK_CLUSTER",
                "required_states": {"chiller_a": "ACTIVE"},
                "prohibited_states": {"alarm_state": "CRITICAL"},
            }
        ],
        "continuous_traits": [
            {"name": "rack_temperature", "initial_value": 45.0, "rate_per_sec": 0.5, "is_decay": False}
        ],
    }

    schema = DeclarativeSchemaLoader.load_from_dict(raw_dict)
    assert schema.schema_name == "smart_datacenter"
    assert len(schema.entities) == 2
    assert schema.entities[0].name == "server_rack_1"
    assert len(schema.invariants) == 1
    assert schema.invariants[0].target_metric == "temp"
    assert schema.invariants[0].threshold == 85.0
    assert len(schema.preconditions) == 1
    assert schema.preconditions[0].action_verb == "OVERCLOCK_CLUSTER"
    assert len(schema.continuous_traits) == 1
    assert schema.continuous_traits[0].name == "rack_temperature"


def test_schema_loader_from_json_file():
    json_content = """
    {
      "schema_name": "microgrid_v1",
      "entities": [{"name": "battery_bank", "properties": {"charge": 80}}],
      "invariants": [{"id": "inv_low_battery", "condition": "charge <= 15.0", "trigger_action": "SHED_LOAD"}]
    }
    """
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write(json_content)
        path = f.name

    try:
        schema = DeclarativeSchemaLoader.load_from_file(path)
        assert schema.schema_name == "microgrid_v1"
        assert schema.entities[0].name == "battery_bank"
        assert schema.invariants[0].trigger_action == "SHED_LOAD"
    finally:
        if os.path.exists(path):
            os.remove(path)
