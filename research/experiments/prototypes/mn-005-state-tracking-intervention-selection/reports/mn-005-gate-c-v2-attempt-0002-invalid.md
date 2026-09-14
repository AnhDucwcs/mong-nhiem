# MN-005 Gate C v2 attempt-0002 — invalid-attempt report

> **Superseded as the scientific interpretation.** This report retains the original post-run classifier crash and the initially incorrect invalid-attempt interpretation. The completion audit established that all required model execution, evaluation, and provenance were already complete; the defect affected only deterministic aggregation of paired wrapper objects. The canonical result is now documented in [MN-005 Gate C v2 attempt-0002](mn-005-gate-c-v2-attempt-0002.md). Raw attempt evidence and this historical report are retained unchanged apart from this supersession notice.

**Attempt:** `attempt-0002`
**Gate C v2 status:** `gate_c_v2_experiment_invalid`
**Efficacy status:** `not_applicable_due_to_invalid_experiment`

## Scope and authority

This report records the canonical prospective execution under frozen MN-005 Gate A and Gate B v2. It does not modify or reinterpret those contracts. The implementation checkpoint was `2143060443d504dc1ca1af6fd08283996ae8e765`; Gate B v2 authority was `3e13c003ed54fb64e8bff34181e9ab3953137a87`.

The retained static preflight, frozen Llama 3.2 3B model artifact, pinned llama.cpp runtime, six ECC-006 8k cases, deterministic sampling settings, and three-arm schedule were used. The environment was clean before the attempt; no attempt was rerun or replaced.

## Execution validity

All six Arm A calls and all twelve B/C paired calls returned and were retained: 18 scored-output records, 30 response payloads, Stage A artifacts, server logs, request metadata, token accounting, and evaluator records.

After the final response, the runner crashed in its post-run classification path. It passed paired dictionaries to a classifier that expects flattened records, raising a `KeyError` before it could generate a canonical classification summary. This is an implementation/infrastructure failure under the frozen validity boundary. The attempt is therefore permanently `experiment_invalid`.

The failure occurred after model calls, but before contract-valid efficacy analysis. Retained raw outcomes cannot be promoted to a primary result by reimplementing or correcting the classifier after the fact. No `attempt-0003` was started.

## Arm outcomes — descriptive only

| Case | Arm A | Arm B | Arm C | Arm C exact reconstruction |
|---|---:|---:|---:|---:|
| ecc006-001 | wrong | wrong | wrong | no |
| ecc006-002 | wrong | wrong | wrong | no |
| ecc006-003 | wrong | wrong | wrong | no |
| ecc006-004 | wrong | wrong | wrong | no |
| ecc006-005 | wrong | wrong | wrong | no |
| ecc006-006 | wrong | wrong | correct | no |

These retained values are descriptive audit data only. They must not be used to calculate or claim `n10`, `n01`, `D`, Arm accuracies, mechanism support, or system-level efficacy because the canonical attempt is invalid.

## Mechanism diagnostics — descriptive only

All six Arm C Stage A artifacts contained four emitted lines, but none met the frozen exact reconstruction condition and none was format-valid under the required target-row grammar. No prohibited-field emission was recorded. The one retained correct Arm C final answer did not have an exact Stage A reconstruction.

This does not establish whether reconstruction staging helps or fails. The frozen protocol requires a valid canonical attempt and the predeclared classification path before such interpretation is permissible.

## Resource evidence

Per-call prompt/completion tokens, finish reasons, latencies, server lifecycle logs, and B/C literal-transport records are retained in the attempt directory. They are audit evidence only, not an efficacy comparison. No resource observation changes the invalid classification.

## Permitted and prohibited conclusions

Permitted:

- `attempt-0002` completed model calls but failed the frozen post-run implementation path.
- The attempt supplies no valid MN-005 efficacy evidence.
- The classifier integration defect must be addressed through a new documented contract/implementation decision before any future prospective attempt.

Prohibited:

- claiming Multi-pass Reconstruction is supported, unsupported, or inconclusive;
- claiming an Arm C versus Arm B causal effect;
- treating retained outcomes as a substitute for a canonical result;
- generalizing to long-context reasoning, other models, external memory, or production architecture.

## Evidence

- Attempt manifest and summary: `runs/attempt-0002/`
- Raw request/response and server lifecycle evidence: `runs/attempt-0002/raw/`
- Literal Stage A artifacts: `runs/attempt-0002/artifacts/`
- Static preflight authority: `preflight/preflight-v2.json`

## Next state

MN-005 efficacy remains unresolved. The first-valid-attempt policy means this invalid attempt cannot be discarded. Any future execution requires an explicit documented repair/authority step; it must not be started automatically.