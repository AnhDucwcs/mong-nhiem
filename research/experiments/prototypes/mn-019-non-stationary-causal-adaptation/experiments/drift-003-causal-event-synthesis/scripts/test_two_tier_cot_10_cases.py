import os
import sys
import json
import time
import copy
import urllib.request
from typing import Dict, Any, List, Tuple, Optional, Set

# Add paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(base_dir, "src"))

from hierarchical_planner import SubGoal
from schema_evolution_engine import SchemaEvolutionRule
from orchestrator import DualEngineOrchestrator


def call_llama(prompt: str, grammar: str, temp: float = 0.0, max_tokens: int = 48, port: int = 18502) -> Tuple[str, float]:
    url = f"http://127.0.0.1:{port}/completion"
    payload = {
        "prompt": prompt,
        "temperature": temp,
        "top_p": 0.9 if temp > 0 else 1.0,
        "n_predict": max_tokens,
        "stop": ["\n\n", "User:", "Observation:"],
        "seed": 42,
    }
    if grammar:
        payload["grammar"] = grammar

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return res.get("content", "").strip(), latency_ms


def compile_grammar_for_turn(orch, mode: str) -> str:
    curr_sg = orch.planner.current_subgoal
    if not curr_sg:
        branches = ['"ACTION: RESOLVE COMPLETE"']
    else:
        viable, pruned = orch.get_active_viable_actions()
        neg_set = set(orch.banned_actions)
        if mode == "mode_direct_baseline":
            # Baseline behavior: ban executed actions unconditionally
            neg_set = neg_set.union(orch.executed_actions)

        effective = [a for a in viable if a not in neg_set and a not in pruned]
        # If effective is empty, but viable has unbanned actions (waiting for tick/entity)
        if not effective and viable:
            unbanned = [a for a in viable if a not in orch.banned_actions]
            effective = unbanned if unbanned else viable

        branches = [f'"ACTION: DISPATCH " "{act}"' for act in effective]
        if orch.planner.is_all_completed():
            branches.append('"ACTION: RESOLVE COMPLETE"')
        if not branches:
            branches.append('"ACTION: RESOLVE COMPLETE"')

    branches_str = " | ".join(branches)

    if mode == "mode_two_tier_cot":
        return (
            f'root ::= "<hypothesis>" [^\\r\\n<]+ "</hypothesis>\\n" action [\\n]?\n'
            f'action ::= {branches_str}\n'
        )
    else:
        return f'root ::= ({branches_str}) [\\n]?\n'


def run_episode(case_data: Dict[str, Any], mode: str, port: int = 18502) -> Dict[str, Any]:
    from orchestrator import DualEngineOrchestrator

    subgoals = [
        SubGoal(
            subgoal_id=g["subgoal_id"],
            description=g["description"],
            target_entity=g["target_entity"],
            target_property=g["target_property"],
            operator=g["operator"],
            target_value=float(g["target_value"]),
            candidate_actions=list(g.get("candidate_actions", [])),
            required_emergent_entity=g.get("required_emergent_entity"),
        )
        for g in case_data["subgoals"]
    ]

    schema_rules = [
        SchemaEvolutionRule(
            rule_id=r["rule_id"],
            lifecycle_action=r["lifecycle_action"],
            target_entity_id=r["target_entity_id"],
            trigger_type=r["trigger_type"],
            trigger_tick=r.get("trigger_tick"),
            trigger_condition=r.get("trigger_condition"),
            payload=r.get("payload", {}),
            causal_hypothesis=r.get("causal_hypothesis", ""),
        )
        for r in case_data.get("schema_rules", [])
    ]

    orch = DualEngineOrchestrator(
        domain=case_data["domain"],
        initial_entities=copy.deepcopy(case_data["initial_entities"]),
        subgoals=subgoals,
        schema_rules=schema_rules,
        arm="arm3_counterfactual_causal_host",
        max_turns=30,
    )

    audit_turns = []
    latencies = []
    cot_hypotheses = []

    for turn in range(30):
        prompt = orch.render_prompt()
        if mode == "mode_two_tier_cot":
            prompt += "Reason about latent risks or emergent entities in <hypothesis>...</hypothesis>, then emit ACTION.\n"

        grammar = compile_grammar_for_turn(orch, mode)
        temp = 0.7 if mode == "mode_two_tier_cot" else 0.0
        max_tok = 96 if mode == "mode_two_tier_cot" else 32

        raw_output, lat_ms = call_llama(prompt, grammar, temp=temp, max_tokens=max_tok, port=port)
        latencies.append(lat_ms)

        # Parse action from raw output
        hypothesis_text = ""
        action_emission = raw_output
        if "<hypothesis>" in raw_output and "</hypothesis>" in raw_output:
            h_start = raw_output.find("<hypothesis>") + len("<hypothesis>")
            h_end = raw_output.find("</hypothesis>")
            hypothesis_text = raw_output[h_start:h_end].strip()
            action_emission = raw_output[h_end + len("</hypothesis>"):].strip()
            cot_hypotheses.append(hypothesis_text)

        ok, msg, meta = orch.execute_turn(action_emission)
        curr_sg = orch.planner.current_subgoal
        active_sg_id = curr_sg.subgoal_id if curr_sg else "NONE"

        audit_turns.append({
            "turn": orch.current_turn,
            "hypothesis": hypothesis_text if hypothesis_text else None,
            "action": action_emission,
            "success": ok,
            "status": msg,
            "latency_ms": lat_ms,
        })

        if action_emission == "ACTION: RESOLVE COMPLETE" and ok:
            break

    summary = orch.finalize()
    summary["case_id"] = case_data["case_id"]
    summary["mode"] = mode
    summary["mean_latency_ms"] = sum(latencies) / len(latencies) if latencies else 0.0
    summary["turns"] = audit_turns
    summary["cot_hypotheses"] = cot_hypotheses
    return summary


