# Gate B Evaluation Contract: Milestone MN-020

## 1. Quantitative Acceptance Criteria Matrix

| Metric ID | Clause Description | Mathematical Bound | Target Arm | Hard Gate |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Multi-Agent Task Resolution Rate | $\ge 85.0\%\ (51/60)$ | Arm 3 | Mandatory PASS |
| **M2** | Governance Superiority Delta | $\ge +40.0\%$ | Arm 3 vs Arm 2 | Mandatory PASS |
| **M3** | Committed Race Condition Breaches | $\equiv 0$ | Arm 3 | Mandatory PASS |
| **M4** | Deadlock / Mutual Starvation Cycles | $\equiv 0$ | Arm 3 | Mandatory PASS |
| **M5** | Per-Turn Prompt Token Ceiling | $\le 512\text{ tokens}$ | All Arms / Turns | Mandatory PASS |
| **M6** | Turn Latency SLA | $< 1000\text{ ms}$ | Host Arbiter Turn | Mandatory PASS |
| **M7** | Multi-Agent AutoDream Compaction | $\ge 70.0\%$ | Arm 3 | Mandatory PASS |
| **M8** | Cryptographic Manifest & Zip Sealing | $100\%$ Conformance | All Runs | Mandatory PASS |

---

## 2. Evidence Packaging & Audit Integrity Invariants

### Clause 8.1 (Zero Loose File Bloat Protocol)
1. **Packaging**: Every benchmark run MUST compress all individual episode audit traces (`*.json`) into a single archive file named `audit_logs.zip` inside the run directory using Python standard library `zipfile` (`ZIP_DEFLATED`).
2. **Post-Compression Cleanup**: Following successful creation and verification of `audit_logs.zip`, all loose JSON files in `audit_logs/` MUST be pruned from the working tree before git staging.
3. **Cryptographic Fingerprint**: The SHA-256 hash of `audit_logs.zip` MUST be recorded in `run_info.json` and committed to the post-run freeze manifest.
4. **Direct Non-Destructive Auditability**: Evaluation scripts and post-run validators (`validate_audit.py`) MUST support inspecting episode traces directly from `audit_logs.zip` without requiring unzipping to disk.

---

## 3. Evaluation Protocol & Model Specifications

1. **Subjects**: Homogeneous pair of $2\times \text{Qwen3.5-2B-Q4_K_M.gguf}$ instances served via local `llama-server.exe` on Port 18502.
2. **Corpus**: $N = 60$ standardized episodes:
   - Domain A: Collaborative Microgrid Balancing ($N=20$).
   - Domain B: Concurrent Orbital Maintenance ($N=20$).
   - Domain C: Joint Fleet Logistics ($N=20$).
3. **Dual-Track Sequencing**:
   - Track 1: Deterministic Multi-Agent Simulator proof.
   - Track 2: Real Model Inference via HTTP API at $T=0.0$.
4. **Anti-Falsification Invariant**: All benchmark metrics must be computed directly from sealed execution logs. No retroactive threshold modifications are permitted.
