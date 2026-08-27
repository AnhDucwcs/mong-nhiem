# Research methodology

Keep four things distinct: hypotheses (proposed explanations), experiment definitions (question, setup, controls, and success criteria), evidence (measured artefacts), and conclusions (bounded interpretations linked to evidence).

Experiments belong in `research/experiments/baselines/` or `research/experiments/prototypes/`. Baselines establish comparison/reference points; prototypes test scoped hypotheses or approaches. MN-002 is a completed, frozen baseline experiment. MN-003 is the active prototype and begins with a measurement baseline: define the hypothesis, unmodified-context baseline, controlled variables, metrics, and success criteria, then measure degradation before testing an architecture intervention. Measured evidence must not be replaced by assumptions, and experimental code does not become reusable package code without an explicit decision.
