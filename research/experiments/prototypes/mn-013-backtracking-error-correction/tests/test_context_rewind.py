"""Unit tests for MN-013 ContextRewindManager."""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

REPO_ROOT = Path(__file__).resolve().parents[5]
CORE_SRC = REPO_ROOT / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from context_rewind import ContextRewindManager
from mong_nhiem.context import ContextPacker
from protocol import format_negative_directive


def test_context_rewind_arm4_negative_directive():
    mgr = ContextRewindManager(max_budget=512)
    neg = format_negative_directive("DISPATCH:transfer:acc_a,acc_b,100", "INSUFFICIENT_FUNDS")
    mgr.rewind_arm4(neg)

    prompt = mgr.build_turn_prompt(
        system_prompt="SYS",
        task_query="Transfer funds",
        state_summary="acc_a=50, acc_b=200",
        latest_observation="Rollback committed",
        arm=4,
    )

    assert "Constraint:\nREJECTED: DISPATCH:transfer:acc_a,acc_b,100" in prompt
    assert "Directive: ACTION:" in prompt


def test_context_rewind_budget_enforcement():
    mgr = ContextRewindManager(max_budget=512)
    prompt = mgr.build_turn_prompt(
        system_prompt="SYS " * 30,
        task_query="Transfer " * 10,
        state_summary="state " * 30,
        latest_observation="obs " * 30,
        arm=4,
    )
    packer = ContextPacker(max_budget=512)
    assert packer.count_tokens(prompt) <= 512
