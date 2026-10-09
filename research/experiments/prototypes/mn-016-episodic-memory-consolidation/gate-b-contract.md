# Gate B Contract — Milestone MN-016: Measurement Contract & Evaluation Protocol

## 1. Workload Specification

The MN-016 evaluation benchmark consists of **40 deterministic long-horizon cases** ($T = 20-50$ steps per case), partitioned across three operational domains:

| Domain | Description | Cases | Target Horizon ($T$) | Primary Invariant Tested |
| :--- | :--- | :---: | :---: | :--- |
| **Domain A** | Multi-Phase Code Refactoring | 15 | $20 - 40$ steps | Function signatures refactored at $T=2$ must be invoked correctly at $T=35$ without stale call site mutations. |
| **Domain B** | Multi-Vault Asset Ledger & Audit | 15 | $25 - 50$ steps | Closed vaults and balance transfers executed early must be audited at $T=45$ without balance amnesia or overdrafts. |
| **Domain C** | Distributed System Registry & Leases | 10 | $20 - 45$ steps | Expired leases and migrated services must be respected across dozens of turns without stale routing. |

---

## 2. Experimental Arms

Evaluation compares three strictly controlled arms on Track 2 (Real Model Inference on `Qwen3.5-2B-Q4_K_M.gguf` via `llama-server.exe`):

- **Arm 1 (Sliding Window FIFO Baseline)**:
  - Working memory truncates oldest turns when approaching 512 tokens.
  - No episodic store, no consolidation, no recall affordances.
  - Measures baseline Historical Amnesia rate on sub-4B models.
- **Arm 2 (Cadence-Only AutoDream Control)**:
  - Host episodic store active with Cadence Gates ($\Delta T \ge 25$ ticks, $M \ge 10$ mutations).
  - *No Emergency Pressure Interceptor*: Evaluates vulnerability to context overflow under burst mutation sequences.
- **Arm 3 (Full MN-016: Dual-Trigger Host-Authoritative AutoDream)**:
  - Autonomous Three Gates (Ticks + Mutations + File Lock) + Emergency Context Budget Pressure Interceptor ($\ge 400$ tokens).
  - Host-Authoritative 4-Phase Consolidation with SHA-256 provenance hashes and deterministic contradiction pruning.
  - Demand-driven `ACTION: RECALL <entity_id>` via Dynamic GBNF logit masking.

---

## 3. Quantitative Success Rules & Support Thresholds

To qualify for Gate D promotion, Arm 3 must satisfy all five prospective gates:

1. **Rule 1 (Primary Efficacy Gate)**:
   $$\text{Accuracy}_{\text{Arm 3}} \ge 90.0\% \quad (36/40 \text{ cases})$$
2. **Rule 2 (Amnesia Remediation Delta)**:
   $$\Delta(\text{Arm 3} - \text{Arm 1}) \ge +50.0\% \quad (\ge +20/40 \text{ cases})$$
3. **Rule 3 (Strict Token Ceiling Invariant)**:
   $$\max(\text{Tokens}_{\text{prompt}}) \le 512 \quad \text{for 100.0\% of Arm 3 turns} \quad (\text{Mean} \le 384)$$
4. **Rule 4 (Latency SLA Invariant)**:
   $$\text{Mean Turn Latency} < 1000\text{ ms} \quad \text{on local GPU runtime}$$
5. **Rule 5 (Memory Contradiction Suppression)**:
   $$\text{Factual Contradiction Rate} = 0.0\% \quad \text{across all persisted entity cards in Arm 3}$$

---

## 4. Execution Protocol & Dual-Track Verification

- **Track 1 (Deterministic Simulator)**:
  - 40/40 cases executed on a verified Python state machine simulating exact tool execution, event logging, lock contention, and consolidation replay.
  - Verifies zero memory leaks, state transition correctness, and $< 0.1\text{ ms}$ consolidation latency.
- **Track 2 (Real Model Inference)**:
  - Real greedy decoding ($T=0.0$) against local `llama-server.exe` on `Qwen3.5-2B-Q4_K_M.gguf`.
  - Every model forward pass, tool dispatch, and memory snapshot persisted to `runs/run_0001/raw_responses.jsonl`.
  - Persist-before-evaluate policy enforced.

---

## 5. Pre-Run Manifest Requirements

Before executing any benchmark inference:
- The benchmark cases (`definition/cases.json`), prototype code (`src/`), and test suite (`tests/`) must be committed.
- All files must be hashed in `definition/pre-run-freeze-manifest.json` under git authority.
