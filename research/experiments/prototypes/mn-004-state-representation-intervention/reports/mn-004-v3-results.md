# MN-004 v3 — retained infrastructure-stop outcome

## Authority and v3 correction

V3 is governed by [Gate B v3](../gate-b-v3-measurement-contract.md), definition fingerprint `6ba424ed7fc208d18aab1be3d03f03974b449b0329b59f82cc96faf4d7ab44a2`, and immutable v1 inventory fingerprint `7183de0be8813764087e77330c5758970d40dfc9fe8553637faccca027d17897`.

V1 remains `contract_not_executable`; v2 remains `invalid_comparison` and was not rescored. V3 changes only the treatment of a correctly executed `finish_reason: length`: it is a valid zero-scored `output_token_limit_reached`, not protocol invalidation.

## Completed valid phases

| Phase | Run ID | Result | Protocol / infrastructure |
| --- | --- | --- | --- |
| Llama frozen 8k reproduction | `v3-20260905T145026Z-llama_8k_reproduction-0aee1b22` | `0/6` | six valid rows; compatible |
| Llama untreated 2k + 8k | `v3-20260905T145251Z-llama_untreated-7236df15` | 2k `3/24`; 8k `0/24` | all 48 rows valid and infrastructure-complete |

The untreated condition retained 42 `incorrect_state`, 2 `malformed_response`, and 1 valid zero-scored `output_token_limit_reached`. The output-limit row did not invalidate the condition, as frozen by v3. There were no protocol-invalid or infrastructure-failed untreated rows.

## Llama ledger infrastructure stop

The matched ledger phase began under the pinned model/runtime and source inventory:

- run: `v3-20260905T145904Z-llama_ledger-d5f0d615`;
- expected / observed records: `48/48`;
- observed provisional pass counts: 2k `2/24`, 8k `0/24`;
- infrastructure failures: `23` rows — 22 connection-refused errors and one connection-reset error;
- valid model-output rows in the attempt: 7 `incorrect_state`, 13 `malformed_response`, and 3 `output_token_limit_reached`.

The frozen v3 canonical policy says that any infrastructure failure during a required phase stops execution. Therefore this ledger phase is not a valid paired scientific condition. The provisional pass counts and failure classes are retained diagnostics only; they are not Llama efficacy or reference-no-harm evidence.

## Mechanical outcome

Final v3 outcome: **`infrastructure_failure`**.

- Llama 8k efficacy thresholds (`ledger >= 12/24`, `delta >= +8/24`): not evaluable.
- Llama 2k reference no-harm: not evaluable.
- Qwen eligibility and no-harm: not run; Qwen was not authorized after an incomplete Llama ledger phase.

No row was selectively retried, no token allowance was changed, and no source case, renderer, threshold, model, runtime, or evaluator was modified after execution began.

## Claim boundary and state

V3 demonstrates only that the taxonomy correction allowed a valid output-limit termination to remain in the untreated denominator. It does not support or refute ledger efficacy, establish no-harm, show Qwen behavior, improve 16k performance, establish token-independent representation causality, generalize to models, or justify Gate D promotion.

V3 is closed at `infrastructure_failure`. Any future work requires a separately versioned design; this run must remain retained unchanged.
