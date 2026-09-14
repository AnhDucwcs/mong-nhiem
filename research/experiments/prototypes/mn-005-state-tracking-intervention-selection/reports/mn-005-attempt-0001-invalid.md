# MN-005 Gate C attempt-0001 — invalid experiment record

## Status

`attempt-0001` is permanently retained as `experiment_invalid`. Its efficacy classification is `not_applicable_due_to_invalid_experiment`; it supplies no Arm B/C denominator, paired count, support result, or conclusion about Multi-pass Reconstruction.

## Preconditions and completed work

The committed implementation checkpoint was `cf50ac56e03d4e923d983cb4786cc3f48522d22f`. The tokenizer-only preflight passed for the six frozen ECC-006 8k cases with the frozen model SHA, llama.cpp `0.2.0-dev` build `10566` commit `bb4caa754`, context `16896`, temperature `0`, and seed `42`. The immediate execution environment was clean: RTX 3050 Laptop GPU, driver `595.95`, zero compute processes, zero reported MiB in use.

Arm A completed first in canonical case order and reproduced `0/6`; its six exact outputs and request evidence are retained in `runs/attempt-0001/results.jsonl`. This observation cannot yield an efficacy conclusion because the paired comparison did not complete.

## First invalidating condition

On `ecc006-001` Arm B Stage A, the model reached the frozen `max_tokens=64` limit while emitting the fixed neutral placeholder. The literal retained artifact ends during the fourth row:

```text
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU
```

The runner transported that literal artifact into the prepared Stage B prompt, then marked the attempt protocol-invalid because it did not equal Gate B's frozen four-row grammar. The retained server log records 64 predicted Stage A tokens and an output-limit termination. Altering the grammar or increasing `max_tokens` would change Gate B; neither is permitted during Gate C. No B/C continuation or retry occurred.

## Evidence and limitation

The attempt retains metadata, six Arm A records, the truncated raw Stage A artifact, and Arm A/B server logs under `runs/attempt-0001/`. A post-run audit records that the invalidating B Stage B raw response was not serialized before the runner raised its protocol exception; this retention defect is itself part of the invalid attempt and must not be repaired by recreating a request or output.

## Consequence

The frozen Gate B active-control grammar/output-budget combination is not executable as specified for this subject/runtime. A new efficacy attempt would require an explicit new research decision reopening Gate B; Gate C must not tune or substitute the control.
