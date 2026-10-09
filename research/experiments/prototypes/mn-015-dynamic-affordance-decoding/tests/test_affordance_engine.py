"""Unit tests for AffordanceEngine in MN-015."""
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from affordance_engine import AffordanceEngine


def test_domain_c_mutual_exclusion_filtering():
    engine = AffordanceEngine()
    env = {
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

    # Turn 1: No rejections yet -> both svc_worker_a_51 and svc_worker_b_51 are candidates
    aff_turn1 = engine.get_active_affordances(
        domain="system_registry",
        env=env,
        query=query,
        rejected_actions=set(),
        target_predicate=target_pred,
        turn_index=1,
    )
    assert not aff_turn1.is_empty()
    assert any("svc_worker_a_51" in disp[1] for disp in aff_turn1.dispatches)
    assert any("svc_worker_b_51" in disp[1] for disp in aff_turn1.dispatches)
    # RESOLVE must NOT be active because goal is not yet met
    assert len(aff_turn1.resolves) == 0

    # Turn 2: svc_worker_a_51 was rejected in rollback
    rejected = {"DISPATCH:activate_service:svc_worker_a_51,AGGRESSIVE_PARALLEL"}
    aff_turn2 = engine.get_active_affordances(
        domain="system_registry",
        env=env,
        query=query,
        rejected_actions=rejected,
        target_predicate=target_pred,
        turn_index=2,
    )
    # svc_worker_a_51 must be completely filtered out!
    assert not any("svc_worker_a_51" in disp[1] for disp in aff_turn2.dispatches)
    # Only svc_worker_b_51 must remain
    assert any("svc_worker_b_51" in disp[1] for disp in aff_turn2.dispatches)
    assert len(aff_turn2.resolves) == 0

    # Turn 3: State mutated, goal predicate is now met
    env["services"]["svc_worker_b_51"]["mode"] = "CONSERVATIVE_PIPELINE"
    aff_turn3 = engine.get_active_affordances(
        domain="system_registry",
        env=env,
        query=query,
        rejected_actions=rejected,
        target_predicate=target_pred,
        turn_index=3,
    )
    # Goal met -> RESOLVE is now active!
    assert len(aff_turn3.resolves) == 1
    assert aff_turn3.resolves[0] == "svc_worker_b_51:CONSERVATIVE_PIPELINE"


def test_domain_b_resource_ledger_filtering():
    engine = AffordanceEngine()
    env = {
        "accounts": {"acc_vault_a": 50, "acc_vault_b": 500, "acc_target": 0}
    }
    query = "Transfer 100 to acc_target. Try acc_vault_a first, else backup acc_vault_b, then resolve final balance."
    target_pred = {
        "type": "account_balance_equals",
        "account": "acc_target",
        "expected_balance": "100",
    }

    # Turn 1: Try acc_vault_a
    aff_turn1 = engine.get_active_affordances(
        domain="resource_ledger",
        env=env,
        query=query,
        rejected_actions=set(),
        target_predicate=target_pred,
        turn_index=1,
    )
    assert any("acc_vault_a" in disp[1] for disp in aff_turn1.dispatches)
    assert len(aff_turn1.resolves) == 0

    # Turn 2: acc_vault_a was rejected due to insufficient funds
    rejected = {"DISPATCH:transfer:acc_vault_a,acc_target,100"}
    aff_turn2 = engine.get_active_affordances(
        domain="resource_ledger",
        env=env,
        query=query,
        rejected_actions=rejected,
        target_predicate=target_pred,
        turn_index=2,
    )
    # acc_vault_a must be excluded
    assert not any("acc_vault_a" in disp[1] for disp in aff_turn2.dispatches)
    # acc_vault_b must remain
    assert any("acc_vault_b" in disp[1] for disp in aff_turn2.dispatches)


def test_domain_a_code_mutation_filtering():
    engine = AffordanceEngine()
    env = {
        "functions": {
            "calculate_tax_1": "def calculate_tax_1(): return 10\n",
            "sanitize_input_1": "def sanitize_input_1(): return 100\n",
        },
        "locked_entities": ["calculate_tax_1"],
    }
    query = "Inspect function calculate_tax_1, dispatch refactor calculate_tax_1:rate=22, and resolve final rate."
    target_pred = {
        "type": "function_rate_updated",
        "target_func": "calculate_tax_1",
        "expected_value": "22",
    }

    aff = engine.get_active_affordances(
        domain="code_mutation",
        env=env,
        query=query,
        rejected_actions=set(),
        target_predicate=target_pred,
        turn_index=1,
    )
    assert "calculate_tax_1" in aff.reads
    assert any("calculate_tax_1" in disp[0] for disp in aff.dispatches)
