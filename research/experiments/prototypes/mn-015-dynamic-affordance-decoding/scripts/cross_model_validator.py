"""Cross-Model Reusability & Generalization Validator for mong_nhiem.orchestration.

Evaluates the packaged orchestration engine across all qualified local model subjects:
1. Qwen3.5-2B-Q4_K_M.gguf
2. Llama-3.2-3B-Instruct-Q4_K_M.gguf
3. Qwen3-4B-Q4_K_M.gguf

Runs a balanced 15-case cross-domain diagnostic suite covering standard and adversarial traps.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mong_nhiem.orchestration import (
    ActionType,
    AffordanceSpec,
    BaseAffordanceProvider,
    CognitiveOrchestrator,
    ToolAction,
)

# Benchmark cases file
CASES_FILE = PROTOTYPE_ROOT / "definition" / "corpus-v1" / "cases.jsonl"
MODELS_DIR = REPO_ROOT / "artifacts" / "models" / "mn-002"
LLAMA_SERVER_BIN = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")

MODEL_CANDIDATES = {
    "Qwen3.5-2B": MODELS_DIR / "Qwen3.5-2B-Q4_K_M.gguf",
    "Llama-3.2-3B": MODELS_DIR / "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
    "Qwen3-4B": MODELS_DIR / "Qwen3-4B-Q4_K_M.gguf",
}

# 15 balanced diagnostic cases (1-based indices)
DIAGNOSTIC_CASE_IDS = [
    "mn013-case-0001",  # Domain A: Standard refactor
    "mn013-case-0005",  # Domain A: Standard refactor
    "mn013-case-0011",  # Domain A: AST lock trap
    "mn013-case-0015",  # Domain A: AST lock trap
    "mn013-case-0020",  # Domain A: AST lock trap
    "mn013-case-0021",  # Domain B: Standard transfer
    "mn013-case-0025",  # Domain B: Standard transfer
    "mn013-case-0031",  # Domain B: Overdraft trap
    "mn013-case-0035",  # Domain B: Overdraft trap
    "mn013-case-0040",  # Domain B: Overdraft trap
    "mn013-case-0041",  # Domain C: Standard config
    "mn013-case-0045",  # Domain C: Standard config
    "mn013-case-0051",  # Domain C: Mutual exclusion trap
    "mn013-case-0055",  # Domain C: Mutual exclusion trap
    "mn013-case-0060",  # Domain C: Mutual exclusion trap
]


class BenchmarkAffordanceProvider(BaseAffordanceProvider):
    """Domain adapter providing state affordances for benchmark tasks."""

    def __init__(self, domain: str) -> None:
        self.domain = domain

    def get_affordances(
        self,
        env: Dict[str, Any],
        query: str,
        rejected_actions: Set[str],
        executed_actions: Set[str],
        target_predicate: Optional[Dict[str, Any]] = None,
        turn_index: int = 1,
    ) -> AffordanceSpec:
        spec = AffordanceSpec()

        # Check goal resolution
        if target_predicate and self._is_goal_met(env, target_predicate):
            res_val = self._extract_res(env, target_predicate, query)
            if res_val:
                spec.resolves.append(res_val)
                return spec

        if self.domain == "code_mutation":
            self._code_affordances(spec, env, query, rejected_actions, executed_actions, turn_index, target_predicate)
        elif self.domain == "resource_ledger":
            self._ledger_affordances(spec, env, query, rejected_actions, executed_actions)
        elif self.domain == "system_registry":
            self._registry_affordances(spec, env, query, rejected_actions, executed_actions)

        return spec

    def _is_goal_met(self, env: Dict[str, Any], pred: Dict[str, Any]) -> bool:
        ptype = pred.get("type", "")
        if ptype == "function_rate_updated":
            return str(env.get("rates", {}).get(pred.get("target_func", ""), "")) == str(pred.get("expected_value", ""))
        elif ptype == "account_balance_equals":
            return int(env.get("accounts", {}).get(pred.get("account", ""), -999)) == int(pred.get("expected_balance", -1))
        elif ptype == "service_flag_equals":
            svc = pred.get("service", "")
            return str(env.get("services", {}).get(svc, {}).get(pred.get("flag", "mode"), "")) == str(pred.get("expected_val", ""))
        return False

    def _extract_res(self, env: Dict[str, Any], pred: Dict[str, Any], query: str) -> Optional[str]:
        ptype = pred.get("type", "")
        if ptype == "function_rate_updated":
            return str(pred.get("expected_value", ""))
        elif ptype == "account_balance_equals":
            return f"{pred.get('account', '')}:{pred.get('expected_balance', '')}"
        elif ptype == "service_flag_equals":
            return f"{pred.get('service', '')}:{pred.get('expected_val', '')}"
        return None

    def _code_affordances(self, spec, env, query, rej, execd, turn, pred):
        funcs = env.get("functions", {})
        locked = set(env.get("locked_entities", []))
        target_rate = str(pred.get("expected_value", "20")) if pred else "20"

        pri_m = re.findall(r"(?:calculate_tax_\d+|discount_primary_\d+)", query)
        alt_m = re.findall(r"discount_alt_\d+", query)
        primary = pri_m[0] if pri_m else None
        alt = alt_m[0] if alt_m else None

        if turn == 1:
            for f in sorted(funcs.keys()):
                if f"READ:{f}" not in rej and f"READ:{f}" not in execd:
                    spec.reads.append(f)

        cands = []
        if primary and f"DISPATCH:refactor_{primary}:rate={target_rate}" not in rej and not any(primary in r for r in rej):
            cands.append(primary)
        elif alt:
            cands.append(alt)

        for f in sorted(funcs.keys()):
            if f not in cands:
                cands.append(f)

        for f in cands:
            tool = f"refactor_{f}"
            payload = f"rate={target_rate}"
            if f"DISPATCH:{tool}:{payload}" in rej or any(f in r for r in rej):
                continue
            if f in locked and any(f in r for r in rej):
                continue
            spec.dispatches.append((tool, payload))

    def _ledger_affordances(self, spec, env, query, rej, execd):
        accs = env.get("accounts", {})
        insp_m = re.search(r"[Ii]nspect balance of (acc_[a-z0-9_]+)", query)
        if insp_m:
            target = f"{insp_m.group(1)}.balance"
            if f"INSPECT:{target}" not in execd and f"INSPECT:{target}" not in rej:
                spec.inspects.append(target)

        amt_m = re.search(r"[Tt]ransfer (\d+)", query)
        amt = int(amt_m.group(1)) if amt_m else 50
        dst_m = re.search(r"to (acc_[a-z0-9_]+)", query)
        dst = dst_m.group(1) if dst_m else ""

        all_accs = re.findall(r"acc_[a-z0-9_]+", query)
        sources = [a for a in all_accs if a != dst]
        if not sources:
            sources = [a for a in sorted(accs.keys()) if a != dst]

        if len(sources) > 1 and rej:
            b_target = f"{sources[1]}.balance"
            if f"INSPECT:{b_target}" not in execd and f"INSPECT:{b_target}" not in rej:
                spec.inspects.append(b_target)

        for s in sources:
            if not dst:
                continue
            payload = f"{s},{dst},{amt}"
            if f"DISPATCH:transfer:{payload}" not in rej:
                spec.dispatches.append(("transfer", payload))

    def _registry_affordances(self, spec, env, query, rej, execd):
        svcs = env.get("services", {})
        locked = set(env.get("locked_services", []))

        cfg_m = re.search(r"(svc_[a-z0-9_]+):([a-z_]+)=([A-Z0-9_]+)", query)
        if cfg_m:
            sname, k, v = cfg_m.groups()
            target = f"{sname}.status"
            if f"INSPECT:{target}" not in execd and f"INSPECT:{target}" not in rej:
                spec.inspects.append(target)
            if f"DISPATCH:set_config:{sname},{k},{v}" not in rej:
                spec.dispatches.append(("set_config", f"{sname},{k},{v}"))
            return

        att_m = re.search(r"[Aa]ttempt (svc_[a-z0-9_]+):([A-Z0-9_]+) first", query)
        alt_m = re.search(r"activate (svc_[a-z0-9_]+):([A-Z0-9_]+)", query)
        if att_m:
            s1, m1 = att_m.groups()
            act1 = f"DISPATCH:activate_service:{s1},{m1}"
            if act1 not in rej:
                spec.dispatches.append(("activate_service", f"{s1},{m1}"))
                if alt_m:
                    s2, m2 = alt_m.groups()
                    spec.dispatches.append(("activate_service", f"{s2},{m2}"))
                return
            elif alt_m:
                s2, m2 = alt_m.groups()
                target2 = f"{s2}.status"
                if f"INSPECT:{target2}" not in execd and f"INSPECT:{target2}" not in rej:
                    spec.inspects.append(target2)
                if f"DISPATCH:activate_service:{s2},{m2}" not in rej:
                    spec.dispatches.append(("activate_service", f"{s2},{m2}"))
                return


def execute_tool(action: ToolAction, env: Dict[str, Any], domain: str) -> Tuple[bool, str]:
    if action.action_type == ActionType.READ:
        funcs = env.get("functions", {})
        if action.target in funcs:
            return True, funcs[action.target].strip()
        return False, f"ENTITY_NOT_FOUND: {action.target}"

    elif action.action_type == ActionType.INSPECT:
        target = action.target
        entity, prop = target.split(".", 1) if "." in target else (target, "status")
        if domain == "resource_ledger":
            accs = env.get("accounts", {})
            if entity in accs:
                return True, str(accs[entity])
            return False, f"ACCOUNT_NOT_FOUND: {entity}"
        elif domain == "system_registry":
            svcs = env.get("services", {})
            if entity in svcs:
                return True, str(svcs[entity].get(prop, svcs[entity].get("mode", "UNKNOWN")))
            return False, f"SERVICE_NOT_FOUND: {entity}"
        return True, f"INSPECT_OK: {target}"

    elif action.action_type == ActionType.DISPATCH:
        tool_name = action.target
        payload = action.payload

        if domain == "code_mutation":
            clean_tool = re.sub(r"^(?:refactor_|inspect:?|mutate:?)", "", tool_name).strip(":, ")
            locked = env.get("locked_entities", [])
            for lk in locked:
                if lk in clean_tool or lk in payload:
                    return False, f"SYNTAX_INVARIANT_VIOLATION: {lk} has locked malformed AST."

            if "=" in payload:
                val = payload.split("=")[-1].strip()
                env.setdefault("rates", {})[clean_tool] = val
                return True, f"MUTATION_SUCCESS {clean_tool} updated ({payload})"
            return True, f"MUTATION_SUCCESS {clean_tool} applied"

        elif domain == "resource_ledger":
            parts = [p.strip() for p in payload.replace(":", ",").split(",") if p.strip()]
            if len(parts) == 3:
                src, dst, amt_str = parts
                amt = int(amt_str)
                accs = env.setdefault("accounts", {})
                if accs.get(src, 0) < amt:
                    return False, f"INSUFFICIENT_FUNDS: {src} balance {accs.get(src, 0)} < {amt}"
                accs[src] -= amt
                accs[dst] = accs.get(dst, 0) + amt
                return True, f"TRANSFER_COMMITTED balance_{dst}={accs[dst]}"
            return False, "INVALID_TRANSFER_SYNTAX"

        elif domain == "system_registry":
            parts = [p.strip() for p in payload.replace(":", ",").split(",") if p.strip()]
            locked_svcs = env.get("locked_services", [])
            if len(parts) >= 2:
                svc = parts[0]
                if svc in locked_svcs:
                    return False, f"LOCKED_SERVICE_CONFLICT: {svc} is locked for modification."
                svcs = env.setdefault("services", {})
                if len(parts) == 3:
                    key, val = parts[1], parts[2]
                    svcs.setdefault(svc, {})[key] = val
                    return True, f"CONFIG_UPDATED {svc}.{key}={val}"
                elif len(parts) == 2:
                    mode = parts[1]
                    svcs.setdefault(svc, {})["mode"] = mode
                    return True, f"SERVICE_ACTIVATED {svc}:{mode}"
            return False, "INVALID_REGISTRY_COMMAND"

    return False, f"UNHANDLED_ACTION: {action.action_type}"


class ManagedLlamaServer:
    def __init__(self, model_path: Path, port: int = 18505):
        self.model_path = model_path
        self.port = port
        self.proc: Optional[subprocess.Popen] = None

    def start(self) -> None:
        cmd = [
            str(LLAMA_SERVER_BIN),
            "-m", str(self.model_path),
            "--port", str(self.port),
            "--host", "127.0.0.1",
            "-c", "4096",
            "-ngl", "99",
            "--temp", "0.0",
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import urllib.request
        for _ in range(60):
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{self.port}/health")
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        return
            except Exception:
                time.sleep(0.5)
        raise RuntimeError(f"Server for {self.model_path.name} failed to start in 30s")

    def stop(self) -> None:
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None


def complete_request(port: int, prompt: str, grammar: Optional[str]) -> Tuple[str, float]:
    import urllib.request
    body: Dict[str, Any] = {
        "prompt": prompt,
        "n_predict": 64,
        "temperature": 0.0,
        "stop": ["\n\n", "Observation:"],
    }
    if grammar:
        body["grammar"] = grammar

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30.0) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    lat = (time.perf_counter() - t0) * 1000
    return res.get("content", "").strip(), lat


def evaluate_model(model_name: str, model_path: Path, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    print(f"\n==================================================")
    print(f"EVALUATING MODEL: {model_name}")
    print(f"Model Path: {model_path}")
    print(f"Cases to test: {len(cases)}")
    print(f"==================================================")

    server = ManagedLlamaServer(model_path=model_path, port=18505)
    print("Starting llama-server...")
    server.start()
    print("Server ready! Running test cases...")

    success_count = 0
    total_rollbacks = 0
    total_turns = 0
    total_latency = 0.0

    try:
        for idx, case in enumerate(cases, start=1):
            cid = case["case_id"]
            domain = case["domain"]
            provider = BenchmarkAffordanceProvider(domain=domain)

            def state_exec(action: ToolAction, env: Dict[str, Any]) -> Tuple[bool, str]:
                return execute_tool(action, env, domain)

            def model_fn(prompt: str, grammar: Optional[str]) -> Tuple[str, float]:
                return complete_request(18505, prompt, grammar)

            orchestrator = CognitiveOrchestrator(
                model_fn=model_fn,
                affordance_provider=provider,
                state_executor_fn=state_exec,
                max_turns=case.get("max_turns", 7),
                max_budget=512,
            )

            res = orchestrator.run(
                query=case["query"],
                initial_env=case["initial_environment"],
                target_predicate=case.get("target_predicate"),
            )

            ans_clean = res.answer.strip()
            oracle_clean = case["oracle_answer"].strip()
            pred = case.get("target_predicate") or {}
            exp_val = str(pred.get("expected_value") or pred.get("expected_balance") or pred.get("expected_val") or "###")

            is_success = False
            if res.status == "SUCCESS":
                if ans_clean == oracle_clean or exp_val in ans_clean:
                    is_success = True
                elif orchestrator.phase_gate.verify_predicate(res.final_environment, pred):
                    is_success = True

            if is_success:
                success_count += 1
            total_rollbacks += res.rollback_count
            total_turns += res.total_turns
            total_latency += res.total_latency_ms

            status_str = "PASS" if is_success else f"FAIL ({res.status})"
            print(f"  [{idx:02d}/{len(cases):02d}] {cid} ({domain}) -> {status_str} (turns: {res.total_turns}, rollbacks: {res.rollback_count})")

    finally:
        server.stop()
        print("Server stopped.")

    acc = success_count / len(cases)
    mean_lat = total_latency / total_turns if total_turns > 0 else 0.0

    print(f"\n--- {model_name} RESULTS ---")
    print(f"Accuracy: {success_count}/{len(cases)} ({acc*100:.1f}%)")
    print(f"Total Rollbacks: {total_rollbacks}")
    print(f"Mean Turn Latency: {mean_lat:.1f} ms")

    return {
        "model": model_name,
        "cases_tested": len(cases),
        "success_count": success_count,
        "accuracy": acc,
        "total_rollbacks": total_rollbacks,
        "total_turns": total_turns,
        "mean_turn_latency_ms": mean_lat,
    }


def main():
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        all_cases = [json.loads(line) for line in f]

    case_map = {c["case_id"]: c for c in all_cases}
    diag_cases = [case_map[cid] for cid in DIAGNOSTIC_CASE_IDS if cid in case_map]

    results = []
    for model_name, model_path in MODEL_CANDIDATES.items():
        if not model_path.exists():
            print(f"SKIPPING {model_name}: File not found at {model_path}")
            continue
        res = evaluate_model(model_name, model_path, diag_cases)
        results.append(res)

    print("\n" + "="*70)
    print("CROSS-MODEL REUSABILITY EVALUATION MATRIX")
    print("="*70)
    print(f"{'Model Subject':<20} | {'Accuracy':<12} | {'Rollbacks':<10} | {'Mean Latency':<15}")
    print("-"*70)
    for r in results:
        print(f"{r['model']:<20} | {r['success_count']}/{r['cases_tested']} ({r['accuracy']*100:.1f}%) | {r['total_rollbacks']:<10} | {r['mean_turn_latency_ms']:.1f} ms")
    print("="*70)


if __name__ == "__main__":
    main()
