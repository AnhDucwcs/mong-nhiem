#!/usr/bin/env python3
"""One-time construction of frozen MCB v0.3.0 JSONL from v0.2.0 files."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import mcb_v030

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmark" / "v0.2.0" / "cases"
TARGET = mcb_v030.CASES
STATE_ALIASES = {
    "state-tracking-002": ["Blue"], "state-tracking-005": ["archive"],
    "state-tracking-006": ["the bead"], "state-tracking-011": ["Aya, Cy"],
}


def aliases(case: dict) -> list[str]:
    answer = str(case["expected"]["value"])
    values = [answer]
    if case["suite"] == "context_retrieval":
        match = re.search(r"what is the (.+) for (.+)\?", case["input"]["prompt"], re.IGNORECASE)
        if match:
            field, subject = match.groups()
            values += [f"the {field} for {subject} is {answer}", f"the {field} is {answer}"]
    elif case["suite"] == "state_tracking":
        values += STATE_ALIASES.get(case["id"], [])
    elif case["suite"] == "causal_reasoning":
        prompt = case["input"]["prompt"].casefold()
        if answer.startswith("the "):
            values.append(answer[4:])
        if prompt.startswith("who wakes"):
            values += ["the guard wakes", "guard wakes"]
        if prompt.startswith("what starts"):
            values += ["the sensor starts", "sensor starts"]
        if not prompt.startswith(("does", "is", "can")):
            values.append(f"the consequence is that {answer}")
    return values


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE.glob("*.jsonl")):
        entries = []
        for line in source.read_text(encoding="utf-8").splitlines():
            case = copy.deepcopy(json.loads(line))
            case["version"] = 3
            if case["evaluation"]["method"] == "json_schema":
                case["expected"]["accepted_values"] = [json.dumps(case["expected"]["schema"], sort_keys=True)]
            else:
                case["expected"]["accepted_values"] = aliases(case)
            entries.append(case)
        (TARGET / source.name).write_text("".join(json.dumps(case, ensure_ascii=False) + "\n" for case in entries), encoding="utf-8")
    mcb_v030.validate_definitions()
    manifest = {"id": "mcb", "version": "0.3.0", "supersedes": "0.2.0", "definition_fingerprint": mcb_v030.definition_fingerprint(), "evaluation_change": "Non-format suites use explicitly declared accepted answers with conservative surface normalization; strict instruction and JSON suites remain strict.", "minimum_overall_score": 0.80, "suites": [{"id": suite, "cases": 20, "critical": True, "minimum_score": threshold} for suite, threshold in zip(mcb_v030.SUITES, (.80, .90, .80, .70, .70), strict=True)]}
    (mcb_v030.BENCHMARK / "manifest.yaml").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
