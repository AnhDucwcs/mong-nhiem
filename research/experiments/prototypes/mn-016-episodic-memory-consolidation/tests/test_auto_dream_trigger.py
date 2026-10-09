"""Unit tests for Autonomous AutoDream Trigger and Context Pressure Interceptor."""

import sys
import tempfile
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from auto_dream_trigger import (
    AutonomousAutoDreamTrigger,
    TriggerConfig,
    TriggerType,
)
from consolidation_lock import ConsolidationState


def test_cadence_gates_progression() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        config = TriggerConfig(min_ticks_interval=20, min_mutations_count=5)
        trigger = AutonomousAutoDreamTrigger(Path(tmpdir), config)
        state = ConsolidationState(last_consolidated_tick=0)

        # 1. Not enough ticks
        res = trigger.evaluate(
            state=state,
            current_tick=10,
            unconsolidated_mutations=10,
            current_working_tokens=250,
        )
        assert not res.should_consolidate
        assert res.trigger_type == TriggerType.NONE

        # 2. Enough ticks but not enough mutations
        res = trigger.evaluate(
            state=state,
            current_tick=25,
            unconsolidated_mutations=2,
            current_working_tokens=250,
        )
        assert not res.should_consolidate
        assert res.trigger_type == TriggerType.NONE

        # 3. Both gates satisfied -> Cadence Trigger Fires!
        res = trigger.evaluate(
            state=state,
            current_tick=25,
            unconsolidated_mutations=6,
            current_working_tokens=250,
        )
        assert res.should_consolidate
        assert res.trigger_type == TriggerType.CADENCE_GATES
        trigger.release_lock()


def test_emergency_context_pressure_bypasses_cadence_gates() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        config = TriggerConfig(
            min_ticks_interval=50,
            min_mutations_count=20,
            context_pressure_token_threshold=400,
        )
        trigger = AutonomousAutoDreamTrigger(Path(tmpdir), config)
        state = ConsolidationState(last_consolidated_tick=0)

        # Only tick 5 and 1 mutation, but tokens = 410 >= 400!
        res = trigger.evaluate(
            state=state,
            current_tick=5,
            unconsolidated_mutations=1,
            current_working_tokens=410,
        )
        assert res.should_consolidate
        assert res.trigger_type == TriggerType.EMERGENCY_PRESSURE
        assert "Context budget saturated" in res.reason
        trigger.release_lock()
