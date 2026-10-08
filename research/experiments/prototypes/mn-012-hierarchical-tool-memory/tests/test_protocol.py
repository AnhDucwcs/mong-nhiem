"""Unit tests for MN-012 Action Protocol Grammar parser and formatter."""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from protocol import ActionType, ToolAction, format_action, parse_action


def test_parse_read_action():
    text = "ACTION: READ calculate_tax_1"
    action = parse_action(text)
    assert action.action_type == ActionType.READ
    assert action.target == "calculate_tax_1"
    assert action.payload == ""


def test_parse_inspect_action():
    text = "ACTION: INSPECT acc_alpha_1.balance"
    action = parse_action(text)
    assert action.action_type == ActionType.INSPECT
    assert action.target == "acc_alpha_1.balance"
    assert action.payload == ""


def test_parse_dispatch_action():
    text = "ACTION: DISPATCH transfer acc_a,acc_b,100"
    action = parse_action(text)
    assert action.action_type == ActionType.DISPATCH
    assert action.target == "transfer"
    assert action.payload == "acc_a,acc_b,100"


def test_parse_resolve_action():
    text = "ACTION: RESOLVE acc_beta_1:800"
    action = parse_action(text)
    assert action.action_type == ActionType.RESOLVE
    assert action.target == ""
    assert action.payload == "acc_beta_1:800"


def test_parse_with_think_tags_and_preamble():
    raw = (
        "<think>Let me first inspect the account balance.</think>\n"
        "I will now inspect the account:\n"
        "ACTION: INSPECT acc_vault.balance"
    )
    action = parse_action(raw)
    assert action.action_type == ActionType.INSPECT
    assert action.target == "acc_vault.balance"


def test_parse_quoted_and_whitespace_args():
    text = "ACTION: DISPATCH refactor \"target_func:multiplier=2\""
    action = parse_action(text)
    assert action.action_type == ActionType.DISPATCH
    assert action.target == "refactor"
    assert action.payload == "target_func:multiplier=2"


def test_parse_invalid_text():
    action = parse_action("Just chatting with no action directive")
    assert action.action_type == ActionType.INVALID
    assert action.target == ""


def test_format_action_canonical():
    assert format_action(ActionType.READ, "my_func") == "ACTION: READ my_func"
    assert format_action(ActionType.INSPECT, "my_acc.balance") == "ACTION: INSPECT my_acc.balance"
    assert format_action(ActionType.DISPATCH, "transfer", "a,b,10") == "ACTION: DISPATCH transfer a,b,10"
    assert format_action(ActionType.RESOLVE, "", "42") == "ACTION: RESOLVE 42"
