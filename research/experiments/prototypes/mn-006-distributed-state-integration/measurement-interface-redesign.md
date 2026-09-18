# MN-006 measurement-interface redesign

## Decision

**Disposition: `single_measurement_interface_candidate_identified`.** MN-006 retains its original distributed-state/locality construct, but retires the v1 equality-to-finite-label adapter from further model execution. The single recommended future interface is a **direct ordered two-entity final-state vector**: the model reports the final state of each of the two already queried entities in a canonical query order.

This is a static research decision. It creates no authority plan, grammar, prompt bytes, executor, model request, run directory, locality result, or intervention.

## Original construct retained

The intended MN-006 comparison remains:

```text
same source events and per-entity histories
same state vocabulary, query entities, model, runtime, and exact scoring
        ↓
contiguous histories versus matched distributed/interleaved histories
```

The target construct is the model's ability to maintain and recover the latest states of multiple queried entities when their updates are separated by other entities' updates. A locality result still requires the later matched schedule comparison; nothing in this redesign is locality evidence.

The v1 equality rule was an answer-oracle safeguard: a host-maintained state register would not itself be the evaluated answer. It was not the target construct and was never meant to add a reasoning-difficulty axis. The retained diagnostic chain shows that this supposedly small adapter is not neutral for the qualified Llama/runtime: a fixed label recurred even after the relation was supplied directly. The v1 protocol was therefore `protocol_valid` but not construct-valid for the intended locality claim.

## Direct state output is permitted for measurement

Making the final observable identical to the maintained semantic state is **not scientifically necessary** for measuring the baseline distributed-state/locality construct. It was desirable only for future anti-oracle intervention comparisons. Keeping that constraint in the untreated measurement path added a construct-irrelevant conditional-selection burden that blocked access to the target state variable.

The future direct-state interface would make the target explicit: the answer is the ordered vector of the two queried entities' final `STATE` values. It intentionally measures state replay/recovery, not equality reasoning. This does not make a host-maintained register acceptable as an intervention: for any later external-state treatment, a direct-state endpoint would again be answer-adjacent and would require a separate treatment-specific anti-oracle decision. No treatment is selected here.

## Replacement-interface requirements

Any future interface must:

- preserve deterministic source events, paired schedules, state semantics, query identity, oracle provenance, and exact machine scoring;
- make recovery of queried final state(s), rather than an unqualified answer adapter, the task-bearing observable;
- have a response channel that is independently qualified **in the same observable form** before locality is assessed;
- not treat explicit copying alone as sufficient qualification;
- hold the response interface fixed across a later contiguous/interleaved comparison;
- remain feasible for the qualified Llama 3.2 3B runtime; and
- keep qualification distinct from locality measurement and from intervention evaluation.

## Candidate landscape

| Candidate | Construct alignment and response burden | Qualification and confounds | Decision |
| --- | --- | --- | --- |
| **A. Direct single-entity state token** | Directly measures one entity's latest-state recovery; response burden is one semantic state token. | Explicit state-token copying can qualify emission, but a task-bearing contiguous endpoint is still required. It loses the original two-query, multi-entity integration requirement and is vulnerable to being interpreted only as per-entity last-update retrieval. | Rejected as the primary MN-006 interface. It is a useful component-level calibration, not a sufficient replacement for the multi-entity construct. |
| **B. Direct ordered two-entity final-state vector** | Reports both queried final states in the declared query order. It removes equality and arbitrary label selection while retaining the intended multi-entity state-recovery burden. | The exact finite vector serialization must be qualified, including order and repeated state values; task-bearing contiguous endpoints must also work before a locality comparison. It can still be solved by replaying/retrieving each entity's last assignment, but that is the operational state-recovery behavior MN-006 is designed to stress by changing schedule locality. | **Selected.** It is the smallest observable that keeps both queried entity histories while removing the known invalid adapter. |
| **C. Direct semantic relation (`EQUAL`/`DIFFERENT`)** | Retains equality computation after recovering two states. | Replaces A/B with another vocabulary, grammar, tokenization, semantic-prior, and response-selection layer. The explicit-relation diagnostic already shows a direct conditional transformation is not neutral. | Rejected. It is more indirect than state output and retains a non-intrinsic reasoning burden. |
| **D. Direct state token plus a minimal transformation** | Could preserve a non-identical answer only by deriving another value from the state. | Any non-identity transformation reintroduces an independently unqualified rule/selection step; an identity transformation is simply direct state output. | Rejected. No weaker useful transformation is identified. |

No additional interface is included. Canonical structured data formats such as JSON would only add serialization syntax, and independently queried single-state prompts are calibration tools rather than a qualitatively different multi-entity measurement interface.

## Selected interface: direct ordered two-entity state vector

The future public task should ask for the final `STATE` values of the two existing query entities, in their already declared query order, using a finite canonical state-vector representation. The precise wording, grammar, whitespace policy, parser, authority records, and order are deliberately **not frozen here**. They require a later construct-validity gate.

The future oracle may reuse the v1 replay layer unchanged and read the two existing canonical query-state values directly. It must not use v1's `derive(equal_state)` or `decide(VALID/INVALID)` layers for the new primary observable. The original semantic histories, state model, scheduler, paired relation, generator seeds, and inventory provenance are retained assets. The v1 public prompt bytes, v1 answer vocabulary, v1 parser/evaluator, and v1 locality scores are historical assets, not a future state-vector authority.

### Why a vector rather than one state

