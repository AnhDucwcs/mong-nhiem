# MN-005 Hierarchical State Representation — Gate A static audit

**Status:** `hierarchical_gate_a_unselected`
**Scope:** design-only candidate audit; no hierarchical treatment, Gate B, runner, measured evidence, model inference, or GPU work was created.

## Transition from Multi-pass Reconstruction

Multi-pass Reconstruction remains a retained MN-005 candidate, not a discarded idea. Its first fully valid canonical experiment is `attempt-0002`, with Arm A=`0/6`, Arm B=`0/6`, Arm C=`1/6`, `n10=1`, `n01=0`, and `D=+1`. None of the six Arm C Stage A artifacts met the frozen exact-reconstruction criterion, including the artifact associated with the sole B-to-C beneficial flip. Its frozen result is `inconclusive`, not supported and not unsupported.

The bounded interpretation is: the frozen treatment produced a `+1/6` paired improvement over its matched active control, but supplies no evidence that the hypothesized model-generated reconstruction mechanism caused that improvement. It is therefore deprioritized for additional ECC-006 efficacy reruns under the existing Gate B v2 formulation. `attempt-0003` is not authorized. A materially different multi-pass hypothesis would require a new candidate decision rather than a replacement run.

## Candidate landscape after attempt-0002

| Candidate | Current evidence position | ECC-006 design implication |
| --- | --- | --- |
| Hierarchical State Representation | This audit finds no independently observable hierarchy variable in frozen ECC-006. | Unselected on ECC-006; needs a workload with genuine distributed membership/scope structure. |
| External State Management | Architecturally relevant, but a host-maintained final state would trivially answer ECC-006. | Needs a downstream reasoning/interface workload where maintained state is not itself the answer. |
| Event-to-State Normalization | Source updates already use one fixed `State update: {entity} changed to {state}.` template. | Weakly motivated on ECC-006; would risk testing syntax change rather than semantic normalization. |
| Multi-pass Reconstruction | Valid measured result: `inconclusive`. | Retain result; do not repeat the same contract. |
| Symmetric State Partitioning | Target histories are already contiguous in the frozen source layout. | Unselected: the proposed interleaving-isolation mechanism is absent. |

These are workload-bounded positions, not universal rankings of intervention classes.

## Frozen ECC-006 facts relevant to hierarchy

ECC-006 asks Llama 3.2 3B for the final state of one entity after exactly four chronological assignments. The raw source uses a fixed natural-language event template; the target block is placed at the midpoint and distractors use the same template. The original experiment did not sweep event hierarchy, entity grouping, update distribution, or position.

Static inspection of the six retained 8k request payloads gives the following event-layout inventory. Event positions are one-based within the rendered source events.

| Case | Source events | Distractor histories | Histories before target | Target positions | Events after target |
| --- | ---: | ---: | ---: | --- | ---: |
| ecc006-001 | 600 | 149 | 75 | 301–304 | 296 |
| ecc006-002 | 596 | 148 | 75 | 301–304 | 292 |
| ecc006-003 | 596 | 148 | 75 | 301–304 | 292 |
| ecc006-004 | 592 | 147 | 74 | 297–300 | 292 |
| ecc006-005 | 596 | 148 | 74 | 297–300 | 296 |
| ecc006-006 | 596 | 148 | 75 | 301–304 | 292 |

Every target's four updates are already contiguous, in source order, with no distractor event between them. The four assignments therefore already form a target-local trajectory in the untreated source. The target is not late-positioned, filtered, or scattered across the context.

## What a real hierarchical independent variable would require

A valid treatment would need an inspectable parent/child relation that a matched flat/grouped control does not already convey. It may not be only headings, indentation, cosmetic formatting, entity grouping, reordering, target filtering, source deletion, duplicate target rows, or a final/current/latest label.

For any future hierarchy test, raw source facts, target question, evaluator, target/distractor symmetry, source membership, within-entity order, and—where locality is relevant—event ordering must be matched. A parent relation may encode existing membership and order, but may not compute a state summary. If a last child is the last update, the control must expose the same child order and must not receive a weaker locality condition.

## Formulations evaluated

### H1 — Entity → update-event hierarchy

A rendering such as `entity=E` followed by four state children is entity partitioning with nesting syntax. In ECC-006 every target already appears as an uninterrupted four-event entity block. Grouping all entities by entity either preserves the existing block order and adds only labels/indentation, or reorders histories and introduces a grouping/order mechanism. The former has no meaningful independent variable beyond formatting; the latter is not hierarchy-alone.

**Finding:** not separable from grouping or presentation on this workload.

### H2 — Entity → local trajectory hierarchy

Treating the parent as a trajectory rather than an entity does not change the source relationship: the target's four state assignments are already an explicit local trajectory. If the treatment renders each child only as `state=S`, it compresses repeated entity identifiers; if it keeps entity identifiers on children, it adds parent labels and token overhead. Either choice adds a confound beyond the intended hierarchy. A matched flat control that shares entity membership and child order would make the remaining difference only syntax/formatting.

**Finding:** target-locality and overwrite scope are already available; no clean causal comparison remains.

### H3 — Multi-level temporal hierarchy

