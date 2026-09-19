# INVALID / BLOCKED RUN

This execution (calibration-run-0001) has been explicitly audited and quarantined.

**Reason:**
1. **Provenance Gap**: The run was executed from a dirty working tree.
2. **Evidence Mutation**: The raw response JSONL file was written with literal `\n` characters instead of actual linebreaks, and was subsequently overwritten in-place using `.split("\\n")` by an external script (`fix_raw.py`). The original pre-fix bytes were destroyed, making lossless repair unprovable.
3. **Persist-Before-Evaluate Violation**: The original executor evaluated the results in-memory rather than reloading the persisted raw artifact from disk.

**Disposition**:
This run must NOT be used to support MN-007 conclusions, calibration evidence, or benchmark behavior. It is retained solely for historical forensic completeness.