def main():
    cases_path = os.path.join(base_dir, "definition", "cases.json")
    with open(cases_path, "r", encoding="utf-8") as f:
        all_cases = json.load(f)

    # Pick 10 target cases: 7 hard timeout cases (009-015) + 3 reference cases (001, 016, 031)
    target_ids = [
        "DRIFT003-CASE-001",
        "DRIFT003-CASE-009",
        "DRIFT003-CASE-010",
        "DRIFT003-CASE-011",
        "DRIFT003-CASE-012",
        "DRIFT003-CASE-013",
        "DRIFT003-CASE-014",
        "DRIFT003-CASE-015",
        "DRIFT003-CASE-016",
        "DRIFT003-CASE-031",
    ]
    test_cases = [c for c in all_cases if c["case_id"] in target_ids]

    print(f"Loaded {len(test_cases)} target cases for ablation.")
    print("=" * 80)
    print(f"{'Case ID':<20} | {'Mode A (Direct T=0)':<22} | {'Mode B (Two-Tier CoT T=0.7)':<25}")
    print("=" * 80)

    results_a = []
    results_b = []

    for c in test_cases:
        cid = c["case_id"]
        # Mode A: Direct GBNF (with non-deadlocking viable action)
        res_a = run_episode(c, mode="mode_direct_fixed")
        results_a.append(res_a)

        # Mode B: Two-Tier CoT (Free hypothesis + clamped GBNF + Host Sandboxing)
        res_b = run_episode(c, mode="mode_two_tier_cot")
        results_b.append(res_b)

        status_a = f"{'PASS' if res_a['is_success'] else 'FAIL'} ({res_a['turns_executed']}t, {res_a['mean_latency_ms']:.0f}ms)"
        status_b = f"{'PASS' if res_b['is_success'] else 'FAIL'} ({res_b['turns_executed']}t, {res_b['mean_latency_ms']:.0f}ms)"

        print(f"{cid:<20} | {status_a:<22} | {status_b:<25}")

    # Summary
    pass_a = sum(1 for r in results_a if r["is_success"])
    pass_b = sum(1 for r in results_b if r["is_success"])
    mean_lat_a = sum(r["mean_latency_ms"] for r in results_a) / len(results_a)
    mean_lat_b = sum(r["mean_latency_ms"] for r in results_b) / len(results_b)

    print("=" * 80)
    print(f"SUMMARY (N=10):")
    print(f"Mode A (Direct GBNF T=0.0):       {pass_a}/10 ({pass_a*10.0:.1f}%) | Mean Latency: {mean_lat_a:.1f} ms")
    print(f"Mode B (Two-Tier CoT T=0.7):      {pass_b}/10 ({pass_b*10.0:.1f}%) | Mean Latency: {mean_lat_b:.1f} ms")
    print("=" * 80)

    # Sample CoT thinking
    print("\nSAMPLE CoT HYPOTHESES FROM MODE B:")
    for r in results_b[:3]:
        print(f"--- Case: {r['case_id']} ---")
        for h in r["cot_hypotheses"][:2]:
            print(f"  * <hypothesis>{h}</hypothesis>")

    out_file = os.path.join(base_dir, "runs", "ablation_10_cases_cot_vs_direct.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"mode_a": results_a, "mode_b": results_b}, f, indent=2)
    print(f"\nDetailed ablation log saved to: {out_file}")


if __name__ == "__main__":
    main()
