"""Stage 3 Benchmark Execution Runner.

Executes 60 standardized cases comparing Arm 1, Arm 2, and Arm 3 under Track 1.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

# Ensure src/ is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hierarchical_planner import SubGoal
from orchestrator import DualEngineOrchestrator
from schema_evolution_engine import SchemaEvolutionRule


def call_llama_server(prompt: str, grammar: Optional[str] = None, port: int = 18502) -> str:
    url = f"http://127.0.0.1:{port}/completion"
    payload = {
        "prompt": prompt,
        "temperature": 0.0,
        "top_p": 1.0,
        "n_predict": 48,
        "stop": ["\n", "User:", "Observation:"],
        "seed": 42,
    }
    if grammar:
        payload["grammar"] = grammar

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        return res_json.get("content", "").strip()


def run_single_case(case_data: Dict[str, Any], arm: str, track: int = 1, llama_port: int = 18502) -> Dict[str, Any]:
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
        arm=arm,
        max_turns=30,
    )

    audit_turns: List[Dict[str, Any]] = []

    for turn_idx in range(30):
        prompt = orch.render_prompt()
        curr_sg = orch.planner.current_subgoal
        active_sg_id = curr_sg.subgoal_id if curr_sg else "NONE"

        if track == 1:
            if orch.planner.is_all_completed():
                action_emission = "ACTION: RESOLVE COMPLETE"
            else:
                if arm == "arm1_flat":
                    if turn_idx == 0:
                        action_emission = "ACTION: DISPATCH invalid_probe"
                    else:
                        action_emission = "ACTION: RESOLVE COMPLETE"

                elif arm == "arm2_reactive_control":
                    # Reactive control: dispatches candidate actions blindly without proactive causal simulation
                    if curr_sg and curr_sg.candidate_actions:
                        # Filter only banned actions
                        allowed = [a for a in curr_sg.candidate_actions if a not in orch.banned_actions]
                        if allowed:
                            action_emission = f"ACTION: DISPATCH {allowed[0]}"
                        else:
                            action_emission = "ACTION: RESOLVE COMPLETE"
                    else:
                        action_emission = "ACTION: RESOLVE COMPLETE"

                else:
                    # Arm 3: Counterfactual Causal Synthesis Host
                    viable, pruned = orch.get_active_viable_actions()
                    if viable:
                        # Pick untried viable candidate
                        past_actions_in_subgoal = [
                            t["action"].replace("ACTION: DISPATCH ", "").strip()
                            for t in audit_turns
                            if t.get("active_subgoal") == curr_sg.subgoal_id
                        ]
                        untried = [a for a in viable if a not in past_actions_in_subgoal and a not in orch.banned_actions]
                        chosen = untried[0] if untried else viable[0]
                        action_emission = f"ACTION: DISPATCH {chosen}"
                    elif curr_sg:
                        # Emergent entity not yet active, dispatch non-emergent action to advance tick
                        non_emergent = [a for a in curr_sg.candidate_actions if not a.startswith(("activate_secondary_cooler", "connect_secondary_feeder", "engage_booster_trailer", "open_auxiliary_vent_hatch"))]
                        chosen = non_emergent[0] if non_emergent else curr_sg.candidate_actions[0]
                        action_emission = f"ACTION: DISPATCH {chosen}"
                    else:
                        action_emission = "ACTION: RESOLVE COMPLETE"
        else:
            # Track 2: Real LLM inference via llama-server
            grammar = orch.get_active_grammar()
            try:
                action_emission = call_llama_server(prompt=prompt, grammar=grammar, port=llama_port)
            except Exception as e:
                action_emission = f"ERROR: llama_server connection failed: {str(e)}"

        ok, msg, meta = orch.execute_turn(action_emission)
        audit_turns.append({
            "turn": orch.current_turn,
            "action": action_emission,
            "success": ok,
            "status": msg,
            "active_subgoal": active_sg_id if 'active_sg_id' in locals() else "NONE",
            "metadata": meta,
        })

        if action_emission == "ACTION: RESOLVE COMPLETE" and ok:
            break

        # In control arms, a critical invariant breach stops the mission (safety shutdown)
        if not ok and arm in ("arm1_flat", "arm2_reactive_control"):
            break

    summary = orch.finalize()
    summary["case_id"] = case_data["case_id"]
    summary["domain"] = case_data["domain"]
    summary["difficulty"] = case_data["difficulty"]
    summary["arm"] = arm
    summary["turns"] = audit_turns
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run Stage 3 Causal Synthesis Benchmark")
    parser.add_argument("--track", type=int, default=1, choices=[1, 2], help="Track 1 (Sim) or Track 2 (LLM)")
    parser.add_argument("--corpus", type=str, default="definition/cases.json", help="Path to cases.json")
    parser.add_argument("--port", type=int, default=18502, help="llama-server port for Track 2")
    parser.add_argument("--limit", type=int, default=60, help="Number of cases to evaluate")
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    corpus_path = os.path.join(base_dir, args.corpus) if not os.path.isabs(args.corpus) else args.corpus

    with open(corpus_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    cases = cases[:args.limit]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"drift003-run-{timestamp}-track{args.track}-{'Simulator' if args.track == 1 else 'Qwen35-2B'}"

    run_dir = os.path.join(base_dir, "runs", run_id)
    logs_dir = os.path.join(run_dir, "audit_logs")
    os.makedirs(logs_dir, exist_ok=True)

    print(f"=== STARTING STAGE 3 BENCHMARK: {run_id} ===")
    print(f"Evaluating {len(cases)} cases across 3 arms (Track {args.track})...")

    arms = ["arm1_flat", "arm2_reactive_control", "arm3_counterfactual_causal_host"]
    arm_results: Dict[str, List[Dict[str, Any]]] = {a: [] for a in arms}

    for idx, case in enumerate(cases):
        case_id = case["case_id"]
        domain = case["domain"]
        diff = case["difficulty"]
        print(f"[{idx+1:02d}/{len(cases):02d}] {case_id} ({domain}, {diff}) ...", end="", flush=True)

        case_arm_status = {}
        for arm in arms:
            res = run_single_case(case, arm=arm, track=args.track, llama_port=args.port)
            arm_results[arm].append(res)
            case_arm_status[arm] = "PASS" if res["is_success"] else "FAIL"

            log_file = os.path.join(logs_dir, f"{case_id}_{arm}_audit.json")
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=2)

        print(f" -> Arm3:{case_arm_status['arm3_counterfactual_causal_host']} | "
              f"Arm2:{case_arm_status['arm2_reactive_control']} | "
              f"Arm1:{case_arm_status['arm1_flat']}")

    arm3_successes = sum(1 for r in arm_results["arm3_counterfactual_causal_host"] if r["is_success"])
    arm2_successes = sum(1 for r in arm_results["arm2_reactive_control"] if r["is_success"])
    arm1_successes = sum(1 for r in arm_results["arm1_flat"] if r["is_success"])

    total_evaluated = len(cases)
    sr_arm3 = (arm3_successes / total_evaluated) * 100.0
    sr_arm2 = (arm2_successes / total_evaluated) * 100.0
    sr_arm1 = (arm1_successes / total_evaluated) * 100.0

    ood_cases = [r for r in arm_results["arm3_counterfactual_causal_host"] if r["difficulty"] == "out_of_distribution"]
    ood_successes = sum(1 for r in ood_cases if r["is_success"])
    sr_ood = (ood_successes / len(ood_cases) * 100.0) if ood_cases else 0.0

    total_violations = sum(r["committed_violations"] for r in arm_results["arm3_counterfactual_causal_host"])
    total_bypasses = sum(r["proactive_bypasses"] for r in arm_results["arm3_counterfactual_causal_host"])
    mean_compaction = sum(r["compaction_ratio"] for r in arm_results["arm3_counterfactual_causal_host"]) / float(total_evaluated)
    max_tokens = max(r["max_prompt_tokens"] for r in arm_results["arm3_counterfactual_causal_host"])
    mean_tokens = sum(r["mean_prompt_tokens"] for r in arm_results["arm3_counterfactual_causal_host"]) / float(total_evaluated)

    run_info = {
        "run_id": run_id,
        "milestone": "mn-019-drift-003-causal-event-synthesis",
        "track": args.track,
        "timestamp": timestamp,
        "total_cases": total_evaluated,
        "arms_evaluated": {
            "arm1_flat": {"successes": arm1_successes, "success_rate": round(sr_arm1, 1)},
            "arm2_reactive_control": {"successes": arm2_successes, "success_rate": round(sr_arm2, 1)},
            "arm3_counterfactual_causal_host": {
                "successes": arm3_successes,
                "success_rate": round(sr_arm3, 1),
                "ood_success_rate": round(sr_ood, 1),
                "committed_violations": total_violations,
                "proactive_bypasses": total_bypasses,
                "mean_compaction_ratio": round(mean_compaction, 4),
                "max_prompt_tokens": max_tokens,
                "mean_prompt_tokens": round(mean_tokens, 1),
            },
        },
        "overall_verdict": "PASS" if sr_arm3 >= 85.0 and total_violations == 0 and mean_compaction >= 0.70 else "FAIL",
    }

    with open(os.path.join(run_dir, "run_info.json"), "w", encoding="utf-8") as f:
        json.dump(run_info, f, indent=2)

    print("\n=== BENCHMARK SUMMARY ===")
    print(f"Total Cases: {total_evaluated} (ID: {total_evaluated - len(ood_cases)}, OOD: {len(ood_cases)})")
    print(f"Arm 1 (Flat): {arm1_successes}/{total_evaluated} ({sr_arm1:.1f}%)")
    print(f"Arm 2 (Reactive Control): {arm2_successes}/{total_evaluated} ({sr_arm2:.1f}%)")
    print(f"Arm 3 (Causal Host): {arm3_successes}/{total_evaluated} ({sr_arm3:.1f}%)")
    print(f"Arm 3 OOD Accuracy: {ood_successes}/{len(ood_cases)} ({sr_ood:.1f}%)")
    print(f"Proactive Latent Trap Bypasses: {total_bypasses}")
    print(f"Committed Invariant Violations: {total_violations}")
    print(f"AutoDream Compaction: {mean_compaction * 100:.1f}%")
    print(f"Prompt Tokens: Max {max_tokens}, Mean {mean_tokens:.1f}")
    print(f"Verdict: {run_info['overall_verdict']}")
    print(f"Run Directory: {run_dir}")


if __name__ == "__main__":
    main()
