# MN-007 Calibration Report (Clean Rerun: calibration-run-0002)

## 1. Execution Summary

- **Run Identifier**: `calibration-run-0002`
- **Execution Git Commit**: `bfecd515d90c97bd7c1d69cf5794e7523532b197`
- **Measurement Authority ID**: `mn007-calibration-measurement-authority-v1`
- **Authority Core SHA-256**: `2d5d82c1a342c34dfb0b3d35d0b6f0cef4dba835d8ebcc75e15398a2beab2633`
- **Model Path**: `artifacts/models/mn-002/Llama-3.2-3B-Instruct-Q4_K_M.gguf`
- **Model SHA-256**: `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`
- **Runtime Executable SHA-256**: `28d861538ffdf4e811e2febb0c5f06063792d184b66a2758f103c165629bc08`
- **Raw Evidence Path**: `runs/calibration-run-0002/raw_responses.jsonl`
- **Raw Evidence SHA-256**: `61f6697e67b33895414a49bc412569a422af10d6af01ba0dca4f300ec355a1d0`
- **Evaluator Results Path**: `runs/calibration-run-0002/evaluator_results.json`
- **Total Requests Attempted**: 108
- **Total Protocol-Valid Responses**: 108
- **Total Infrastructure Failures / Invalid Cases**: 0
- **Total Exact Correct Cases**: 14 / 108
- **Final Outcome**: `no usable operating region in bounded landscape`

## 2. Integrity & Provenance Validation

This clean rerun satisfies all strict provenance and hermetic execution constraints:
1. **Clean-Tree Gate**: Verified zero untracked or modified files before server launch at commit `bfecd51`.
2. **Preflight Environmental Hermeticity**:
   - `PROGRAMDATA\llama.cpp\config.ini` verified absent.
   - `APPDATA\llama.cpp\config.ini` verified absent.
   - All `LLAMA_*` prefixed variables and execution-relevant variables verified absent/unset.
   - GPU was idle at `0 MiB` memory, `0%` utilization prior to launch.
   - Zero stale `llama-server` or `llama-bench` processes existed.
3. **Exact Request Order**: 108 requests executed strictly in accordance with `mn007-interleaved-cell-round-robin-v1` (18 waves x 6 cells).
4. **Persist-Before-Evaluate**:
   - Every single response was flushed and fsynced to `raw_responses.jsonl` immediately upon receipt.
   - The server process was terminated before evaluation began.
   - `scripts/mn007_evaluator.py` reloaded and parsed the raw evidence directly from disk.
5. **No Mutation / No Retries**:
   - Zero retries, zero re-sendings, zero parameter tweaks.
   - Zero in-place string mutation or repair utilities used.

## 3. Cell Calibration Results

| Cell ID | Description | Total Attempted ($P_i$) | Exact Correct ($C_i$) | Accuracy | Classification |
|---|---|---|---|---|---|
| `e3-terminal` | 3 entities, terminal probe | 18 | 3 | 16.7% | `floor` |
| `e3-leading` | 3 entities, leading probe | 18 | 4 | 22.2% | `floor` |
| `e5-terminal` | 5 entities, terminal probe | 18 | 1 | 5.6% | `floor` |
| `e5-leading` | 5 entities, leading probe | 18 | 2 | 11.1% | `floor` |
| `e7-terminal` | 7 entities, terminal probe | 18 | 1 | 5.6% | `floor` |
| `e7-leading` | 7 entities, leading probe | 18 | 3 | 16.7% | `floor` |

## 4. Classification & Operating Region Determination

- **Criteria**:
  - `ceiling`: $P_i = 18 \land C_i \ge 17$
  - `usable`: $P_i = 18 \land 15 \le C_i \le 16$
  - `floor`: $P_i = 18 \land C_i \le 14$
- **Findings**:
  - All 6 candidate cells scored $C_i \le 4$, placing them definitively in the `floor` regime.
  - Zero cells qualified as `usable` or `ceiling`.
- **Selected Seed Cell**: None (`None`).
- **Conclusion**:
  - **`no usable operating region in bounded landscape`**.
  - As defined by the authoritative MN-007 design contract, this is a **bounded negative result**.
  - No adaptive degrees of freedom (modifying prompts, changing entity numbers, altering temperature, adjusting thresholds) are permitted within MN-007.
