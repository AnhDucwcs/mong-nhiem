"""Context budget configuration and model profiling subsystem for Mộng Nhiễm.

Enforces a deterministic default hard budget limit (512 tokens), while allowing
dynamic configuration via environment variables, programmatic overrides, or model profiles.
"""
from __future__ import annotations

import os
from typing import Dict, Optional

# Default hard context budget invariant (empirically validated in MN-009 & MN-011)
DEFAULT_CONTEXT_BUDGET: int = 512

# Canonical model budget profiles
# Accounts for tokenizer vocabulary density differences (e.g. 248k BPE subword expansion)
MODEL_BUDGET_PROFILES: Dict[str, int] = {
    "qwen3.5-2b": 420,
    "qwen3.5-4b": 512,
    "llama-3.2-3b": 512,
    "qwen3-4b": 512,
}


def register_model_budget_profile(model_name: str, budget: int) -> None:
    """Register or update a model budget profile."""
    if budget <= 0:
        raise ValueError(f"Budget must be positive, got {budget}")
    MODEL_BUDGET_PROFILES[model_name.strip().lower()] = budget


def resolve_context_budget(
    model_name: Optional[str] = None,
    override_budget: Optional[int] = None,
) -> int:
    """Resolve the effective hard context budget ceiling.

    Resolution precedence (highest to lowest):
    1. Explicit override_budget argument (if provided and positive).
    2. MONG_NHIEM_MAX_BUDGET environment variable (if set and valid int).
    3. Model-specific profile mapping from MODEL_BUDGET_PROFILES.
    4. DEFAULT_CONTEXT_BUDGET (512 tokens).
    """
    if override_budget is not None and override_budget > 0:
        return override_budget

    env_val = os.environ.get("MONG_NHIEM_MAX_BUDGET")
    if env_val and env_val.strip().isdigit():
        parsed = int(env_val.strip())
        if parsed > 0:
            return parsed

    if model_name:
        normalized = model_name.strip().lower()
        for key, budget in MODEL_BUDGET_PROFILES.items():
            if key in normalized:
                return budget

    return DEFAULT_CONTEXT_BUDGET
