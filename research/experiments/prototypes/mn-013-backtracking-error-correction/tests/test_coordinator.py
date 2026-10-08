"""Unit tests for MN-013 BacktrackingCoordinator across 4 arms."""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

REPO_ROOT = Path(__file__).resolve().parents[5]
CORE_SRC = REPO_ROOT / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from coordinator import BacktrackingCoordinator


def test_coordinator_arm4_trap_recovery_success():
    """Simulates a model that hits a trap on turn 1, receives negative directive, and routes through backup."""
    def simulated_model(prompt: str) -> str:
        if "balance_acc_treasury=400" in prompt:
            return "ACTION: RESOLVE acc_treasury:400"
        elif "REJECTED: DISPATCH:transfer:acc_vault_a" in prompt:
            # Successfully read negative directive for acc_vault_a and routed to backup vault_b!
            return "ACTION: DISPATCH transfer acc_vault_b,acc_treasury,300"
        elif "Latest Observation:\nNone" in prompt or "Latest Observation:" not in prompt:
            # Initial attempt: tries primary vault (insufficient funds trap!)
            return "ACTION: DISPATCH transfer acc_vault_a,acc_treasury,300"
        return "ACTION: RESOLVE UNKNOWN"

    env = {
        "accounts": {
            "acc_vault_a": 50,    # Trap: 50 < 300
            "acc_vault_b": 800,   # Backup
            "acc_treasury": 100,
        }
    }
    predicate = {
        "type": "account_balance_equals",
        "account": "acc_treasury",
        "expected_balance": 400,
    }

    coordinator = BacktrackingCoordinator(
        model_fn=simulated_model,
        max_turns=7,
        max_budget=512,
        arm=4,
    )

    res = coordinator.run(
        query="Transfer 300 to acc_treasury. Try acc_vault_a first, then acc_vault_b.",
        initial_env=env,
        domain="resource_ledger",
        target_predicate=predicate,
    )

    assert res.status == "RESOLVED"
    assert res.answer == "acc_treasury:400"
    assert res.rollback_count == 1
    assert res.all_under_budget is True


def test_coordinator_arm3_deadlock_detection():
    """Simulates Arm 3: context is rewound with NO negative mask; greedy model loops same action."""
    def simulated_greedy_model(prompt: str) -> str:
        # Without negative mask, prompt at retry is identical -> model emits exact same action!
        return "ACTION: DISPATCH transfer acc_vault_a,acc_treasury,300"

    env = {
        "accounts": {
            "acc_vault_a": 50,
            "acc_treasury": 100,
        }
    }

    coordinator = BacktrackingCoordinator(
        model_fn=simulated_greedy_model,
        max_turns=7,
        max_budget=512,
        arm=3,
    )

    res = coordinator.run(
        query="Transfer 300 to acc_treasury.",
        initial_env=env,
        domain="resource_ledger",
    )

    assert res.status == "DEADLOCK_CYCLE_DETECTED"
    assert res.answer == ""
