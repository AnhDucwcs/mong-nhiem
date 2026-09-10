# MN-004 v4 runtime-feasibility outcome

## Scope

V4 measures operational execution stability only. It does not score or interpret exact final-state correctness, does not resume v3, and does not make an efficacy claim about the globally indexed ledger.

## Authority

- V4 definition fingerprint: `43c6d00df6dd7daf55705f94ac04f361e74f682aba4b03c30082d2394024c1e4`
- Immutable source inventory fingerprint: `7183de0be8813764087e77330c5758970d40dfc9fe8553637faccca027d17897`
- Llama artifact SHA-256: `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`
- llama.cpp: `0.2.0-dev`, build `10566`, commit `bb4caa754`
- Frozen runtime: context `16,896`; output allowance `16`; temperature `0`; seed `42`; threads `12`; batch `2,048`; one parallel slot; flash attention enabled; prompt cache disabled.

## Retained blocked preflight

The first Stage A preflight, `v4-20260905T160852Z-stage_a_untreated-f0e92902`, found `Rusty's Retirement.exe` (PID `22548`) using the target GPU. It recorded `environment_contaminated` and correctly started neither llama-server nor a request. Because it had zero server starts and zero requests, it was a blocked preflight rather than the contract's single canonical Stage A attempt; it remains retained evidence.

## Stage A — untreated environment control

Canonical run: `v4-20260905T162540Z-stage_a_untreated-bfe64031`.

- Pre-phase compute processes: none.
- Fresh server: started, healthy, then intentionally terminated after the phase.
- Operational completion: `24/24` requests.
- Infrastructure/protocol failures: none.
- Prompt tokens: `8,136–8,192`, median `8,169.5`.
- Request latency: `6,469.080–9,038.457 ms`, median `6,831.768 ms`.
- GPU used VRAM at request boundaries: `2,267–2,279 MiB`; free VRAM `1,684–1,696 MiB`.

Model-output content and exact-answer score were retained but did not contribute to this operational verdict.

## Stage B — persistent-server ledger

Canonical run: `v4-20260905T163015Z-stage_b_ledger-db7c2c11`.

- Pre-phase compute processes: none.
- Fresh server: started, healthy, then intentionally terminated after the phase.
- Operational completion: `24/24` requests.
- Infrastructure/protocol failures: none.
- CUDA OOM/fatal CUDA/ggml diagnostics: none.
- Prompt tokens: `11,098–11,189`, median `11,150.5`.
- Request latency: `9,402.202–13,417.152 ms`, median `10,140.018 ms`.
- GPU used VRAM at request boundaries: `2,267–2,279 MiB`; free VRAM `1,684–1,696 MiB`.

The ledger median prompt was `2,981.0` tokens longer and its median request latency `3,308.250 ms` higher than untreated. The server log retained 17 allocator warnings about making room for a prompt-cache entry, but no CUDA/OOM/process-failure signature. These are operational diagnostics, not efficacy metrics.

## Stage C

Not authorized. Stage B completed all 24 requests, so the contract forbids C1/C2 crash-mechanism diagnostics.

## Operational conclusion

**`ledger_persistent_phase_completed`**

The v3 ledger CUDA OOM/process loss was not reproduced in this one uncontaminated v4 persistent-server attempt. This result does not establish ledger stability, does not identify why v3 crashed, and does not weaken or replace the retained v3 postmortem classification. V4 cannot distinguish per-request resource pressure from persistent-server/cumulative-state pressure because its predeclared diagnostic trigger did not occur.

## Efficacy boundary

Ledger efficacy remains unknown. V4 has no exact final-state reliability result, no treatment comparison for correctness, no Qwen execution, and no architecture-promotion evidence.
