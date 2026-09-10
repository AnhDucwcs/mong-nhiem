# MN-004 Gate A — hypothesis selection

## Status

Frozen Gate A design note. This selects one hypothesis only; it is not an experiment definition, implementation, treatment run, or evidence of improvement.

## Failure-mode interpretation

ECC-006 establishes a bounded Llama 3.2 3B State Tracking failure region under exact scoring. It does not identify a unique internal cause. The retained failures are valid `incorrect_state` responses; all 21 are values from earlier updates of the target entity. That pattern motivates a test of state-update representation, but it does not prove forgetting, retrieval failure, attention decay, or inability to apply an update.

## Candidates considered

### A. Globally indexed event ledger — selected

Transform every state-update event into a fixed-field row while preserving the complete global event sequence. The model must still identify the named entity and infer its final state from the ordered updates.

### B. Per-entity grouped histories — rejected

Grouping records by entity destroys global interleaving and places the target's updates in an isolated local sequence. It substantially reduces distractor pressure and risks turning the task into finding the last item in a target-specific list.

### C. Target-only recap alongside the log — rejected

Repeating only the target updates changes target salience and duplicates task-relevant information. Any gain would be inseparable from an added cue and extra prompt material.

### D. Current-state register — rejected

Preprocessing the updates into a current-state field computes the answer that the model is meant to infer. It is answer leakage rather than a representation intervention.

## Selected representation: globally indexed state-transition ledger

For every original event, in original left-to-right order, emit exactly one ASCII line:

`event=<positive decimal index> | entity=<original entity identifier> | new_state=<original state token>`

The complete treatment prompt is the heading `Chronological state-transition ledger:` followed by those rows and the unchanged ECC-006 question. Indexing starts at 1, increases by exactly 1 for every event, has no zero padding, and is global across target and distractor events. The target has no special marker, section, duplicate, or positional relocation.

For a case whose ordered source events are e1 through en, the exact content layout is:

    Chronological state-transition ledger:
    render(e1)
    ...
    render(en)

    Question:
    What is the current state of <original target entity>? Return only the state.

render(ei) uses ASCII literal field names and delimiters exactly as shown: event=<i> | entity=<ENTITY> | new_state=<STATE>. There is one line per event, one newline between rows, one blank line before Question:, no trailing whitespace, and no other prose. <ENTITY> and <STATE> are byte-for-byte copies of the source event fields. new_state means the value assigned by that individual event, never an aggregated current value.

The transformation is one-to-one: every baseline `State update: ENTITY changed to STATE.` event provides exactly its ENTITY and STATE fields; no event is added, removed, merged, reordered, inferred, or rewritten. The ledger replaces the natural-language event log rather than appearing beside it. The model sees no original log, per-entity grouping, latest/current field, derived final state, answer key, target-only recap, or evaluator-side reconstruction.

## Deterministic derivation and refresh semantics

The renderer consumes the complete frozen event sequence once, left to right. For source event number `i`, it emits ledger row `i` using the exact entity identifier and state token from that event. A row is emitted once and is never revised after later updates. The renderer holds no per-entity current state, does not compute one, and produces no summary. Distractor events follow the identical rule.

## Falsifiable hypothesis

Given the same ordered ECC-006 State Tracking information and task semantics, exposing the globally indexed state-transition ledger will increase Llama 3.2 3B exact final-state reliability in the inherited failure region relative to direct natural-language presentation, because explicit global event order and fixed state fields reduce the burden of identifying ordered overwrite events without supplying their final value.

The independent variable is event rendering: direct natural-language event sentences versus the ledger above. The dependent variable is exact final-state reliability. Facts, event order, target identity, final-state question, answer semantics, and exact evaluator remain invariant.

The hypothesis is falsified for this contract if the predeclared Gate B comparison shows no qualifying Llama improvement in the failure region, shows regression, or cannot attribute an apparent difference to the rendering rather than a controlled confound. A successful result would support only this bounded representation/failure-mode interaction.

## Confounds and prohibited transformations

The ledger changes tokenization, syntactic regularity, information density, and the visual salience of ordering. Gate B must control or measure prompt-token length, context budget, target placement, number and ratio of distractor events, prompt-template overhead, and model/inference settings. It must not call a result representational if it is explained by a shorter context, a moved target sequence, added inference budget, removed distractor pressure, or duplicated information.

The treatment must not add local per-entity ordinals, group by entity, label a row as latest/current/final, emit a summary, retain the original log alongside the ledger, change event count/order, mark the target, change the question/evaluator, or calculate the final state outside the model.

## Qwen control feasibility

The transformation is syntactically applicable only to workloads whose facts are ordered state-update events. MN-003 contains no frozen Qwen State Tracking workload, so Gate A does not name a Qwen control or claim no harm. Gate B must either identify a frozen reliable Qwen workload for which this same one-to-one event rendering is semantically equivalent, or record that the required Qwen no-harm claim cannot be made for this candidate.

## Gate A decision

Candidate A is selected because it has one explicit independent variable, a deterministic one-to-one provenance rule, preserved global order and distractor material, no external machinery, and a direct falsification path. Its possible benefit is not assumed. Gate B remains pending.
