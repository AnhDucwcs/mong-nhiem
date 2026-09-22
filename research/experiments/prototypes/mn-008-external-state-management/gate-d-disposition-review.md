# MN-008 Gate D — Disposition and Promotion Review

## Final Status

**Completed and closed — Unpromoted / Hypothesis UNSUPPORTED.**

```text
Final Milestone Disposition: unpromoted_hypothesis_unsupported
Promotion to src/mong_nhiem/: DENIED (Zero code promoted)
Canonical Evidence: runs/mn008-execution-run-0001/
Canonical Report: reports/mn008-gate-c-run-0001-report.md
```

This disposition is bounded to the qualified model/runtime (`Llama-3.2-3B-Instruct-Q4_K_M` on `llama.cpp`) and the frozen MN-008 Gate B workload and measurement contract.

---

## 1. Empirical Evidence Summary

The canonical Gate C execution (`mn008-execution-run-0001`, executed at commit `2ad5916`) completed all 96 model calls across 24 counterbalanced cases in strict case-interleaved order $(A_i \rightarrow B_{1,i} \rightarrow B_{2,i} \rightarrow C_{2,i})$ with 100% protocol validity and persist-before-validate enforcement:

| Arm | Description | Score | Accuracy | Frozen Threshold | Gate Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Arm A** | Monolithic Single-Pass (Raw Context) | 0/24 | 0.0% | $A \le 6/24$ ($25.0\%$) | **PASS** (Floor Compatibility) |
| **Arm B** | Active Two-Call Control (Neutral Grammar) | 2/24 | 8.3% | — | Control Reference |
| **Arm C** | External State Management (Host Snapshot) | 2/24 | 8.3% | $C \ge 18/24$ ($75.0\%$) | **FAIL** (Primary Efficacy Gate) |
| **Delta** | $C - B$ Causal Utility | +0 | +0.0% | $C - B \ge 10/24$ ($+41.7\%$) | **FAIL** (Utility Gate) |
| **Policy** | Strict Non-Regression ($n_{B=1, C=0}$) | 2 | — | $n_{B=1, C=0} == 0$ | **FAIL** (Policy Violation) |

- Exact one-sided binomial upper tail: $P(X \ge 2 \mid n=24, p=0.25) \approx 0.9910$.
- Diagnostic Probing: Offline probe tests evaluating rigid BNF grammar adapters (`root ::= "ACTION_" [0-3]`) and step-by-step instruction framing confirmed that the model remains at or below chance floor ($16.7\%$ and $0.0\%$, respectively), exhibiting mode collapse rather than conditional reasoning.

---

## 2. Gate D Promotion Assessment

In accordance with Mộng Nhiễm governance:
- *"Do not silently promote experimental code into `src/mong_nhiem/`."*
- *"Promote code into the reusable package only after evidence and an explicit decision."*

Because the frozen Gate B primary efficacy gate ($C \ge 18/24$), causal utility gate ($C - B \ge 10/24$), and strict non-regression policy ($n_{B=1, C=0} = 0$) all failed, **promotion into `src/mong_nhiem/` is formally DENIED**.

All experimental artifacts, corpus manifests, scripts (`mn008_materialization.py`, `mn008_executor.py`, `mn008_evaluator.py`), and runs remain strictly confined to `research/experiments/prototypes/mn-008-external-state-management/` as immutable historical research evidence.

---

## 3. Scientific and Architectural Conclusions

1. **The Dual-Bottleneck Reality:**
   Decoupling deterministic state tracking to an external host engine ($O(1)$ memory lookup) completely resolved the input context load bottleneck, collapsing 15 chronological transition events into a minimal 2-entity snapshot ($87$ tokens). However, supplying external state snapshots alone does not enable downstream conditional decision reasoning ($E1 \land E2 \rightarrow \text{ACTION}$) in small language models (<4B) over abstract neutral variables.
2. **Response-Channel vs. Inherent Capacity:**
   Under unconstrained greedy decoding, small instruct models default to conversational preamble ("It appears that the decision rules are..."), exhausting small completion budgets (`max_tokens = 16`). However, enforcing a hard BNF grammar adapter revealed an underlying capacity ceiling: the model collapsed into template-recitation bias (`ACTION_0` mode collapse), scoring $\le 16.7\%$ (below the $25.0\%$ random chance baseline).
3. **The Tautology & Engineering Boundary:**
   To build reliable decision systems with small language models:
   - If a business problem requires strict conjunctive boolean rules over discrete state tables, **both state tracking AND rule evaluation must reside in deterministic host code** ($O(1)$ symbolic engine).
   - Offloading only state tracking while expecting a small LLM to evaluate abstract truth tables zero-shot yields floor reliability.

---

## 4. Frozen Milestone Closure

MN-008 is formally **completed and closed**.

No further model execution is authorized under MN-008, including:
- Iterative prompt engineering or rewrites;
- Lowering the frozen support thresholds ($C \ge 18$, $C - B \ge 10$);
- Retrying execution with altered sampling or grammar parameters;
- Promoting prototype code into `src/mong_nhiem/`.

All raw responses, manifests, and reports are permanently archived. Future work investigating hybrid deterministic/LLM architectures or larger model classes must be chartered under a new prospective milestone.
