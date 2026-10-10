"""Corpus generator for Milestone MN-017: Dynamic World Ticks & Hierarchical Planning.

Generates 40 deterministic concurrent benchmark cases across three domains:
- Domain A: Infrastructure Migration & Lease Expiry (15 cases, Cases 0001-0015)
- Domain B: Asset Logistics & Resource Depletion (15 cases, Cases 0016-0030)
- Domain C: Concurrent System Registry & Failover (10 cases, Cases 0031-0040)
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

DEFINITION_DIR = Path(__file__).resolve().parent.parent / "definition" / "corpus-v1"
CASES_FILE = DEFINITION_DIR / "cases.json"
MANIFEST_FILE = DEFINITION_DIR / "manifest.json"


def generate_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    # =========================================================================
    # Domain A: Infrastructure Migration & Lease Expiry (15 Cases: 0001 - 0015)
    # =========================================================================
    for i in range(1, 16):
        case_num = f"{i:04d}"
        res_id = f"res_{i}"
        lease_id = f"lease_{i}"
        ticks_per_turn = 1 if i <= 10 else 2  # Cases 11-15 are multi-rate stress cases (2 ticks/turn)
        lease_ttl = 15 if i <= 10 else 10

        case = {
            "case_id": f"mn017-case-{case_num}",
            "domain": "domain_a",
            "domain_name": "Infrastructure Migration & Lease Expiry",
            "title": f"Migrate database partition {res_id} under concurrent lease {lease_id}",
            "global_mission": (
                f"Mission: Migrate database partition '{res_id}' safely without data loss. "
                f"You must strictly complete 4 phases in order: "
                f"1. Acquire/Renew lease '{lease_id}' with active lock. "
                f"2. Migrate payload chunks to '{res_id}'. "
                f"3. Verify data checksum on '{res_id}'. "
                f"4. Release lease and finalize migration on '{res_id}'. "
                f"Beware: World ticks elapse asynchronously and leases expire if delayed!"
            ),
            "ticks_per_turn": ticks_per_turn,
            "initial_entities": [
                {
                    "entity_id": lease_id,
                    "entity_type": "Lease",
                    "version": 1,
                    "ttl": lease_ttl,
                    "properties": {"holder": "none", "locked": False, "status": "ACTIVE"},
                },
                {
                    "entity_id": res_id,
                    "entity_type": "DataPartition",
                    "version": 1,
                    "properties": {
                        "payload_migrated": False,
                        "checksum_verified": False,
                        "migration_finalized": False,
                    },
                },
            ],
            "subgoals": [
                {
                    "goal_id": "G1",
                    "title": f"Acquire Exclusive Lease {lease_id}",
                    "description": f"Lock resource by acquiring lease {lease_id}.",
                    "prerequisites": [],
                    "allowed_actions": [f"acquire_lease {lease_id}", f"inspect_lease {lease_id}"],
                    "target_entity": lease_id,
                    "predicate_updates": {"holder": "agent", "locked": True},
                },
                {
                    "goal_id": "G2",
                    "title": f"Migrate Payload {res_id}",
                    "description": f"Transfer payload chunks to partition {res_id}.",
                    "prerequisites": ["G1"],
                    "allowed_actions": [f"migrate_payload {res_id}", f"check_payload {res_id}"],
                    "target_entity": res_id,
                    "predicate_updates": {"payload_migrated": True},
                },
                {
                    "goal_id": "G3",
                    "title": f"Verify Checksum {res_id}",
                    "description": f"Compute and verify SHA256 checksum on {res_id}.",
                    "prerequisites": ["G2"],
                    "allowed_actions": [f"verify_checksum {res_id}"],
                    "target_entity": res_id,
                    "predicate_updates": {"checksum_verified": True},
                },
                {
                    "goal_id": "G4",
                    "title": f"Release Lease and Finalize {res_id}",
                    "description": f"Mark partition finalized and release {lease_id}.",
                    "prerequisites": ["G3"],
                    "allowed_actions": [f"finalize_migration {res_id}", f"release_lease {lease_id}"],
                    "target_entity": res_id,
                    "predicate_updates": {"migration_finalized": True},
                },
            ],
            "scheduled_events": [
                # Scheduled drift event at tick 6 for stress cases
                {
                    "trigger_tick": 6,
                    "event_name": f"telemetry_sync_{res_id}",
                    "target_entity": res_id,
                    "property_updates": {"telemetry_synced": True},
                }
            ] if i > 10 else [],
        }
        cases.append(case)

    # =========================================================================
    # Domain B: Asset Logistics & Resource Depletion (15 Cases: 0016 - 0030)
    # =========================================================================
    for i in range(16, 31):
        case_num = f"{i:04d}"
        asset_id = f"cargo_{i}"
        vessel_id = f"transport_{i}"
        ticks_per_turn = 1 if i <= 25 else 2
        start_power = 25.0 if i <= 25 else 18.0

        case = {
            "case_id": f"mn017-case-{case_num}",
            "domain": "domain_b",
            "domain_name": "Asset Logistics & Resource Depletion",
            "title": f"Dispatch asset {asset_id} via transport vessel {vessel_id}",
            "global_mission": (
                f"Mission: Coordinate transport of cargo '{asset_id}' using vessel '{vessel_id}'. "
                f"You must strictly complete 4 phases in order: "
                f"1. Inspect cargo specifications on '{asset_id}'. "
                f"2. Allocate fuel/power reserve on '{vessel_id}'. "
                f"3. Dispatch cargo transfer from '{asset_id}' to '{vessel_id}'. "
                f"4. Settle delivery ledger for '{asset_id}'. "
                f"Beware: Vessel battery decays by -0.5 per world tick!"
            ),
            "ticks_per_turn": ticks_per_turn,
            "initial_entities": [
                {
                    "entity_id": asset_id,
                    "entity_type": "CargoUnit",
                    "version": 1,
                    "properties": {
                        "inspected": False,
                        "transferred": False,
                        "settled": False,
                    },
                },
                {
                    "entity_id": vessel_id,
                    "entity_type": "Vessel",
                    "version": 1,
                    "properties": {
                        "power": start_power,
                        "reserve_allocated": False,
                    },
                    "rate_of_decay": {"power": -0.5},
                },
            ],
            "subgoals": [
                {
                    "goal_id": "G1",
                    "title": f"Inspect Cargo {asset_id}",
                    "description": f"Verify manifests and cargo status for {asset_id}.",
                    "prerequisites": [],
                    "allowed_actions": [f"inspect_cargo {asset_id}"],
                    "target_entity": asset_id,
                    "predicate_updates": {"inspected": True},
                },
                {
                    "goal_id": "G2",
                    "title": f"Allocate Reserve {vessel_id}",
                    "description": f"Allocate dedicated energy buffer on {vessel_id}.",
                    "prerequisites": ["G1"],
                    "allowed_actions": [f"allocate_reserve {vessel_id}", f"check_power {vessel_id}"],
                    "target_entity": vessel_id,
                    "predicate_updates": {"reserve_allocated": True},
                },
                {
                    "goal_id": "G3",
                    "title": f"Dispatch Cargo Transfer {asset_id}",
                    "description": f"Execute loading and transfer of {asset_id}.",
                    "prerequisites": ["G2"],
                    "allowed_actions": [f"transfer_cargo {asset_id}"],
                    "target_entity": asset_id,
                    "predicate_updates": {"transferred": True},
                },
                {
                    "goal_id": "G4",
                    "title": f"Settle Delivery Ledger {asset_id}",
                    "description": f"Verify delivery receipt and settle ledger for {asset_id}.",
                    "prerequisites": ["G3"],
                    "allowed_actions": [f"settle_ledger {asset_id}"],
                    "target_entity": asset_id,
                    "predicate_updates": {"settled": True},
                },
            ],
            "scheduled_events": [],
        }
        cases.append(case)

    # =========================================================================
    # Domain C: Concurrent System Registry & Failover (10 Cases: 0031 - 0040)
    # =========================================================================
    for i in range(31, 41):
        case_num = f"{i:04d}"
        cluster_id = f"cluster_{i}"
        node_id = f"node_{i}"
        standby_id = f"standby_{i}"
        ticks_per_turn = 2 if i > 35 else 1

        case = {
            "case_id": f"mn017-case-{case_num}",
            "domain": "domain_c",
            "domain_name": "Concurrent System Registry & Failover",
            "title": f"Failover primary {node_id} to replica {standby_id} in {cluster_id}",
            "global_mission": (
                f"Mission: Execute automated failover in '{cluster_id}'. "
                f"Primary node '{node_id}' is degraded. "
                f"You must strictly complete 4 phases in order: "
                f"1. Probe cluster health and confirm degradation on '{node_id}'. "
                f"2. Drain traffic and isolate '{node_id}'. "
                f"3. Promote standby replica '{standby_id}' to primary. "
                f"4. Update routing table on '{cluster_id}' and finalize. "
                f"Beware: Standby node heartbeat mutates every 3 world ticks!"
            ),
            "ticks_per_turn": ticks_per_turn,
            "initial_entities": [
                {
                    "entity_id": node_id,
                    "entity_type": "PrimaryNode",
                    "version": 1,
                    "properties": {"status": "DEGRADED", "drained": False, "isolated": False},
                },
                {
                    "entity_id": standby_id,
                    "entity_type": "StandbyReplica",
                    "version": 1,
                    "properties": {"status": "STANDBY", "promoted": False, "heartbeat": 100},
                },
                {
                    "entity_id": cluster_id,
                    "entity_type": "RoutingCluster",
                    "version": 1,
                    "properties": {"active_primary": node_id, "routing_updated": False},
                },
            ],
            "subgoals": [
                {
                    "goal_id": "G1",
                    "title": f"Probe Node {node_id}",
                    "description": f"Diagnose degradation on {node_id}.",
                    "prerequisites": [],
                    "allowed_actions": [f"probe_node {node_id}", f"read_metrics {node_id}"],
                    "target_entity": node_id,
                    "predicate_updates": {"probed": True},
                },
                {
                    "goal_id": "G2",
                    "title": f"Drain and Isolate {node_id}",
                    "description": f"Drain active sessions and isolate {node_id}.",
                    "prerequisites": ["G1"],
                    "allowed_actions": [f"drain_node {node_id}", f"isolate_node {node_id}"],
                    "target_entity": node_id,
                    "predicate_updates": {"drained": True, "isolated": True},
                },
                {
                    "goal_id": "G3",
                    "title": f"Promote Standby {standby_id}",
                    "description": f"Promote standby replica {standby_id} to primary.",
                    "prerequisites": ["G2"],
                    "allowed_actions": [f"promote_replica {standby_id}"],
                    "target_entity": standby_id,
                    "predicate_updates": {"promoted": True, "status": "PRIMARY"},
                },
                {
                    "goal_id": "G4",
                    "title": f"Update Routing {cluster_id}",
                    "description": f"Switch routing traffic to {standby_id}.",
                    "prerequisites": ["G3"],
                    "allowed_actions": [f"update_routing {cluster_id}"],
                    "target_entity": cluster_id,
                    "predicate_updates": {"active_primary": standby_id, "routing_updated": True},
                },
            ],
            "scheduled_events": [
                {
                    "trigger_tick": 4,
                    "event_name": f"heartbeat_update_{standby_id}",
                    "target_entity": standby_id,
                    "property_updates": {"heartbeat": 101},
                }
            ],
        }
        cases.append(case)

    return cases


def main() -> None:
    DEFINITION_DIR.mkdir(parents=True, exist_ok=True)
    cases = generate_cases()
    assert len(cases) == 40, f"Expected 40 cases, got {len(cases)}"

    content_str = json.dumps(cases, indent=2, sort_keys=True)
    CASES_FILE.write_text(content_str, encoding="utf-8")
    cases_sha256 = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    manifest = {
        "milestone": "MN-017",
        "corpus_version": "v1",
        "total_cases": len(cases),
        "domain_distribution": {
            "domain_a_infrastructure": 15,
            "domain_b_asset_logistics": 15,
            "domain_c_system_registry": 10,
        },
        "cases_sha256": cases_sha256,
        "cases_file": "cases.json",
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Generated 40 deterministic cases in {CASES_FILE}")
    print(f"Manifest written to {MANIFEST_FILE} (SHA-256: {cases_sha256})")


if __name__ == "__main__":
    main()
