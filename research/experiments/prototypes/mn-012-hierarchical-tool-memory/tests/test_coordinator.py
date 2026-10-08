"""Unit tests for MN-012 HierarchicalToolCoordinator and CircuitBreaker."""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

REPO_ROOT = Path(__file__).resolve().parents[5]
CORE_SRC = REPO_ROOT / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from coordinator import HierarchicalToolCoordinator


def test_circuit_breaker_cycle_detection():
    cb = CircuitBreaker(max_turns=5)
    assert cb.record_action("INSPECT:acc_a.balance") == CircuitBreakerStatus.ACTIVE
    # Repeat same action
    assert cb.record_action("INSPECT:acc_a.balance") == CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED


def test_circuit_breaker_consecutive_rejections():
    cb = CircuitBreaker(max_turns=5, max_consecutive_rejections=2)
    assert cb.record_action("DISPATCH:transfer:bad_args", is_rejected=True) == CircuitBreakerStatus.ACTIVE
    assert cb.record_action("DISPATCH:transfer:bad_args2", is_rejected=True) == CircuitBreakerStatus.TRIPPED_REJECTION_LIMIT


def test_circuit_breaker_max_turns():
    cb = CircuitBreaker(max_turns=3)
    assert cb.record_action("READ:f1") == CircuitBreakerStatus.ACTIVE
    assert cb.record_action("READ:f2") == CircuitBreakerStatus.ACTIVE
    assert cb.record_action("READ:f3") == CircuitBreakerStatus.TRIPPED_MAX_TURNS


def test_coordinator_end_to_end_simulation():
    # Simulated model function that executes a 3-turn transfer workflow
    def simulated_model(prompt: str) -> str:
        if "Latest Observation:\nNone" in prompt or "Latest Observation:" not in prompt:
            return "ACTION: INSPECT acc_alpha.balance"
        elif "Latest Observation:\n1000" in prompt:
            return "ACTION: DISPATCH transfer acc_alpha,acc_beta,300"
        elif "TRANSFER_COMMITTED" in prompt:
            return "ACTION: RESOLVE acc_beta:800"
        return "ACTION: RESOLVE UNKNOWN"

    env = {"accounts": {"acc_alpha": 1000, "acc_beta": 500}}
    coordinator = HierarchicalToolCoordinator(model_fn=simulated_model, max_turns=5, max_budget=512)

    res = coordinator.run(
        query="Transfer 300 from acc_alpha to acc_beta and resolve final balance of acc_beta.",
        initial_env=env,
    )

    assert res.status == "RESOLVED"
    assert res.answer == "acc_beta:800"
    assert res.total_turns == 3
    assert res.all_under_budget is True
    assert res.l2_state_snapshot["accounts"]["acc_alpha"] == 700
    assert res.l2_state_snapshot["accounts"]["acc_beta"] == 800
