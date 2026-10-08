"""Unit tests for MN-013 PhaseGateInterceptor."""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from phase_gate import PhaseGateInterceptor
from protocol import parse_action


def test_phase_gate_blocks_premature_resolve():
    action = parse_action("ACTION: RESOLVE acc_beta:500")
    env = {"accounts": {"acc_beta": 200}}  # Has not reached 500 yet!
    predicate = {"type": "account_balance_equals", "account": "acc_beta", "expected_balance": 500}

    valid, reason = PhaseGateInterceptor.validate_resolution(action, env, predicate)
    assert valid is False
    assert "PREMATURE_RESOLVE" in reason


def test_phase_gate_permits_valid_resolve():
    action = parse_action("ACTION: RESOLVE acc_beta:500")
    env = {"accounts": {"acc_beta": 500}}  # Target balance reached
    predicate = {"type": "account_balance_equals", "account": "acc_beta", "expected_balance": 500}

    valid, reason = PhaseGateInterceptor.validate_resolution(action, env, predicate)
    assert valid is True
    assert reason == "PREDICATE_SATISFIED"
