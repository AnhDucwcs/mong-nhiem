#!/usr/bin/env python3
"""Deterministic benchmark corpus generator for MN-010 multi-hop reasoning.

Generates 30 multi-hop cases across 3 domains:
- 10 code_ast cases (transitive function calls)
- 10 knowledge_graph cases (transitive entity relations)
- 10 state_table cases (indirected table/key lookups)

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


def generate_cases() -> list[dict]:
    cases = []

    # Domain A: Codebase Dependency AST (10 cases)
    for i in range(1, 11):
        case_id = f"mn010-case-{i:04d}"
        f_entry = f"process_transaction_{i}"
        f_helper = f"validate_payload_{i}"
        f_target = f"compute_fee_{i}"
        val = 100 * i + 42

        code_repo = {
            f_entry: (
                f"def {f_entry}(req):\n"
                f"    status = {f_helper}(req)\n"
                f"    if not status:\n"
                f"        return -1\n"
                f"    return {f_target}(req['tier'])\n"
            ),
            f_helper: (
                f"def {f_helper}(req):\n"
                f"    # Helper checking signature\n"
                f"    return req.get('active', True)\n"
            ),
            f_target: (
                f"def {f_target}(tier):\n"
                f"    # Terminal target calculation\n"
                f"    return {val}\n"
            ),
        }

        cases.append({
            "case_id": case_id,
            "domain": "code_ast",
            "hop_depth": 2,
            "query": f"What is the non-error return value of {f_entry}()?",
            "entry_target": f_entry,
            "expected_hops": [f_target],
            "oracle_answer": str(val),
            "environment": code_repo,
            "initial_context": code_repo[f_entry],
        })

    # Domain B: Knowledge Graph Paths (10 cases)
    departments = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa"]
    roles = ["Director", "Lead Architect", "Principal SRE", "Security Officer", "Data Custodian"]
    for i in range(1, 11):
        case_id = f"mn010-case-{i + 10:04d}"
        e_proj = f"Project_Valkyrie_{i}"
        e_lead = f"Operator_{i}"
        dept = departments[i - 1]
        role = roles[(i - 1) % len(roles)]
        room = f"Sector_{i * 7}"

        kg = {
            e_proj: f"Project {e_proj} is assigned to Lead Operator {e_lead}. Priority: High.",
            e_lead: f"Operator {e_lead} belongs to Department {dept} with role '{role}'. Working location: {room}.",
            room: f"Physical Sector {room} access clearance required: Level {i}.",
        }

        cases.append({
            "case_id": case_id,
            "domain": "knowledge_graph",
            "hop_depth": 2,
            "query": f"What is the physical working location sector of the lead operator for {e_proj}?",
            "entry_target": e_proj,
            "expected_hops": [e_lead],
            "oracle_answer": room,
            "environment": kg,
            "initial_context": kg[e_proj],
        })

    # Domain C: System State & Config Tables (10 cases)
    clusters = ["prod-us-east", "prod-eu-west", "staging-ap-south", "dr-sa-east", "edge-na-central"]
    for i in range(1, 11):
        case_id = f"mn010-case-{i + 20:04d}"
        cluster = f"{clusters[(i - 1) % len(clusters)]}-{i}"
        svc = f"svc-auth-router-{i}"
        cfg_key = f"CFG_VAULT_KEY_{i}"
        ip_addr = f"10.240.{i}.108"
        port = 8440 + i

        st = {
            cluster: f"Cluster '{cluster}' runs primary service '{svc}'. Status: HEALTHY.",
            svc: f"Service '{svc}' fetches secure database credentials using token pointer '{cfg_key}'.",
            cfg_key: f"Secret pointer '{cfg_key}' maps to Vault endpoint IP '{ip_addr}:{port}'.",
        }

        cases.append({
            "case_id": case_id,
            "domain": "state_table",
            "hop_depth": 2,
            "query": f"What is the vault endpoint IP and port for the primary service in cluster '{cluster}'?",
            "entry_target": cluster,
            "expected_hops": [svc, cfg_key],
            "oracle_answer": f"{ip_addr}:{port}",
            "environment": st,
            "initial_context": st[cluster],
        })

    return cases


def main() -> None:
    cases = generate_cases()
    lines = [json.dumps(c, ensure_ascii=False) for c in cases]
    content = "\n".join(lines) + "\n"

    CASES_FILE.write_text(content, encoding="utf-8")
    sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

    manifest = {
        "version": "1.0.0",
        "total_cases": len(cases),
        "domains": {
            "code_ast": 10,
            "knowledge_graph": 10,
            "state_table": 10,
        },
        "sha256": sha256,
        "cases_file": CASES_FILE.name,
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(cases)} cases -> {CASES_FILE} (SHA256: {sha256})")


if __name__ == "__main__":
    main()
