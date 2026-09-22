# MN-008 Gate A — External State Management hypothesis selection

## Status

**Frozen Gate A design note.** This selects one causal hypothesis, three conceptual arms, the host boundary framework, and the Latin Square counterbalancing protocol. It is not a measurement contract, implementation, runner, schema, or evidence of efficacy.

- Gate A: complete and frozen for External State Management.
- Gate B: not started.
- Gate C implementation and measured evidence: not authorized.
- Gate D promotion: not authorized.

MN-008 inherits MN-003 (ECC-006), MN-004, MN-005, MN-006, and MN-007 as immutable historical evidence. It does not alter, rescore, or continue prior contracts.

## Inherited evidence and selection rationale

Accumulated evidence demonstrates a structural limitation in small language models (<4B parameters, qualified subject `Llama-3.2-3B-Instruct`):

1. **MN-003 (ECC-006):** In-context state tracking decays monotonically under context load, reaching zero accuracy (`0/6`) at 8k and 16k tokens.
2. **MN-004:** Structuring input events into a globally indexed transition ledger improved 8k accuracy from `0/24` to `7/24`, but failed both frozen support thresholds (`>=12/24`, delta `>=+8/24`) and incurred high latency and token cost.
3. **MN-005:** Multi-pass self-reconstruction was inconclusive (`1/6` Arm C vs `0/6` control). It established that if the evaluated question merely requests the final state of an entity, host-side state tracking becomes a trivial copy-paste lookup tautology with zero downstream reasoning.
4. **MN-006 & MN-007:** Contiguous two-entity latest-state recovery without external support remained at the floor across all six difficulty cells ($C_i \le 4/18$, $16.7\%$ aggregate pass rate), leading to formal milestone closure at `no usable operating region in bounded landscape`.

In-context latent attention tracking is therefore rejected as a viable mechanism for multi-entity state tracking on this model class. MN-008 addresses this by decoupling deterministic event bookkeeping to an external host engine, providing structured snapshots to the LLM solely for downstream conditional reasoning.

## Selected causal question

> For `Llama-3.2-3B-Instruct`, does offloading deterministic state tracking to a host-managed engine (which provides a minimal structured state snapshot) significantly improve reliability on downstream multi-entity conditional decision reasoning compared to a matched single-pass in-context baseline and an active two-call control receiving the same raw event stream?

## Falsifiable hypothesis

Given an identical raw event stream, identical queried entities, and an identical case-specific 4-branch decision rule table:

Supplying a host-maintained scoped state snapshot (`E1=S0; E2=S1`) to a fresh inference call will achieve statistically significant improvement in exact decision action selection (`ACTION_0` .. `ACTION_3`) over:
- **Arm A (Monolithic In-Context Baseline):** where the model must simultaneously track states through the raw event stream and evaluate the rule table in one pass; and
- **Arm B (Active Two-Call Control):** where the model reads the raw event stream in Stage 1 and passes a budget-matched neutral summary to Stage 2;

because offloading deterministic state transitions ($O(1)$ RAM updates) removes the latent attention degradation bottleneck while preserving the model's capacity for non-trivial conditional branch evaluation.

The primary independent variable is **the presence of a deterministic host-managed scoped state snapshot during conditional rule evaluation**.

## Frozen conceptual arms

### Arm A — Monolithic single-pass baseline
- **Inputs:** Complete raw event sequence + canonical decision rule table + decision task query.
- **Inference budget:** Single model call, large context ($O(N \times L)$ tokens).
- **Purpose:** Direct continuity with prior failure modes, establishing the baseline difficulty when small models must track state and reason simultaneously in-context.

### Arm B — Active two-call control
- **Stage 1:** Receives raw event sequence and queried entities. Instructed to emit a fixed-budget, content-neutral intermediate summary (placeholder grammar predeclared in Gate B, $\le 64$ tokens). No state extraction or rule pre-evaluation allowed.
- **Stage 2:** Receives literal Stage 1 artifact + canonical decision rule table + decision task query. Emits final action token.
- **Purpose:** Controls for the compute advantage of a two-stage procedure, prompt restructuring, and repeated query exposure without granting access to an external state engine.

### Arm C — External State Management treatment
- **Stage 1 (Host Engine):** Deterministic host engine executes exact event replay in memory ($O(1)$ amortized) and extracts a scoped state snapshot for the two queried entities: `E1=<state>; E2=<state>`.
- **Stage 2 (LLM Reasoning):** Receives literal scoped snapshot + canonical decision rule table + decision task query. Emits final action token.
- **Purpose:** Isolates the causal effect of external deterministic state tracking on downstream conditional reasoning.

## Host-process contract

Between raw event input and model inference, the host process is strictly bounded:

### Permitted actions:
1. Ingest raw events and maintain exact state mappings in memory via the hardened `replay()` protocol inherited from MN-007.
2. Extract scoped snapshots restricted exclusively to the queried entities (`scoped_replay`).
3. Serialize the scoped snapshot into a flat, minimal key-value representation: `E1=S0; E2=S1`.
4. Assemble immutable prompt scaffolding combining snapshot, decision rule table, and query.
5. Compute and log SHA-256 digests of all intermediate artifacts for provenance auditing.

