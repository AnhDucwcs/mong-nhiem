# Roadmap

## MN-001 — Development foundation

Status: completed.

## MN-002 — Model qualification

Status: completed and frozen. MCB v0.3.0 is the canonical capability-qualification benchmark (fingerprint `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`). Llama 3.2 3B and Qwen3-4B are qualified capability baselines; capability and runtime evidence remain separate. This is not a production-model choice.

## MN-003 — Effective Context Capacity

Status: active baseline research. ECC-001, ECC-002, and ECC-003 infrastructure and canonical measurements are complete; MN-003 remains open while direct-context evidence is extended without an architecture intervention.

1. ECC-001 establishes a falsifiable direct-context degradation hypothesis, 20 deterministic Context Retrieval cases, and a controlled token-length ladder.
2. ECC-001 supports both MN-002-qualified capability baselines and fixes midpoint evidence, generation, evaluation, model, and runtime controls.
3. The canonical runner and offline validator retain actual per-model token counts, raw evidence, degradation curves, and threshold metrics.
4. Canonical complete evidence from both qualified models has been produced and validated from clean commit `701fb1fe417bde7db6f4749479955c37a734616d`.
5. ECC-001 found stable 1.00 accuracy through 16,384 requested tokens. ECC-002 then increased only semantic interference by placing the unmarked target among same-template confusable registry records; its frozen fingerprint is `824ba4d6df62f8ddf4a49d90a2e2d4d44211399c730c831f2bf0338ba8e5c7cf`.
6. ECC-002 measured a monotonic Llama 3.2 3B curve from 1.00 to 0.85 (ECC95 = 4,096; ECC90 = 8,192; ECC80 >= 16,384 tested tokens) while Qwen3-4B remained 1.00 through the ladder (all three thresholds right-censored >= 16,384). This is direct-context evidence, not a production-model selection or architecture result.
7. ECC-003 isolates evidence position in the ECC-002 confusable task. It finds Llama 3.2 3B position-sensitive at 16,384 tested tokens (early 1.00, middle 0.85, late 0.70) while Qwen3-4B remains 1.00 at all tested positions and levels. The Llama late curve is non-monotonic, so this is not a simple lost-in-the-middle conclusion. Its frozen fingerprint is `9c7e541c2810fa0e7d063b45f94312d434d58c87e965131c90dff3e0613345f2`.
8. Continue with a bounded confirmatory direct-context experiment—more independent cases or a harder inherited capability—before considering retrieval, memory, RAG, summarization, compression, or context-routing architectures.
9. Keep any future architecture experiment separate, and promote only proven reusable components into `src/mong_nhiem/` through an explicit decision.
