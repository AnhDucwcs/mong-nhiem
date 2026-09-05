# MN-004 v4 runtime-feasibility outcome

## Scope

V4 measures operational execution stability only. It does not score or interpret exact final-state correctness, does not resume v3, and does not make an efficacy claim about the globally indexed ledger.

## Authority

- V4 definition fingerprint: `43c6d00df6dd7daf55705f94ac04f361e74f682aba4b03c30082d2394024c1e4`
- Immutable source inventory fingerprint: `7183de0be8813764087e77330c5758970d40dfc9fe8553637faccca027d17897`
- Llama artifact SHA-256: `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`
- llama.cpp: `0.2.0-dev`, build `10566`, commit `bb4caa754`
- Frozen runtime: context `16,896`; output allowance `16`; temperature `0`; seed `42`; threads `12`; batch `2,048`; one parallel slot; flash attention enabled; prompt cache disabled.

## Stage A — untreated environment control

Run: `v4-20260905T160852Z-stage_a_untreated-f0e92902`.

Before starting llama-server, required `nvidia-smi` telemetry found a non-experiment compute process on the target GPU:

- PID `22548`: `Rusty's Retirement.exe`
- GPU: NVIDIA GeForce RTX 3050 Laptop GPU, driver `595.95`
- VRAM at observation: `190 MiB` used of `4,096 MiB`

The frozen contamination rule therefore produced `environment_contaminated`. No llama-server process was started, no request was issued, and no model response or exact-answer score exists. Stage A completion is `0/24` requests because the canonical phase was not allowed to begin, not because the model failed.

## Stage B and Stage C

Stage B ledger was blocked because Stage A did not complete under an uncontaminated environment. Stage C diagnostics were consequently not authorized. There is no untreated-versus-ledger resource comparison and no v4 reproduction test of the v3 CUDA OOM.

## Operational conclusion

**`environment_contaminated`**

V4 cannot distinguish per-request resource pressure from persistent-server/cumulative-state pressure. It does not weaken or strengthen the retained v3 postmortem classification; it supplies no new ledger runtime-failure evidence because no canonical model execution occurred.

## Efficacy boundary

Ledger efficacy remains unknown. V4 has no exact final-state reliability result, no Llama treatment comparison, no Qwen execution, and no architecture-promotion evidence.
