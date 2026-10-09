"""Integration tests for GrammarBacktrackingCoordinator in MN-014."""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from coordinator import GrammarBacktrackingCoordinator


def test_coordinator_trap_recovery_arm2():
    """Simulates Arm 2 (GBNF constrained) hitting a trap and recovering via alternative branch."""
    # Environment: acc_vault_a has 50 (fails transfer 300), acc_vault_b has 500 (succeeds)
    env = {
        "accounts": {
            "acc_vault_a": 50,
            "acc_vault_b": 500,
            "acc_treasury": 100,
        }
    }
    target_predicate = {
        "type": "account_balance_equals",
        "account": "acc_treasury",
        "expected_balance": 400,
    }

    step = [0]

    def mock_model(prompt: str, use_grammar: bool):
        assert use_grammar is True
        step[0] += 1
        if "REJECTED: DISPATCH:transfer:acc_vault_a,acc_treasury,300" in prompt:
            # Model observes negative constraint and picks alternative vault_b
            if "TRANSFER_COMMITTED" in prompt:
                return "ACTION: RESOLVE acc_treasury:400", 10.0
            return "ACTION: DISPATCH transfer acc_vault_b,acc_treasury,300", 10.0

        if step[0] == 1:
            return "ACTION: DISPATCH transfer acc_vault_a,acc_treasury,300", 10.0
        return "ACTION: RESOLVE acc_treasury:400", 10.0

    coord = GrammarBacktrackingCoordinator(
        model_fn=mock_model,
        token_counter_fn=lambda p: len(p.split()),
        max_turns=5,
        max_budget=512,
        arm=2,
    )

    res = coord.run(
        query="Transfer 300 to treasury and resolve.",
        initial_env=env,
        domain="resource_ledger",
        target_predicate=target_predicate,
    )

    assert res.status == "RESOLVED"
    assert res.answer == "acc_treasury:400"
    assert res.rollback_count == 1
    assert res.final_environment["accounts"]["acc_treasury"] == 400
    assert res.final_environment["accounts"]["acc_vault_b"] == 200
    assert res.final_environment["accounts"]["acc_vault_a"] == 50  # Restored bit-for-bit
