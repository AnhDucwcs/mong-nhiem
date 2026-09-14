# MN-005 Gate A — Multi-pass Reconstruction hypothesis selection

## Status

**Frozen Gate A design note.** This selects one causal hypothesis and three conceptual arms only. It is not a measurement contract, implementation, runner, schema, run, or evidence of improvement.

- Gate A: complete and frozen for target-aware model-generated reconstruction.
- Gate B: not started.
- Gate C implementation and measured evidence: not authorized.
- Gate D promotion: not authorized.

MN-005 inherits MN-003 ECC-006 and MN-004 as immutable historical evidence. It does not rescore, alter, or continue either milestone.

## Inherited evidence and selection rationale

ECC-006 establishes a bounded Llama 3.2 3B State Tracking failure region: one named target has four ordered updates and the model must return its exact final state. Accuracy falls from `2/6` at 512 to `0/6` at 8k and 16k. The retained failures are valid `incorrect_state` outputs; the diagnosed values are earlier states of the named target.

The frozen 8k source layout already places the four target updates contiguously at the midpoint. MN-005 therefore does not select entity partitioning or cross-entity-interleaving reduction as its mechanism. The remaining bounded question is whether model-side reconstruction and final answer selection should be separated procedurally.

MN-004 tested a different intervention: a globally indexed, fixed-field input ledger. Its final valid Llama 8k result (`0/24` untreated to `7/24` ledger) missed both frozen support thresholds and incurred material token and latency cost. MN-005 is not a ledger retry, renderer change, or MN-004 continuation.

## Selected causal question

For Llama 3.2 3B in the frozen ECC-006 State Tracking failure region, does making a target-aware, model-generated reconstruction artifact available to a fresh final-answer inference stage improve exact final-state selection beyond an otherwise matched two-call procedure whose first-stage artifact is content-neutral?

## Falsifiable hypothesis

Given unchanged ECC-006 source facts, target question, final answer semantics, and exact evaluator, a target-aware Stage A that transcribes the target's source update events in source order, with its literal unmodified output supplied to a fresh Stage B, will improve exact final-state reliability relative to an active two-call control with the same source rereading, target/question availability, Stage B structure, and scheduled Stage A completion budget, because the model-generated reconstruction artifact separates source-update reconstruction from final answer selection.

The primary independent variable is **the availability of a target-aware model-generated reconstruction artifact during a fresh final-answer inference stage within a matched two-call procedure**. Instruction-directed model computation is part of the intervention. This hypothesis does not claim to separate reconstruction from every consequence of additional inference computation.

## Frozen conceptual arms

### Arm A — direct single-pass compatibility baseline

Arm A receives the unchanged frozen source history and unchanged original question in one model call. It returns the original exact final-state answer under the unchanged evaluator.

Its purpose is continuity with the frozen ECC-006 failure region and system-level interpretation of the two-call bundle. Arm A alone cannot establish that reconstruction content caused a difference.

### Arm B — two-call active control

Arm B uses two fresh calls with no hidden conversational, session, or KV-state continuity.

Stage A receives the unchanged raw source history and the unchanged original question, including the target identity. It is instructed to emit a fixed-shape, content-neutral artifact. The artifact must use only a predeclared placeholder vocabulary independent of source event text, entity identifiers, state values, source ordering, target identity, and expected answer. It must not reconstruct, summarize, retrieve, classify, rank, or reason about target state.

Stage B receives the unchanged raw source history, the complete literal Stage A output, and the unchanged original question and final-answer instruction. It returns only the exact final-state answer under the unchanged evaluator.

The active control controls the second call, raw-source rereading, target/question availability, literal intermediate-output transport, Stage B prompt structure, and the scheduled maximum Stage A completion budget. Its placeholder grammar and sizing policy must be predeclared before measured execution and must not be retrospectively matched to observed Arm C outputs. Gate B will freeze the exact grammar and tokenizer-aware sizing before measured efficacy runs; Gate A freezes this semantic-neutrality and predeclaration requirement.

### Arm C — Multi-pass Reconstruction treatment

Arm C uses two fresh calls with no hidden conversational, session, or KV-state continuity.

Stage A receives the unchanged raw source history and unchanged original question, including the target identity. It is instructed to transcribe every source state-update event for that target in original source order, using only source-derived event information. The intended artifact has one row per target source event, with source order represented by row position, and may contain only:

- unchanged entity identifier; and
- unchanged assigned state token.

If the frozen source representation explicitly supplies an ordinal, the model may copy it verbatim; a global ordinal is neither mandatory nor to be inferred or calculated. The artifact must not emit a `current`, `latest`, `final`, `answer`, summary, conclusion, derived state, or host-calculated field.

Stage B receives the unchanged raw source history, the complete literal Stage A output, and the unchanged original question and final-answer instruction. It returns only the exact final-state answer under the unchanged evaluator.

## Host-process contract

