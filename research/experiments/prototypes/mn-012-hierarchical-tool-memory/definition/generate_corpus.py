#!/usr/bin/env python3
"""Deterministic benchmark corpus generator for MN-012.

Generates 60 stateful multi-turn evaluation cases across 3 domains:
- 20 code_mutation cases (AST inspection, refactoring, syntax invariant checks)
- 20 resource_ledger cases (Account balances, transfer mutations, conservation laws)
- 20 system_registry cases (Hierarchical configs, prerequisite checks, deployment readiness)

Outputs:
- definition/corpus-v1/cases.jsonl
- definition/corpus-v1/manifest.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "corpus-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CASES_FILE = OUT_DIR / "cases.jsonl"
MANIFEST_FILE = OUT_DIR / "manifest.json"


def generate_code_mutation_cases() -> list[dict]:
    cases = []
    # Cases 1 to 12: Standard multi-turn transitive refactoring (T=3)
    for i in range(1, 13):
        case_id = f"mn012-case-{i:04d}"
        f_entry = f"handle_request_{i}"
        f_helper = f"sanitize_input_{i}"
        f_target = f"calculate_tax_{i}"
        base_rate = 10 + i
        multiplier = 2
        oracle_answer = str(base_rate * multiplier)

        environment = {
            "functions": {
                f_entry: (
                    f"def {f_entry}(data):\n"
                    f"    clean = {f_helper}(data)\n"
                    f"    return {f_target}(clean)\n"
                ),
                f_helper: (
                    f"def {f_helper}(data):\n"
                    f"    return data.get('amount', 100)\n"
                ),
                f_target: (
                    f"def {f_target}(amount):\n"
                    f"    rate = {base_rate}\n"
                    f"    return rate\n"
                ),
            },
            "ast_invariants": ["valid_python_syntax", "deterministic_return"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "code_mutation",
            "subtype": "standard_refactor",
            "turn_horizon": 3,
            "query": (
                f"Inspect function {f_entry}, read its downstream target {f_target}, "
                f"dispatch refactor '{f_target}:rate_multiplier={multiplier}', "
                f"and resolve the updated return rate."
            ),
            "initial_context": (
                f"Repository contains endpoint '{f_entry}' with helper '{f_helper}' "
                f"and calculation function '{f_target}'."
            ),
            "environment": environment,
            "target_entity": f_target,
            "mutation_command": f"refactor {f_target}:multiplier={multiplier}",
            "oracle_answer": oracle_answer,
            "invariants": ["valid_syntax"],
        })

    # Cases 13 to 16: Syntax Invariant Rejection & Self-Recovery (T=4-5)
    for i in range(13, 17):
        case_id = f"mn012-case-{i:04d}"
        f_entry = f"audit_pipeline_{i}"
        f_target = f"compute_checksum_{i}"
        fixed_val = 500 + i
        oracle_answer = str(fixed_val)

        environment = {
            "functions": {
                f_entry: f"def {f_entry}():\n    return {f_target}()\n",
                f_target: f"def {f_target}():\n    return 0\n",
            },
            "ast_invariants": ["valid_python_syntax"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "code_mutation",
            "subtype": "syntax_invariant_recovery",
            "turn_horizon": 4,
            "query": (
                f"Refactor {f_target} to return {fixed_val}. "
                f"Ensure the AST is strictly valid Python syntax before resolving the return value."
            ),
            "initial_context": f"Pipeline '{f_entry}' depends on target function '{f_target}'.",
            "environment": environment,
            "target_entity": f_target,
            "adversarial_injection": f"refactor {f_target}:syntax_error=def 123 invalid!!!",
            "mutation_command": f"refactor {f_target}:return={fixed_val}",
            "oracle_answer": oracle_answer,
            "invariants": ["valid_syntax"],
        })

    # Cases 17 to 20: Deep Multi-Hop Dependency Chains (T=4-5)
    for i in range(17, 21):
        case_id = f"mn012-case-{i:04d}"
        f_entry = f"ingress_gateway_{i}"
        f_h1 = f"auth_filter_{i}"
        f_h2 = f"rate_limiter_{i}"
        f_target = f"core_executor_{i}"
        mult = 3
        base = 50 * i
        oracle_answer = str(base * mult)

        environment = {
            "functions": {
                f_entry: f"def {f_entry}(r):\n    return {f_h1}(r)\n",
                f_h1: f"def {f_h1}(r):\n    return {f_h2}(r)\n",
                f_h2: f"def {f_h2}(r):\n    return {f_target}(r)\n",
                f_target: f"def {f_target}(r):\n    return {base}\n",
            },
            "ast_invariants": ["valid_python_syntax"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "code_mutation",
            "subtype": "deep_chain_refactor",
            "turn_horizon": 5,
            "query": (
                f"Trace ingress chain from {f_entry} through {f_h1} and {f_h2} to {f_target}. "
                f"Dispatch refactor '{f_target}:multiplier={mult}' and resolve final return value."
            ),
            "initial_context": f"Gateway entrypoint is '{f_entry}'.",
            "environment": environment,
            "target_entity": f_target,
            "mutation_command": f"refactor {f_target}:multiplier={mult}",
            "oracle_answer": oracle_answer,
            "invariants": ["valid_syntax"],
        })

    return cases


def generate_resource_ledger_cases() -> list[dict]:
    cases = []
    # Cases 21 to 32: Standard Multi-Entity Balance Transfer (T=3)
    for i in range(21, 33):
        case_id = f"mn012-case-{i:04d}"
        acc_a = f"acc_alpha_{i}"
        acc_b = f"acc_beta_{i}"
        acc_c = f"acc_gamma_{i}"
        bal_a = 1000 + i * 50
        bal_b = 500
        bal_c = 200
        xfer = 300
        final_b = bal_b + xfer
        oracle_answer = f"{acc_b}:{final_b}"

        environment = {
            "accounts": {
                acc_a: bal_a,
                acc_b: bal_b,
                acc_c: bal_c,
            },
            "total_supply": bal_a + bal_b + bal_c,
            "invariants": ["non_negative_balances", "conservation_of_total_supply"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "resource_ledger",
            "subtype": "standard_transfer",
            "turn_horizon": 3,
            "query": (
                f"Inspect balance of {acc_a}, dispatch transfer of {xfer} from {acc_a} to {acc_b}, "
                f"and resolve the final balance of {acc_b} in format '{acc_b}:<balance>'."
            ),
            "initial_context": f"Ledger accounts active: '{acc_a}', '{acc_b}', '{acc_c}'.",
            "environment": environment,
            "source_entity": acc_a,
            "target_entity": acc_b,
            "mutation_command": f"transfer {acc_a},{acc_b},{xfer}",
            "oracle_answer": oracle_answer,
            "invariants": ["conservation_law"],
        })

    # Cases 33 to 36: Overdraft Rejection & Bound Recovery (T=4-5)
    for i in range(33, 37):
        case_id = f"mn012-case-{i:04d}"
        acc_a = f"acc_reserve_{i}"
        acc_b = f"acc_vault_{i}"
        bal_a = 250
        bal_b = 100
        overdraft_req = 500  # Will be rejected
        valid_req = 150       # Corrected amount
        final_a = bal_a - valid_req
        oracle_answer = f"{acc_a}:{final_a}"

        environment = {
            "accounts": {
                acc_a: bal_a,
                acc_b: bal_b,
            },
            "total_supply": bal_a + bal_b,
            "invariants": ["non_negative_balances", "conservation_of_total_supply"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "resource_ledger",
            "subtype": "overdraft_recovery",
            "turn_horizon": 4,
            "query": (
                f"Transfer requested funds from {acc_a} to {acc_b}. "
                f"If {overdraft_req} exceeds balance, adjust transfer to {valid_req} "
                f"and resolve final remaining balance of {acc_a} in format '{acc_a}:<balance>'."
            ),
            "initial_context": f"Vault account '{acc_b}' requests transfer from reserve '{acc_a}'.",
            "environment": environment,
            "source_entity": acc_a,
            "target_entity": acc_b,
            "adversarial_injection": f"transfer {acc_a},{acc_b},{overdraft_req}",
            "mutation_command": f"transfer {acc_a},{acc_b},{valid_req}",
            "oracle_answer": oracle_answer,
            "invariants": ["conservation_law", "no_overdraft"],
        })

    # Cases 37 to 40: Multi-Party Triangle Transfers (T=4-5)
    for i in range(37, 41):
        case_id = f"mn012-case-{i:04d}"
        acc_a = f"acc_node_a_{i}"
        acc_b = f"acc_node_b_{i}"
        acc_c = f"acc_node_c_{i}"
        bal_a = 600
        bal_b = 300
        bal_c = 100
        xfer_ab = 200
        xfer_bc = 150
        final_c = bal_c + xfer_bc
        oracle_answer = f"{acc_c}:{final_c}"

        environment = {
            "accounts": {
                acc_a: bal_a,
                acc_b: bal_b,
                acc_c: bal_c,
            },
            "total_supply": bal_a + bal_b + bal_c,
            "invariants": ["conservation_of_total_supply"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "resource_ledger",
            "subtype": "triangle_transfer",
            "turn_horizon": 5,
            "query": (
                f"Execute two-stage allocation: dispatch transfer of {xfer_ab} from {acc_a} to {acc_b}, "
                f"then transfer {xfer_bc} from {acc_b} to {acc_c}, and resolve final balance of {acc_c}."
            ),
            "initial_context": f"Triangle network routing: '{acc_a}' -> '{acc_b}' -> '{acc_c}'.",
            "environment": environment,
            "mutation_command": f"transfer {acc_a},{acc_b},{xfer_ab};transfer {acc_b},{acc_c},{xfer_bc}",
            "oracle_answer": oracle_answer,
            "invariants": ["conservation_law"],
        })

    return cases


def generate_system_registry_cases() -> list[dict]:
    cases = []
    # Cases 41 to 52: Standard Service Configuration & Flag Activation (T=3)
    for i in range(41, 53):
        case_id = f"mn012-case-{i:04d}"
        svc = f"svc_auth_engine_{i}"
        db = f"db_cluster_{i}"
        target_mode = "production"
        oracle_answer = f"{svc}.status=ACTIVE"

        environment = {
            "registry": {
                f"{db}.mode": "standby",
                f"{svc}.status": "MAINTENANCE",
                f"{svc}.upstream": db,
            },
            "invariants": ["prerequisite_active_db"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "system_registry",
            "subtype": "standard_flag_activation",
            "turn_horizon": 3,
            "query": (
                f"Inspect configuration of {svc}, dispatch flag mutation '{svc}.status=ACTIVE', "
                f"and resolve the final status of {svc}."
            ),
            "initial_context": f"Service registry contains service '{svc}' backed by '{db}'.",
            "environment": environment,
            "target_entity": svc,
            "mutation_command": f"set_flag {svc}.status=ACTIVE",
            "oracle_answer": oracle_answer,
            "invariants": ["service_validity"],
        })

    # Cases 53 to 56: Conflicting Flag Stress & Dependency Correction (T=4-5)
    for i in range(53, 57):
        case_id = f"mn012-case-{i:04d}"
        svc = f"svc_payment_api_{i}"
        kms = f"kms_vault_{i}"
        oracle_answer = f"{svc}.deployment=READY"

        environment = {
            "registry": {
                f"{kms}.key_loaded": "false",
                f"{svc}.deployment": "BLOCKED",
                f"{svc}.required_key": kms,
            },
            "invariants": ["kms_key_must_be_loaded"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "system_registry",
            "subtype": "prerequisite_conflict_recovery",
            "turn_horizon": 4,
            "query": (
                f"Activate {svc}. If activation is blocked by unloaded KMS key, "
                f"first dispatch '{kms}.key_loaded=true', then set '{svc}.deployment=READY' "
                f"and resolve final deployment state."
            ),
            "initial_context": f"Service '{svc}' depends on security module '{kms}'.",
            "environment": environment,
            "target_entity": svc,
            "adversarial_injection": f"set_flag {svc}.deployment=READY",  # will be rejected first
            "mutation_command": f"set_flag {kms}.key_loaded=true;set_flag {svc}.deployment=READY",
            "oracle_answer": oracle_answer,
            "invariants": ["dependency_prerequisite"],
        })

    # Cases 57 to 60: Deep Nested Registry Keys (T=4-5)
    for i in range(57, 61):
        case_id = f"mn012-case-{i:04d}"
        root = f"cluster_{i}"
        leaf_key = f"{root}.region_us.node_4.telemetry.drain_state"
        oracle_answer = f"{leaf_key}=DRAINED"

        environment = {
            "registry": {
                f"{root}.status": "online",
                f"{root}.region_us.status": "degraded",
                leaf_key: "ACTIVE",
            },
            "invariants": ["tree_integrity"],
        }

        cases.append({
            "case_id": case_id,
            "domain": "system_registry",
            "subtype": "deep_nested_registry",
            "turn_horizon": 5,
            "query": (
                f"Traverse hierarchical registry from {root} to find leaf '{leaf_key}'. "
                f"Dispatch mutation '{leaf_key}=DRAINED' and resolve the final state."
            ),
            "initial_context": f"Cluster registry root is '{root}'.",
            "environment": environment,
            "mutation_command": f"set_flag {leaf_key}=DRAINED",
            "oracle_answer": oracle_answer,
            "invariants": ["tree_integrity"],
        })

    return cases


def main() -> None:
    cases = []
    cases.extend(generate_code_mutation_cases())
    cases.extend(generate_resource_ledger_cases())
    cases.extend(generate_system_registry_cases())

    assert len(cases) == 60, f"Expected 60 cases, got {len(cases)}"

    # Write cases.jsonl
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Generate cryptographic manifest
    corpus_bytes = CASES_FILE.read_bytes()
    corpus_sha = hashlib.sha256(corpus_bytes).hexdigest()

    manifest = {
        "version": "1.0.0",
        "benchmark": "MN-012 Stateful Tool & Memory Benchmark",
        "case_count": len(cases),
        "domains": {
            "code_mutation": 20,
            "resource_ledger": 20,
            "system_registry": 20,
        },
        "sha256": corpus_sha,
        "files": {
            "cases.jsonl": corpus_sha,
        },
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {len(cases)} benchmark cases:")
    print(f"  Corpus file: {CASES_FILE}")
    print(f"  Manifest:    {MANIFEST_FILE} (SHA-256: {corpus_sha})")


if __name__ == "__main__":
    main()
