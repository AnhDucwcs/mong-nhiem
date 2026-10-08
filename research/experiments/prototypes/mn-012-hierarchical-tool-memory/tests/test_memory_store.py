"""Unit tests for MN-012 Dual-Tier Memory Store and Invariant Checker."""
import json
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from memory_store import HostStateStore


def test_read_function():
    env = {
        "functions": {
            "calc_fee": "def calc_fee(x):\n    return x * 2\n",
        }
    }
    store = HostStateStore(env)
    assert "def calc_fee" in store.read("calc_fee")
    assert "ENTITY_NOT_FOUND" in store.read("non_existent")


def test_inspect_account_and_registry():
    env = {
        "accounts": {"acc_a": 1000},
        "registry": {"db.mode": "active"},
    }
    store = HostStateStore(env)
    assert store.inspect("acc_a.balance") == "1000"
    assert store.inspect("db.mode") == "active"
    assert "PROPERTY_NOT_FOUND" in store.inspect("unknown.key")


def test_dispatch_resource_transfer_valid_and_conservation():
    env = {
        "accounts": {"acc_a": 1000, "acc_b": 500},
    }
    store = HostStateStore(env)
    res = store.dispatch("transfer", "acc_a,acc_b,300")
    assert "TRANSFER_COMMITTED" in res
    assert store.env["accounts"]["acc_a"] == 700
    assert store.env["accounts"]["acc_b"] == 800


def test_dispatch_resource_overdraft_rejection():
    env = {
        "accounts": {"acc_a": 200, "acc_b": 500},
    }
    store = HostStateStore(env)
    res = store.dispatch("transfer", "acc_a,acc_b,300")
    assert "ACTION_REJECTED OverdraftForbidden" in res
    # State remains unchanged
    assert store.env["accounts"]["acc_a"] == 200
    assert store.env["accounts"]["acc_b"] == 500


def test_dispatch_code_ast_mutation_and_syntax_rejection():
    env = {
        "functions": {"calc_rate": "def calc_rate():\n    return 10\n"},
    }
    store = HostStateStore(env)
    # Valid mutation
    res = store.dispatch("refactor", "calc_rate:multiplier=2")
    assert "MUTATION_SUCCESS" in res

    # Syntax error injection
    res_err = store.dispatch("refactor", "calc_rate:def 123 invalid!!!")
    assert "ACTION_REJECTED InvalidSyntax" in res_err


def test_dispatch_system_registry_prerequisite_rejection():
    env = {
        "registry": {"kms.key_loaded": "false", "svc.deployment": "BLOCKED"},
        "invariants": ["kms_key_must_be_loaded"],
    }
    store = HostStateStore(env)
    # Attempting to activate service before KMS key is loaded
    res_err = store.dispatch("set_flag", "svc.deployment=READY")
    assert "ACTION_REJECTED PrerequisiteUnmet" in res_err

    # Load KMS key first
    res_ok = store.dispatch("set_flag", "kms.key_loaded=true")
    assert "FLAG_UPDATED" in res_ok

    # Now activate service
    res_deploy = store.dispatch("set_flag", "svc.deployment=READY")
    assert "FLAG_UPDATED" in res_deploy


def test_audit_log_append(tmp_path):
    log_file = tmp_path / "audit.jsonl"
    env = {"accounts": {"a": 100, "b": 50}}
    store = HostStateStore(env, audit_log_path=log_file)
    store.dispatch("transfer", "a,b,20")
    assert log_file.exists()
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["action_type"] == "transfer"
    assert record["status"] == "COMMITTED"
