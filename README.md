# Mộng Nhiễm

Mộng Nhiễm is a reusable research engine/library for helping small language models work effectively with knowledge and context spaces that exceed their native context window.

The repository is currently a development foundation only: it contains no research algorithms, model integrations, or established component interfaces.

## Repository layout

- `docs/` is the project source of truth.
- `src/mong_nhiem/` is the future reusable Python package.
- `experiments/` contains research work that is separate from the library.
- `configs/`, `tests/`, and `scripts/` are reserved for approved project work.
- `data/` and `artifacts/` hold local generated material and are ignored by Git.

## Development

Python 3.11 or newer is required. Install the minimal development tooling and run checks:

```powershell
python -m pip install -e ".[dev]"
ruff check .
pytest
```

Read [docs/PROJECT.md](docs/PROJECT.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) before making design or implementation changes.