Between stages, the host is transport-only. It may preserve Stage A bytes, concatenate frozen deterministic prompt scaffolding, send Stage B, and record hashes and resource accounting. It must not:

- semantically parse Stage A;
- determine whether the reconstruction is correct;
- repair, filter, reorder, or selectively reinject Stage A rows;
- select state values or target evidence;
- compute the final state;
- inspect or use the expected answer; or
- replace Stage A with a corrected artifact.

Malformed, incomplete, wrong, or otherwise nonconforming Stage A output remains model behavior and must be passed to Stage B literally. It is not an excuse for host-side correction.

## Target-awareness and leakage boundary

Stage A is intentionally target-aware. The original ECC-006 question already exposes the target, and both two-call arms receive equivalent target/question availability. Target-blind reconstruction would be a substantially different, much more expensive hypothesis.

A correct Stage A transcription is answer-relevant: the final target update corresponds to the ECC-006 answer. This is permitted only because the tested model generates the artifact from unchanged source facts and the host neither calculates nor selects that event. MN-005 tests model-side self-reconstruction, not a stronger notion of answer-information removal.

MN-005 does not test target-blind state maintenance, complete world-state reconstruction, external memory, multi-entity persistence, retrieval, or external state management.

## Compute and resource interpretation

Arm C necessarily uses more calls, repeated raw-source exposure, and likely more latency and decoded tokens than Arm A. A C-versus-A difference therefore supports only the system-level two-call procedural bundle.

The primary causal comparison is C versus B. Those arms must match the number of fresh calls, raw-source exposures, target/question availability, Stage B interface, scheduled maximum Stage A completion budget, and relevant runtime configuration. The maximum budget, the predeclared active-control placeholder grammar/sizing policy, actual completion-token counts, and resulting Stage B prompt-token counts are distinct quantities. Actual prompt tokens, completion tokens, wall-clock latency, and resource use may still differ and must be reported rather than treated as exactly matched.

## Claim and falsification boundaries

If Arm C outperforms Arm A under a later frozen measurement contract, the supported system-level claim is limited to:

> Target-aware staged reconstruction under a larger two-call procedural inference budget improved exact final-state reliability in the bounded ECC-006/Llama setting.

If Arm C outperforms Arm B under the later frozen primary comparison, the supported causal claim is limited to:

> The literal model-generated reconstruction artifact contributed to exact final-state reliability beyond the matched two-call/source-rereading procedure in the bounded ECC-006/Llama setting.

If Arm C does not satisfy the future frozen C-versus-B support rule, the result reduces priority for explicit target-aware model-side reconstruction as the missing mechanism for these prior-target-state failures. It does not reject multi-pass methods generally.

No outcome may establish decomposition independent of all compute, general long-context reasoning, cross-model effectiveness, external-memory effectiveness, architectural efficiency, or general mutable-state reliability.

## Experiment-invalidating conditions

The causal comparison is invalid before efficacy interpretation if any of the following occurs:

- source facts, target identity availability, question semantics, or final evaluator differ between corresponding arms;
- the host semantically modifies, repairs, filters, or selectively reinjects Stage A output;
- hidden conversational, session, prompt-cache, or KV-state continuity differs between two-call arms;
- treatment receives expected-answer information or an externally computed/selected target state;
- the active-control artifact reconstructs, summarizes, retrieves, ranks, or otherwise assists target-state reasoning;
- runtime configuration differs beyond the later frozen comparability rules; or
- literal Stage A preservation and Stage B prompt provenance cannot be audited.

Wrong, malformed, truncated, incomplete, or nonconforming model outputs are ordinary model outcomes unless a later frozen protocol rule identifies a genuine transport or execution invalidation. They must not be converted into corrected prompts or selectively removed from the treatment.

## Gate A / Gate B boundary

Gate A freezes the causal question, hypothesis, conceptual arms, intended independent variable, host boundary, target-awareness policy, leakage boundary, allowed claims, negative interpretation, and invalidation conditions.

Gate B must still freeze implementation-specific measurement details, including sample and case policy, efficacy and no-harm thresholds, run counts, exact predeclared placeholder grammar and tokenizer-aware sizing policy, prompt text, output limits, runtime/hardware accounting, execution order, evidence retention, and failure taxonomy. The placeholder policy must be fixed before measured efficacy runs, never retrospectively matched to observed Arm C outputs.

## Relation to prior work

MN-003 measured direct-context State Tracking; it did not test an intervention. MN-004 changed input representation through a globally indexed ledger; MN-005 leaves source event representation unchanged and changes model inference procedure. The unselected partitioning direction concerns input organization; this Gate A does not group or reorder source records. External state management would move state maintenance outside the model; this Gate A keeps reconstruction inside model inference and limits the host to literal transport.

## Gate A decision

Multi-pass Reconstruction is selected as the sole MN-005 Gate A hypothesis. Gate B is the next required decision point. No implementation, runner, model execution, or measured evidence is authorized by this note.
