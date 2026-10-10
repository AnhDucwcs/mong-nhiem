"""Dedicated Standalone Benchmark and Validation Suite for AutoDream Consolidation.

Rigorously verifies:
1. Single-cycle and multi-cycle compression ratios strictly meeting >= 70.0% (Criterion M5).
2. Elimination of multi-cycle compounding accumulation defects (monotonic non-decreasing ratio).
3. Ground-truth state alignment and zero memory contradictions.
4. Active pruning and purging of expired entities from declarative memory.
5. Cross-domain generalization across Orbital Station, Smart Microgrid, and Fleet Logistics.
6. Full end-to-end integration within CognitiveOrchestrator with bounded prompt ceilings.
"""
import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from autodream_engine import AutoDreamEngine
from episodic_memory import EpisodicLog
from microworld_engine import MicroworldEngine, WorldEntity
from hierarchical_planner import HierarchicalPlanner, MissionGraph, SubGoal
from orchestrator import MN018Orchestrator


def test_autodream_single_cycle_compression_threshold():
    """Verify that a single consolidation cycle achieves >= 70.0% compression ratio."""
    engine = MicroworldEngine(domain="orbital_station")
    engine.register_entity(WorldEntity("o2_scrubber", "scrubber", properties={"flow_rate": 12.0, "pwr": 45.0}))
    engine.register_entity(WorldEntity("co2_filter", "filter", properties={"saturation_pct": 18.5, "flow": 8.0}))
    engine.register_entity(WorldEntity("water_recycler", "recycler", properties={"reservoir_liters": 420.0, "purity": 99.4}))

    log = EpisodicLog()
    dream = AutoDreamEngine(event_threshold=15, token_threshold=350)

    # Append 15 realistic episodic events
    for i in range(15):
        log.append(
            tick=i + 1,
            entity_id=["o2_scrubber", "co2_filter", "water_recycler"][i % 3],
            action_name="TELEMETRY_SAMPLE",
            status="SUCCESS",
            details={
                "metric_a": 10.5 + i,
                "metric_b": 20.0,
                "status_code": "NOMINAL",
                "checksum": f"chk_{i:04d}",
            },
        )

    assert dream.should_trigger(log)
    did_run, count = dream.consolidate(log, engine)
    assert did_run
    assert count == 15
    assert dream.stats.total_cycles == 1

    # Verify Criterion M5: Compression Ratio >= 70.0%
    ratio = dream.stats.compression_ratio
    assert ratio >= 0.70, f"Expected compression ratio >= 0.70, got {ratio:.3f}"

    # Verify declarative cards are compact and bounded
    assert len(dream.declarative_cards) == 3
    card_chars = sum(len(c) for c in dream.declarative_cards.values())
    compact_tokens = card_chars // 4
    assert compact_tokens <= 48 * 3


def test_autodream_multi_cycle_compounding_immunity():
    """Verify that multiple consecutive consolidation cycles do NOT suffer from compounding degradation.
    
    The compression ratio across 4 cycles must remain >= 70.0% and monotonically non-decreasing.
    """
    engine = MicroworldEngine(domain="industrial_microgrid")
    engine.register_entity(WorldEntity("solar_pv_array", "generator", properties={"output_kw": 120.0, "irradiance": 850.0}))
    engine.register_entity(WorldEntity("battery_bank", "storage", properties={"charge_kwh": 350.0, "temp_c": 26.5}))
    engine.register_entity(WorldEntity("grid_feeder_a", "switch", properties={"breaker_state": "CLOSED", "pf": 0.98}))

    log = EpisodicLog()
    dream = AutoDreamEngine(event_threshold=15, token_threshold=350)

    ratios = []

    for cycle in range(1, 5):
        # Generate 15 events for this cycle
        for i in range(15):
            idx = (cycle - 1) * 15 + i
            log.append(
                tick=idx + 1,
                entity_id=["solar_pv_array", "battery_bank", "grid_feeder_a"][i % 3],
                action_name="DISPATCH_MUTATION",
                status="SUCCESS",
                details={
                    "cycle_num": cycle,
                    "event_seq": idx,
                    "voltage_bus": 480.0 + (i % 5),
                    "frequency_hz": 60.01,
                    "telemetry_flag": "VALID",
                },
            )

        assert dream.should_trigger(log)
        did_run, count = dream.consolidate(log, engine)
        assert did_run
        assert count == 15

        current_ratio = dream.stats.compression_ratio
        ratios.append(current_ratio)

        # Every cycle must strictly pass >= 70.0%
        assert current_ratio >= 0.70, f"Cycle {cycle} failed threshold: {current_ratio:.3f} < 0.70"

    # Multi-cycle monotonicity: compression ratio should strictly grow as event history accumulates
    for c in range(1, len(ratios)):
        assert ratios[c] >= ratios[c - 1], (
            f"Compounding degradation detected: Cycle {c + 1} ({ratios[c]:.3f}) < Cycle {c} ({ratios[c - 1]:.3f})"
        )


