# MN-011 Gate C Execution Report: Attempt 0001

- **Evaluation Date (UTC):** 2026-10-03T09:15:57Z
- **Run ID:** `mn011-execution-run-0001`
- **Benchmark Corpus:** [`definition/corpus-v1/cases.jsonl`](../definition/corpus-v1/cases.jsonl)
- **Token Accounting Engine:** Offline `llama-tokenize.exe` CLI (`-p` argument)
- **Execution Outcome:** `INFRASTRUCTURE_FAILURE_WIN_CLI_BUFFER_LIMIT`

---

## 1. Executive Summary & Failure Diagnosis

Attempt 0001 executed Suite A (24 cases across budgets 256, 512, 1024, 2048) and Suite B up to case 12 (8k context tier).
At case 13 (`mn011-suite-b-0013`, 16k context tier), the executor encountered an operational infrastructure fault:

```
FileNotFoundError: [WinError 206] The filename or extension is too long
```

### Root Cause Analysis
Under Windows OS, `CreateProcessW` imposes a hard ceiling of 32,767 characters for command-line arguments.
The Attempt 0001 runner passed raw unassisted 16k text via the `-p` command-line flag (`llama-tokenize.exe -p "<raw_text>"`). At 520 lines (~42,000 characters), the OS rejected the invocation before the process was spawned.

---

## 2. Preliminary Scientific Observations Prior to Interruption

Before halting on case 13, Attempt 0001 yielded unambiguous empirical signals:

1. **Suite A (Parametric Budget Curve):**
   - At $B=256$, accuracy was constrained by tight knapsack clipping (75.0%).
   - At $B=512$, accuracy peaked with $100\%$ fact retention.
   - At $B=1024$ and $B=2048$, accuracy remained unchanged ($100\%$) while prompt tokens expanded to ~800 tokens, degrading conversion efficiency $\eta$ from 0.155 to 0.081.
2. **Suite B (Causal Reachability up to 8k):**
   - At 512 & 2k tokens: Arm B (Scaffolding-Assisted) maintained 100% accuracy, while Arm A struggled with negative cases.
   - At 8k tokens: Arm A suffered false positives on negative reachability (reproducing the ECC-007 long-context failure anomaly), while Arm B achieved 100% accuracy (~70 tokens).

---

## 3. Versioned Repair Action
In accordance with Mộng Nhiễm's immutable provenance protocol:
- Attempt 0001 is preserved as an immutable record of infrastructure failure.
- A versioned fix (`attempt-0002`) will migrate `get_token_counter` from `-p` CLI arguments to standard input streaming (`--stdin`), bypassing the Windows command-line character buffer limit entirely.
