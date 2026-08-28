# Mộng Nhiễm

Mộng Nhiễm researches how small language models can work reliably with knowledge and context spaces beyond their current effective capability.

MN-001 established the development foundation. MN-002 is complete and frozen: MCB v0.3.0 is the canonical reproducible capability-qualification benchmark, with definition fingerprint `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`. Llama 3.2 3B and Qwen3-4B are qualified capability baselines, not production-model selections. MN-003 has completed its bounded Effective Context Capacity direct-context measurement and synthesis phase. Its retained evidence maps model-specific retrieval, State Tracking, and causal-reasoning behavior under context pressure; no context-management architecture has been selected.

## Layout

- `research/` is the canonical research knowledge base and Obsidian vault.
- `research/experiments/` contains research baselines and prototypes, separate from reusable code.
- `src/mong_nhiem/` is the reusable package boundary.
- `data/` and `artifacts/` hold local generated material and are ignored by Git.

## Development

Python 3.11 or newer is required.

```powershell
python -m pip install -e ".[dev]"
ruff check .
pytest
```

Read the [research index](research/00-mong-nhiem.md), [current state](research/current-state.md), [MN-002 overview](research/experiments/baselines/mn-002-model-qualification/README.md), and [MN-003 charter](research/experiments/prototypes/mn-003-effective-context-capacity/README.md) before contributing.
