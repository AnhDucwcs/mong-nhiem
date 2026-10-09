# Agent Guide

`research/` is Mộng Nhiễm's canonical research knowledge base and may be opened directly as an Obsidian vault.

## 1. Mandatory Reading Before Substantial Implementation or Design Work

Before undertaking substantial implementation, architectural, or experiment work, you MUST read:
- `research/00-mong-nhiem.md` (Master entrypoint and navigational hub).
- `research/concepts/architecture.md` (Core architectural principles and state separation).
- `research/current-state.md` (Latest authoritative project state and empirical findings).
- `research/roadmap.md` (Canonical milestone sequencing and active phase).
- `research/decisions/decisions.md` (Authoritative Architectural Decision Records; read before proposing or modifying decisions).
- `research/research.md` (Empirical research methodology, falsification criteria, and gate protocols).
- For work inside `research/experiments/`: read `research/experiments/README.md` and the specific milestone prototype files (`README.md`, `charter.md`, and `gate-b-contract.md`).

## 2. Mandatory Synchronization & Documentation Updates Upon Completion

After completing any milestone prototype, experiment, or architectural phase, you MUST synchronously update:
- `research/current-state.md`: Update milestone progress, empirical evidence tables, and active transition handoffs.
- `research/decisions/decisions.md`: Append an ADR record for any meaningful architectural or evaluation disposition.
- `research/roadmap.md`: Update status markers (mark finished milestone as completed/verified, activate next milestone).
- `research/00-mong-nhiem.md`: Synchronize milestone narrative summary and update Obsidian navigation links.
- `research/experiments/README.md`: Append the milestone to the active experiments inventory.
- Root `README.md`: Synchronize the master Milestone Progression table.
- Prototype milestone artifacts:
  - `README.md`: Summary of milestone, architecture, and reproduction steps.
  - `charter.md`: Formal Gate A research questions and falsification criteria.
  - `gate-b-contract.md`: Quantitative acceptance criteria and evaluation bounds.
  - `reports/*.md`: Empirical evaluation reports generated from benchmark runs.
  - `gate-d-disposition-review.md`: Architectural disposition review and promotion recommendations.
  - Cryptographic manifests: Ensure `pre-run-freeze-manifest.json` and `post-run-freeze-manifest.json` are fully hashed and committed.

## 3. Academic Reporting & Technical Documentation Standards

All research reports, prototypes, manifests, diagrams, and knowledge base files MUST adhere to strict academic standards:
- **Language Invariant:** 100% professional technical English. Never use non-English text or informal colloquialisms anywhere in `research/` or technical artifacts (except the project name "Mộng Nhiễm").
- **Zero Decorative Icons / Emojis:** Strictly prohibited from using emojis, symbols, or icons (such as checkmarks, crosses, warning signs, or decorative emblems) in any report, table, heading, or code comment. Use plain text tokens (`PASS`, `FAIL`, `INCONCLUSIVE`, `WARNING`).
- **Academic Report Structure:** All benchmark reports (`reports/*.md`) must follow a peer-reviewed academic paper format:
  1. *Executive Summary / Abstract*: Quantitative headline metrics and disposition verdict.
  2. *Hypotheses Formulation*: Explicit mathematical statements ($H_1, H_2, \dots$) with falsification thresholds.
  3. *Experimental Methodology*: Independent variables (arms), control variables, token ceilings ($\le 512$), and hardware configuration.
  4. *Quantitative Results*: Full empirical distributions (Mean, Median, P95, Max) for task success, token consumption, and turn latency ($< 1000\text{ ms}$).
  5. *Failure Taxonomy & Error Analysis*: Rigorous categorization of failure modes (e.g., token overflow, state regression, syntax violation).
  6. *Threats to Validity*: Internal, external, and construct validity limitations.
  7. *Compliance Assessment*: Unambiguous clause-by-clause audit against the Gate B evaluation contract.
- **Empirical & Mathematical Rigor:** Present all equations and budget constraints using LaTeX math notation ($O(1)$, $\le 512$ tokens, $\Delta T \ge 25$, $M \ge 10$).
- **Raison d'Être Invariant:** Preserve the fundamental architectural separation: the LLM is an isolated reasoning engine emitting structured actions; the Host maintains absolute authority over state integrity, provenance auditing, and deterministic state replay.

## 4. Development & Governance Constraints

- Treat `papers/` and `concepts/` as knowledge and reference, not implementation requirements; hypotheses require validation, while decisions are authoritative.
- Respect recorded architectural decisions; do not treat hypotheses as facts.
- Keep tasks narrow and do not implement future roadmap items unless explicitly requested.
- **Do not silently promote experimental code into `src/mong_nhiem/`:** Prototypes remain quarantined in `research/experiments/prototypes/` until earned promotion under a formal Gate D disposition review.
- Run the full relevant test suite (`pytest`) and verify zero regressions before finalizing work.

