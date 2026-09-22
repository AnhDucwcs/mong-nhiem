# MN-008 Gate B — External State Management measurement contract

## Status

**Frozen Gate B measurement contract.**
This document defines the 24-case corpus, the Latin Square counterbalancing design, the case-interleaved execution schedule, the token sizing policy, and the exact support decision rules for MN-008.

- Gate A: complete and frozen.
- Gate B: complete and frozen.
- Gate C runner implementation and model inference: not authorized without static preflight.

## Workload and sample design

1. **Model subject:** `Llama-3.2-3B-Instruct-Q4_K_M` running on `llama.cpp` local runtime.
2. **Corpus size:** Exactly $N = 24$ cases.
3. **Ordinal convention:**
   - Internal case ordinals are 0-indexed: `case_ordinal` $\in \{0, 1, \dots, 23\}$.
   - Public identifiers are 1-indexed: `mn008-case-0001` through `mn008-case-0024`.
   - Structural mapping: `case_ordinal = case_number - 1`.
4. **Difficulty dimensions (inherited from MN-007):**
   - Active entities: $E = 5$.
   - Updates per entity: $U = 3$.
   - Queried entities: exactly 2 distinct entities $(E_1, E_2)$ per case.
   - Total events per stream: $N_{\text{events}} = 15$.
5. **State representation:** Neutral vocabulary `STATE_VOCABULARY = ("S0", "S1")`.

## Latin Square counterbalancing protocol

To eliminate positional, semantic, and label-frequency priors:
1. **State-pair strata:** The four binary state combinations `(("S0", "S0"), ("S0", "S1"), ("S1", "S0"), ("S1", "S1"))` appear in exactly 6 cases each.
2. **Cyclical label permutation:** Actions are assigned via Latin Square of order 4 using the 0-indexed `case_ordinal`:
   ```python
   STATE_PAIRS = (("S0", "S0"), ("S0", "S1"), ("S1", "S0"), ("S1", "S1"))
   ACTION_VOCABULARY = ("ACTION_0", "ACTION_1", "ACTION_2", "ACTION_3")

   def get_counterbalanced_mapping(case_ordinal: int) -> dict[tuple[str, str], str]:
       shift = case_ordinal % 4  # 0, 1, 2, 3
       shifted_actions = ACTION_VOCABULARY[shift:] + ACTION_VOCABULARY[:shift]
       return dict(zip(STATE_PAIRS, shifted_actions, strict=True))
   ```
3. **Target label balance:** Each action token (`ACTION_0` .. `ACTION_3`) is the oracle target in exactly 6 cases.
4. **Chance baseline:** Strictly $25.0\%$ ($6/24$).
5. **Prompt rule ordering:** Always rendered in the fixed canonical order of `STATE_PAIRS` to eliminate appearance-order cues.

## Experimental arms and execution schedule

```text
For case_ordinal in 0..23:
[Arm A: Monolithic Single-Pass]
Prompt: Raw Events (15 lines) + Canonical Rule Table + Task Query -> LLM (1 call)

[Arm B: Active Two-Call Control]
Stage 1: Raw Events -> LLM -> Fixed-Grammar Neutral Artifact (<= 64 tokens)
Stage 2: Neutral Artifact + Canonical Rule Table + Task Query -> LLM (1 call)

[Arm C: External State Management Treatment]
Stage 1: Raw Events -> Host Engine -> Scoped Snapshot (E1=S0; E2=S1)
Stage 2: Scoped Snapshot + Canonical Rule Table + Task Query -> LLM (1 call)
```

- **Host Engine Complexity:**
  - Raw event replay: $O(N_{\text{events}})$ time, $O(E)$ memory RAM.
  - Scoped state lookup: $O(1)$ amortized memory retrieval per queried entity.
  - Context reduction: Converts $O(N_{\text{events}} \times L_{\text{event}})$ raw history into an $O(1)$ 2-entity snapshot for LLM attention.
- **Arm B Stage 1 Frozen Neutral Grammar:**
  ```text
  root ::= line "\n" line "\n" line "\n" line
  line ::= "pad=" token (" " token)*
  token ::= "KAPPA" | "LAMBDA" | "MU" | "NU" | "XI" | "OMICRON" | "PI" | "RHO"
  ```
