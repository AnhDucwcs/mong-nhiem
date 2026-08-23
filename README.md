# Mộng Nhiễm

Mộng Nhiễm researches how small language models can work reliably with knowledge and context spaces beyond their current effective capability.

MN-001 established the development foundation. MN-002 established a reproducible local model-qualification baseline; it does not validate an Effective Context Capacity (ECC) mechanism or select a production architecture. Under frozen MCB v0.3.0, Llama 3.2 3B and Qwen3-4B are qualified local baseline candidates.

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

Read the [research index](research/00-mong-nhiem.md), [current state](research/current-state.md), and [MN-002 overview](research/experiments/baselines/mn-002-model-qualification/README.md) before contributing.
