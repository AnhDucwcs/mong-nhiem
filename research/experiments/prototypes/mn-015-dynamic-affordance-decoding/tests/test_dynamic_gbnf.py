"""Unit tests for Dynamic GBNF Compiler in MN-015."""
import sys
import time
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from dynamic_gbnf import STATIC_FALLBACK_GBNF, compile_dynamic_gbnf
from protocol import Affordances


def test_compile_empty_fallback():
    aff = Affordances()
    grammar = compile_dynamic_gbnf(aff)
    assert grammar == STATIC_FALLBACK_GBNF


def test_compile_single_branch_resolve():
    aff = Affordances(resolves=["svc_worker_b_51:CONSERVATIVE_PIPELINE"])
    grammar = compile_dynamic_gbnf(aff)
    assert 'root ::= action ("\\n" | "")' in grammar
    assert 'action ::= "ACTION: " resolve-action' in grammar
    assert 'resolve-action ::= "RESOLVE " valid-resolve-target' in grammar
    assert 'valid-resolve-target ::= "svc_worker_b_51:CONSERVATIVE_PIPELINE"' in grammar
    # Must NOT contain read, inspect, or dispatch branches!
    assert "read-action" not in grammar
    assert "dispatch-action" not in grammar


def test_compile_multi_branch_dispatch_and_inspect():
    aff = Affordances(
        inspects=["svc_worker_b_51.status"],
        dispatches=[("activate_service", "svc_worker_b_51,CONSERVATIVE_PIPELINE")],
    )
    grammar = compile_dynamic_gbnf(aff)
    assert 'action ::= "ACTION: " ( inspect-action | dispatch-action )' in grammar
    assert 'inspect-action ::= "INSPECT " valid-inspect-target' in grammar
    assert 'valid-inspect-target ::= "svc_worker_b_51.status"' in grammar
    assert 'dispatch-action ::= "DISPATCH " valid-dispatch-call' in grammar
    assert '"activate_service svc_worker_b_51,CONSERVATIVE_PIPELINE"' in grammar


def test_compilation_latency_sub_millisecond():
    aff = Affordances(
        reads=["func_a", "func_b"],
        inspects=["svc_1.status", "svc_2.status"],
        dispatches=[("transfer", "acc_1,acc_2,100"), ("transfer", "acc_3,acc_2,100")],
        resolves=["acc_2:100"],
    )
    t0 = time.perf_counter()
    for _ in range(100):
        _ = compile_dynamic_gbnf(aff)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0 / 100.0
    assert elapsed_ms < 0.1, f"Expected < 0.1 ms, got {elapsed_ms:.4f} ms"
