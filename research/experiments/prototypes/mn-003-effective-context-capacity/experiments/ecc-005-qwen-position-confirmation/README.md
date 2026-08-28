# ECC-005 — Qwen Position Confirmation

Definition frozen; execution pending. ECC-005 is a Qwen3-4B-only direct-context control for ECC-003, using 30 fresh cases at 8,192/16,384 requested tokens and early/late positions only: exactly 120 canonical requests. It reuses Qwen's `enable_thinking=false` inference contract and restart-per-position server lifecycle to release 4 GB GPU VRAM. It is not a production selection or architecture experiment.

The primary endpoint is 16k early−late accuracy and paired early-pass/late-fail versus reverse transitions. The predeclared interpretation treats a gap no greater than 0.10 with no four-case directional transition imbalance as stable; early>late otherwise is possible sensitivity; gap >=0.10 with at least four net early-pass/late-fail transitions is position sensitivity observed. Exact scoring remains unchanged; deterministic diagnostics include numeric-suffix malformed output.
