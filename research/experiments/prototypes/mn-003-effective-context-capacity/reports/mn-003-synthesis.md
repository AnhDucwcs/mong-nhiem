# MN-003 synthesis — effective context capability map

## Decision

MN-003's bounded **direct-context measurement phase is complete**. Its canonical experiments and evidence remain immutable and retained. The synthesis outcome is **C**: no further ECC experiment is justified before the next step, but no context-management architecture is selected. The next work, if authorized, should be a separate intervention-design/hypothesis milestone rather than an ECC-008 replication of a non-decision-critical outlier.

MN-003 asks how reliable small-model capability changes under controlled direct-context pressure; it does not measure advertised context-window size. Every conclusion below is limited to the named model, task contract, local runtime, and tested range.

## Evidence inventory and capability map

All canonical runs used deterministic construction, actual model-token accounting, a fixed llama.cpp family/runtime contract, exact deterministic evaluation, retained raw evidence, and offline validators. The model subject is part of every conclusion.

| Experiment | Capability / subject | Controlled task and range | Observed reliability pattern | Dominant failure / confound status | Stable degradation, floor, or ceiling | Position or interference result | Confidence and architecture implication |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ECC-001 | Retrieval — Llama 3.2 3B; Qwen3-4B | One marked single fact, midpoint, 20 cases, 512–16,384 | Both 1.00 at every level | None; zero invalid/truncated rows | No degradation; high-task ceiling through tested range | No semantic competition; position fixed at midpoint | Valid easy-task lower bound only; does not motivate an intervention |
| ECC-002 | Retrieval — Llama 3.2 3B | One unmarked confusable registry record, midpoint, 20 cases, 512–16,384 | 1.00, 1.00, 0.95, 0.95, 0.90, 0.85 | Exact retrieval failures; no runtime, malformed, invalid, or truncation confound | Yes: monotonic bounded decline; ECC95 4,096, ECC90 8,192, ECC80 >=16,384 tested | Same-template semantic interference is necessary for the observed decline versus ECC-001 | Strong bounded direct-context limitation; reason/remedy not identified |
| ECC-002 | Retrieval — Qwen3-4B | Same as Llama ECC-002 | 1.00 at every level | None | No observed degradation; ceiling/right-censored through 16,384 | No measured interference sensitivity | Bounded null result; no intervention inference |
| ECC-003 / ECC-004 | Retrieval — Llama 3.2 3B | ECC-002 task with early/middle/late positions; 20 full-ladder cases then 40 fresh confirmatory cases at 8k/16k | ECC-003 at 16k: early/middle/late 1.00/0.85/0.70. ECC-004 fresh 16k: 1.00/0.925/0.825 | ECC-004's 18 failures are partial expected codes, not tracked distractor selections; zero invalid/truncated/runtime rows | Yes: predeclared fresh-case 16k early-over-late criterion replicated (gap 0.175; 7 one-way paired transitions) | Replicated bounded late-position sensitivity; not a general lost-in-the-middle mechanism | Strongest retrieval/position finding, but it does not establish that retrieval, routing, or compression would fix the partial-output behavior |
| ECC-003 / ECC-005 | Retrieval — Qwen3-4B | ECC-003 full position ladder; ECC-005 30 fresh early/late cases at 8k/16k | 1.00 throughout both canonical matrices | None | No observed position effect; high-task ceiling at tested resolution | Qwen fresh control has zero early-minus-late gap and zero directional transitions | Bounded null result; no retrieval architecture implication |
| ECC-006 | Integration / State Tracking — Llama 3.2 3B | Four ordered target updates, midpoint, six cases, 512/2,048/8,192/16,384 | 0.333, 0.167, 0, 0 | 21 `incorrect_state` outputs; zero runtime, malformed, invalid, or truncation confound | Strong floor concern at 512 plus monotonic decline; ECC95/ECC90/ECC80 = 512 | Position, update-count, and state-representation dimensions were held fixed/not swept | Strong evidence that this bounded state-tracking contract is a Llama capability bottleneck; context length is not proven to be its sole cause |
| ECC-007 | Inference / Causal Reasoning — Qwen3-4B | Two-hop reachability, 4 YES/4 NO, midpoint, 512/2,048/8,192/16,384 | 1.00, 1.00, 0.875, 1.00 | One unreachable-graph false positive at 8k; zero other confounds | No stable degradation boundary; high-task ceiling and only eight cases | Position/interference not swept | High reliability in the tested range, with low resolution; no causal intervention implication |

