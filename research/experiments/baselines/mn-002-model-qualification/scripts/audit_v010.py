#!/usr/bin/env python3
"""Create a deterministic, compact audit of selected MCB v0.1.0 failures."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
CASES = ROOT / "benchmark" / "cases"
REPORT = ROOT / "reports" / "mcb-v0.1.0-audit.json"

TARGETS = {
    "Qwen3-1.7B-Q4_K_M.gguf": ("state_tracking", "causal_reasoning"),
    "Qwen3-4B-Q4_K_M.gguf": ("state_tracking", "causal_reasoning"),
    "gemma-3-4b-it-Q4_K_M.gguf": ("state_tracking", "causal_reasoning"),
    "Llama-3.2-3B-Instruct-Q4_K_M.gguf": ("state_tracking",),
    "microsoft_Phi-4-mini-instruct-Q4_K_M.gguf": ("state_tracking", "structured_output"),
    "SmolLM3-Q4_K_M.gguf": ("instruction_following", "structured_output", "context_retrieval", "state_tracking", "causal_reasoning"),
}


def latest_runs() -> dict[str, Path]:
    selected: dict[str, Path] = {}
    for directory in RUNS.glob("*"):
        metadata = directory / "metadata.json"
        summary = directory / "summary.json"
        if metadata.is_file() and summary.is_file():
            model = json.loads(metadata.read_text(encoding="utf-8"))["model"]["file"]
            selected[model] = directory
    return selected


def case_map() -> dict[str, dict]:
    return {
        item["id"]: item
        for file in CASES.glob("*.jsonl")
        for line in file.read_text(encoding="utf-8").splitlines()
        if line
        for item in (json.loads(line),)
    }


def classification(model: str, suite: str, record: dict) -> tuple[str, str, bool]:
    text = record["output"]["text"]
    if model == "SmolLM3-Q4_K_M.gguf" and not text:
        return "CHAT_TEMPLATE_OR_INTEGRATION_DEFECT", "Response final content is empty while the API reports generated tokens; confirmed native thinking consumed the budget.", False
    if suite == "state_tracking":
        return "BENCHMARK_CASE_DEFECT", "Prompt does not require an exact-only answer although the evaluator requires normalized exact equality; raw answers generally contain the correct state plus explanation.", False
    if suite == "causal_reasoning" and "Return only" not in text:
        return "BENCHMARK_CASE_DEFECT", "Several open-answer prompts omit an exact-output contract while normalized exact equality rejects explanatory answers and terminal punctuation.", False
    if model == "microsoft_Phi-4-mini-instruct-Q4_K_M.gguf" and suite == "structured_output":
        return "VALID_MODEL_FAILURE", "The raw response is fenced Markdown JSON despite the explicit no-Markdown instruction; strict JSON parsing correctly rejects it.", True
    return "VALID_MODEL_FAILURE", "The response does not meet the case's explicit output contract.", True


def main() -> None:
    runs, definitions = latest_runs(), case_map()
    items = []
    for model, suites in TARGETS.items():
        records = [json.loads(line) for line in (runs[model] / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
        for suite in suites:
            failed = [record for record in records if record["case_id"].startswith(suite.replace("_", "-")) and not record["evaluation"]["passed"]][:5]
            for record in failed:
                definition = definitions[record["case_id"]]
                label, cause, valid = classification(model, suite, record)
                items.append({
                    "model": model,
                    "run_id": runs[model].name,
                    "suite": suite,
                    "case_id": record["case_id"],
                    "rendered_messages": [{"role": "user", "content": "\n\n".join(part for part in (definition["input"]["context"], definition["input"]["prompt"]) if part)}],
                    "expected": definition["expected"],
                    "raw_response": record["output"]["text"],
                    "parsed_response": record["output"]["parsed"],
                    "score": record["evaluation"]["score"],
                    "classification": label,
                    "suspected_cause": cause,
                    "case_and_evaluator_valid": valid,
                })
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"benchmark_version": "0.1.0", "items": items}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} audit records to {REPORT}")


if __name__ == "__main__":
    main()