One queried entity is enough to demonstrate per-entity state recovery, but it does not retain the original question's multi-entity integration requirement. A two-position ordered vector forces recovery of both query trajectories while avoiding the equality comparison and arbitrary answer mapping that made v1 non-diagnostic. The vector's order must be declared by the query, not inferred from entity identifier sorting after generation.

### Retrieval and copying limits

Direct state output can be affected by token copying or by locating an entity's latest assignment instead of materializing a richer internal register. Neither possibility invalidates the operational construct: MN-006's direct-assignment workload defines state recovery as retaining/recovering each query entity's latest valid update in global context. It does, however, bound the claim. A qualified direct-state measurement would not establish general multi-step reasoning, hidden-state representations, or a mechanism beyond the exact state-recovery task.

Explicit vector copying only tests response availability. Following the S0 lesson, it cannot by itself establish task-derived vector selection. A task-bearing contiguous endpoint qualification is therefore required before schedule locality is interpreted.

## Minimum qualification before locality

The recommended interface has one finite state-vector response space: three state values in each of two ordered positions. A later gate should freeze, at minimum, these coverage classes under the exact future parser and grammar:

| Qualification layer | Minimum coverage | Purpose | Not evidence of |
| --- | ---: | --- | --- |
| Exact-vector copying | All 9 ordered `STATE × STATE` vectors | Shows that every state token, position, repeated-value form, and canonical serialization can be emitted when explicit. | Task-derived state selection or locality. |
| Task-bearing contiguous endpoint | All 9 ordered final-state vectors from deterministic two-query histories | Shows that the exact response observable can follow state-bearing input on the non-locality control. | An interleaving effect or a locality failure. |

This gives a minimum **18-request qualification battery for one interface**, not a locality experiment and not a new authority plan. It is exhaustive over the finite output vector space rather than chosen for expected accuracy. Every request should be independent, use the same qualified model/runtime, and be prospectively frozen in one later clean-environment run. Exact output and correctness must be required for every qualification cell; a parser failure, infrastructure failure, or any incorrect cell disqualifies the interface for locality measurement rather than being averaged away.

The later gate must also prove that the task-bearing contiguous cases do not leak final states through fields named `final`, `current`, `answer`, or equivalent authority-only data. It must preserve the v1 event grammar and state provenance. No contiguous/interleaved paired science result is produced during qualification.

If qualification succeeds, a separate static locality gate—not the qualification battery—must freeze a new direct-state vector inventory and the paired contiguous/interleaved analysis. It may reuse v1 semantic cases and scheduling only after proving source-event and query equivalence under the new prompt serializer. If qualification fails, MN-006 becomes `measurement_interface_blocked` for the qualified model/runtime: this redesign does not authorize iterative interface searching, prompt tuning, alternate labels, or adaptive retries.

## Reasoning boundary

Equality is not necessary in the redesigned primary measurement path. It can be studied separately only if a future question makes it intrinsic to the construct or if its response interface is independently qualified as neutral. Direct vector recovery intentionally excludes it so that a failure can be attributed more closely to state recovery/locality rather than a downstream rule.

This does not conclude that the model cannot reason, that reasoning should be removed from all MN-006 work, or that direct state recovery is a complete test of reasoning. It records a methodological constraint: a deterministic rule is not automatically a neutral adapter merely because its depth and arity are small.

## Micro-screening decision

A multi-interface micro-screening battery is **not recommended**. The candidate landscape contains one interface with superior construct alignment and a finite, exhaustively qualifiable response space. Adding a single-state interface would mix a reduced construct with the primary construct; adding semantic relation or transformed answers would reintroduce the exact unqualified downstream burden that v1 retired. That would increase factors without adding a serious alternative measurement strategy.

The 18-request qualification described above is a bounded screen of one response interface, not a competition among interfaces. Its predeclared decision rule is:

```text
all exact vector-copy and task-bearing contiguous cells valid and correct
    -> direct two-entity state-vector interface is qualified for a separate locality gate

any infrastructure, parse, serialization, or task-bearing correctness failure
    -> interface is not qualified; MN-006 is measurement-interface blocked for this model/runtime
```

The rule does not use aggregate accuracy, relative candidate accuracy, or any schedule effect to select an interface.

## Retained and retired v1 assets

| Retained for later static review | Retired from future model execution |
| --- | --- |
| State vocabulary, direct-assignment events, initial state, per-entity histories, deterministic generator/oracle replay, query identities, contiguous/interleaved scheduler, paired case provenance, inventory integrity tools, runtime/evidence discipline, and all measured records | `VALID`/`INVALID` answer adapter, equality-derived answer scoring, A/B fixed-label diagnostics, their response parsers/grammars as locality observables, D2, and every v1 locality score as evidence of the target construct |

The semantic v1 inventory is not silently regenerated or reclassified. A later redesign may reuse its semantic cases only through a new frozen authority that records precisely which semantic artifacts and fields are inherited.

## Authorization boundary

- D2 remains permanently unauthorized under the v1 protocol.
- Locality remains unmeasured; the new interface has not been qualified or measured.
- The perfect-state diagnostic, `attempt-0003`, source-event reconstruction, and all interventions remain unauthorized.
- No model test follows from this document.

The next permitted action is a **separate static construct-validity gate for the direct ordered two-entity state-vector interface**. That gate may freeze the response grammar/parser, task-bearing qualification inventory, exact scoring, and no-leakage checks. Only after a static executor boundary would a separately authorized clean-environment qualification measurement be permitted.
