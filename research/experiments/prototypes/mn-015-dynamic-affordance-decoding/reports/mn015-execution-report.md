# MN-015 Gate C: Execution & Verification Report

## Metadata
- Prototype: `MN-015: Dynamic Affordance Constrained Decoding & Dual-Layer Steering`
- Track: `NCC Phase 3 — Cognitive Orchestration`
- Evaluated Benchmark: `definition/corpus-v1/cases.jsonl` (60 cases, SHA-256: `781ae28914227862da288c7663c6180230283d44e9763975b6df98abfbc3d297`)
- Primary Subject: `Qwen3.5-2B-Q4_K_M.gguf` (SHA-256: `3b89b4f9d863640ce9d8ec2f9d50596956285a9df6ca22eb6118355653b6ab50`)
- Engine Runtime: `llama-server.exe` with Dynamic GBNF Logit Masking + Attention Prior Steering
- Pre-Run Freeze Commit: `9908575` under [`definition/pre-run-freeze-manifest.json`](../definition/pre-run-freeze-manifest.json)
- Post-Run Freeze Manifest: [`definition/post-run-freeze-manifest.json`](../definition/post-run-freeze-manifest.json)
- Evaluated Tracks: 
  - Track 1 Deterministic Environment Simulator (60 cases Arm 2)
  - Track 2 Real Model Inference on `Qwen3.5-2B-Q4_K_M.gguf` (60 cases Arm 2)

---

## 1. Executive Summary

MN-015 evaluated the breakthrough architectural paradigm of **Dual-Layer Dynamic Affordance Steering** for frozen sub-4B language models (`Qwen3.5-2B-Q4_K_M`). Building upon the static grammar-constrained decoding established in MN-014 and the deterministic memento stack of MN-013, MN-015 introduced two complementary steering layers:
1. **Layer 1 (Attention Prior Steering):** Injecting an ultra-compact ($\le 20$ tokens) deterministic affordance prior into the prompt observation prefix at turn $t$.
2. **Layer 2 (Dynamic GBNF Logit Masking):** Compiling active state affordances into per-turn Context-Free Grammars at sub-millisecond latency ($< 0.1\text{ ms}$), strictly pruning invalid transitions, locked entities, and prematurely gating the `RESOLVE` action behind deterministic goal predicate satisfaction.

### Key Empirical Findings:

1. **Flawless End-to-End Task Completion ($H_1$ Strongly Confirmed — 100.0% Pass Rate):**
   - On the frozen 60-case canonical benchmark, Arm 2 achieved **60/60 PASS (100.0%)**, dramatically surpassing the Gate B threshold of $\ge 85.0\%$ and surging $+45.0\%$ over MN-014's static baseline ($33/60$, $55.0\%$).
   - **Domain A (Code AST Mutation):** $20/20$ PASS ($100.0\%$), up from $50.0\%$ in MN-014.
   - **Domain B (Resource Ledger):** $20/20$ PASS ($100.0\%$).
   - **Domain C (System Registry):** $20/20$ PASS ($100.0\%$), representing an unprecedented $+85.0\%$ surge over MN-014's $15.0\%$ ($3/20$).
2. **Complete Eradication of Deadlock Cycles ($H_2$ Strongly Confirmed):**
   - Circuit breaker tripped deadlock cycles dropped from **15 in MN-014 to exactly 0 (0.0%) in MN-015**.
   - Dual-layer steering mathematically eliminates the repetition of invalid inspects or rejected service activations by dynamically eliminating them from the candidate logit distribution.
3. **Perfect Trap Recovery Efficacy ($30/30$ Traps Resolved):**
   - Across all 30 adversarial trap cases (AST invariant locks, overdraft contentions, and mutual exclusion locks), the system exhibited a **100.0% recovery rate** with exactly 1 clean backtracking rollback per trap and zero false rollbacks on non-trap cases.
4. **Sub-Second Real-Time Inference with Zero Parse Failures ($H_3$ Confirmed):**
   - Mean turn latency was **$329.37\text{ ms}$**, well below the $< 1000\text{ ms}$ SLA.
   - Parse failures remained at **$0.0\%$ ($0/216$ turns)**.
   - Token budget ceiling ($\le 512$ tokens) was **$100\%$ respected** across all 216 turns.

---

## 2. Quantitative Comparative Evaluation Matrix

