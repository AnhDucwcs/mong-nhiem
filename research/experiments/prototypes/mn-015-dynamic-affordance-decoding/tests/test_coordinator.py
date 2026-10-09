"""Unit tests for Integrated Host Coordinator in MN-015."""
import re
import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from coordinator import Coordinator


def test_coordinator_trap_recovery_simulation():
    # True grammar-compliant model simulation: selects an action permitted by the GBNF grammar
    def mock_model_fn(prompt: str, grammar: str):
        task_section = prompt.split("Task: Activate")[-1]
        if "resolve-action" in grammar:
            m = re.search(r'valid-resolve-target ::= "([^"]+)"', grammar)
            val = m.group(1) if m else "unknown"
            return f"ACTION: RESOLVE {val}", 5.0
        elif "ROLLBACK_COMMITTED" in task_section or "Constraint:" in task_section:
            return "ACTION: DISPATCH activate_service svc_worker_b_51,CONSERVATIVE_PIPELINE", 5.0
        else:
            return "ACTION: DISPATCH activate_service svc_worker_a_51,AGGRESSIVE_PARALLEL", 5.0

    coord = Coordinator(arm=2, max_turns=7, model_fn=mock_model_fn)
    initial_env = {
        "services": {
            "svc_worker_a_51": {"mode": "OFFLINE", "status": "LOCKED"},
            "svc_worker_b_51": {"mode": "STANDBY", "status": "AVAILABLE"},
        },
        "locked_services": ["svc_worker_a_51"],
    }
    query = (
        "Activate high-throughput processing. Attempt svc_worker_a_51:AGGRESSIVE_PARALLEL first. "
        "If rejected due to lock conflict, rollback and activate svc_worker_b_51:CONSERVATIVE_PIPELINE, "
        "then resolve final mode of svc_worker_b_51."
    )
    target_pred = {
        "type": "service_flag_equals",
        "service": "svc_worker_b_51",
        "flag": "mode",
        "expected_val": "CONSERVATIVE_PIPELINE",
    }

    result = coord.run(
        query=query,
        initial_env=initial_env,
        domain="system_registry",
        target_predicate=target_pred,
    )

    assert result.status == "SUCCESS"
    assert result.answer == "svc_worker_b_51:CONSERVATIVE_PIPELINE"
    assert result.rollback_count == 1
    assert result.all_under_budget is True


def test_coordinator_budget_under_512_tokens():
    # Ensure all prompts generated across multi-turn recovery stay <= 512 tokens
    prompts_collected = []

    def tracking_model_fn(prompt: str, grammar: str):
        prompts_collected.append(prompt)
        task_section = prompt.split("Task: Transfer")[-1]
        if "resolve-action" in grammar:
            m = re.search(r'valid-resolve-target ::= "([^"]+)"', grammar)
            val = m.group(1) if m else "demo_dst:100"
            return f"ACTION: RESOLVE {val}", 2.0
        elif "ROLLBACK_COMMITTED" in task_section or "Constraint:" in task_section:
            return "ACTION: DISPATCH transfer demo_sec,demo_dst,100", 2.0
        return "ACTION: DISPATCH transfer demo_pri,demo_dst,100", 2.0

    coord = Coordinator(arm=2, max_turns=5, max_budget=512, model_fn=tracking_model_fn)
    initial_env = {
        "accounts": {"demo_pri": 10, "demo_sec": 500, "demo_dst": 0}
    }
    query = "Transfer 100 to demo_dst. Try demo_pri first, else backup demo_sec, then resolve balance of demo_dst."
    target_pred = {
        "type": "account_balance_equals",
        "account": "demo_dst",
        "expected_balance": "100",
    }

    res = coord.run(
        query=query,
        initial_env=initial_env,
        domain="resource_ledger",
        target_predicate=target_pred,
    )

    assert res.status == "SUCCESS"
    for p in prompts_collected:
        approx_toks = len(p) // 4
        assert approx_toks < 512, f"Prompt exceeded 512 tokens: {approx_toks}"
