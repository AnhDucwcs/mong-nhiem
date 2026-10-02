"""Static deterministic MN-009 30-case corpus materializer and validator.

Generates 30 evaluation cases across 5 size tiers (2k, 4k, 8k, 16k, 32k)
and 3 data structures (text_stream, graph_table, code_ast) under strict
Gate B contract definitions.
"""
from __future__ import annotations

import ast
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

PROTOTYPE_ROOT = Path(__file__).resolve().parents[1]
DEFINITION_ROOT = PROTOTYPE_ROOT / "definition" / "corpus-v1"
CASES_FILE = DEFINITION_ROOT / "cases.jsonl"
MANIFEST_FILE = DEFINITION_ROOT / "manifest.json"

SIZES = [2048, 4096, 8192, 16384, 32768]
CATEGORIES = ["text_stream", "graph_table", "code_ast"]


def sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def generate_text_stream_case(case_idx: int, target_tokens: int) -> dict[str, Any]:
    """Generate narrative timeline case with causal events and latest state."""
    case_num = case_idx + 1
    target_words = int(target_tokens * 0.75)
    
    entities = ["Alex", "Brenda", "Carlos", "Diana", "Evan"]
    target_entity = entities[case_idx % len(entities)]
    final_status = "SECURED" if case_idx % 2 == 0 else "QUARANTINED"
    final_location = f"Sector-{case_num % 10 + 1}"
    
    # Executive Anchor (Chunk 0)
    lead_in = (
        f"Mission Briefing Omega-{case_num:03d}: Tactical operation commenced at Alpha Base. "
        f"Active operatives deployed across field sectors include {', '.join(entities)}. "
        f"All units must adhere to directive protocol Alpha-9.\n\n"
    )
    
    events = []
    # Generate background narrative events
    num_events = max(10, target_words // 25)
    for step in range(num_events):
        ent = entities[step % len(entities)]
        status = f"PATROLLING_{step % 3}"
        loc = f"Sector-{(step * 3) % 10 + 1}"
        events.append(
            f"At timestamp {1000 + step * 10}: Operative {ent} reported location at {loc} "
            f"with operational status {status}. Ambient conditions remained stable."
        )
    
    # Invariant: explicit latest state at the end
    latest_event = (
        f"At timestamp {1000 + num_events * 10 + 50}: Operative {target_entity} successfully reached "
        f"{final_location} and reported definitive final condition {final_status}."
    )
    events.append(latest_event)
    
    full_content = lead_in + "\n\n".join(events)
    
    return {
        "case_id": f"mn009-case-{case_num:04d}",
        "category": "text_stream",
        "raw_token_count": target_tokens,
        "raw_content": full_content,
        "query": f"What is the final condition and location of Operative {target_entity}?",
        "target_fact": f"Operative {target_entity} is {final_status} at {final_location}.",
        "required_entities": [target_entity],
        "oracle_answer": f"{final_status} at {final_location}",
    }


def generate_graph_table_case(case_idx: int, target_tokens: int) -> dict[str, Any]:
    """Generate tabular state and graph adjacency network case."""
    case_num = case_idx + 1
    num_nodes = max(50, target_tokens // 25)
    
    target_entity = f"Node_{case_idx * 3 % num_nodes}"
    companion_entity = f"Node_{(case_idx * 3 + 1) % num_nodes}"
    target_status = "AUTHORIZED" if case_idx % 2 == 0 else "REVOKED"
    target_role = f"ADMIN_TIER_{case_idx % 4 + 1}"
    
    # 1. Tabular state records (JSON-like lines)
    table_lines = [
        f"Entity: Node_{i} | Role: WORKER_{i % 5} | Access: STANDARD | Clearance: LEVEL_{i % 3}"
        for i in range(num_nodes)
    ]
    # Update target entity latest state
    table_lines.append(
        f"Entity: {target_entity} | Role: {target_role} | Access: {target_status} | Clearance: LEVEL_HIGH"
    )
    table_lines.append(
        f"Entity: {companion_entity} | Role: ASSISTANT | Access: AUTHORIZED | Clearance: LEVEL_MED"
    )
    
    # 2. Graph topology
    graph_lines = [
        f"Link: Node_{i} -> Node_{(i + 1) % num_nodes}, Node_{(i + 3) % num_nodes}"
        for i in range(num_nodes)
    ]
    
    content = "=== SYSTEM ACCESS REGISTRY ===\n" + "\n".join(table_lines) + "\n\n=== NETWORK TOPOLOGY ===\n" + "\n".join(graph_lines)
    
    return {
        "case_id": f"mn009-case-{case_num:04d}",
        "category": "graph_table",
        "raw_token_count": target_tokens,
        "raw_content": content,
        "query": f"What is the access status and role of {target_entity}?",
        "target_fact": f"{target_entity} has role {target_role} and access status {target_status}.",
        "required_entities": [target_entity, companion_entity],
        "oracle_answer": f"{target_status} ({target_role})",
    }


def generate_code_ast_case(case_idx: int, target_tokens: int) -> dict[str, Any]:
    """Generate Python codebase with multiple functions, untyped helpers, and target logic."""
    case_num = case_idx + 1
    num_funcs = max(15, target_tokens // 100)
    
    target_func_name = f"execute_pipeline_{case_num}"
    helper_short_name = f"_compute_delta_{case_num}"
    expected_output = f"RESULT_OK_{case_num}"
    
    funcs = [
        '"""Module generated for MN-009 AST slicing evaluation."""',
        "from typing import Any, Dict, List",
        f"GLOBAL_SETTING_{case_num} = {{'multiplier': {case_num}, 'mode': 'FAST'}}",
        "",
        f"def {helper_short_name}(base, factor):",
        "    # Short helper inlined",
        "    return base * factor + 1",
        "",
    ]
    
    # Add dummy long functions
    for i in range(num_funcs):
        funcs.append(f"def auxiliary_routine_{i}(x, y, z):")
        funcs.append(f'    """Auxiliary routine {i} docstring."""')
        funcs.append("    acc = 0")
        funcs.append("    for step in range(10):")
        funcs.append(f"        acc += step * {i + 1}")
        funcs.append("    return acc")
        funcs.append("")
    
    # Target function
    funcs.append(f"def {target_func_name}(val_a: int, val_b: int) -> str:")
    funcs.append(f'    """Execute primary target pipeline {case_num}."""')
    funcs.append(f"    sub_calc = {helper_short_name}(val_a, val_b)")
    funcs.append("    if sub_calc > 0:")
    funcs.append(f"        return '{expected_output}'")
    funcs.append("    return 'FAIL'")
    
    code_content = "\n".join(funcs)
    # Verify validity of generated code
    ast.parse(code_content)
    
    return {
        "case_id": f"mn009-case-{case_num:04d}",
        "category": "code_ast",
        "raw_token_count": target_tokens,
        "raw_content": code_content,
        "query": f"What string does {target_func_name} return when val_a=2 and val_b=3?",
        "target_fact": f"{target_func_name} returns '{expected_output}'.",
        "required_entities": [target_func_name, helper_short_name],
        "oracle_answer": expected_output,
    }


def build_30_case_corpus() -> list[dict[str, Any]]:
    """Build exact 30-case Latin/Tiers matrix (10 text, 10 graph/table, 10 code)."""
    cases: list[dict[str, Any]] = []
    case_idx = 0
    
    # 1. Nhóm A: Text Stream (10 cases: 2 per size tier)
    for size in SIZES:
        for _ in range(2):
            cases.append(generate_text_stream_case(case_idx, size))
            case_idx += 1
            
    # 2. Nhóm B: Graph & State Tables (10 cases: 2 per size tier)
    for size in SIZES:
        for _ in range(2):
            cases.append(generate_graph_table_case(case_idx, size))
            case_idx += 1
            
    # 3. Nhóm C: Codebase AST Slicing (10 cases: 2 per size tier)
    for size in SIZES:
        for _ in range(2):
            cases.append(generate_code_ast_case(case_idx, size))
            case_idx += 1
            
    return cases


def materialize() -> None:
    DEFINITION_ROOT.mkdir(parents=True, exist_ok=True)
    cases = build_30_case_corpus()
    
    # Write cases.jsonl
    lines = [json.dumps(c, ensure_ascii=False, sort_keys=True) for c in cases]
    jsonl_bytes = ("\n".join(lines) + "\n").encode("utf-8")
    CASES_FILE.write_bytes(jsonl_bytes)
    
    # Write manifest.json
    manifest = {
        "namespace": "mn009-corpus-v1",
        "case_count": len(cases),
        "categories": {
            "text_stream": sum(1 for c in cases if c["category"] == "text_stream"),
            "graph_table": sum(1 for c in cases if c["category"] == "graph_table"),
            "code_ast": sum(1 for c in cases if c["category"] == "code_ast"),
        },
        "size_tiers": SIZES,
        "cases_sha256": sha256_bytes(jsonl_bytes),
        "case_ids": [c["case_id"] for c in cases],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    MANIFEST_FILE.write_bytes(manifest_bytes)
    
    print(f"Materialized {len(cases)} cases into {CASES_FILE}")
    print(f"Manifest written to {MANIFEST_FILE}")
    print(f"Cases SHA-256: {manifest['cases_sha256']}")


if __name__ == "__main__":
    materialize()