## Retrieval findings

Easy marked-fact retrieval is stable for both qualified subjects through the tested ladder (ECC-001). Adding same-template semantic competition changes the Llama result materially: ECC-002 has a monotonic decline from 1.00 to 0.85 while Qwen remains perfect in that bounded task. The later position experiments establish more than a one-off curve: Llama's early-over-late direct-context effect at 16k was independently confirmed on 40 fresh cases by ECC-004 under a frozen endpoint rule. Qwen's lack of an early/late effect was also independently controlled on 30 fresh cases by ECC-005.

The confirmed Llama retrieval limitation is therefore **bounded semantic-interference and late-position sensitivity under a synthetic confusable exact-output contract**. It is not evidence of a generic advertised-window limit, a causal attention mechanism, or successful selection of a competing distractor: ECC-004 failures are expected-code numeric suffixes rather than tracked distractor codes. That diagnostic matters—context selection or routing may be relevant candidates later, but retained evidence does not show they would repair this particular failure mode.

## State Tracking findings

ECC-006 provides the clearest short-to-long reliability loss for a single subject. Llama 3.2 3B receives exactly four ordered target updates at fixed midpoint placement; accuracy is 2/6 at 512, 1/6 at 2,048, and 0/6 at 8,192 and 16,384. All 21 failures are deterministic `incorrect_state` outputs; no malformed response, overflow, truncation, invalid case, or runtime failure confounds that capability result.

This establishes that the frozen four-update State Tracking contract is a **capability bottleneck for Llama 3.2 3B**, with a material floor effect already at short context. The monotonic curve shows that more irrelevant context is associated with additional degradation under this contract. It does not isolate context length as the only cause, because update count, representation, and sequence structure were deliberately held fixed rather than independently swept.

## Causal Reasoning findings

ECC-007 is a Qwen3-4B-only two-hop direct-context reachability baseline with eight canonical cases. It has 32 valid rows and the accuracy curve 1.000, 1.000, 0.875, 1.000 at 512, 2,048, 8,192, and 16,384 requested tokens. The sole miss is an `incorrect_causal_inference` false positive on an unreachable graph at 8k.

The contiguous-prefix metric convention correctly yields ECC95/ECC90 = 2,048 and an ECC80 lower bound >=16,384 tested tokens. That metric is **not** the research conclusion: the 8k miss is isolated and non-monotonic, so ECC-007 does not establish a stable causal context-length degradation boundary. Its eight-case, near-ceiling resolution also limits what can be inferred from the null pattern.

## Cross-experiment comparability limits

The MN-003 inventory is a capability map, not one scalar benchmark ladder.

- ECC-006 measures **Llama 3.2 3B** State Tracking; ECC-007 measures **Qwen3-4B** causal reachability. Their scores cannot support “State Tracking is weaker than Causal Reasoning” or “causal is stronger than state tracking.” A same-model comparison would be required if an architecture decision depended on that contrast.
- Retrieval results are most comparable within the same subject and task lineage: ECC-002/ECC-003 middle and ECC-004 for Llama; ECC-003/ECC-005 for Qwen. ECC-001 is intentionally easier and is a lower bound, not a replacement for the confusable task.
- Case counts and resolutions differ: 20 retrieval cases, 40 Llama confirmation cases, 30 Qwen control cases, six State Tracking cases, and eight causal cases. Ceiling/floor interpretation must retain those resolutions instead of forcing a common ECC number.
- Runtime/model identity is sufficiently documented for reproducibility, but small differences in lifecycle handling and experiment-specific context ladders mean timing is descriptive only.

