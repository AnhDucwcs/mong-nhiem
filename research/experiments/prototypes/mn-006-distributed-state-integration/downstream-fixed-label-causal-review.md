# MN-006 downstream fixed-label causal review

## Status

**`behavioral_boundary_reached_l1c_l1d_not_cleanly_identifiable`.** This is a static review of immutable canonical evidence. It creates no authority plan, executor, run directory, model request, locality measurement, perfect-state control, or intervention.

The immediate question is whether the direct conditional-rule operations still jointly present in the explicit-relation control can be split one further without either revealing the final label or introducing an equally material new mapping abstraction.

## Immutable evidence basis

| Evidence | Exact observed behavior | What it establishes |
| --- | --- | --- |
| [S0](reports/mn-006-output-selection-s0-run-0001.md) | `A, B, B, A` for explicit target labels under both `G_AB` and `G_BA` | The qualified model/runtime can emit and copy both surface labels through the constrained channel. |
| [explicit-relation direct-rule control](reports/mn-006-explicit-relation-direct-rule-run-0001.md) | explicit `different` -> `A` (expected `B`); explicit `equal` -> `A` (expected `A`) | Structured-state extraction and equality comparison are not necessary for the recurring fixed-`A` behavior. |
| [S1](reports/mn-006-output-selection-s1-run-0001.md) | `A` for all four structured-state direct-rule requests | The same behavior recurs when state extraction and equality comparison are also required. |
| [D1](reports/mn-006-label-selection-d1-run-0001.md) | `A` for all 16 counterbalanced mapping-table requests; zero `G_AB`/`G_BA` disagreements | The behavior persists across both mapping directions and grammar orders in the higher-level direct-state diagnostic. |

The minimality authority plan remains SHA-256 `8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827`; the explicit-relation authority plan remains SHA-256 `dc40c15a896f5f0413783818c39593b8a9c34eeea3ef4ce284e1b311112bc80a`. This review neither changes nor rescores either plan or any retained record.

## Updated causal boundary

The evidence supports the following boundary:

```text
L0    explicit surface-label availability/copying
      supported by S0

L1a   structured-state extraction
      not necessary for the observed fixed-A behavior

L1b   equality/difference computation
      not necessary for the observed fixed-A behavior

L1c   conditional-rule interpretation/application
      unresolved

L1d   constrained label selection after task-bearing processing
      unresolved
```

The explicit-relation prompt still comprises four linked operations:

```text
L1c1  read and represent `Relation: equal` or `Relation: different`
L1c2  match that value to the corresponding conditional branch
L1c3  recover the A/B label attached to the selected branch
L1d   select and emit that label through the grammar-constrained response channel
```

`L1c1` and `L1c2` can be treated as condition/branch matching; `L1c3` and `L1d` are distinct conceptually, but not independently observable under this interface. If the attached output label is kept hidden until the branch is selected, the task necessarily retains branch-to-label application. If the label is supplied explicitly, the task reduces to S0-style copying.

This is the important distinction:

```text
S0: explicit final label -> copy it
```

versus:

```text
explicit-relation: task-bearing condition -> branch -> attached label -> constrained output
```

S0 establishes only availability/copying of the literal surface label. It does not establish that the model conditions output on an intermediate task result.

## Viable hypotheses and evidential limits

| Hypothesis | Compatible evidence | Evidence against or weakened by canonical records | Minimum discriminating observation | Remaining entanglement |
| --- | --- | --- | --- | --- |
| `conditional_branch_matching_failure` | The explicit relation may not be matched to the intended `if` branch. | S0 proves neither label is mechanically unavailable. | Hold a branch selector explicit while retaining distinct attached labels. | The resulting task still requires branch-to-label application and constrained selection. |
| `branch_to_label_application_failure` | The relevant branch may be available internally but its attached label may not be recovered or applied. | No retained result directly observes a correct branch before label selection. | Observe an independently verifiable selected branch while withholding the label. | Withholding the label necessarily leaves the branch-to-label step under test. |
| `post_task_fixed_label_default` | `A` recurs whenever the label must follow task-bearing input; S0 produces B only when B is explicit. | It is behavioral evidence, not an identified internal default or logit mechanism. | A task-bearing condition whose only remaining operation is output selection. | Such a condition exposes the final label and collapses to S0, or retains an intermediate mapping. |
| `specific_rule_wording_or_semantic_relation_confound` | The relation prompt uses the loaded terms `equal`/`different` and two conditional sentences. | S1 and D1 also fail under different surrounding representations, so a single wording-only explanation is not established. | A new wording/interface control. | It would be a prompt-vocabulary experiment, not a clean L1c/L1d separation. |
| `surface_A_prior` | All task-bearing A/B diagnostics selected A, including B-required cells. | S0 emitted B under both grammar orders. | Lower-level rule-direction counterbalance in the direct relation interface. | It would distinguish surface behavior from one forward rule, but still not separate rule application from post-task selection. |
| `grammar_or_first_alternative_explanation` | The explicit-relation and S1 controls use `G_AB`. | S0 emitted B once under each grammar order; D1 was A for both orders with no paired disagreement. | A new grammar-order test in this exact prompt. | Existing evidence strongly weakens alternative-order mechanics, but cannot identify filtered token mass, logits, or every prompt-specific interaction. |
| `general_conditional_instruction_failure` | The recurring result may be caused by the exact model/interface failing to condition on arbitrary conditional instructions. | No canonical task has isolated this from label selection after an intermediate result. | An arbitrary selector-rule control. | It changes semantic vocabulary and still combines condition matching, rule application, and output selection. |

