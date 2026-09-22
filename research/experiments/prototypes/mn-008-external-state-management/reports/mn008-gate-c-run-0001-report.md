# MN-008 Gate C — Run 0001 Execution Report

## Status

**Protocol-valid completed run — Hypothesis UNSUPPORTED.**

- Run ID: `mn008-execution-run-0001`
- Execution timestamp: `2026-09-22T10:45:51Z` to `2026-09-22T10:47:41Z` (Duration: 110.1s)
- Git commit: `2ad5916663738289a8078ee337d57227c376acae`
- Model subject: `Llama-3.2-3B-Instruct-Q4_K_M` on local `llama.cpp` (build 10566, commit `bb4caa754`)
- Execution order: Strict case-interleaved $(A_i \rightarrow B_{1,i} \rightarrow B_{2,i} \rightarrow C_{2,i})$ for $i \in \{0..23\}$ (96 calls total)
- Evidence contract: Persist-before-validate enforced (`runs/mn008-execution-run-0001/raw_responses.jsonl`)

## Quantitative Results Summary

| Arm | Description | Total Cases | Exact Passes | Accuracy | Gate B Support Threshold | Criterion Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Arm A** | Monolithic Single-Pass (Raw Context) | 24 | 0 | **0.0%** ($0/24$) | $A \le 6/24$ ($25.0\%$) | **PASS** (Compatibility Floor) |
| **Arm B** | Active Two-Call Control (Neutral Grammar) | 24 | 2 | **8.3%** ($2/24$) | — | Control Reference |
| **Arm C** | External State Management (Host Snapshot) | 24 | 2 | **8.3%** ($2/24$) | $C \ge 18/24$ ($75.0\%$) | **FAIL** (Primary Efficacy Gate) |

### Gate B Formal Criteria Assessment

1. **Baseline Compatibility Criterion ($A \le 6/24$):**
   - Actual: $0/24$ ($0.0\%$).
   - Status: **PASS**. Confirms continuity with the MN-007 floor baseline; single-pass in-context joint state-tracking and conditional reasoning is completely at the floor.
2. **Primary Efficacy Gate ($C \ge 18/24$):**
   - Actual: $2/24$ ($8.3\%$).
   - Exact one-sided binomial p-value: $P(X \ge 2 \mid n=24, p=0.25) \approx 0.9910$.
   - Status: **FAIL**. Arm C fails the primary efficacy threshold by a wide margin ($2/24$ vs $\ge 18/24$).
3. **Causal Utility over Multi-Call Gate ($C - B \ge 10/24$):**
   - Actual: $2 - 2 = 0$ ($+0.0\%$).
   - Status: **FAIL**. Offloading state to the host engine yielded zero net improvement over the two-call neutral control.
4. **Strict Engineering Non-Regression Policy ($n_{B=1, C=0} = 0$):**
   - Actual: $n_{B=1, C=0} = 2$ (Cases `mn008-case-0001` and `mn008-case-0017` passed under Arm B but failed under Arm C).
   - Status: **FAIL**. Two paired regression violations observed.

**Canonical Verdict: `UNSUPPORTED`**

---

## Detailed Failure and Behavioral Analysis

Across all 96 model calls, the raw completions reveal a structural response-channel behavior under `Llama-3.2-3B-Instruct` when prompted without a rigid response grammar or explicit imperative verb:

1. **Preamble and Essay Generation:**
   - Instead of emitting a solitary action token (`ACTION_X`), the model defaulted to conversational commentary:
     - *"It appears that the decision rules are defining the actions to be taken based on the..."*
     - *"It appears to be a simple decision-making system using a finite state machine..."*
     - *"Based on the decision rules, the actions are: - ACTION_0: ..."*
2. **Exhaustion of Completion Budget (`max_tokens = 16`):**
   - Because `max_tokens` was fixed at 16, conversational preamble immediately exhausted the completion window before the model could output a concluding decision token.
3. **First-Line Parroting Artifact:**
   - In cases where an action token was captured within the 16-token window, the model was merely reciting the first rule from the prompt table (`- IF E1=S0 AND E2=S0 THEN ACTION_X`), rather than selecting the active branch.
   - For Arm B, the model output `ACTION_0` whenever it produced an action token, scoring $2/24$ passes purely by random alignment with cases where `ACTION_0` was the target.
   - For Arm C, the model recited line 1 of the counterbalanced rule table, scoring $2/24$ passes coincidentally when line 1 matched the target action.

---

## 3-Expert Evaluation

### 🏛️ Systems Architect
- **Mechanistic Root Cause:** Decoupling state tracking to an external host engine successfully collapsed the input context from $15$ raw event transitions to a clean $2$-entity snapshot (`E1=S0; E2=S1`, measuring only $87$ tokens). However, downstream conditional branch reasoning failed to materialize because the LLM subject did not execute the conjunction logic ($E1 \land E2 \rightarrow \text{ACTION}$).
- **Architecture Takeaway:** Small language models (<4B) exhibit a two-fold failure: they fail at latent state tracking (proven in MN-003 through MN-007), but supplying external state alone does not guarantee reliable conditional execution if the prompt interface allows unconstrained conversational generation.

### 🛡️ Security Engineer
- **Construct Validity:** The experiment maintains 100% protocol validity: zero data leakage, complete isolation of the host state engine, exact Latin Square balance, and full persistence before validation.
- **Vulnerability / Non-Regression:** The failure of the strict non-regression policy ($n_{B=1, C=0} = 2$) proves that under greedy decoding without grammar guidance, small model outputs are dominated by stochastic template-recitation rather than monotonic conditional evaluation.

### 🛠️ Pragmatist
- **Empirical Rigor:** The experiment was executed cleanly, reproducibly, and without ad-hoc parameter tampering. The negative result is definitive for this contract: External State Management under open-ended prompt formulation does not resolve conditional decision reasoning on `Llama-3.2-3B-Instruct`.
- **Recommendation:** Do not tune prompt templates post-hoc or lower thresholds to rescue the run. Record the result as canonical evidence and proceed to Gate D disposition review.