- **Case-interleaved execution schedule:** To prevent thermal throttling, cache drift, and background load confounds, execution strictly follows:
  $$(A_i \rightarrow B_{1,i} \rightarrow B_{2,i} \rightarrow C_{2,i}) \quad \forall i \in \{0..23\}$$
- **Stateless invocation invariant:** `temperature = 0.0`, `seed = 42`, `prompt_cache = false`, zero KV-cache persistence across requests.

## Token sizing and prompt budget policy

1. **Arm C Prompt Size (< 100 tokens) — Hard Preflight Gate:**
   - Every Arm C Stage 2 prompt (including system scaffolding, scoped snapshot, rule table, and query) must measure **strictly $< 100$ tokens** under the frozen Llama 3.2 tokenizer.
   - Any single case measuring $\ge 100$ tokens in static preflight immediately fails the preflight check and aborts the attempt.
2. **Unfrozen Completion Budgets (Deterministic Sizing Formula):**
   - Exact completion caps remain unfrozen until tokenizer and runtime authorities are verified.
   - When verified, Stage 1 caps must follow the immutable sizing formula:
     ```python
     def compute_stage_a_cap(measured_artifact_tokens: int) -> int:
         headroom = measured_artifact_tokens + 8
         return ((headroom + 15) // 16) * 16
     ```
   - Final action completion allowance (Arm A, Arm B Stage 2, Arm C Stage 2): fixed at `max_tokens = 16`.

## Support and decision rules

A complete, protocol-valid execution is classified according to these criteria:

1. **Compatibility Baseline Criterion:**
   - **$A \le 6/24$ ($25.0\%$):** Confirms continuity with the MN-007 floor baseline. This is a non-dominance compatibility check, not an independent test of model competence.
2. **Primary Efficacy Gate:**
   - **$C \ge 18/24$ ($75.0\%$):** Establishes statistically significant reliability against the chance baseline:
     $$P(X \ge 18 \mid n=24, p=0.25) = \sum_{k=18}^{24} \binom{24}{k} (0.25)^k (0.75)^{24-k} \approx 3.89 \times 10^{-7}$$
     (Exact tail sum: $3.885491644 \times 10^{-7}$).
3. **Causal Utility over Multi-Call Gate:**
   - **$C - B \ge 10/24$:** Confirms that the performance advantage is causally attributable to host-managed state rather than procedural two-call decomposition.
4. **Strict Engineering Non-Regression Policy:**
   - **$n_{B=1, C=0} = 0$:** Where $n_{B=1, C=0}$ is defined as the exact count of paired cases where Arm B passes and Arm C fails:
     $$n_{B=1, C=0} = \left|\{ i \in \{0..23\} \mid \text{Arm B}_i = \text{PASS} \land \text{Arm C}_i = \text{FAIL} \}\right|$$
   - This is declared as an intentional, strict engineering design policy reflecting zero tolerance for regression under external state management, not a relaxed statistical hypothesis.
5. **Note on $C - A$:** Omitted as a separate gate because $C \ge 18$ and $A \le 6$ mathematically implies $C - A \ge 12 \ge 10$.

## Execution and provenance invariants

1. **Persist-before-validate:** Every HTTP response body, raw bytes, request payload, token counts, timestamps, and latency must be persisted to disk (`runs/<run_id>/raw_responses.jsonl`) *before* executing schema validation or error handling.
2. **Hash Chaining:** The materialized corpus (`semantic-cases.jsonl`, `public-prompts.jsonl`, `evaluator-records.jsonl`) must be fingerprinted into `manifest.json` with physical UTF-8/LF SHA-256 hashes.
3. **Exact deterministic evaluation:**
   - Regex: `\b(ACTION_[0-3])\b`.
   - Exact string match against materialized ground truth.
4. **Invalidating conditions:**
   - Grammar mismatch or state leakage in Arm B Stage 1 output.
   - Pre-evaluation of rules or decision leaking in Host Engine.
   - KV-cache or session retention across cases.
   - Discrepancy between physical artifact hashes and `manifest.json`.
