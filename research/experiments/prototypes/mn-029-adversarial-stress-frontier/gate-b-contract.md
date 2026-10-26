# Gate B Evaluation Contract: Milestone MN-029

## 1. Frozen Acceptance Clauses ($M_1 \to M_{12}$)

This contract establishes the quantitative acceptance criteria for Milestone MN-029: Adversarial Cognitive Frontier & Stress-Test Suite. All thresholds are frozen prior to benchmark execution and cannot be relaxed retroactively under Mộng Nhiễm anti-falsification rules.

| Clause ID | Metric Name | Mathematical Definition | Acceptance Threshold | Falsification Condition |
| :--- | :--- | :--- | :--- | :--- |
| **M1** | Lookahead Deadlock Avoidance | $\frac{N_{\text{survived}}}{N_{\text{total}}}$ on 4-step lookahead scenarios | $\ge 95.0\%$ | $M_1 < 95.0\%$ |
| **M2** | Commit-Time Invariant Breaches | Count of physical threshold violations during mid-inference spikes | $\equiv 0$ breaches | $M_2 > 0$ |
| **M3** | Diagnostic Probe Forcing Rate | $\frac{N_{\text{probe\_enforced}}}{N_{\text{equifinality}}}$ on stuck sensor telemetry | $\equiv 100.0\%$ | $M_3 < 100.0\%$ |
| **M4** | Operator Intent Extraction Accuracy | $\frac{N_{\text{correct\_action}}}{N_{\text{chaotic\_utterances}}}$ under GBNF dynamic enum | $\ge 95.0\%$ | $M_4 < 95.0\%$ |
| **M5** | Cumulative Drift Retention Rate | $\frac{N_{\text{retained}}}{N_{\text{cumulative}}}$ across 100-tick compaction runs | $\equiv 100.0\%$ | $M_5 < 100.0\%$ |
| **M6** | Bimodal Coherence & Zero False Positives | Detection accuracy on desync pairs ($\ge 98.0\%$) AND FP rate on contrastive speech | Acc $\ge 98.0\%$, FP $\equiv 0.0\%$ | Acc $< 98\%$ or FP $> 0\%$ |
| **M7** | Multi-Agent Livelock Resolution | $\frac{N_{\text{preempted}}}{N_{\text{cyclic\_standby}}}$ within 3 ticks of deadlock | $\equiv 100.0\%$ | $M_7 < 100.0\%$ |
| **M8** | FFI Soak Memory Drift & Safety | $\Delta\text{RSS}$ over $100,000\text{ ticks}$ AND process crash count | $\Delta\text{RSS} < 0.5\text{ MB}$, Crashes $\equiv 0$ | $\Delta\text{RSS} \ge 0.5\text{ MB}$ or Crash |
| **M9** | Three-Way Crash Recovery Determinism | Rate of clean recovery to tick $N-1$ with KV slot cache erased | $\equiv 100.0\%$ | $M_9 < 100.0\%$ |
| **M10** | Max Working Prompt Tokens | $\max_t \text{Tokens}_t$ across all scenarios | $\le 512\text{ tokens}$ | $\text{Tokens}_{\max} > 512$ |
| **M11** | Mean Turn Latency | $\frac{1}{K}\sum_{k=1}^K T_{\text{turn}, k}$ on local hardware | $< 1000\text{ ms}$ SLA | $\bar{T}_{\text{turn}} \ge 1000\text{ ms}$ |
| **M12** | Zero Loose File Bloat Protocol | Verification of sealed `audit_logs.zip` and zero loose JSON logs | $\equiv 100.0\%$ | Loose JSON logs present |

---

## 2. Phased Execution Batching

To ensure surgical containment and prevent regression across the 515 existing test cases, evaluation proceeds across three sequential batches:

1. **Batch 1 (Real-Time Safety & C-ABI Robustness):**
   - Targets: $M_2$ (Mid-Inference Race), $M_6$ (Bimodal Desync), $M_8$ (FFI Soak & Fuzzing).
   - Test Suite: `tests/stress/test_batch1_safety_and_ffi.py`.
2. **Batch 2 (Concurrency, Lookahead & Crash Persistence):**
   - Targets: $M_1$ (Lookahead Deadlock), $M_7$ (Multi-Agent Livelock), $M_9$ (Three-Way Crash Recovery).
   - Test Suite: `tests/stress/test_batch2_concurrency_and_persistence.py`.
3. **Batch 3 (Perception, Memory & Speech Intent):**
   - Targets: $M_3$ (Byzantine Sensor), $M_4$ (Chaotic Operator ASR), $M_5$ (Sub-Threshold Compaction).
   - Test Suite: `tests/stress/test_batch3_memory_and_perception.py`.

---

## 3. Mandatory Telemetry & Audit Packaging

In accordance with the **Zero Loose File Bloat Protocol**:
1. All raw test execution logs must be sealed into `audit_logs.zip` archives within `runs/`.
2. No loose JSON log files may be committed to Git.
3. Each run directory must contain an authenticated `summary.json` manifest recording the aggregate metric distribution and SHA-256 archive checksum.
