# MN-002 qualification artefact retention

Keep every immutable benchmark definition, manifest/fingerprint, selected-run metadata, `results.jsonl`, summary, validation result, and the rendered qualification report in version control. These files are the reproducible evidence for a qualification decision.

Keep raw server diagnostics only for selected valid runs and for an invalid run that documents a material integration or model failure. Do not commit disposable retry diagnostics, model binaries, caches, or server executables. Record any deleted diagnostic's run ID, reason, and retention decision in the next qualification report.

The historical v0.1.0 and v0.2.0 artefacts remain unchanged. Their files are evidence for the audit, not inputs to v0.3.0 selection.