### Prohibited actions (invalidating conditions):
1. Semantic parsing or normalization of state values beyond exact string equality.
2. Evaluating conditional predicates (e.g. checking whether `state(E1) == state(E2)`).
3. Pre-matching or pre-filtering decision rules based on host-computed state.
4. Suggesting, biasing, or selecting action candidate labels.
5. Inspecting or utilizing ground-truth oracle answers prior to evaluation completion.

## Anti-tautology and construct validity boundary

To prevent the trivial copy-paste lookup trap identified in MN-005:
- The task **MUST NOT** be a state recovery question (e.g. *"What is the state of E1?"*).
- The task **MUST** require evaluating a 4-branch mutually exclusive, collectively exhaustive (MECE) decision rule matrix conditioning on the joint states of two distinct entities ($E_1, E_2$).
- Neither entity's state in isolation determines the correct action; the LLM must execute joint conditional conjunction (`AND`).

## Vocabulary and Latin Square counterbalancing protocol

### 1. State vocabulary
Reuses the frozen neutral vocabulary from MN-007:
```python
STATE_VOCABULARY = ("S0", "S1")
```
Using neutral tokens eliminates pre-training semantic priors (e.g. associations with `active`, `locked`, `ready`).

### 2. Action vocabulary
```python
ACTION_VOCABULARY = ("ACTION_0", "ACTION_1", "ACTION_2", "ACTION_3")
```

### 3. Latin Square counterbalancing
To guarantee absolute fairness across arms and prevent positional or label memorization:
- State pair space: $4$ combinations: `(("S0", "S0"), ("S0", "S1"), ("S1", "S0"), ("S1", "S1"))`.
- Across the $N = 24$ test cases, each state pair appears exactly $6$ times.
- The mapping between state pairs and action labels is deterministically permuted per case using a Latin Square of order 4:
```python
def get_counterbalanced_mapping(case_ordinal: int) -> dict[tuple[str, str], str]:
    shift = case_ordinal % 4
    shifted_actions = ACTION_VOCABULARY[shift:] + ACTION_VOCABULARY[:shift]
    return dict(zip(STATE_PAIRS, shifted_actions, strict=True))
```
- Each action is the ground-truth target in exactly $6$ of the $24$ cases.
- Random guess baseline is strictly $25.0\%$.
- All three arms receive the exact same case-specific rule table for case $i$.

### 4. Canonical rule presentation
Rules in the prompt must always be rendered in the canonical order of `STATE_PAIRS` to eliminate order-of-appearance cues:
```text
[DECISION RULES]
- IF E1=S0 AND E2=S0 THEN ACTION: <mapped_action>
- IF E1=S0 AND E2=S1 THEN ACTION: <mapped_action>
- IF E1=S1 AND E2=S0 THEN ACTION: <mapped_action>
- IF E1=S1 AND E2=S1 THEN ACTION: <mapped_action>
```

## Compute and resource interpretation

- **Arm A:** High context load ($O(N \times L)$ tokens), single call, vulnerable to positional degradation.
- **Arm B:** Two calls, moderate context load in Stage 1, bounded intermediate transport.
- **Arm C:** Single call to LLM with compact context ($< 100$ tokens), plus negligible host compute ($O(N)$ CPU time, $O(E)$ RAM).

A performance advantage of Arm C over Arm A confirms the system-level benefit of offloading state. A performance advantage of Arm C over Arm B confirms that the structured state snapshot provides specific causal utility beyond a two-stage procedure.

## Claim and falsification boundaries

- If Arm C significantly outperforms Arm A and Arm B under the Gate B criteria, the supported claim is:
  > Offloading deterministic multi-entity state tracking to a host-managed engine enables reliable downstream conditional decision reasoning in small language models, overcoming the in-context latent state degradation bottleneck.
- If Arm C fails to outperform Arm A or Arm B, the hypothesis is falsified for this contract; external state representation does not resolve conditional reasoning limitations on this model class.
- This design does not claim general autonomous reasoning, multi-turn dialogue memory, or unconstrained external knowledge retrieval.

## Experiment-invalidating conditions

An experiment run is invalidated if:
1. Event histories, queried entities, or rule tables differ across paired arms for any case.
2. The host engine leaks decision tokens or pre-evaluates rule conditions.
3. KV-cache or conversational state persists across distinct test cases.
4. Response outputs violate the single-token action schema (`ACTION_0` .. `ACTION_3`).
5. Artifact SHA-256 digests do not match frozen materialization manifests.

## Gate A / Gate B boundary

- **Gate A freezes:** The causal question, hypothesis, 3 conceptual arms, host boundary contract, anti-tautology rule, neutral state/action vocabularies, and Latin Square counterbalancing design.
- **Gate B must freeze:** The 24-case corpus manifest, raw event generators, exact token budgets, preflight criteria, statistical support thresholds (e.g. minimum passes and delta rules), and execution order.

## Gate A decision

External State Management is selected as the sole MN-008 Gate A hypothesis. Gate B measurement contract design is the next required step. No runner implementation, model inference, or empirical evidence is authorized by this note.