def test_autodream_zero_contradiction_latest_truth():
    """Verify ground-truth synchronization: mutating entity properties updates Fact Card without contradictions."""
    engine = MicroworldEngine(domain="orbital_station")
    entity = WorldEntity("coolant_loop_a", "thermal", properties={"temp_c": 45.0, "pressure_kpa": 120.0})
    engine.register_entity(entity)

    log = EpisodicLog()
    dream = AutoDreamEngine(event_threshold=5, token_threshold=100)

    # Initial events at tick 1-5
    for i in range(5):
        log.append(tick=i + 1, entity_id="coolant_loop_a", action_name="POLL", status="SUCCESS", details={"val": i})
    dream.consolidate(log, engine, force=True)

    initial_card = dream.declarative_cards["coolant_loop_a"]
    assert "temp_c:45" in initial_card
    assert "pressure_kpa:120" in initial_card

    # Mutate entity in authoritative engine (cooling activated)
    engine.mutate_entity("coolant_loop_a", {"temp_c": 22.5, "pressure_kpa": 105.0})

    # Subsequent events at tick 6-10
    for i in range(5):
        log.append(tick=i + 6, entity_id="coolant_loop_a", action_name="PUMP", status="SUCCESS", details={"pwr": 20})
    dream.consolidate(log, engine, force=True)

    updated_card = dream.declarative_cards["coolant_loop_a"]
    # Only 1 single card in store (zero duplicates / zero contradiction)
    assert len(dream.declarative_cards) == 1
    assert "temp_c:22.5" in updated_card
    assert "pressure_kpa:105" in updated_card
    assert "temp_c:45" not in updated_card


def test_autodream_entity_expiration_pruning():
    """Verify that expired entities are cleanly pruned from declarative memory upon consolidation."""
    engine = MicroworldEngine(domain="fleet_supply_chain")
    engine.register_entity(WorldEntity("hub_alpha", "depot", properties={"inventory": 500}))
    engine.register_entity(WorldEntity("temp_drone_lease", "vehicle", properties={"battery": 90}, ttl=3))

    log = EpisodicLog()
    dream = AutoDreamEngine()

    # Step 1: Consolidate while temp_drone_lease is active
    for i in range(6):
        eid = "temp_drone_lease" if i % 2 == 0 else "hub_alpha"
        log.append(tick=i + 1, entity_id=eid, action_name="REGISTER", status="SUCCESS", details={})
    dream.consolidate(log, engine, force=True)

    assert "hub_alpha" in dream.declarative_cards
    assert "temp_drone_lease" in dream.declarative_cards

    # Step 2: Advance engine ticks to expire TTL
    engine.step_ticks(5)
    assert engine.get_entity("temp_drone_lease").is_expired()

    # Step 3: Run consolidation pass
    for i in range(5):
        log.append(tick=i + 6, entity_id="hub_alpha", action_name="AUDIT", status="SUCCESS", details={})
    dream.consolidate(log, engine, force=True)

    # temp_drone_lease must be pruned; hub_alpha remains
    assert "temp_drone_lease" not in dream.declarative_cards
    assert "hub_alpha" in dream.declarative_cards


