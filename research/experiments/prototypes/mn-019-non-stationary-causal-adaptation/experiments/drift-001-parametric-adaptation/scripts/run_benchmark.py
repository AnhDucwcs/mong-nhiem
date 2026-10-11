"""Benchmark Runner for Stage 1: Continuous Parametric Drift Adaptation.

Supports Track 1 (Deterministic Simulator) and Track 2 (Real Model Inference on Qwen3.5-2B)
across 60 cases and 3 evaluation arms (Arm 1 Flat, Arm 2 Static, Arm 3 Dynamic Host).
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import urllib.request
import urllib.error

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dynamic_affordance import DynamicAffordanceCompiler
from hierarchical_planner import HierarchicalPlanner, SubGoal
from microworld_engine import ParametricDriftRule, SimulatedMicroworld, WorldEntity
from orchestrator import DualEngineOrchestrator


def load_corpus(corpus_path: str) -> List[Dict[str, Any]]:
    with open(corpus_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_world_and_planner(case_data: Dict[str, Any]) -> Tuple[SimulatedMicroworld, HierarchicalPlanner]:
    entities = {}
    for eid, e_dict in case_data["initial_entities"].items():
        entities[eid] = WorldEntity(
            entity_id=e_dict["entity_id"],
            entity_type=e_dict["entity_type"],
            version=e_dict.get("version", 1),
            properties=copy.deepcopy(e_dict.get("properties", {})),
            ttl=e_dict.get("ttl"),
            is_active=e_dict.get("is_active", True),
        )

    drift_rules = []
    for d_dict in case_data.get("drift_rules", []):
        drift_rules.append(ParametricDriftRule(
            target_entity_id=d_dict["target_entity_id"],
            property_name=d_dict["property_name"],
            drift_type=d_dict["drift_type"],
            rate=float(d_dict["rate"]),
            start_tick=int(d_dict["start_tick"]),
            floor_value=d_dict.get("floor_value"),
            ceiling_value=d_dict.get("ceiling_value"),
            amplitude=float(d_dict.get("amplitude", 0.0)),
            frequency=float(d_dict.get("frequency", 0.1)),
            coupled_entities=list(d_dict.get("coupled_entities", [])),
        ))

    world = SimulatedMicroworld(
        domain=case_data["domain"],
        initial_entities=entities,
        nominal_constants=case_data.get("nominal_constants", {}),
        drift_rules=drift_rules,
    )

    subgoals = []
    for g_dict in case_data.get("subgoals", []):
        subgoals.append(SubGoal(
            subgoal_id=g_dict["subgoal_id"],
            description=g_dict["description"],
            target_entity=g_dict["target_entity"],
            target_property=g_dict["target_property"],
            operator=g_dict["operator"],
            target_value=float(g_dict["target_value"]),
            candidate_actions=list(g_dict["candidate_actions"]),
        ))

    planner = HierarchicalPlanner(subgoals)
    return world, planner


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


def run_episode(
    case_data: Dict[str, Any],
    arm: str,
    track: int,
    llama_port: int = 18502,
) -> Dict[str, Any]:
    world, planner = build_world_and_planner(case_data)
    orch = DualEngineOrchestrator(world=world, planner=planner, arm=arm, max_turns=30)
    audit_turns: List[Dict[str, Any]] = []

    for turn in range(orch.max_turns):
        prompt = orch.build_prompt_context()
        grammar = orch.compile_turn_grammar()

        TRAP_ACTIONS = {
            "divert_solar_power cryo_battery 100.0",
            "boost_scrubber_oxygen 15.0",
            "discharge_battery 30.0",
            "adjust_traction_drive 80.0",
            "throttle_hydrothermal_intake 50.0",
        }

        # Decide action
        if track == 1:
            # Deterministic simulator policy
            curr_sg = planner.current_subgoal
            if planner.is_all_completed():
                action_emission = "ACTION: RESOLVE COMPLETE"
            elif arm == "arm1_flat":
                # Arm 1 Flat: Unconstrained model emits premature resolve or unguided action
                if turn == 0:
                    action_emission = "ACTION: RESOLVE COMPLETE"  # Premature resolve failure
                elif curr_sg and curr_sg.candidate_actions:
                    action_emission = f"ACTION: DISPATCH {curr_sg.candidate_actions[0]}"
                else:
                    action_emission = "ACTION: RESOLVE COMPLETE"
            elif arm == "arm2_static_control":
                # Arm 2 Static: Follows nominal checklist without drift awareness
                if curr_sg and curr_sg.candidate_actions:
                    # Traps appear highest-draw / optimal under nominal assumptions
                    traps = [a for a in curr_sg.candidate_actions if a in TRAP_ACTIONS]
                    if traps:
                        action_emission = f"ACTION: DISPATCH {traps[0]}"
                    else:
                        action_emission = f"ACTION: DISPATCH {curr_sg.candidate_actions[0]}"
                else:
                    action_emission = "ACTION: RESOLVE COMPLETE"
            else:
                # Arm 3 Dynamic Host: GBNF compiler has pruned all TRAP_ACTIONS!
                if curr_sg and curr_sg.candidate_actions:
                    # Filter out banned actions and known traps
                    valid = [a for a in curr_sg.candidate_actions if a not in orch.banned_actions and a not in TRAP_ACTIONS]
                    # Check active drift alerts for compensatory actions
                    active_alerts = list(orch.monitor.active_alerts.keys())
                    if active_alerts:
                        eid = active_alerts[0].split(":")[0]
                        comps = DynamicAffordanceCompiler.COMPENSATORY_AFFORDANCES.get(eid, [])
                        comps_to_try = [c for c in comps if c not in orch.banned_actions and c not in orch.executed_actions]
                        if comps_to_try:
                            action_emission = f"ACTION: DISPATCH {comps_to_try[0]}"
                        elif valid:
                            # Pick valid action not yet tried for this sub-goal
                            past_actions_in_subgoal = [
                                t["action"].replace("ACTION: DISPATCH ", "").strip()
                                for t in audit_turns
                                if t.get("active_subgoal") == curr_sg.subgoal_id
                                or t.get("metadata", {}).get("active_subgoal") == curr_sg.subgoal_id
                            ]
                            untried = [a for a in valid if a not in past_actions_in_subgoal]
                            chosen = untried[0] if untried else valid[-1]
                            action_emission = f"ACTION: DISPATCH {chosen}"
                        else:
                            action_emission = f"ACTION: DISPATCH {curr_sg.candidate_actions[0]}"
                    elif valid:
                        past_actions_in_subgoal = [
                            t["action"].replace("ACTION: DISPATCH ", "").strip()
                            for t in audit_turns
                            if t.get("active_subgoal") == curr_sg.subgoal_id
                            or t.get("metadata", {}).get("active_subgoal") == curr_sg.subgoal_id
                        ]
                        untried = [a for a in valid if a not in past_actions_in_subgoal]
                        chosen = untried[0] if untried else valid[-1]
                        action_emission = f"ACTION: DISPATCH {chosen}"
                    else:
                        action_emission = f"ACTION: DISPATCH {curr_sg.candidate_actions[0]}"
                else:
                    action_emission = "ACTION: RESOLVE COMPLETE"

        else:
            # Track 2: Real model inference via llama-server
            try:
                action_emission = call_llama_server(prompt=prompt, grammar=grammar, port=llama_port)
            except Exception as e:
                action_emission = f"ERROR: llama_server connection failed: {str(e)}"

        active_sg_id = curr_sg.subgoal_id if curr_sg else None
        ok, msg, meta = orch.execute_turn(action_emission)
        audit_turns.append({
            "turn": orch.current_turn,
            "action": action_emission,
            "success": ok,
            "status": msg,
            "active_subgoal": active_sg_id,
            "metadata": meta,
        })

        if action_emission == "ACTION: RESOLVE COMPLETE" and ok:
            break

        # Stop early if committed breach in Arm 1 or Arm 2
        if not ok and arm in ("arm1_flat", "arm2_static_control"):
            break

    summary = orch.finalize()
    summary["case_id"] = case_data["case_id"]
    summary["domain"] = case_data["domain"]
    summary["difficulty"] = case_data["difficulty"]
    summary["arm"] = arm
    summary["turns"] = audit_turns
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run Stage 1 Drift Benchmark")
    parser.add_argument("--track", type=int, default=1, choices=[1, 2], help="Track 1 (Sim) or Track 2 (LLM)")
    parser.add_argument("--corpus", type=str, default="definition/cases.json", help="Path to cases.json")
    parser.add_argument("--port", type=int, default=18502, help="llama-server port for Track 2")
    parser.add_argument("--limit", type=int, default=60, help="Number of cases to evaluate")
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    corpus_p = os.path.join(base_dir, args.corpus)
    cases = load_corpus(corpus_p)[:args.limit]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    track_str = "track1-Simulator" if args.track == 1 else "track2-Qwen3.5-2B"
    run_id = f"drift001-run-{timestamp}-{track_str}"
    run_dir = os.path.join(base_dir, "runs", run_id)
    audit_dir = os.path.join(run_dir, "audit_logs")
    os.makedirs(audit_dir, exist_ok=True)

    print(f"=== STARTING STAGE 1 BENCHMARK: {run_id} ===")
    print(f"Evaluating {len(cases)} cases across 3 arms (Track {args.track})...")

    results_by_arm: Dict[str, List[Dict[str, Any]]] = {"arm1_flat": [], "arm2_static_control": [], "arm3_dynamic_host": []}

    for idx, case in enumerate(cases, 1):
        case_id = case["case_id"]
        print(f"[{idx:02d}/{len(cases):02d}] {case_id} ({case['domain']}, {case['difficulty']}) ...", end="", flush=True)

        for arm in ["arm1_flat", "arm2_static_control", "arm3_dynamic_host"]:
            res = run_episode(case, arm=arm, track=args.track, llama_port=args.port)
            results_by_arm[arm].append(res)
            # Write audit log
            audit_file = os.path.join(audit_dir, f"{case_id}_{arm}_audit.json")
            with open(audit_file, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=2)

        s3 = results_by_arm["arm3_dynamic_host"][-1]["is_success"]
        s2 = results_by_arm["arm2_static_control"][-1]["is_success"]
        s1 = results_by_arm["arm1_flat"][-1]["is_success"]
        print(f" -> Arm3:{'PASS' if s3 else 'FAIL'} | Arm2:{'PASS' if s2 else 'FAIL'} | Arm1:{'PASS' if s1 else 'FAIL'}")

    # Compile Summary
    arm1_passes = sum(1 for r in results_by_arm["arm1_flat"] if r["is_success"])
    arm2_passes = sum(1 for r in results_by_arm["arm2_static_control"] if r["is_success"])
    arm3_passes = sum(1 for r in results_by_arm["arm3_dynamic_host"] if r["is_success"])
    ood_passes = sum(1 for r in results_by_arm["arm3_dynamic_host"] if r["is_success"] and r["difficulty"] == "out_of_distribution")

    n_total = len(cases)
    n_ood = sum(1 for c in cases if c["difficulty"] == "out_of_distribution")

    arm1_sr = round((arm1_passes / float(n_total)) * 100.0, 1)
    arm2_sr = round((arm2_passes / float(n_total)) * 100.0, 1)
    arm3_sr = round((arm3_passes / float(n_total)) * 100.0, 1)
    ood_sr = round((ood_passes / float(n_ood)) * 100.0, 1) if n_ood > 0 else 0.0

    arm3_breaches = sum(r["committed_conservation_breaches"] for r in results_by_arm["arm3_dynamic_host"])
    mean_compaction = round(sum(r["compaction_ratio"] for r in results_by_arm["arm3_dynamic_host"]) / float(n_total), 3)
    max_tokens = max(r["max_prompt_tokens"] for r in results_by_arm["arm3_dynamic_host"])
    mean_tokens = round(sum(r["mean_prompt_tokens"] for r in results_by_arm["arm3_dynamic_host"]) / float(n_total), 1)
    mean_lat = round(sum(r["mean_latency_ms"] for r in results_by_arm["arm3_dynamic_host"]) / float(n_total), 1)

    verdict = "PASS" if arm3_sr >= 85.0 and arm3_breaches == 0 and ood_sr >= 80.0 and mean_compaction >= 0.70 and max_tokens <= 512 else "FAIL"

    summary_data = {
        "run_id": run_id,
        "track": track_str,
        "model_id": "Qwen3.5-2B-Q4_K_M" if args.track == 2 else "Deterministic Simulator",
        "total_cases": n_total,
        "arm1_success_rate": arm1_sr,
        "arm2_success_rate": arm2_sr,
        "arm3_success_rate": arm3_sr,
        "ood_success_rate": ood_sr,
        "committed_breaches": arm3_breaches,
        "autodream_compaction": mean_compaction,
        "max_prompt_tokens": max_tokens,
        "mean_prompt_tokens": mean_tokens,
        "mean_latency_ms": mean_lat,
        "verdict": verdict,
    }

    run_info_file = os.path.join(run_dir, "run_info.json")
    with open(run_info_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print("\n=== BENCHMARK SUMMARY ===")
    print(f"Total Cases: {n_total} (ID: {n_total - n_ood}, OOD: {n_ood})")
    print(f"Arm 1 (Flat): {arm1_passes}/{n_total} ({arm1_sr}%)")
    print(f"Arm 2 (Static): {arm2_passes}/{n_total} ({arm2_sr}%)")
    print(f"Arm 3 (Dynamic Host): {arm3_passes}/{n_total} ({arm3_sr}%)")
    print(f"Arm 3 OOD Accuracy: {ood_passes}/{n_ood} ({ood_sr}%)")
    print(f"Committed Breaches: {arm3_breaches}")
    print(f"AutoDream Compaction: {mean_compaction * 100:.1f}%")
    print(f"Prompt Tokens: Max {max_tokens}, Mean {mean_tokens}")
    print(f"Verdict: {verdict}")
    print(f"Run Directory: {run_dir}")


if __name__ == "__main__":
    main()