A `temporal region → entity → event` rendering must choose temporal regions. Fixed regions derived from source ordinal, history count, or event count are arbitrary new chunk boundaries in ECC-006. They can alter target region position, adjacency, and delimiter salience. Matching the same region partition and order in a flat control leaves indentation/parent syntax as the only difference; not matching it confounds hierarchy with chunking and reordering.

Because each target trajectory already occupies one contiguous midpoint block, an added temporal parent does not create missing target-locality. It instead risks positional artifacts and a large number of new labels.

**Finding:** no non-arbitrary multi-level relation in the frozen source produces an observable hierarchy mechanism.

### H4 — Hierarchy from a new semantic relation

A stronger hierarchy would need a relation not present in ECC-006, such as entities participating in shared objects, roles, temporal episodes with cross-entity dependencies, or parent/child state scopes. Deriving that relation from the answer, a host state calculation, or target identity would leak or change the task. Adding it externally would create a new workload rather than an ECC-006-adjacent representation transformation.

**Finding:** defensible generally, but not available from frozen ECC-006 facts.

## Matched-control conclusion

A causally clean future design would need three conceptual representations:

1. **Raw reference:** unchanged ECC-006, for system-level context only.
2. **Flat/grouped control:** exactly the treatment's source facts, event membership, entity locality, global and local ordering, and non-answer information, without parent/child representation.
3. **Hierarchical treatment:** the same facts and ordering with a specific parent/child relation.

ECC-006 cannot make the second and third arms meaningfully different without adding a non-hierarchical variable. Keeping repeated entity facts in every flat child makes the hierarchy mostly labels and indentation. Omitting them from hierarchy children creates compression. Changing ordering makes grouping/reordering primary. Consequently, no matched control can isolate hierarchy well enough here for a future Gate B.

## Leakage, compression, and resource audit

No H1–H3 proposal needs to explicitly label a final state to become problematic. Because target updates are already contiguous, a parent with ordered children makes selecting the last child conspicuous. This can be allowed only if the flat control shares the same ordered child sequence and target accessibility. On ECC-006, that matching removes the claimed hierarchy mechanism.

A treatment with roughly one parent heading per source history would add approximately 148–150 structural lines at 8k if it preserves entity identifiers on children. Removing repeated entity identifiers avoids that overhead but is information compression. Exact model-token accounting is deliberately deferred; static inspection is sufficient to establish that hierarchy cannot be isolated before token cost becomes the next question.

## Narrow hypothesis that would be needed elsewhere

A hierarchy candidate could be falsifiable on a different workload as follows:

> On a workload with distributed entity-local updates and independently meaningful parent/child scopes, an explicit non-answer-computing representation of entity-local trajectories improves exact state-dependent reasoning beyond a matched flat representation containing the same facts, entity locality, and ordering.

Support would require a hierarchy-over-matched-flat gain while source conservation, identical target availability, shared ordering/locality, no derived-state fields, and measured token/runtime costs rule out deletion, filtering, reordering, or compression. Falsifiers include an equivalent flat control, benefit attributable only to reordering or token change, hierarchy that mechanically reveals the answer, or no hierarchy-over-flat difference.

That is not the same claim as ECC-006's currently frozen final-state endpoint.

## Comparative design assessment

Scores are 1–5, where 5 is favorable for the criterion. They are decision aids, not a scalar selection rule.

| Candidate | Mechanistic distinctness | ECC-006 observability | Confound control | Leakage safety | Evidence interpretability | Generalization potential | Avoids new workload | Token/runtime efficiency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hierarchical representation | 2 | 1 | 2 | 3 | 1 | 3 | 1 | 2 |
| External state management | 5 | 1 | 3 | 2 | 4 | 5 | 1 | 3 |
| Event-to-state normalization | 3 | 1 | 3 | 4 | 2 | 3 | 4 | 4 |
| Multi-pass Reconstruction (measured) | 4 | 5 | 4 | 3 | 4 | 3 | 5 | 1 |
| Symmetric partitioning | 1 | 1 | 2 | 3 | 1 | 3 | 5 | 3 |

Hierarchy has architectural relevance beyond games, but that does not compensate for its lack of a measurable independent variable in this source layout. External state is more structurally distinct and broadly relevant, yet it needs a different downstream task to avoid trivially computing the evaluated answer. Normalization is cheaper but weakly motivated because ECC-006 already has regular source syntax. Multi-pass has now consumed its single frozen attempt and remains evidence-bearing but inconclusive.

## Decision and next research transition

**Decision:** `hierarchical_gate_a_unselected`.

The candidate is coherent in general, but frozen ECC-006 cannot observe a hierarchy-specific mechanism independently of existing target contiguity, grouping, formatting, reordering, or compression. No Hierarchical Gate B should be created from this audit.

The more informative next transition is to design a new workload with distributed state membership and a nontrivial downstream state-dependent task. That workload can make a hierarchy-versus-matched-flat comparison falsifiable and can also later support a fair External State Management evaluation without making host-maintained state identical to the final answer. External State Management remains the stronger architectural class, but selecting it now would still require that new task/interface contract.

## Static safeguards for any future hierarchy workload

A future implementation should mechanically validate source-event conservation, one-to-one source-to-rendered-event provenance, symmetric entity handling, deterministic parent assignment, deterministic parent/child ordering, target-independent preprocessing, absence of derived current/final/latest fields, no source-value deletion or duplication, and matched-control equality for source facts and order. These are future design requirements only; no validator or treatment was implemented here.