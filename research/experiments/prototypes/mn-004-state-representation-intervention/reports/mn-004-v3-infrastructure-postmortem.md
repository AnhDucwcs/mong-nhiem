# MN-004 v3 infrastructure postmortem

## Scope

This is a retained-evidence-only diagnosis of the failed v3 ledger phase. No model request was repeated, no source/evaluator/runtime setting was changed, and no provisional ledger output is treated as efficacy evidence.

## Timeline

The phase `v3-20260905T145904Z-llama_ledger-d5f0d615` expected and attempted 48 rows in fixed inventory order.

1. Rows 1–24: all 2,048-level ledger requests completed. Prompt range was 2,718–2,743 tokens; no infrastructure error occurred.
2. Row 25: `ecc006-001` at 8,192 completed (`11,189` prompt tokens; 600 events; target token positions 5,570/5,588/5,606/5,625).
3. Row 26: `ecc006-002` at 8,192 was the first infrastructure failure (`11,166` prompt tokens; 596 events; target positions 5,582/5,600/5,619/5,637). It returned `ConnectionResetError: [WinError 10054]` after 20,874.240 ms.
4. Rows 27–48: all returned `URLError` / WinError 10061 connection refused. They are dependent client observations after the listener was gone, not 22 independent primary faults.

The raw server log identifies the first 8k request as task 317 and the failing next request as task 325. Task 317 completed at server elapsed `1:21.785`; task 325 began at `1:25.420`. At `1:28.190`, stderr recorded `MUL_MAT failed` and `CUDA error: out of memory`.

## Server and process evidence

The retained stderr records the short diagnostic sequence:

> `E ggml_cuda_compute_forward: MUL_MAT failed`
>
> `E CUDA error: out of memory`

Windows Application Error 1000 at local 22:00:35 (15:00:35Z) records `llama-server.exe` crashing in `ucrtbase.dll` with exception `0xc0000409`; Windows Error Reporting 1001 corroborates the crash. The retained runner did not persist the child exit code, but log order, connection reset/refusals, and Windows telemetry establish process loss after the CUDA error.

## Untreated comparison

Reproduction, untreated, and ledger metadata all pin the same Llama artifact SHA, llama.cpp `0.2.0-dev` build `10566` commit `bb4caa754`, context 16,896, output allowance 16, temperature 0, seed 42, RTX 3050 Laptop GPU, and driver `595.95`.

The valid untreated 8k prompts were 8,136–8,192 tokens (median 8,169.5) and completed all 24 rows, with median latency 8,731.5 ms. Ledger 8k prompts were materially larger: the sole completed request had 11,189 tokens and took 11,792.9 ms; the next 11,166-token request coincided with CUDA OOM and process crash. This is an observed timing/resource association, not proof that every ledger prompt or fixed-field syntax is independently causal.

## Runner-policy audit

Gate B v3 required a canonical phase to stop on any infrastructure failure. `run_mn004_v3.py` catches each request exception, converts it into an invalid record, appends it, and continues the `for row in rows` loop. It did not fail fast after row 26. This is an implementation-policy nonconformance.

The nonconformance does not change the final v3 verdict: the first infrastructure failure already made the required ledger condition incomplete. Rows 27–48 are diagnostic residue, not independent evidence or an efficacy denominator.

## Root-cause classification

**`treatment_coupled_runtime_failure` — high confidence.**

Supporting evidence:

- 24 ledger 2k requests and one ledger 8k request completed before the failure.
- The process crashed while handling the next, substantially larger 8k ledger request.
- llama.cpp stderr reports CUDA OOM immediately before the listener disappears.
- Windows Application Error/Windows Error Reporting identify an `llama-server.exe` crash at the matching time.
- Same pinned hardware/runtime completed the untreated 2k+8k phase.

Limitation: retained telemetry does not isolate the exact allocation or prove that no unrelated concurrent GPU pressure contributed. There is no positive evidence of an external driver/OS interruption, and no runner evidence that port handling caused the CUDA OOM.

## Scientific meaning

Efficacy remains unknown: there is no valid ledger-versus-untreated reliability comparison, Llama no-harm result, or Qwen result. Operational feasibility has negative bounded evidence: this frozen ledger workload caused or coincided with CUDA OOM and llama-server process instability under the pinned environment.

## Telemetry gaps and future-contract implications

Historical evidence lacks persisted unexpected child exit code, process-death timestamp, per-request GPU-memory measurements, health checks after every request, request ordinal as an explicit field, fail-fast phase state, and a stderr-tail attachment keyed to the first error. A future separately authorized contract should retain those diagnostics and fail the whole canonical phase immediately at first infrastructure error. This is a requirement only, not a v4 design.
