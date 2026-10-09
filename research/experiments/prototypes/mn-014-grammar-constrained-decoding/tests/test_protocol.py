"""Unit tests for deterministic protocol parsing in MN-014."""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from protocol import ActionType, parse_action, format_action, format_negative_directive


def test_parse_read_action():
    action = parse_action("ACTION: READ calculate_tax_1")
    assert action.action_type == ActionType.READ
    assert action.target == "calculate_tax_1"
    assert action.payload == ""


def test_parse_inspect_action():
    action = parse_action("ACTION: INSPECT account_a.balance")
    assert action.action_type == ActionType.INSPECT
    assert action.target == "account_a.balance"


def test_parse_dispatch_action_with_spaces():
    action = parse_action("ACTION: DISPATCH refactor_calculate_tax_1 rate=22")
    assert action.action_type == ActionType.DISPATCH
    assert action.target == "refactor_calculate_tax_1"
    assert action.payload == "rate=22"


def test_parse_resolve_action():
    action = parse_action("ACTION: RESOLVE 42")
    assert action.action_type == ActionType.RESOLVE
    assert action.payload == "42"


def test_parse_invalid_action():
    action = parse_action("Here is my analysis: calculate_tax_1")
    assert action.action_type == ActionType.INVALID


def test_format_negative_directive():
    dir_str = format_negative_directive("DISPATCH:tool:arg", "LOCKED_RESOURCE")
    assert "REJECTED: DISPATCH:tool:arg (LOCKED_RESOURCE)" in dir_str
    assert "Do NOT repeat this action" in dir_str
