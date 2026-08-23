#!/usr/bin/env python3
"""Derive auxiliary llama-bench rates from its preserved JSON arrays."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for run in ROOT.joinpath("runs").glob("*"):
    source = run / "raw" / "llama-bench-verified.stdout.txt"
    summary_file = run / "summary.json"
    if not source.is_file() or not summary_file.is_file():
        continue
    try:
        tests = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(tests, list):
            continue
        pp = next((float(x["avg_ts"]) for x in tests if x.get("n_prompt", 0) > 0 and x.get("n_gen", 0) == 0), None)
        tg = next((float(x["avg_ts"]) for x in tests if x.get("n_gen", 0) > 0 and x.get("n_prompt", 0) == 0), None)
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        summary["performance"]["llama_bench_prompt_tokens_per_second"] = pp
        summary["performance"]["llama_bench_generation_tokens_per_second"] = tg
        summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{run.name}: pp={pp} tg={tg}")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"{run.name}: could not parse performance: {error}")
