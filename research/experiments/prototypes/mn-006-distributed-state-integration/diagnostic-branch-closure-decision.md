# MN-006 diagnostic-branch closure decision

## Decision

**`close_fixed_label_branch_redirect_mn006`.** The fixed-label diagnostic branch is complete and closed. MN-006 remains open only as a redirected research milestone: its frozen v1 semantic workload and retained evidence stay authoritative, but the current finite-label measurement interface is retired from further model execution because it cannot identify the intended distributed-state/locality mechanism for the qualified model/runtime.

This decision creates no replacement plan, executor, model run, locality measurement, or intervention.

## Original MN-006 objective

MN-006 was designed to establish whether a deterministic, candidate-neutral workload can expose a small model's difficulty integrating multiple entities' latest states when their histories are distributed/interleaved rather than contiguous. Its primary causal comparison was always, within profile:

```text
same canonical histories, state model, query, equality rule, and answer class
        ↓
contiguous scheduling versus matched interleaved scheduling
```

The expected causal claim required an observed, construct-valid degradation attributable to changed global state locality/scheduling. The equality rule was deliberately a fixed depth-1, arity-2 answer-oracle adapter: it prevented a maintained state representation from being identical to the final answer. It was not an intended reasoning-difficulty axis, locality was the target phenomenon, and a candidate intervention required a usable locality-sensitive failure signal first.

## Immutable evidence basis

| Artifact | Protocol status and observed behavior | Relevance |
| --- | --- | --- |
| [`attempt-0001`](reports/mn-006-attempt-0001.md) | `protocol_valid`; 128 malformed unconstrained outputs | Free-form response channel did not yield a usable finite-answer measurement. |
| [`attempt-0002`](reports/mn-006-attempt-0002.md) | `protocol_valid`; 128 `INVALID` labels; both profiles `16/32` contiguous and `16/32` interleaved | Grammar made parsing usable but did not create access to the locality construct. |
| [D1](reports/mn-006-label-selection-d1-run-0001.md) | `protocol_valid` / `fixed_label_preference_supported`; `A × 16`; zero grammar-order disagreements | The direct-state counterbalanced A/B diagnostic collapsed before it could diagnose state integration or mapping following. |
| [S0](reports/mn-006-output-selection-s0-run-0001.md) | `protocol_valid` / `direct_copy_supported`; `A, B, B, A` | Explicit A/B surface-label copying works under the constrained channel. |
| [S1](reports/mn-006-output-selection-s1-run-0001.md) | `protocol_valid` / `fixed_label_preference_recurred`; `A × 4` | Fixed A recurs when direct state relation and rule application are required. |
| [explicit-relation control](reports/mn-006-explicit-relation-direct-rule-run-0001.md) | `protocol_valid` / `fixed_label_preference_persisted`; explicit `different -> A`, explicit `equal -> A` | State extraction and equality comparison are not necessary for the observed fixed-A behavior. |
| [downstream review](downstream-fixed-label-causal-review.md) | `behavioral_boundary_reached_l1c_l1d_not_cleanly_identifiable` | The current A/B protocol cannot split conditional-rule application from post-task label selection without duplicating S0 or reintroducing a comparable mapping/selector abstraction. |

The minimality authority plan remains SHA-256 `8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827`; the explicit-relation authority plan remains SHA-256 `dc40c15a896f5f0413783818c39593b8a9c34eeea3ef4ce284e1b311112bc80a`. This review neither changes nor rescores either plan or any retained record.

## Protocol validity is not construct validity

Each listed model run completed according to its frozen execution, parser, evidence-retention, and integrity rules. That is **protocol validity**. It establishes that the retained record faithfully represents the predeclared test.

For D1 and the baseline locality comparison to be **construct-valid** evidence about distributed-state integration, the model would also need to traverse the lower response/rule layer in a way that permits failures above that layer to be attributed to state reconstruction or locality. The evidence shows that condition was not met: fixed A persists even after the relation itself is supplied. Consequently, the model's D1 result is not attributable to distributed-state integration, locality, state reconstruction, or mapping abstraction.

D1 remains valid evidence that the current direct-state A/B measurement protocol has a lower-level response-selection confound. It is not invalid, erased, or reclassified; it is non-diagnostic for MN-006's intended higher-level causal question.

## Fixed-label branch closure

The branch was opened to find the lowest observable failure layer behind D1's all-A output. It established:

- explicit label availability/copying is supported;
- the recurring fixed-A behavior does not require structured-state extraction or equality comparison; and
- the remaining conditional-rule/conditioned-output region cannot be cleanly decomposed further with the current constrained A/B protocol.

The frozen closure conclusion is:

