# MN-004 v5 final efficacy outcome

## Authority

V5 is the final bounded efficacy experiment for the unchanged Gate A globally indexed state-transition ledger. The v5 definition fingerprint is `224c44720bdec08d238dfc7129221a1311a69cebeeea79cf1be43437411a5e0c`; the immutable inventory fingerprint is `7183de0be8813764087e77330c5758970d40dfc9fe8553637faccca027d17897`. The implementation pins the Gate A rendering, v3 validity taxonomy, v4 lifecycle safeguards, frozen artifacts, llama.cpp identity, context `16,896`, and output allowance `16`.

V5 evidence is fresh only. It does not reuse v1--v4 scores or provisional outputs.

| Phase | Run ID | Outcome |
| --- | --- | --- |
| Llama 8k reproduction | `v5-20260905T172625Z-llama_8k_reproduction-9401939f` | valid, compatible `0/6` |
| Llama untreated 2k + 8k | `v5-20260905T173305Z-llama_untreated-1a7b89d4` | valid, 48/48 complete |
| Llama ledger 2k + 8k | `v5-20260905T173832Z-llama_ledger-44b0d0b1` | valid, 48/48 complete |
| Qwen untreated 8k | `v5-20260905T174631Z-qwen_8k_untreated-6594ed44` | valid, 24/24 complete; control not qualified |

## Offline validation and environment

Before inference, v5 authority, immutable selection, semantic-pair equality, and retained token feasibility passed. The offline validator checked 48 authorized rows and 144 model/condition preflight pairs. Relevant MN-004 tests passed `47/47`; scoped Ruff and `git diff --check` passed. Every canonical phase began with no unexpected GPU compute process and used a fresh server. All issued requests completed; no protocol invalidation, CUDA OOM, process loss, timeout, or request failure occurred. Normal runner cleanup terminated each server after its phase.

## Llama reproduction

The six frozen ECC-006 cases at 8k completed with exact `0/6`, all protocol-valid and infrastructure-complete. All six were `incorrect_state` and diagnosed as prior-target-state responses. This satisfies the frozen compatibility rule and authorizes the paired v5 conditions.

## Llama matched results

| Level | Untreated exact passes | Ledger exact passes | Delta | Untreated prompt tokens (min/median/max) | Ledger prompt tokens (min/median/max) | Role |
| --- | ---: | ---: | ---: | --- | --- | --- |
| 2,048 | 4/24 | 2/24 | -2 | 1,998 / 2,015.5 / 2,023 | 2,718 / 2,736 / 2,743 | reference no-harm |
| 8,192 | 0/24 | 7/24 | +7 | 8,136 / 8,169.5 / 8,192 | 11,098 / 11,150.5 / 11,189 | primary efficacy |

The 8k ledger has a retained median prompt-token overhead of `+2,981` and a median first-target token-position shift from 4,040 to 5,522. Median request latency changed from 7,200.955 ms untreated to 10,704.8785 ms ledger at 8k. At 2k, median prompt-token overhead is `+720.5`, first-target position shifts from 984 to 1,346, and median latency changes from 1,552.234 ms to 2,753.008 ms. These are measured consequences of the specified representation package, not evidence that fixed fields act independently of token footprint.

### Primary threshold evaluation

- Valid completed paired 8k comparison: **yes**.
- `L8 >= 12/24`: `7/24` — **no**.
- `L8 - U8 >= +8/24`: `+7/24` — **no**.

The frozen primary efficacy thresholds are therefore not met.

### Llama 2k reference

- `U2 = 4/24`; `L2 = 2/24`.
- Frozen rule: `L2 >= U2 - 2`.
- `2 >= 2` — **pass**.

The reference did not cross the predeclared regression margin. It does not make the 8k threshold miss a supported result.

## Paired and failure diagnostics

At 2k, paired transitions are: wrong untreated to correct ledger `1`; correct untreated to wrong ledger `3`; wrong both `19`; correct both `1`. At 8k: wrong untreated to correct ledger `7`; correct untreated to wrong ledger `0`; wrong both `17`; correct both `0`. These diagnostics do not replace the frozen primary thresholds.

| Condition and level | Correct | Incorrect state | Malformed response | Output token limit reached | Prior-target diagnostics |
| --- | ---: | ---: | ---: | ---: | ---: |
| Llama untreated 2k | 4 | 16 | 3 | 1 | 16 |
| Llama ledger 2k | 2 | 9 | 12 | 1 | 9 |
| Llama untreated 8k | 0 | 24 | 0 | 0 | 24 |
| Llama ledger 8k | 7 | 17 | 0 | 0 | 17 |

Malformed output and output-limit termination were retained as valid zero-score model outcomes. No protocol-invalid or infrastructure-failure row entered a denominator.

## Qwen regression control

Fresh Qwen untreated 8k completed all 24 requests and scored `14/24`. Frozen eligibility requires at least `20/24`; therefore the control outcome is **`control_not_qualified`**. Qwen ledger was prohibited and did not run. This gives neither a Qwen no-harm result nor a Qwen improvement claim.

## Final frozen-rule outcome

The Llama precedence rule yields **`unsupported_no_effect_or_insufficient_effect`**: the valid 2k reference passes, but both 8k support thresholds miss. The Qwen control is separately `control_not_qualified`.

The frozen globally indexed ledger produced an observed 8k pass increase in this matched workload, but it did not meet the predeclared minimum pass count or minimum delta. MN-004 therefore does not support the bounded efficacy hypothesis. This is a valid negative result for this exact representation, inventory, runtime, and threshold contract.

No conclusion is supported about 16k, a general long-context solution, token-independent fixed-field causality, effective-context mechanisms in general, model-general improvement, Qwen improvement, architecture promotion, or production readiness. V1--v4 remain visible historical outcomes. V5 closes MN-004 for this frozen Gate A intervention; no v6, retry, threshold change, renderer change, case replacement, or runtime adjustment is authorized automatically.