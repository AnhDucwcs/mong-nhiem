#!/usr/bin/env python3
"""Deterministic benchmark corpus generator for MN-013: Backtracking & Error Self-Correction.

Generates 60 stateful multi-turn evaluation cases across 3 domains:
- 20 code_mutation cases (10 standard, 10 trap-injected AST refactorings)
- 20 resource_ledger cases (10 standard, 10 trap-injected balance contention transfers)
- 20 system_registry cases (10 standard, 10 trap-injected mutual exclusion configurations)

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
    # Cases 1 to 10: Standard multi-turn transitive refactoring (No trap)
    for i in range(1, 11):
        case_id = f"mn013-case-{i:04d}"
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
            "has_trap": False,
            "query": (
                f"Inspect function {f_target}, dispatch refactor {f_target}:rate={oracle_answer}, "
                f"and resolve final rate."
            ),
            "initial_environment": environment,
            "target_predicate": {
                "type": "function_rate_updated",
                "target_func": f_target,
                "expected_value": oracle_answer,
            },
            "oracle_trajectory": [
                f"ACTION: READ {f_target}",
                f"ACTION: DISPATCH refactor_{f_target} rate={oracle_answer}",
                f"ACTION: RESOLVE {oracle_answer}",
            ],
            "oracle_answer": oracle_answer,
            "max_turns": 5,
        })

    # Cases 11 to 20: Injected AST Trap cases (Trap triggers rollback & alternative path)
    for i in range(11, 21):
        case_id = f"mn013-case-{i:04d}"
        f_entry = f"process_order_{i}"
        f_primary = f"discount_primary_{i}"
        f_alt = f"discount_alt_{i}"
        base_rate = 20 + i
        valid_answer = str(base_rate + 5)

        environment = {
            "functions": {
                f_entry: f"def {f_entry}(order):\n    return {f_primary}(order)\n",
                f_primary: f"def {f_primary}(val):\n    # LOCKED: Malformed AST prevents direct mutation\n    syntax_error ::::\n",
                f_alt: f"def {f_alt}(val):\n    return {base_rate}\n",
            },
            "ast_invariants": ["valid_python_syntax"],
            "locked_entities": [f_primary],
        }

        cases.append({
            "case_id": case_id,
            "domain": "code_mutation",
            "subtype": "ast_syntax_trap",
            "has_trap": True,
            "trap_description": f"Mutating {f_primary} fails syntax invariant; model must rollback and route through {f_alt}.",
            "query": (
                f"Inspect {f_primary}. If refactoring fails or violates syntax, rollback and refactor "
                f"{f_alt} with value={valid_answer}, then resolve final rate."
            ),
            "initial_environment": environment,
            "target_predicate": {
                "type": "function_rate_updated",
                "target_func": f_alt,
                "expected_value": valid_answer,
            },
            "oracle_trajectory": [
                f"ACTION: READ {f_primary}",
                f"ACTION: DISPATCH refactor_{f_primary} rate=999",  # Fails! Triggers rollback
                # Host rewinds context and injects negative mask
                f"ACTION: READ {f_alt}",
                f"ACTION: DISPATCH refactor_{f_alt} rate={valid_answer}",
                f"ACTION: RESOLVE {valid_answer}",
            ],
            "oracle_answer": valid_answer,
            "max_turns": 7,
        })

    return cases


def generate_resource_ledger_cases() -> list[dict]:
    cases = []
    # Cases 21 to 30: Standard resource transfer (No trap)
    for i in range(21, 31):
        case_id = f"mn013-case-{i:04d}"
        acc_src = f"acc_alpha_{i}"
        acc_dst = f"acc_beta_{i}"
        init_src = 1000 + (i * 50)
        init_dst = 200 + (i * 20)
        amount = 150 + i
        oracle_answer = f"{acc_dst}:{init_dst + amount}"

        environment = {
            "accounts": {
                acc_src: init_src,
                acc_dst: init_dst,
            },
            "min_balance": 0,
        }

        cases.append({
            "case_id": case_id,
            "domain": "resource_ledger",
            "subtype": "standard_transfer",
            "has_trap": False,
            "query": (
                f"Inspect balance of {acc_src}, transfer {amount} from {acc_src} to {acc_dst}, "
                f"and resolve final balance of {acc_dst}."
            ),
            "initial_environment": environment,
            "target_predicate": {
                "type": "account_balance_equals",
                "account": acc_dst,
                "expected_balance": init_dst + amount,
            },
            "oracle_trajectory": [
                f"ACTION: INSPECT {acc_src}.balance",
                f"ACTION: DISPATCH transfer {acc_src},{acc_dst},{amount}",
                f"ACTION: RESOLVE {oracle_answer}",
            ],
            "oracle_answer": oracle_answer,
            "max_turns": 5,
        })

    # Cases 31 to 40: Contention / Overdraft Trap (Trap triggers rollback & secondary route)
    for i in range(31, 41):
        case_id = f"mn013-case-{i:04d}"
        acc_primary = f"acc_vault_a_{i}"
        acc_secondary = f"acc_vault_b_{i}"
        acc_dst = f"acc_treasury_{i}"
        init_primary = 50   # Insufficient!
        init_secondary = 800
        init_dst = 100
        amount = 300
        oracle_answer = f"{acc_dst}:{init_dst + amount}"

        environment = {
            "accounts": {
                acc_primary: init_primary,
                acc_secondary: init_secondary,
                acc_dst: init_dst,
            },
            "min_balance": 0,
        }

        cases.append({
            "case_id": case_id,
            "domain": "resource_ledger",
            "subtype": "overdraft_contention_trap",
            "has_trap": True,
            "trap_description": f"Transfer from {acc_primary} triggers overdraft rejection (balance 50 < 300); model must rollback and transfer from {acc_secondary}.",
            "query": (
                f"Transfer {amount} from primary vault {acc_primary} to {acc_dst}. "
                f"If rejected for insufficient funds, rollback and transfer from backup vault {acc_secondary} to {acc_dst}, then resolve final balance of {acc_dst}."
            ),
            "initial_environment": environment,
            "target_predicate": {
                "type": "account_balance_equals",
                "account": acc_dst,
                "expected_balance": init_dst + amount,
            },
            "oracle_trajectory": [
                f"ACTION: DISPATCH transfer {acc_primary},{acc_dst},{amount}",  # Rejected! Overdraft
                # Host rewinds context & injects negative directive
                f"ACTION: INSPECT {acc_secondary}.balance",
                f"ACTION: DISPATCH transfer {acc_secondary},{acc_dst},{amount}",
                f"ACTION: RESOLVE {oracle_answer}",
            ],
            "oracle_answer": oracle_answer,
            "max_turns": 7,
        })

    return cases


def generate_system_registry_cases() -> list[dict]:
    cases = []
    # Cases 41 to 50: Standard system configuration (No trap)
    for i in range(41, 51):
        case_id = f"mn013-case-{i:04d}"
        svc_name = f"svc_gateway_{i}"
        flag_key = "log_level"
        target_val = "VERBOSE"
        oracle_answer = f"{svc_name}:{target_val}"

        environment = {
            "services": {
                svc_name: {
                    "status": "ACTIVE",
                    flag_key: "INFO",
                    "dependencies": [],
                }
            },
            "mutual_exclusions": [],
        }

        cases.append({
            "case_id": case_id,
            "domain": "system_registry",
            "subtype": "standard_config",
            "has_trap": False,
            "query": (
                f"Inspect status of {svc_name}, dispatch configuration update {svc_name}:{flag_key}={target_val}, "
                f"and resolve final {flag_key} of {svc_name}."
            ),
            "initial_environment": environment,
            "target_predicate": {
                "type": "service_flag_equals",
                "service": svc_name,
                "flag": flag_key,
                "expected_val": target_val,
            },
            "oracle_trajectory": [
                f"ACTION: INSPECT {svc_name}.status",
                f"ACTION: DISPATCH set_config {svc_name},{flag_key},{target_val}",
                f"ACTION: RESOLVE {oracle_answer}",
            ],
            "oracle_answer": oracle_answer,
            "max_turns": 5,
        })

    # Cases 51 to 60: Mutual Exclusion Conflict Trap (Trap triggers rollback & alternative mode)
    for i in range(51, 61):
        case_id = f"mn013-case-{i:04d}"
        svc_primary = f"svc_worker_a_{i}"
        svc_fallback = f"svc_worker_b_{i}"
        mode_aggressive = "AGGRESSIVE_PARALLEL"
        mode_safe = "CONSERVATIVE_PIPELINE"
        oracle_answer = f"{svc_fallback}:{mode_safe}"

        environment = {
            "services": {
                svc_primary: {"mode": "OFFLINE", "status": "LOCKED"},
                svc_fallback: {"mode": "STANDBY", "status": "AVAILABLE"},
            },
            "locked_services": [svc_primary],
            "mutual_exclusions": [(svc_primary, mode_aggressive)],
        }

        cases.append({
            "case_id": case_id,
            "domain": "system_registry",
            "subtype": "mutual_exclusion_trap",
            "has_trap": True,
            "trap_description": f"Enabling {mode_aggressive} on {svc_primary} violates locked status; host rejects, rolls back, and model must activate {mode_safe} on {svc_fallback}.",
            "query": (
                f"Activate high-throughput processing. Attempt {svc_primary}:{mode_aggressive} first. "
                f"If rejected due to lock conflict, rollback and activate {svc_fallback}:{mode_safe}, then resolve final mode of {svc_fallback}."
            ),
            "initial_environment": environment,
            "target_predicate": {
                "type": "service_flag_equals",
                "service": svc_fallback,
                "flag": "mode",
                "expected_val": mode_safe,
            },
            "oracle_trajectory": [
                f"ACTION: DISPATCH activate_service {svc_primary},{mode_aggressive}",  # Rejected! Locked
                # Host rewinds context & injects negative directive
                f"ACTION: INSPECT {svc_fallback}.status",
                f"ACTION: DISPATCH activate_service {svc_fallback},{mode_safe}",
                f"ACTION: RESOLVE {oracle_answer}",
            ],
            "oracle_answer": oracle_answer,
            "max_turns": 7,
        })

    return cases


def main():
    cases = []
    cases.extend(generate_code_mutation_cases())
    cases.extend(generate_resource_ledger_cases())
    cases.extend(generate_system_registry_cases())

    assert len(cases) == 60, f"Expected 60 cases, got {len(cases)}"

    with open(CASES_FILE, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Compute SHA-256
    hasher = hashlib.sha256()
    with open(CASES_FILE, "rb") as f:
        hasher.update(f.read())
    cases_sha = hasher.hexdigest()

    manifest = {
        "benchmark_version": "v1.0.0",
        "milestone": "MN-013",
        "case_count": len(cases),
        "cases_file": "cases.jsonl",
        "cases_sha256": cases_sha,
        "domains": {
            "code_mutation": 20,
            "resource_ledger": 20,
            "system_registry": 20,
        },
        "trap_cases_count": 30,
        "standard_cases_count": 30,
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated 60 cases at {CASES_FILE} (SHA-256: {cases_sha})")
    print(f"Manifest written to {MANIFEST_FILE}")


if __name__ == "__main__":
    main()