## Capability limitations versus practical runtime limitations

Capability limitations are wrong answers from valid, complete direct-context requests. The replicated Llama late-position retrieval effect, ECC-002's monotonic Llama confusable-retrieval curve, and ECC-006's incorrect-state curve meet that definition.

Practical runtime limitations are separate. Across the retained RTX 3050 Laptop GPU (4 GiB) runs, median request time rises substantially at 16k: approximately 18–20 seconds for the Llama long-context retrieval confirmations, 28–31 seconds for Qwen long-context retrieval controls, and 24.6 seconds for Qwen ECC-007. Qwen long-context logs record prompt-cache eviction and ECC-003 required lifecycle restarts between position batches after a discarded OOM diagnostic. These are meaningful local operating-cost constraints, but none demonstrates a decline in retrieval, state, or causal capability by itself.

## Confirmed, unresolved, and excluded claims

### Confirmed limitations

1. Llama 3.2 3B has a replicated, bounded direct-context confusable-retrieval late-position limitation at long context under exact-output scoring.
2. Llama 3.2 3B has a strong State Tracking bottleneck on the fixed four-update contract, including a short-context floor and a monotonic decline as context increases.
3. Long direct context has material practical local runtime cost on the recorded 4 GiB hardware configuration.

### Unresolved observations

1. ECC-007's 8k Qwen false positive is an isolated non-monotonic observation, insufficient evidence of a systematic causal context-length effect.
2. The causal task has no canonical Llama subject under the same 16-token YES/NO contract, and the state task has no canonical Qwen subject. This prevents cross-capability, cross-model ranking.
3. The retained Llama retrieval diagnostics do not determine whether the missing code prefix is a retrieval, output-format, or another interaction effect.

### MN-003 does not prove

- either model's advertised context capacity or reliability beyond 16,384 tested tokens;
- a universal model ranking or a production-model selection;
- a generic lost-in-the-middle mechanism;
- that runtime slowdown causes capability loss;
- that retrieval, RAG, memory, summarization, compression, routing, embeddings, or external state will fix any observed result.

## Architecture implications and next milestone

No architecture is selected. The most decision-relevant limitation is the Llama State Tracking bottleneck, because it occurs even at short context, declines to zero under controlled pressure, and is not confounded by invalid execution. Its **candidate intervention class** is an explicit, inspectable state representation or externalized state-management hypothesis—not an adopted design and not a retrieval/RAG decision. The replicated Llama position effect is a separate candidate problem for future context-selection research, but its partial-code diagnostic prevents claiming that routing/retrieval is the remedy.

There is no decision-critical reason to create ECC-008 for the ECC-007 8k miss: whether that one miss is noise or reproducible would not change the conclusion that Qwen causal reliability has no established stable degradation boundary, nor would it select an intervention. Rerunning only to obtain a smoother curve would violate the frozen-evidence discipline.

The recommended next milestone is **MN-004 — State Representation Intervention Design** (proposed, not started). Its first deliverable should be a pre-execution hypothesis and a minimal design contract asking: *For Llama 3.2 3B on the frozen ECC-006 four-update task, can a specified explicit state representation improve exact final-state reliability relative to the direct-context baseline without changing task semantics or hiding failures?* The milestone must first select and justify one candidate representation, preserve the direct baseline, predeclare success/no-harm criteria, and avoid assuming retrieval, RAG, memory, summarization, compression, routing, embeddings, or external state as a solution.

## Validation boundary

This synthesis does not alter canonical experiment definitions, fingerprints, raw runs, scores, or metrics. It is derived from the retained reports, definitions, summaries, metadata, and validators for ECC-001 through ECC-007.
