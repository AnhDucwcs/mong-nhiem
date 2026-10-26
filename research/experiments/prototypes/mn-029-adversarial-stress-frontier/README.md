# Milestone MN-029: Adversarial Cognitive Frontier & Stress-Test Suite

## Executive Overview

Milestone MN-029 subjects the Mộng Nhiễm cognitive kernel (`v0.2.0`) to a rigorous adversarial stress-test battery across nine critical boundary scenarios identified by adversarial peer review. While milestones MN-001 through MN-028 verified nominal contracts and 1-step invariants in synchronized synthetic microworlds, MN-029 targets untested failure frontiers: asynchronous state mutations during inference latency, bimodal action-communication divergence, multi-step lookahead traps, byzantine telemetry equifinality, cyclic multi-agent livelocks, memory leaks across the C-ABI FFI boundary, and three-way transactional crash desynchronization.

The methodology strictly enforces **Test-Driven Falsification (TDD)**:
1. **Falsification Baseline (Red):** Implement automated test harnesses exposing baseline vulnerabilities before introducing any defensive architectural code.
2. **Surgical Remediation (Green):** Implement Host-authoritative mathematical constraints, commit-time invariants, bounded GBNF grammars, and C-ABI panic-safe transactional barriers.
3. **Multi-Model Empirical Qualification:** Verify resolution across qualified models (`Qwen3.5-2B-Q4_K_M`, `Llama-3.2-3B-Instruct-Q4_K_M`, `Qwen3-4B-Q4_K_M`).

## Directory Layout

- `charter.md`: Formal Gate A research questions, causal hypotheses, and falsification criteria.
- `gate-b-contract.md`: Frozen quantitative acceptance criteria ($M_1 \to M_9$).
- `definition/`: Declarative scenario definitions and adversarial telemetry sequences.
- `reports/`: Empirical academic evaluation reports generated from benchmark runs.
- `runs/`: Authenticated episode traces sealed in `audit_logs.zip` archives with zero loose JSON files.

## Reproduction Steps

```powershell
# 1. Run Batch 1 stress tests (Real-Time Safety & C-ABI)
python -m pytest tests/stress/test_batch1_safety_and_ffi.py -v

# 2. Run with live SLM backend (optional)
python -m pytest tests/stress/test_batch1_safety_and_ffi.py -v --live-slm
```
