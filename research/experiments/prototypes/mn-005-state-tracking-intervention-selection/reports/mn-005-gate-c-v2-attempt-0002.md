# MN-005 Gate C v2 attempt-0002 — canonical result

**Attempt:** `attempt-0002`
**Gate C v2 status:** `gate_c_v2_completed`
**Efficacy status:** `inconclusive`

## Authority and validity

Gate A is frozen; Gate B v1 remains historical; and Gate B v2 is frozen at `3e13c003ed54fb64e8bff34181e9ab3953137a87`. The execution implementation checkpoint was `2143060443d504dc1ca1af6fd08283996ae8e765`. `attempt-0001` remains permanently `experiment_invalid`.

All required execution completed for `attempt-0002`: six Arm A records, six Arm B records, six Arm C records, and 30 retained request/response payloads. Every scored record has `protocol_valid: true` and `infrastructure_status: complete`; all reached B/C Stage B requests retain literal-transport provenance. The raw responses, evaluator results, Stage A diagnostics, token accounting, and server evidence are retained under the attempt directory.

The original runner raised a `KeyError` only after the final model response, while it was aggregating paired B/C wrapper dictionaries as though each wrapper were a scored record. The repaired offline classifier traverses the nested B and C records. It was tested with synthetic supported, unsupported, insufficient-positive, dirty-reconstruction, baseline-drift, invalid, and real pair-wrapper cases before processing retained evidence. The repair used no model request and changed no raw response, evaluator output, diagnostic, provenance record, or frozen threshold.

Therefore `attempt-0002` is the first fully protocol-valid and infrastructure-complete attempt. Under the frozen first-valid-attempt rule, it is the canonical efficacy attempt and may not be replaced because of its outcome.

## Exact outcomes

| Case | A | B | C | C exact reconstruction |
| --- | ---: | ---: | ---: | --- |
| ecc006-001 | 0 | 0 | 0 | no |
| ecc006-002 | 0 | 0 | 0 | no |
| ecc006-003 | 0 | 0 | 0 | no |
| ecc006-004 | 0 | 0 | 0 | no |
| ecc006-005 | 0 | 0 | 0 | no |
| ecc006-006 | 0 | 0 | 1 | no |

Arm A was `0/6`; Arm B was `0/6`; Arm C was `1/6`. The frozen paired quantities are `n10 = 1`, `n01 = 0`, and `D = +1`.

## Frozen classification

The frozen result is **`inconclusive`**. Arm A reproduced the required `0/6` compatibility baseline, but Arm C did not reach `4/6`, `n10` did not reach 4, and the only B-to-C beneficial flip did not have a clean exact four-row reconstruction. The support rule is consequently not met. The result is not `unsupported`, because the frozen unsupported condition requires `D <= 0`.

## Stage A mechanism diagnostics

None of the six Arm C artifacts met the frozen exact-reconstruction criterion. The one correct Arm C final answer, on `ecc006-006`, occurred without a clean exact reconstruction artifact. This attempt therefore provides no mechanism evidence satisfying the predeclared requirement for support. It does not establish that reconstruction staging is harmful or that multi-pass methods generally fail.

## Resource evidence

Resource accounting is descriptive. Across six cases, Arm A Stage B used 49,009 prompt tokens, 19 completion tokens, and 39,644.333 ms recorded latency. Arm B used 49,735/432 Stage A prompt/completion tokens and 49,525/17 Stage B prompt/completion tokens, with 77,983.889 ms and 39,415.072 ms recorded stage latencies. Arm C used 49,489/262 Stage A prompt/completion tokens and 49,355/19 Stage B prompt/completion tokens, with 60,264.589 ms and 39,529.105 ms recorded stage latencies. These observed differences do not change the frozen efficacy classification.

## Bounded conclusion and non-claims

On the frozen Llama 3.2 3B ECC-006 8k workload, the measured Multi-pass Reconstruction treatment produced only a `+1/6` paired improvement over the matched active control, and the sole beneficial flip lacked the required exact reconstruction artifact. Under the predeclared Gate B v2 rule, the result is inconclusive.

This result does not support a general long-context solution, cross-model effectiveness, compute-independent benefit, external-memory effectiveness, architecture promotion, production readiness, or general mutable-state reliability.

## Canonicalization and retained history

The prior [invalid-attempt report](mn-005-gate-c-v2-attempt-0002-invalid.md) is retained with a supersession notice, along with the original traceback and all raw attempt evidence. No evidence has been deleted or rewritten. `attempt-0003` is not authorized; any future execution requires separately authorized replication or a new research contract.

## Evidence

- Canonical summary and records: `runs/attempt-0002/`
- Raw request/response and server lifecycle evidence: `runs/attempt-0002/raw/`
- Literal Stage A artifacts: `runs/attempt-0002/artifacts/`
- Static preflight authority: `preflight/preflight-v2.json`