No row above licenses a claim about tokenizer defects, grammar defects, logits, an internal architecture, or general reasoning ability.

## Candidate diagnostic landscape

| Candidate | Removes from explicit-relation control | Retains | New confound / duplication | Minimum new requests | Causal decision |
| --- | --- | --- | --- | --- | --- |
| Explicit branch-selector -> label | Semantic relation wording and relation-to-branch matching (`L1c1`/part of `L1c2`) | selected-branch interpretation, branch-to-label application (`L1c3`), and `L1d` | Ordinal or named-branch abstraction; a new mapping-like layer | At least two selectors | Does not split `L1c3` from `L1d`; a failure remains non-identifying. |
| Arbitrary binary selector rule (`X`/`Y`) | Equality semantics | conditional matching, branch-to-label application, `L1d` | New selector vocabulary and its learned semantics | At least two balanced selectors | Could test a broader conditional interface, but changes the question rather than creating the needed adjacent cut. |
| Explicit selected-output branch | Branch matching if the applicable branch is named | label recovery and output selection | If the rule says branch 2 outputs B, it adds a mapping/ordinal abstraction; if it says output B directly, it becomes S0 | Two branch cases | Either it recreates D1-like mapping work or collapses into copying. |
| Direct intermediate-label copying | All task-bearing transformation | only literal A/B emission | Semantically equivalent to S0 with an extra wrapper | Two labels | Duplicates S0; adds no information about conditioned selection. |
| Reversed direct rule | Nothing; reverses the label assignment | relation, conditional matching, label application, `L1d` | Reintroduces a mapping direction factor | A new balanced forward/reverse set, not a single complementary request | Can probe surface/rule-direction behavior, but cannot separate `L1c` from `L1d`. It is not the smallest useful decomposition now. |
| Semantic outputs (`EQUAL`/`DIFFERENT`) | Arbitrary A/B mapping | relation recognition and a new output selection | Changes grammar, vocabulary, tokenization, and semantic priors | At least both relation values | Not comparable to the established A/B response channel. |

### Reversed-rule and prior-evidence analysis

D1 meaningfully counterbalanced equal/unequal labels and grammar order: B-required mapping-table cells still returned A. That weakens a claim that the observed behavior follows the declared mapping direction or grammar alternative order. It does **not** tell us whether the lower-level explicit-relation wording would follow a reversed direct rule, because D1 also retained state comparison and mapping-table parsing.

Nonetheless, a reversed direct rule is not a clean solution to the remaining L1c/L1d problem. It leaves all of `L1c1`–`L1c3` and `L1d` intact while adding a rule-direction factor. A future forward/reverse comparison would need a separately frozen, self-contained run: the existing forward two-request run cannot serve as its prospective counterpart without mixing run boundaries, request order, runtime date/template context, and independently recorded evidence. Reusing historical forward evidence would make the desired comparison non-paired and weaker precisely where the new factor is meant to be causal.

Thus a reversed-rule study could answer a different, broader surface-label/rule-direction question. It would not behaviorally identify whether this interface fails to apply the selected branch's label (`L1c3`) or instead defaults during constrained output selection after task processing (`L1d`). It is not authorized by this review.

## Behavioral identifiability limit

`L1d` cannot be isolated behaviorally here without revealing the target label. Once the prompt explicitly gives the model `B` as the final required result, the observation is direct copying and is already covered by S0. If the prompt withholds that final label, it must provide or require an intermediate condition, branch, rule, or mapping. The model must then turn that intermediate representation into an A/B label, which is exactly an `L1c3`-type operation entangled with `L1d`.

Naming an intermediate as a branch, selector, or rule result does not remove this problem. It either adds a new mapping abstraction of comparable size to the one removed, or explicitly tells the model the label and duplicates S0. Therefore the current interface supports a behavioral boundary—not an internal-mechanism diagnosis—between explicit copying and conditioned answer selection.

## Disposition

**`behavioral_boundary_reached_l1c_l1d_not_cleanly_identifiable`.** No next diagnostic is identified by this review.

The available evidence is sufficient to establish that, under the frozen model/runtime/interface, explicit A/B copying works while selecting A/B after the tested task-bearing relation/rule input does not reliably condition on the B-requiring condition. It is not sufficient to cleanly attribute that behavior to conditional-branch matching, branch-to-label application, or post-task constrained-label selection. A further minimal test would either duplicate S0, reintroduce a material mapping/selector abstraction, or switch the output channel.

## Exact current scientific and authorization boundary

The evidence supports:

- explicit A/B label copying under S0;
- fixed A after a relation is explicitly supplied under the fixed direct rule; and
- the fact that structured-state extraction and equality comparison are not necessary conditions for the recurring fixed-A behavior in this exact protocol.

The evidence does not support:

- a specific internal mechanism, grammar defect, token/logit defect, or general reasoning failure;
- state-reconstruction or distributed-state integration failure;
- any locality effect or perfect-state eligibility;
- candidate-intervention need, selection, or efficacy.

D2 remains blocked by its independent D1 `mapping_following_supported` prerequisite. Locality remains unmeasured. The perfect-state diagnostic, `attempt-0003`, source-event reconstruction, and all interventions remain unauthorized. S0, S1, D1, attempts 0001/0002, and MN-003/MN-004/MN-005 frozen evidence remain immutable.

The next permitted action is a separately authorized decision about how to close or redirect this diagnostic branch; no new model diagnostic, plan, executor, or intervention is authorized by this review.