def test_autodream_cross_domain_evaluation():
    """Verify AutoDream performance across all three benchmark domains."""
    domains_data = [
        ("orbital_station", [
            WorldEntity("life_support", "scrubber", properties={"o2_level": 94.0, "power": 35.0}),
            WorldEntity("thermal_radiator", "cooling", properties={"temp_c": 18.0, "glycol_pct": 100.0}),
        ]),
        ("industrial_microgrid", [
            WorldEntity("diesel_gen_1", "backup", properties={"fuel_liters": 850.0, "rpm": 1800}),
            WorldEntity("substation_main", "switch", properties={"load_mw": 4.5, "status": "ONLINE"}),
        ]),
        ("fleet_supply_chain", [
            WorldEntity("central_hub", "depot", properties={"packages": 1200, "docks": 8}),
            WorldEntity("carrier_drone_x", "uav", properties={"payload_kg": 15.0, "range_km": 45.0}),
        ]),
    ]

    for domain_name, entities in domains_data:
        engine = MicroworldEngine(domain=domain_name)
        for ent in entities:
            engine.register_entity(ent)

        log = EpisodicLog()
        dream = AutoDreamEngine(event_threshold=15, token_threshold=300)

        for i in range(16):
            log.append(
                tick=i + 1,
                entity_id=entities[i % len(entities)].entity_id,
                action_name="DOMAIN_EVENT",
                status="SUCCESS",
                details={"domain": domain_name, "tick": i, "payload": 100 + i, "sensor_readout": "VALID"},
            )

        assert dream.should_trigger(log)
        did_run, count = dream.consolidate(log, engine)
        assert did_run
        assert count == 16
        assert dream.stats.compression_ratio >= 0.70

        # Declarative context budget check
        decl_text = dream.render_declarative_context()
        decl_tokens = len(decl_text) // 4
        assert decl_tokens <= 128, f"Domain {domain_name} exceeded 128-token budget: {decl_tokens} tokens"


def test_autodream_orchestrator_end_to_end_integration():
    """Verify end-to-end integration: CognitiveOrchestrator executes Arm 3 with terminal finalize pass."""
    engine = MicroworldEngine(domain="orbital_station")
    engine.register_entity(WorldEntity("o2_sys", "life_support", properties={"o2_level": 18.0, "scrubber": "IDLE"}))
    engine.register_entity(WorldEntity("cooling", "thermal", properties={"temp": 35.0}))

    mission = MissionGraph("test_mission", "Orbital Maintenance")
    subgoal = SubGoal(
        goal_id="g1",
        title="Activate Scrubber",
        description="Raise o2_level to 21.0",
        prerequisites=[],
        allowed_actions=["scrubber_on o2_sys", "scrubber_off o2_sys"],
        completion_predicate=lambda eng: eng.get_entity("o2_sys").properties.get("o2_level", 0) >= 21.0,
    )
    mission.add_subgoal(subgoal)

    orch = MN018Orchestrator(
        engine=engine,
        mission=mission,
        arm="arm3",
        ticks_per_turn=2,
    )

    def simple_executor(act_type: str, act_target: str, eng: MicroworldEngine):
        if act_target == "scrubber_on o2_sys":
            return eng.mutate_entity("o2_sys", {"o2_level": 22.0, "scrubber": "ACTIVE"})[:2]
        return True, "No-op"

    # Step turns until completion
    orch.step("ACTION: RECALL o2_sys", simple_executor)
    orch.step("ACTION: DISPATCH scrubber_on o2_sys", simple_executor)
    orch.step("ACTION: RESOLVE COMPLETE", simple_executor)

    # Terminal finalization
    orch.finalize()

    # Verify AutoDream consolidated the episode
    assert orch.autodream.stats.total_cycles >= 1
    assert orch.autodream.stats.total_events_consolidated >= 2
    # With compact Fact Cards, compression ratio should be robustly >= 0.70
    assert orch.autodream.stats.compression_ratio >= 0.70
    assert len(orch.episodic_log.get_unconsolidated_events()) == 0