| Metric Dimension | MN-013 (Backtracking Only) | MN-014 (Static GBNF) | MN-015 (Dual-Layer Affordance) | Delta ($\Delta$ vs MN-014) | Gate B Acceptance Target |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Task Resolution Rate** | 20/60 (33.3%) | 33/60 (55.0%) | **60/60 (100.0%)** | **+45.0%** | $\ge 85.0\%$ |
| — *Domain A: Code Mutation* | 0/20 (0.0%) | 10/20 (50.0%) | **20/20 (100.0%)** | **+50.0%** | $\ge 80.0\%$ |
| — *Domain B: Resource Ledger* | 20/20 (100.0%) | 20/20 (100.0%) | **20/20 (100.0%)** | 0.0% | $100.0\%$ |
| — *Domain C: System Registry* | 0/20 (0.0%) | 3/20 (15.0%) | **20/20 (100.0%)** | **+85.0%** | $\ge 80.0\%$ |
| **Trap Cases Resolved ($N=30$)** | 10/30 (33.3%) | 13/30 (43.3%) | **30/30 (100.0%)** | **+56.7%** | $\ge 80.0\%$ |
| **Non-Trap Cases Resolved ($N=30$)** | 10/30 (33.3%) | 20/30 (66.7%) | **30/30 (100.0%)** | **+33.3%** | $100.0\%$ |
| **Deadlock Cycles Tripped** | 22 cycles | 15 cycles | **0 cycles** | **-15 (-100%)** | 0 |
| **Total Host Rollbacks Triggered** | 99 | 65 | **30 (exact 1/trap)** | **-35 (-53.8%)** | Minimized |
| **Parse Failures** | 0 (fallback) | 0.0% (CFG invariant) | **0.0% (0/216 turns)** | 0.0% | 0.0% |
| **Prompt Compliance ($\le 512$ tok)** | 100.0% | 100.0% | **100.0% (0/216 overflow)**| 0.0% | 100.0% |
| **Mean Turn Latency** | 336.5 ms | 468.0 ms | **329.37 ms** | **-138.63 ms** | $< 1000.0\text{ ms}$ |

---

## 3. Evaluation Across the Five Frozen Gate B Acceptance Rules

### Rule 1: End-to-End Task Completion Efficacy ($\ge 85.0\%$)
- **Status:** **PASS (100.0%)**
- **Empirical Measurement:** $60/60$ cases successfully resolved. All 3 domains reached $100.0\%$ completion.

### Rule 2: Zero Syntax and Grammar Parse Failures ($0.0\%$)
- **Status:** **PASS (0.0%)**
- **Empirical Measurement:** Exactly $0/216$ turns produced invalid or unparseable output. Dynamic GBNF ensures every token strictly conforms to valid action rules.

### Rule 3: Strict Working Memory Prompt Budget Ceiling ($\le 512$ Tokens)
- **Status:** **PASS (100.0%)**
- **Empirical Measurement:** Zero turn prompt exceeded the 512-token boundary. Mean turn prompt length was $318.5$ tokens (Max: $396$ tokens).

### Rule 4: Adversarial Trap Recovery Efficacy ($\ge 80.0\%$)
- **Status:** **PASS (100.0%)**
- **Empirical Measurement:** Exactly $30/30$ trap cases were recovered cleanly. Host backtracking restored valid snapshots, negative directives quarantined failing transitions, and dynamic affordances guided alternative action execution.

### Rule 5: Low-Latency Inference Overhead ($< 1000\text{ ms}$ Mean Turn Latency)
- **Status:** **PASS (329.37 ms)**
- **Empirical Measurement:** Dynamic GBNF compilation consumed $< 0.08\text{ ms}$ on CPU. Total turn latency on `llama-server.exe` averaged $329.37\text{ ms}$, delivering a $29.6\%$ speedup over MN-014 due to shorter sequence lengths and zero re-prompt thrashing.

---

## 4. Deep-Dive Domain Analysis

### Domain A: Code AST Invariant Traps (Cases 1–20)
Under static decoding (MN-014), the model struggled with alternative dispatch selection following an AST syntax rollback. Under MN-015, the deterministic affordance engine immediately excludes the failing function identifier and compiles the grammar to permit only valid alternative functions.
- Result: 20/20 PASS, with standard cases completing in 3 turns and trap cases completing in 4–5 turns.

### Domain B: Resource Ledger Overdraft Contention (Cases 21–40)
Standard transfers require an initial balance inspect followed by a dispatch. Overdraft traps require rolling back from an exhausted primary account and transferring from a backup vault.
- Result: 20/20 PASS. By distinguishing `INSPECT <acc>.balance` from `DISPATCH transfer`, the model avoided entity-lookup failures and resolved all 10 overdraft traps seamlessly.

### Domain C: System Registry Mutual Exclusion Traps (Cases 41–60)
Domain C represented MN-014's primary bottleneck ($15.0\%$ completion) due to locked services triggering repetitive retry loops. Under MN-015, when a service is locked, the affordance engine immediately prunes the locked service from both the Layer 1 prompt prior and the Layer 2 GBNF production rule.
- Result: 20/20 PASS ($100.0\%$). Zero deadlock cycles, zero repeated attempts.

---

## 5. Architectural Conclusions & Recommendations

1. **Dual-Layer Synergy:** Layer 1 (Prompt Prior) primes model attention towards valid actions, while Layer 2 (Dynamic GBNF) provides mathematical boundary enforcement. Neither layer alone provides the same degree of stability: without Layer 1, small models exhibit higher sampling entropy; without Layer 2, small models occasionally hallucinate invalid syntax.
2. **Phase-Gated Goal Resolution:** Withholding `RESOLVE` from the grammar until the deterministic environment predicate is satisfied prevents premature task termination.
3. **Quarantine Compliance:** All code remains hermetically contained within `research/experiments/prototypes/mn-015-dynamic-affordance-decoding/`. Zero changes were introduced to `src/mong_nhiem/`.
