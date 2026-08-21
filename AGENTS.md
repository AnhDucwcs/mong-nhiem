# Agent guide

`research/` is Mộng Nhiễm's canonical research knowledge base. It may be opened directly as an Obsidian vault.

Before substantial implementation or design work, read `research/00-mong-nhiem.md`, `research/concepts/architecture.md`, and `research/current-state.md`.

- Read `research/decisions/decisions.md` before making or changing architectural decisions.
- Read `research/research.md` when planning, implementing, evaluating, or interpreting research experiments.
- Treat `papers/` and `concepts/` as knowledge and reference, not implementation requirements; hypotheses require validation, while decisions are authoritative.
- Respect recorded architectural decisions; do not treat hypotheses as facts.
- Keep tasks narrow and do not implement roadmap items unless explicitly requested.
- Do not silently promote experimental code into `src/mong_nhiem/`.
- Run relevant tests before finishing.
- Update `research/current-state.md` after implementation work.
- Update `research/decisions/decisions.md` only for meaningful architectural changes.
