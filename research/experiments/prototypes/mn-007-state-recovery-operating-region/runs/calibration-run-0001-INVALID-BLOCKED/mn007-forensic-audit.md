# MN-007 Forensic Audit Report

## 1. Exact Execution Chronology

Based on system task logs and git history:

1. **Invocation 1 (13:13:46Z)**: `python scripts/mn007_executor.py`
   - **Result**: Failed preflight (`measurement/design blocked: Forbidden execution var set: LOCALAPPDATA`).
   - **Type**: Preflight-only invocation. No server launch.
2. **Invocation 2 (13:13:55Z, Task-743)**: `$env:LOCALAPPDATA = ... python scripts/mn007_executor.py`
   - **Result**: Passed preflight. Launched `llama-server.exe`. Crashed immediately with `KeyError: 'public_prompt'` before sending any requests.
   - **Type**: Model-serving invocation. 0 requests sent.
3. **Invocation 3 (13:14:11Z, Task-749)**: `$env:LOCALAPPDATA = ... python scripts/mn007_executor.py`
   - **Result**: Passed preflight. Launched `llama-server.exe`. Crashed with `KeyError: 'public_prompt'`.
   - **Type**: Model-serving invocation. 0 requests sent.
4. **Staging Cleanup (13:14:45Z)**: `rm -Recurse -Force runs/calibration_pass` executed.
5. **Invocation 4 (13:14:54Z, Task-767)**: `$env:LOCALAPPDATA = ... python scripts/mn007_executor.py`
   - **Result**: Passed preflight. Launched server. Sent 108 requests. Wrote to `runs/calibration-run-0001/raw_responses.jsonl` (with literal `\n` bug). Evaluated in memory and printed results to stdout at 13:16:03Z.
   - **Type**: Request-sending invocation. 108 requests sent.
6. **Repair Invocation (13:16:09Z)**: `python scripts/fix_raw.py` executed to mutate the raw evidence file.
7. **Evidence Commit (13:16:27Z)**: Git commit `736a125` incorporating both the dirty executor and the repaired evidence.

## 2. Deleted Staging Directory (`runs/calibration_pass`)
- The directory was created by Invocation 2 and 3.
- Because the script crashed at the request preparation stage (`req_data = ... p["public_prompt"]`), it never executed the `open(..., "a")` statement.
- **Fact**: `runs/calibration_pass` existed but contained NO calibration request/response evidence or partial execution state. It was an empty directory when deleted.

## 3. Raw Evidence Mutation & Lossless-Repair
- **Original format**: Task 767 wrote each JSON record followed by the two literal characters `\n` (`\\n` in Python).
- **Mutation**: `fix_raw.py` read the file into memory, applied `.split("\\n")`, and wrote back using the standard LF (`\n`) delimiter.
- **Danger**: `split("\\n")` performs a global string split. If any model response payload had contained a literal `\n`, the JSON object would have been corrupted/split.
- **Pre-fix bytes**: The original malformed bytes were overwritten in-place and were **not retained** in any git commit or complete log output.
- **Lossless determination**: Because the original artifact no longer exists, a lossless repair transformation *cannot be cryptographically proven*. The provenance is unresolved.

## 4. Exactly-Once Audit
- 108 requests were sent exclusively during Invocation 4.
- However, because the raw evidence provenance is broken by the in-place repair, the exactly-once persistence cannot be independently verified from the final artifact alone without relying on trust.

## 5. Executor Provenance
- The executor was initially committed at `ec3cef9`.
- It was then modified in the working tree (fixing `prompt`, `expected_vector`, and run directory).
- Invocation 4 ran using this **uncommitted, dirty working tree**.
- The executor was finally committed in `736a125` after execution and repair.
- **Conclusion**: There is a provenance gap. The exact executor state during measurement was not frozen in Git prior to execution.

## 6. Evaluation Integrity
Chronology:
1. Model response received.
2. Raw persistence (with literal `\n` defect).
3. **Evaluation** (performed *in-memory* on the Python dictionary objects at 13:16:03Z).
4. Raw repair (`fix_raw.py` at 13:16:09Z).
- **Fact**: The evaluator did NOT read from the persisted artifact. It evaluated data prior to its defective serialization and subsequent repair. 

## 7. Final Classification
**`measurement/design blocked`**

**Reasoning**:
Evidence integrity cannot be confirmed due to:
1. **Unresolved Lossless Repair**: Original raw bytes were destroyed, preventing verification that `fix_raw.py` did not semantically alter the JSON payloads.
2. **Evaluator Provenance Gap**: The evaluator scored in-memory data rather than the persisted immutable artifact, violating the strict `persist-before-evaluate` read boundary.
3. **Executor Provenance Gap**: The measurement was executed from an uncommitted working tree.
