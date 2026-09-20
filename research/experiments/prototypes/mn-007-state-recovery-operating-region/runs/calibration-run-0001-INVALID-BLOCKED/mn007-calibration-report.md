# MN-007 Calibration Report

## 1. Execution Summary

- **Measurement Authority**: `mn007-calibration-measurement-authority-v1`
- **Final Outcome**: `no usable operating region in bounded landscape`
- **Total Requests Attempted**: 108
- **Total Protocol-Valid Responses**: 108
- **Total Infrastructure Failures / Invalid Cases**: 0
- **Total Exact Correct Cases**: 14 / 108

## 2. Integrity Validation

All pre-flight execution constraints were met, ensuring hermetic measurement limits:
- **Corpus Fingerprints**: Unchanged.
- **Authority Core SHA-256**: `2d5d82c1a342c34dfb0b3d35d0b6f0cef4dba835d8ebcc75e15398a2beab2633` (Unchanged).
- **Model / Runtime / Request Order**: Unchanged.
- **Environment**: Clean (case-insensitive `LLAMA_*` check passed, config paths `PROGRAMDATA` / `APPDATA` verified absent and frozen in child process).
- **Execution Policy**: Strictly exactly-once, NO retries invoked.

## 3. Evaluated Metrics

| Cell | Total Attempted ($P_i$) | Exact Correct ($C_i$) | Classification |
|---|---|---|---|
| `e3-terminal` | 18 | 3 | `floor` |
| `e3-leading` | 18 | 4 | `floor` |
| `e5-terminal` | 18 | 1 | `floor` |
| `e5-leading` | 18 | 2 | `floor` |
| `e7-terminal` | 18 | 1 | `floor` |
| `e7-leading` | 18 | 3 | `floor` |

## 4. Conclusion

The model (Meta Llama 3.2 3B Instruct, Q4_K_M) failed to establish a reliable baseline operating region for the exact ordered two-state vector extraction task within the bounded search space (E3 - E7). All cells fell into the `floor` classification ($C_i \le 14$).

Following the MN-007 rule strictly, this constitutes a bounded negative result. We will **NOT** adaptively change thresholds, prompts, search boundaries, or fallback rules within this experiment space.

The execution boundary is successfully concluded. No usable seed cell identified.