> The fixed-label diagnostic branch is complete. It establishes a lower-level response-selection confound that prevents the current A/B protocol from identifying the intended MN-006 distributed-state/locality mechanism for this qualified model/runtime.

No additional diagnostic using the current A/B protocol is authorized by this branch. Repeating, reversing, or elaborating the rule would either duplicate established copying evidence, add an equally material mapping/selector abstraction, or change the measurement channel without first designing a new construct-valid strategy.

## MN-006-level dispositions considered

| Option | Assessment | Decision |
| --- | --- | --- |
| `close_fixed_label_branch_redirect_mn006` | Closes the non-identifying response-selection branch while preserving MN-006's candidate-neutral distributed-state question and static workload authority. Requires a new measurement-interface design before any later model test. | **Selected.** |
| `close_mn006_inconclusive_measurement_blocked` | Would close the entire milestone because its current measurement chain is construct-blocked. | Rejected now: the blocked interface does not falsify or exhaust the original distributed-state question, and retaining the milestone allows a separately justified construct-valid redesign without rewriting evidence. |
| `close_mn006_with_negative_scientific_result` | Would treat no observed locality signal as evidence against the distributed-state hypothesis. | Rejected: lower-level response selection prevents attribution, so the intended construct was not measured. |
| `retain_mn006_without_redirect` | Would continue the current v1 A/B measurement chain later. | Rejected: it contradicts the behavioral-identifiability boundary and would not create new construct-valid locality evidence. |

## Redirected MN-006 status

MN-006 is now **measurement-interface redirected**. The frozen semantic workload, generator, oracle, validators, inventory, baseline records, and diagnostic records remain research assets and historical evidence. They do not, by themselves, authorize another model request or a treatment comparison.

Before model testing can resume within MN-006, a separate static research-design decision must specify a measurement approach that, at minimum:

1. makes distributed-state/locality the target construct rather than an unverified downstream capability;
2. does not use arbitrary conditioned A/B label mapping as the sole observable of state integration;
3. retains exact, machine-verifiable scoring and a clear public/evaluator/authority boundary;
4. provides a pre-model check that response-channel competence is not the bottleneck for the intended task-bearing output;
5. does not introduce a stronger reasoning requirement than the state-integration construct it aims to test;
6. supports a matched locality comparison with causal interpretation; and
7. remains bounded enough for qualified small-model evaluation and retained raw evidence.

These are conceptual requirements, not a new output vocabulary, prompt, benchmark, intervention, or implementation plan.

## D2 and locality

D2 remains historically defined but permanently unauthorized under the current v1 response protocol: its independent D1 prerequisite, `mapping_following_supported`, did not occur. It is not to be executed, repaired, or repurposed.

Locality is **unmeasured**, not failed and not supported. The canonical records establish no usable locality-sensitive state-integration failure signal because the measurement chain did not achieve construct-valid access to locality.

The perfect-state diagnostic remains unauthorized. `attempt-0003` remains prohibited.

## Reasoning and intervention implications

The equality rule was intended as a minimal adapter, not as MN-006's research subject. The evidence teaches a methodological constraint: even a bounded conditional transformation cannot be presumed neutral merely because it is deterministic and exactly scored. A future interface must separately demonstrate that its response/rule layer does not mask the target state-integration variable. This does not show that reasoning should be removed from MN-006, that the model cannot reason generally, or that reasoning-oriented evaluation should be abandoned.

The fixed-label confound supplies no rationale to select Hierarchical State Representation, External State Management, Event-to-State Normalization, Multi-pass Reconstruction, Symmetric Partitioning, or any other intervention. It is a measurement-interface blocker, not evidence for a state-representation mechanism. All interventions remain unselected and unauthorized.

## Methodological lessons frozen for MN-006

- Protocol-valid execution does not by itself establish construct-valid measurement.
- An arbitrary finite label mapping can become a lower-level capability bottleneck even when labels are balanced and parsing is exact.
- Explicit label copying is not evidence that a model can select that label after task-bearing processing.
- A diagnostic ladder should stop once further decomposition becomes behaviorally non-identifiable rather than accumulating confounded prompt variants.
- Failures below the target construct prevent attribution to higher-level state, locality, or intervention mechanisms.

## Future authorization boundary

The only future MN-006 work permitted by this decision is a separately authorized **static measurement-interface redesign decision**. If such work is approved, it must proceed through:

```text
static research design
        ↓
static construct-validity gate
        ↓
static executor boundary
        ↓
separately authorized clean-environment measurement
```

No model experiment, candidate intervention, locality measurement, D2 execution, perfect-state diagnostic, authority plan, executor, or run directory is authorized by this decision.