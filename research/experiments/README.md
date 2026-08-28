# Research experiments

This tree records reproducible research evidence and remains separate from `src/mong_nhiem/`.

- `baselines/` establishes comparison/reference evidence; the completed, frozen baseline is [MN-002 model qualification](baselines/mn-002-model-qualification/README.md).
- `prototypes/` holds exploratory research used to test new hypotheses or approaches; [MN-003 Effective Context Capacity](prototypes/mn-003-effective-context-capacity/README.md) has completed its bounded direct-context measurement and synthesis phase, beginning with [ECC-001 Context Retrieval](prototypes/mn-003-effective-context-capacity/experiments/ecc-001-context-retrieval/README.md).
- The next prepared prototype is [MN-004 State Representation Intervention Design](prototypes/mn-004-state-representation-intervention/README.md). It has a charter only: no intervention, experiment definition, code, or evidence exists yet.

Each experiment documents its question, scope/non-goals, setup, environment/runtime, inputs/configuration, evaluation, evidence, limitations, and conclusions. A prototype must establish its hypothesis, baseline, variables, metrics, and success criteria before testing an architecture intervention. Keep immutable definitions, selected-run metadata/results, validation outputs, and reports; retain raw diagnostics according to the experiment's retention policy. Promote code into the reusable package only after evidence and an explicit decision.
