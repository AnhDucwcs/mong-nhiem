"""Unit Tests for Promoted Continuous State Engine."""

import os
import tempfile

from mong_nhiem.state import ContinuousStateEngine


def test_continuous_state_decay_and_growth():
    engine = ContinuousStateEngine()
    engine.register_variable(
        name="battery",
        initial_value=100.0,
        min_val=0.0,
        max_val=100.0,
        rate_per_unit=5.0,  # 5% decay per unit time
        is_decay=True,
    )
    engine.register_variable(
        name="heat",
        initial_value=30.0,
        min_val=0.0,
        max_val=150.0,
        rate_per_unit=2.0,  # 2 deg growth per unit time
        is_decay=False,
    )

    fired = engine.step_time(2.0)
    assert len(fired) == 0
    assert engine.get_variable("battery") == 90.0  # 100 - 5*2
    assert engine.get_variable("heat") == 34.0     # 30 + 2*2


def test_continuous_state_threshold_trigger():
    engine = ContinuousStateEngine()
    engine.register_variable("temperature", initial_value=350.0, rate_per_unit=10.0, is_decay=False)
    engine.register_trigger(
        variable_name="temperature",
        threshold=370.0,
        comparison=">=",
        trigger_action="EMERGENCY_VENT",
    )

    # Step 1: 350 + 10 = 360 (< 370)
    fired1 = engine.step_time(1.0)
    assert len(fired1) == 0

    # Step 2: 360 + 15 = 375 (>= 370) -> Fires
    fired2 = engine.step_time(1.5)
    assert fired2 == ["EMERGENCY_VENT"]

    # Step 3: 375 + 10 = 385 (>= 370) -> Already fired, should not refire
    fired3 = engine.step_time(1.0)
    assert len(fired3) == 0


def test_continuous_state_atomic_disk_persistence():
    engine = ContinuousStateEngine()
    engine.register_variable("pressure", initial_value=85.5, rate_per_unit=1.0)
    engine.register_trigger("pressure", threshold=90.0, comparison=">=", trigger_action="PURGE")

    with tempfile.TemporaryDirectory() as tmpdir:
        save_file = os.path.join(tmpdir, "test_state.json")
        engine.save_to_disk_atomic(save_file)
        assert os.path.exists(save_file)

        # Restore into clean engine
        engine2 = ContinuousStateEngine()
        loaded = engine2.load_from_disk(save_file)
        assert loaded is True
        assert engine2.get_variable("pressure") == 85.5
        assert len(engine2.triggers) == 1
        assert engine2.triggers[0].trigger_action == "PURGE"
