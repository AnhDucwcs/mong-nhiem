"""Deterministic generator for MN-016 Benchmark Corpus (40 long-horizon cases).

Domains:
- Domain A: Multi-Phase Code Refactoring (15 cases, T=25..40)
- Domain B: Multi-Vault Asset Ledger & Audit (15 cases, T=28..50)
- Domain C: Distributed System Registry & Leases (10 cases, T=22..45)
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def generate_domain_a_cases() -> list[dict[str, Any]]:
    """Generate 15 code refactoring cases (0001 - 0015)."""
    cases = []
    func_names = [
        "auth_validator", "payment_calculator", "order_serializer", "session_verifier",
        "route_dispatcher", "query_builder", "cache_serializer", "token_parser",
        "header_sanitizer", "payload_encoder", "signature_checker", "metric_formatter",
        "event_normalizer", "schema_migrator", "policy_evaluator"
    ]
    
    for i, base_name in enumerate(func_names, start=1):
        case_id = f"mn016-case-{i:04d}"
        target_entity = f"func_{base_name}_{i:02d}"
        horizon = 30 + (i % 8) * 2  # 30 to 44
        
        # Initial signatures
        old_sig = f"{base_name}(user_id, raw_token)"
        new_sig = f"{base_name}(auth_context, options=None)"
        
        steps = []
        # Step 1: Initial inspect
        steps.append({
            "tick": 1,
            "instruction": f"Inspect function {target_entity} definition",
            "action": f"ACTION: READ {target_entity}",
            "tool_result": {
                "status": "ok",
                "state_delta": {target_entity: {"status": "legacy", "signature": old_sig, "version": 1}},
            },
            "entity_modified": target_entity,
        })
        
        # Step 2: Critical refactor
        steps.append({
            "tick": 2,
            "instruction": f"Refactor {target_entity} to accept unified auth_context",
            "action": f"ACTION: DISPATCH refactor_{target_entity} signature={new_sig}",
            "tool_result": {
                "status": "success",
                "state_delta": {target_entity: {"status": "active", "signature": new_sig, "version": 2}},
            },
            "entity_modified": target_entity,
        })
        
        # Intermediate steps (3 to horizon - 4) modifying helper modules
        helpers = ["db_pool", "cache_layer", "logger", "metrics", "router", "config_store", "worker_pool"]
        burst_start = horizon - 7
        for t in range(3, horizon):
            is_burst = (burst_start <= t <= burst_start + 4)
            h_idx = (t % len(helpers))
            h_name = f"{helpers[h_idx]}_{i:02d}"
            
            if is_burst:
                # Burst mutation inflating token size
                steps.append({
                    "tick": t,
                    "instruction": f"Burst update batch configuration key_{t} for {h_name}",
                    "action": f"ACTION: DISPATCH sync_config_{h_name} batch_update=k{t}_v{t*100}",
                    "tool_result": {
                        "status": "success",
                        "state_delta": {h_name: {"status": "active", f"param_{t}": f"val_{t*100}", "last_sync": t}},
                    },
                    "entity_modified": h_name,
                    "is_burst": True,
                })
            else:
                steps.append({
                    "tick": t,
                    "instruction": f"Check status of subsystem {h_name}",
                    "action": f"ACTION: READ {h_name}",
                    "tool_result": {
                        "status": "ok",
                        "state_delta": {h_name: {"status": "active", "load": f"{10 + t % 20}%"}},
                    },
                    "entity_modified": h_name,
                    "is_burst": False,
                })
        
        # Final audit step
        steps.append({
            "tick": horizon,
            "instruction": f"Audit and invoke {target_entity} for high-priority inbound request",
            "recall_target": target_entity,
            "expected_recall_action": f"ACTION: RECALL {target_entity}",
            "expected_final_action": f"ACTION: DISPATCH invoke_{target_entity} args=auth_context",
            "stale_fifo_action": f"ACTION: DISPATCH invoke_{target_entity} args=user_id,raw_token",
            "expected_state": {"status": "active", "signature": new_sig, "version": 2},
            "is_crucial_step": True,
        })
        
        cases.append({
            "case_id": case_id,
            "domain": "code_refactoring",
            "horizon": horizon,
            "target_entity": target_entity,
            "description": f"Multi-phase refactoring of {target_entity}: signature update at T=2, burst at T={burst_start}, invoke at T={horizon}.",
            "initial_entities": {
                target_entity: {"status": "legacy", "signature": old_sig, "version": 1},
                f"db_pool_{i:02d}": {"status": "active", "pool_size": 10},
            },
            "steps": steps,
        })
        
    return cases


def generate_domain_b_cases() -> list[dict[str, Any]]:
    """Generate 15 asset ledger & audit cases (0016 - 0030)."""
    cases = []
    
    for idx in range(16, 31):
        case_id = f"mn016-case-{idx:04d}"
        target_entity = f"vault_omega_{idx:02d}"
        dest_vault = f"vault_prime_{idx:02d}"
        horizon = 32 + (idx % 9) * 2  # 32 to 48
        
        steps = []
        # Step 1: Query initial balance
        steps.append({
            "tick": 1,
            "instruction": f"Inspect initial balance for {target_entity}",
            "action": f"ACTION: READ {target_entity}",
            "tool_result": {
                "status": "ok",
                "state_delta": {target_entity: {"status": "open", "balance": 5000, "vault_type": "escrow"}},
            },
            "entity_modified": target_entity,
        })
        
        # Step 2: Close vault and sweep balance
        steps.append({
            "tick": 2,
            "instruction": f"Close {target_entity} and sweep full balance 5000 to {dest_vault}",
            "action": f"ACTION: DISPATCH sweep_and_close_{target_entity} target={dest_vault} amount=5000",
            "tool_result": {
                "status": "success",
                "state_delta": {
                    target_entity: {"status": "closed", "balance": 0, "swept_to": dest_vault, "closed_tick": 2},
                    dest_vault: {"status": "open", "balance": 15000},
                },
            },
            "entity_modified": target_entity,
        })
        
        # Intermediate steps: transactions across other accounts
        accounts = [f"acct_alpha_{idx:02d}", f"acct_beta_{idx:02d}", f"acct_gamma_{idx:02d}", f"acct_theta_{idx:02d}"]
        burst_start = horizon - 8
        for t in range(3, horizon):
            is_burst = (burst_start <= t <= burst_start + 5)
            a_idx = (t % len(accounts))
            a_name = accounts[a_idx]
            
            if is_burst:
                steps.append({
                    "tick": t,
                    "instruction": f"Burst transaction transfer {100*t} to {a_name}",
                    "action": f"ACTION: DISPATCH transfer_{a_name} amount={100*t}",
                    "tool_result": {
                        "status": "success",
                        "state_delta": {a_name: {"status": "open", "balance": 2000 + 100 * t, "last_tx": t}},
                    },
                    "entity_modified": a_name,
                    "is_burst": True,
                })
            else:
                steps.append({
                    "tick": t,
                    "instruction": f"Audit account {a_name} statement",
                    "action": f"ACTION: READ {a_name}",
                    "tool_result": {
                        "status": "ok",
                        "state_delta": {a_name: {"status": "open", "audit_verified": True}},
                    },
                    "entity_modified": a_name,
                    "is_burst": False,
                })
                
        # Final audit step
        steps.append({
            "tick": horizon,
            "instruction": f"Process withdrawal request TX-{idx*100} for 1000 from {target_entity}",
            "recall_target": target_entity,
            "expected_recall_action": f"ACTION: RECALL {target_entity}",
            "expected_final_action": f"ACTION: DISPATCH reject_withdrawal_{target_entity} reason=vault_closed",
            "stale_fifo_action": f"ACTION: DISPATCH approve_withdrawal_{target_entity} amount=1000",
            "expected_state": {"status": "closed", "balance": 0, "swept_to": dest_vault, "closed_tick": 2},
            "is_crucial_step": True,
        })
        
        cases.append({
            "case_id": case_id,
            "domain": "asset_ledger",
            "horizon": horizon,
            "target_entity": target_entity,
            "description": f"Multi-vault ledger closure for {target_entity}: swept to {dest_vault} at T=2, audit withdrawal at T={horizon}.",
            "initial_entities": {
                target_entity: {"status": "open", "balance": 5000, "vault_type": "escrow"},
                dest_vault: {"status": "open", "balance": 10000},
            },
            "steps": steps,
        })
        
    return cases


def generate_domain_c_cases() -> list[dict[str, Any]]:
    """Generate 10 system registry & lease cases (0031 - 0040)."""
    cases = []
    
    for idx in range(31, 41):
        case_id = f"mn016-case-{idx:04d}"
        target_entity = f"svc_gateway_{idx:02d}"
        migrated_target = f"svc_gateway_v2_{idx:02d}"
        new_endpoint = f"10.0.{idx}.50:8443"
        old_endpoint = f"10.0.{idx}.10:8080"
        horizon = 26 + (idx % 7) * 2  # 26 to 38
        
        steps = []
        # Step 1: Inspect legacy endpoint
        steps.append({
            "tick": 1,
            "instruction": f"Inspect route for {target_entity}",
            "action": f"ACTION: READ {target_entity}",
            "tool_result": {
                "status": "ok",
                "state_delta": {target_entity: {"status": "active", "endpoint": old_endpoint, "lease_ttl": 60}},
            },
            "entity_modified": target_entity,
        })
        
        # Step 2: Migrate service and revoke old lease
        steps.append({
            "tick": 2,
            "instruction": f"Migrate {target_entity} to {migrated_target} at {new_endpoint}",
            "action": f"ACTION: DISPATCH migrate_{target_entity} target={migrated_target} endpoint={new_endpoint}",
            "tool_result": {
                "status": "success",
                "state_delta": {
                    target_entity: {
                        "status": "migrated",
                        "target": migrated_target,
                        "endpoint": new_endpoint,
                        "migrated_tick": 2,
                    }
                },
            },
            "entity_modified": target_entity,
        })
        
        # Intermediate steps: nodes & health checks
        nodes = [f"node_worker_{idx:02d}_a", f"node_worker_{idx:02d}_b", f"node_redis_{idx:02d}"]
        burst_start = horizon - 6
        for t in range(3, horizon):
            is_burst = (burst_start <= t <= burst_start + 4)
            n_idx = (t % len(nodes))
            n_name = nodes[n_idx]
            
            if is_burst:
                steps.append({
                    "tick": t,
                    "instruction": f"Burst registry sync node {n_name} heartbeats",
                    "action": f"ACTION: DISPATCH heartbeat_{n_name} tick={t}",
                    "tool_result": {
                        "status": "success",
                        "state_delta": {n_name: {"status": "healthy", "heartbeat_tick": t, "load_factor": 0.45}},
                    },
                    "entity_modified": n_name,
                    "is_burst": True,
                })
            else:
                steps.append({
                    "tick": t,
                    "instruction": f"Read health stats for {n_name}",
                    "action": f"ACTION: READ {n_name}",
                    "tool_result": {
                        "status": "ok",
                        "state_delta": {n_name: {"status": "healthy"}},
                    },
                    "entity_modified": n_name,
                    "is_burst": False,
                })
                
        # Final routing step
        steps.append({
            "tick": horizon,
            "instruction": f"Route mission-critical packet to {target_entity}",
            "recall_target": target_entity,
            "expected_recall_action": f"ACTION: RECALL {target_entity}",
            "expected_final_action": f"ACTION: DISPATCH route_traffic_{target_entity} endpoint={new_endpoint}",
            "stale_fifo_action": f"ACTION: DISPATCH route_traffic_{target_entity} endpoint={old_endpoint}",
            "expected_state": {
                "status": "migrated",
                "target": migrated_target,
                "endpoint": new_endpoint,
                "migrated_tick": 2,
            },
            "is_crucial_step": True,
        })
        
        cases.append({
            "case_id": case_id,
            "domain": "system_registry",
            "horizon": horizon,
            "target_entity": target_entity,
            "description": f"Service migration for {target_entity}: migrated to {migrated_target} ({new_endpoint}) at T=2, route at T={horizon}.",
            "initial_entities": {
                target_entity: {"status": "active", "endpoint": old_endpoint, "lease_ttl": 60},
            },
            "steps": steps,
        })
        
    return cases


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    def_dir = root / "definition"
    corpus_dir = def_dir / "corpus-v1"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    
    all_cases = []
    all_cases.extend(generate_domain_a_cases())
    all_cases.extend(generate_domain_b_cases())
    all_cases.extend(generate_domain_c_cases())
    
    assert len(all_cases) == 40, f"Expected 40 cases, got {len(all_cases)}"
    
    cases_json_path = corpus_dir / "cases.json"
    with open(cases_json_path, "w", encoding="utf-8") as f:
        json.dump(all_cases, f, indent=2)
        
    # Also save top-level definition/cases.json for convenience
    with open(def_dir / "cases.json", "w", encoding="utf-8") as f:
        json.dump(all_cases, f, indent=2)
        
    # Compute sha256
    with open(cases_json_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
        
    manifest = {
        "milestone": "MN-016",
        "corpus_version": "v1",
        "case_count": len(all_cases),
        "sha256": sha256,
        "domains": {
            "code_refactoring": 15,
            "asset_ledger": 15,
            "system_registry": 10,
        },
        "target_horizon_range": "20-50",
    }
    
    manifest_path = corpus_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Generated {len(all_cases)} cases successfully.")
    print(f"Cases saved to: {cases_json_path} (SHA-256: {sha256})")
    print(f"Manifest saved to: {manifest_path}")


if __name__ == "__main__":
    main()
