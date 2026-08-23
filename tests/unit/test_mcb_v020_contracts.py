from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[2] / "research" / "experiments" / "baselines" / "mn-002-model-qualification" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import mcb_v020


def test_state_and_causal_cases_require_exact_only_answers() -> None:
    cases = mcb_v020.benchmark_cases()
    for case in cases:
        if case["suite"] in {"state_tracking", "causal_reasoning"}:
            assert "Return only" in case["input"]["prompt"]
            assert "without punctuation or explanation" in case["input"]["prompt"]


def test_native_thinking_is_disabled_only_for_verified_models() -> None:
    assert mcb_v020.template_kwargs("Qwen3-1.7B-Q4_K_M.gguf") == {"enable_thinking": False}
    assert mcb_v020.template_kwargs("SmolLM3-Q4_K_M.gguf") == {"enable_thinking": False}
    assert mcb_v020.template_kwargs("Llama-3.2-3B-Instruct-Q4_K_M.gguf") is None
